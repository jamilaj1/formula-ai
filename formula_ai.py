import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION & GLOBAL THEME ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# CSS for Gemini Dark Aesthetics (Eliminating all white backgrounds)
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_db()

# Session state for user management
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    theme_toggle = st.toggle("Dark Mode ✨", value=True, key="main_theme_switch")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_info = supabase.auth.get_user()
            display_name = user_info.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except Exception:
            display_name = "Jamil Abduljalil"
            
        st.markdown(f"**Operator:**\n### {display_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="logout_action_btn"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free Usage: {st.session_state.free_usage}/2 Formulas")
        if st.button("Unlock Pro 🔓", key="unlock_pro_sidebar_btn"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        e_in = st.text_input("Professional Email", key="auth_login_email_field")
        p_in = st.text_input("Security Password", type="password", key="auth_login_pass_field")
        if st.button("Authenticate & Enter", key="auth_login_submit_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_in, "password": p_in})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception:
                st.error("❌ Authentication Failed: Please check your credentials.")

    with tab2:
        n_in = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="auth_reg_name_field")
        e_s = st.text_input("Email Address", key="auth_reg_email_field")
        p_s = st
