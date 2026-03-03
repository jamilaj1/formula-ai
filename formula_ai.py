import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. GLOBAL THEME & INTERFACE CONFIG ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="wide")

# Forcing Gemini Dark Mode and styling the chat input
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
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & SESSION MANAGEMENT ---
@st.cache_resource
def init_db() -> Client:
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    is_dark = st.toggle("Dark Mode ✨", value=True, key="global_theme_toggle_switch")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            display_name = user_data.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except Exception:
            display_name = "Jamil Abduljalil"
            
        st.markdown(f"**Operator:**\n### {display_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="sidebar_logout_btn_unique"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Free Formulas")
        if st.button("Unlock Pro 🔓", key="sidebar_upgrade_btn_unique"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register"])
    
    with tab1:
        e_log = st.text_input("Professional Email", key="auth_login_email_unique")
        p_log = st.text_input("Password", type="password", key="auth_login_pass_unique")
        if st.button("Authenticate & Enter", key="auth_login_submit_unique"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception:
                st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        n_reg = st.text_input("Full Name", placeholder="e.g. Jamil Abduljalil", key="auth_reg_name_unique")
        e_reg = st.text_input("Professional Email", key="auth_reg_email_unique")
        p_reg = st.text_input("Password (6+ characters)", type="password", key="auth_reg_pass_unique")
        if st.button("Initialize Pro Account", key="auth_reg_submit_unique"):
            try:
                res = supabase.auth.sign_up({"email": e_reg, "password": p_reg, "options": {"data": {"full_name": n_reg}}})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error during registration: {e}")

# --- 5. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue.")
        return

    # AI Configuration
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your manufacturing query...", key="main_chat_input_unique"):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat.send_message(f"Professional Engineering Response: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_e:
                    st.error(f"AI System Busy: {ai_e}")
    except Exception as e:
        st.error(f"Critical System Error: {e}")

# --- 6. ROUTING ENGINE ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Laboratory", key="global_back_nav_unique"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
