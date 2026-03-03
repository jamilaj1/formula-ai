import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# ==========================================
# 1. PAGE CONFIG & DEEP DARK THEME
# ==========================================
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# Force-kill white backgrounds and implement Gemini Charcoal aesthetics
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

# ==========================================
# 2. DATABASE & SESSION INITIALIZATION
# ==========================================
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# ==========================================
# 3. AUTHENTICATION (FIXED DUPLICATE IDs)
# ==========================================
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    with tab1:
        # Unique keys are CRITICAL to stop the DuplicateElementId crash
        e_log = st.text_input("Professional Email", key="unique_auth_login_email")
        p_log = st.text_input("Security Password", type="password", key="unique_auth_login_pass")
        if st.button("Authenticate & Enter", key="unique_auth_login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Please verify your credentials.")

    with tab2:
        n_reg = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="unique_auth_reg_name")
        e_reg = st.text_input("Professional Email", key="unique_auth_reg_email")
        p_reg = st.text_input("New Password (6+ characters)", type="password", key="unique_auth_reg_pass")
        if st.button("Initialize Pro Account", key="unique_auth_reg_btn"):
            try:
                # Basic signup to bypass schema cache issues (PGRST205)
                res = supabase.auth.sign_up({"email": e_reg, "password": p_reg, "options": {"data": {"full_name": n_reg}}})
                st.success("Account initialized successfully! You can now login.")
            except Exception as e:
                st.error(f"Registration Error: {e}")

# ==========================================
# 4. MAIN LABORATORY (FIXED 404 MODEL)
# ==========================================
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="unique_global_logout_btn"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; margin-top:-20px;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # Standard stable model identifier to avoid 404 errors
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Display historical workspace messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Final chat input located at page bottom
        if prompt := st.chat_input("Enter manufacturing query or batch requirements...", key="unique_main_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing parameters..."):
                    try:
                        response = model.generate_content(f"Expert Chemical Engineer Response for Jamil: {prompt}")
                        answer = response.text
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as ai_e:
                        st.error(f"AI System Busy. Details: {ai_e}")
    except Exception as sys_e:
        st.error(f"System Configuration Error: {sys_e}")

# ==========================================
# 5. GLOBAL ROUTING
# ==========================================
if not st.session_state.user_email:
    render_auth()
    if st.button("← Back to Preview", key="unique_global_back_btn"):
        st.session_state.user_email = None
        st.rerun()
else:
    render_main()
