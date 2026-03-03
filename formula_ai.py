import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. PAGE CONFIG & VISUAL OVERRIDE ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# CSS to force the Jamil Formula Dark Theme and eliminate white backgrounds
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

# --- 2. SESSION & DATABASE ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- 3. AUTHENTICATION (Fixed Duplicate ID & Schema Errors) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    with tab1:
        # Unique keys prevent the 'DuplicateElementId' error from your previous screenshots
        e_log = st.text_input("Professional Email", key="unique_log_email")
        p_log = st.text_input("Password", type="password", key="unique_log_pass")
        if st.button("Authenticate & Enter", key="unique_log_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Please verify credentials.")

    with tab2:
        e_reg = st.text_input("Professional Email", key="unique_reg_email")
        p_reg = st.text_input("Create Password", type="password", key="unique_reg_pass")
        if st.button("Initialize Account", key="unique_reg_btn"):
            try:
                # Signup using standard Auth to avoid schema issues (PGRST205)
                supabase.auth.sign_up({"email": e_reg, "password": p_reg})
                st.success("Account created successfully! You can now login.")
            except Exception as e:
                st.error(f"Registration Error: {e}")

# --- 4. MAIN LABORATORY (Gemini 1.5 Stable) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        # Direct personalization for Jamil Abduljalil
