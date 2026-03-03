import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. STABLE PAGE CONFIGURATION ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# The Professional Dark Style that worked perfectly
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    section[data-testid="stSidebar"] { background-color: #1e1f20; }
    .gemini-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stChatInputContainer { background-color: #1e1f20; border-radius: 28px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION & DB INITIALIZATION ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- 3. AUTHENTICATION MODULE (Fixed Unique Keys) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        # Fixed DuplicateElementId by using unique keys for Jamil's app
        e_log = st.text_input("Professional Email", key="auth_login_email_safe")
        p_log = st.text_input("Password", type="password", key="auth_login_pass_safe")
        if st.button("Access Laboratory", key="btn_login_safe"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Please check credentials.")

    with tab2:
        e_reg = st.text_input("Professional Email", key="auth_reg_email_safe")
        p_reg = st.text_input("Password", type="password", key="auth_reg_pass_safe")
        if st.button("Initialize Account", key="btn_reg_safe"):
            try:
                supabase.auth.sign_up({"email": e_reg, "password": p_reg})
                st.success("Account created successfully! Please login.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. MAIN WORKSPACE (Gemini 1.5 Flash Stable) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        # Direct reference to Jamil's operator status
        st.success(f"Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="btn_logout_safe"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.write("Advanced Industrial Intelligence Laboratory")

    # AI Config - Fixed model call to ensure stability
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Displaying historical workspace dialogue
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input at the bottom of the workspace
        if prompt := st.chat_input("Enter your manufacturing query...", key="chat_input_safe"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Senior Engineer persona for Jamil Abduljalil
                response = model.generate_content(f"Expert Industrial Engineer: {prompt}")
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
    except Exception as e:
        st.error(f"AI Core Busy. Details: {e}")

# --- 5. ROUTING ENGINE ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
