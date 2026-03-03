import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIG & GEMINI DARK THEME ---
st.set_page_config(page_title="Formula AI | Pro", page_icon="🧪", layout="wide")

# Theme State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# Gemini Dark Palette Colors
if st.session_state.theme_mode == "Dark":
    main_bg = "#131314"
    card_bg = "#1e1f20"
    sidebar_bg = "#1e1f20"
    text_main = "#e3e3e3"
    text_dim = "#b4b4b4"
    accent = "linear-gradient(90deg, #4285f4, #9b72cb, #d96570)"
else:
    main_bg = "#ffffff"
    card_bg = "#f0f4f9"
    sidebar_bg = "#f0f4f9"
    text_main = "#1f1f1f"
    text_dim = "#444746"
    accent = "#0b57d0"

# Professional CSS Injection
st.markdown(f"""
<style>
    .stApp {{ background-color: {main_bg}; color: {text_main}; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg}; border-right: 1px solid rgba(255,255,255,0.05); }}
    
    /* Gemini-style Main Title */
    .gemini-title {{
        font-size: 3.5rem; font-weight: 700; text-align: left;
        background: {accent}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px; font-family: 'Google Sans', sans-serif;
    }}
    
    /* Card Design */
    .premium-card {{
        background: {card_bg};
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Buttons */
    .stButton>button {{
        border-radius: 50px; background-color: {accent if st.session_state.theme_mode == "Light" else "#1e1f20"};
        color: white; border: 1px solid rgba(255,255,255,0.1); padding: 10px 24px; transition: 0.3s;
    }}
    .stButton>button:hover {{ border-color: #4285f4; transform: scale(1.02); }}

    /* Chat Styling */
    .stChatMessage {{ background-color: transparent; border: none; font-size: 1.1rem; }}
    .stChatInputContainer {{ background-color: {card_bg}; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); }}
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE LOGIC ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Workspace")
    
    # Elegant Theme Toggle
    theme_toggle = st.toggle("Dark Mode ✨", value=(st.session_state.theme_mode == "Dark"))
    st.session_state.theme_mode = "Dark" if theme_toggle else "Light"
    
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            name = user_data.user.user_metadata.get("full_name", "Operator")
        except: name = "Member"
        
        st.markdown(f"**Verified Account**\n### {name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCOUNT</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free formulas: {st.session_state.free_usage}/2")
        if st.button("Get Full Access 🔓"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. MAIN LABORATORY INTERFACE ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:{text_dim}; font-size:1.5rem; margin-top:-20px;'>How can I help you today?</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.markdown(f"""
        <div class="premium-card">
            <h2 style="color:#d96570">Usage limit reached</h2>
            <p style="color:{text_dim}">Please login to continue using the industrial formulation engine.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Chat Engine
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your request..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = model.generate_content(f"User is {name if is_pro else 'Guest'}. Answer in user language but technicals in English: {prompt}")
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"System overloaded: {e}")

# --- 5. AUTHENTICATION MODULE ---
def render_auth():
    st.markdown('<p class="gemini-title">Welcome to Formula AI</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("Enter Workspace"):
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user_email = res.user.email
            st.rerun()
    with tab2:
        n = st.text_input("Full Name")
        e_s = st.text_input("Email")
        p_s = st.text_input("Password", type="password")
        if st.button("Create Account"):
            res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
            st.session_state.user_email = res.user.email
            st.rerun()

# --- 6. ROUTING ENGINE ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
