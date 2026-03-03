import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. THE ULTIMATE VISUAL OVERRIDE (Hard-Coded Dark Mode) ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# CSS to force Gemini Dark Theme and eliminate all white background patches
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

# --- 2. DATABASE & SESSION INITIALIZATION ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- 3. AUTHENTICATION MODULE (Fixed Duplicate IDs & Schema Errors) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    with tab1:
        email = st.text_input("Professional Email", key="unique_login_email")
        password = st.text_input("Password", type="password", key="unique_login_pass")
        if st.button("Access Laboratory", key="unique_login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Please verify your credentials.")

    with tab2:
        reg_email = st.text_input("Professional Email", key="unique_reg_email")
        reg_pass = st.text_input("New Password", type="password", key="unique_reg_pass")
        if st.button("Initialize Account", key="unique_reg_btn"):
            try:
                # Basic registration that works even without extra DB tables
                supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                st.success("Account created successfully! You can now login.")
            except Exception as e:
                st.error(f"Registration Error: {e}")

# --- 4. MAIN LABORATORY INTERFACE (Gemini-1.5-Flash Stable) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="unique_logout_btn"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; margin-top:-20px;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    # AI Engine Configuration
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # Standard stable model string to avoid 404
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Display Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input Area
        if prompt := st.chat_input("Enter your manufacturing query...", key="unique_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing parameters..."):
                    try:
                        response = model.generate_content(f"Expert Chemical Engineer Response: {prompt}")
                        answer = response.text
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"AI System Busy. Error: {e}")
    except Exception as sys_e:
        st.error(f"System Configuration Error: {sys_e}")

# --- 5. GLOBAL ROUTING ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
