import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. SETTINGS & THEME ENGINE ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Gemini Dark Colors
if st.session_state.theme_mode == "Dark":
    bg, side, txt, card = "#131314", "#1e1f20", "#e3e3e3", "#1e1f20"
    border = "#444746"
else:
    bg, side, txt, card = "#ffffff", "#f0f4f9", "#1f1f1f", "#f8fafd"
    border = "#c4c7c5"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {side} !important; border-right: 1px solid rgba(255,255,255,0.05); }}
    .gemini-title {{
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}
    .stChatInputContainer {{ background-color: {card} !important; border: 1px solid {border} !important; border-radius: 28px !important; }}
    section[data-testid="stSidebar"] .stMarkdown p {{ color: {txt} !important; }}
    header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR (Toggle & Profile) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
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

# --- 4. AUTHENTICATION PAGE ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Email", key="log_e")
        p = st.text_input("Password", type="password", key="log_p")
        if st.button("Access Laboratory", key="btn_log"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Invalid credentials.")
    with tab2:
        n = st.text_input("Full Name", key="reg_n")
        e_s = st.text_input("Email", key="reg_e")
        p_s = st.text_input("Password", type="password", key="reg_p")
        if st.button("Initialize Pro", key="btn_reg"):
            try:
                res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as ex: st.error(f"Error: {ex}")

# --- 5. MAIN APP ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#b4b4b4; font-size:1.2rem;'>Welcome to your workspace, {st.session_state.theme_mode} mode active.</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue.")
        return

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # التصحيح: استدعاء الموديل بالاسم الصحيح
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask anything about formulations..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat.send_message(f"As an expert chemical engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_err:
                    st.error(f"AI Error: {ai_err}")
    except Exception as e:
        st.error(f"System Error: {e}")

# --- 6. ROUTING ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Preview"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
