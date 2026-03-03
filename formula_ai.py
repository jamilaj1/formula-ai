import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. SETTINGS & FORCE GEMINI DARK THEME ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# CSS to kill the white background and force Charcoal/Dark theme
st.markdown("""
<style>
    .stApp { background-color: #131314 !important; color: #e3e3e3 !important; }
    section[data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid rgba(255,255,255,0.05); }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #444746 !important; border-radius: 28px !important; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ---
@st.cache_resource
def init_db():
    try: return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_db()
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR (Personalized for Jamil Abduljalil) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace", unsafe_allow_html=True)
    is_dark = st.toggle("Dark Mode ✨", value=True) # Always defaults to Dark
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_res = supabase.auth.get_user()
            name = user_res.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except: name = "Jamil Abduljalil"
        st.markdown(f"**Operator:**\n### {name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Formulas")
        if st.button("Unlock Full Access 🔓"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE (Fixed Duplicate IDs) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Email", key="login_email_unique")
        p = st.text_input("Password", type="password", key="login_pass_unique")
        if st.button("Enter Laboratory", key="btn_login_final"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Invalid credentials.")
    with tab2:
        n = st.text_input("Full Name", key="signup_name_unique")
        e_s = st.text_input("Email", key="signup_email_unique")
        p_s = st.text_input("Password", type="password", key="signup_pass_unique")
        if st.button("Initialize Pro Account", key="btn_signup_final"):
            try:
                res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as ex: st.error(f"Error: {ex}")

# --- 5. MAIN APP INTERFACE ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue.")
        return

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
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
                    response = st.session_state.chat.send_message(f"Expert Chemical Engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_err: st.error(f"AI System Busy: {ai_err}")
    except Exception as e: st.error(f"System Load Error: {e}")

# --- 6. ROUTING ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Preview", key="back_to_lab"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
