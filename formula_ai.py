import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime
import uuid

# --- 1. PAGE & FORCE DARK THEME ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# CSS to kill white patches and force Jamil's custom workspace look
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

# --- 2. SESSION INITIALIZATION ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 3. DATABASE & AI CORE ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

def get_ai_model():
    genai.configure(api_key=st.secrets["API_KEY"])
    # Fixed model name to avoid 404 errors
    return genai.GenerativeModel("gemini-1.5-flash")

# --- 4. AUTHENTICATION (Fixed Duplicate IDs) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        # Added unique keys to prevent DuplicateElementId error
        email_log = st.text_input("Professional Email", key="login_email_unique")
        pass_log = st.text_input("Password", type="password", key="login_pass_unique")
        if st.button("Access Laboratory", key="login_btn_unique"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email_log, "password": pass_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Authentication failed. Please check credentials.")

    with tab2:
        name_reg = st.text_input("Full Name", placeholder="Jamil Abduljalil", key="reg_name_unique")
        email_reg = st.text_input("Professional Email", key="reg_email_unique")
        pass_reg = st.text_input("Password", type="password", key="reg_pass_unique")
        if st.button("Create Account", key="reg_btn_unique"):
            try:
                # Signup only (removed the users_usage table call to avoid PGRST205 error)
                supabase.auth.sign_up({"email": email_reg, "password": pass_reg, "options": {"data": {"full_name": name_reg}}})
                st.success("Account created! Please login to continue.")
            except Exception as e: st.error(f"Registration Error: {e}")

# --- 5. MAIN LABORATORY ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="logout_btn_main"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    
    model = get_ai_model()

    # Display Chat History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Chat Interaction
    if prompt := st.chat_input("Enter manufacturing inquiry...", key="main_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # System prompt for engineering expertise
                response = model.generate_content(f"As a Senior Chemical Engineer, answer Jamil's query: {prompt}")
                answer = response.text
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"AI Core Busy. Error: {e}")

    if st.button("Clear Chat", key="clear_chat_btn"):
        st.session_state.chat_history = []
        st.rerun()

# --- 6. ROUTING ---
if not st.session_state.user_email:
    render_auth()
    if st.button("← Back to Preview", key="back_btn_nav"):
        st.session_state.user_email = None # Placeholder for back nav
        st.rerun()
else:
    render_main()
