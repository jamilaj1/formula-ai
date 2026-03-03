import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# --- 2. DYNAMIC THEME ENGINE ---
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Define colors based on theme selection
if st.session_state.theme_mode == "Dark":
    bg, side, txt, card, border = "#131314", "#1e1f20", "#e3e3e3", "#1e1f20", "#444746"
else:
    bg, side, txt, card, border = "#ffffff", "#f0f4f9", "#1f1f1f", "#f8fafd", "#c4c7c5"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {side} !important; }}
    .stChatInputContainer {{ background-color: {card} !important; border: 1px solid {border} !important; border-radius: 28px !important; }}
    .gemini-title {{
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    section[data-testid="stSidebar"] .stMarkdown p {{ color: {txt} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE & SESSION ---
@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_db()
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 4. SIDEBAR (Restored Toggle & Profile) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    
    # Restored Dark Mode Switch
    is_dark = st.toggle("Dark Mode ✨", value=(st.session_state.theme_mode == "Dark"))
    st.session_state.theme_mode = "Dark" if is_dark else "Light"
    
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_res = supabase.auth.get_user()
            name = user_res.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except: name = "Jamil Abduljalil"
        
        st.markdown(f"**Operator:**\n### {name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free usage: {st.session_state.free_usage}/2")
        if st.button("Unlock Pro 🔓"):
            st.session_state.show_auth = True
            st.rerun()

# --- 5. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#b4b4b4; font-size:1.2rem;'>Welcome to your workspace, {st.session_state.theme_mode} mode active.</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please login to continue.")
        return

    # Chat Engine (Fixed Model Name)
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask anything about formulations..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = model.generate_content(f"Expert Engineer: {prompt}")
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"AI Core Error: {e}")

# --- 6. AUTHENTICATION & ROUTING ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("Access Lab"):
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user_email = res.user.email
            st.rerun()
    with tab2:
        n = st.text_input("Full Name")
        e_s = st.text_input("Email")
        p_s = st.text_input("Password", type="password")
        if st.button("Initialize Pro"):
            res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
            st.session_state.user_email = res.user.email
            st.rerun()

if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
