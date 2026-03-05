import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import uuid

# --- 1. PAGE SETUP (Must be the first Streamlit command) ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# CSS Force Dark Theme
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
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_connections():
    # Supabase Connection
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    # AI Config
    genai.configure(api_key=st.secrets["API_KEY"])
    return sb

supabase = init_connections()

# --- 3. AUTHENTICATION (Fixed Duplicate ID & Schema Errors) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        e_log = st.text_input("Professional Email", key="auth_login_email_safe")
        p_log = st.text_input("Password", type="password", key="auth_login_pass_safe")
        if st.button("Authenticate & Enter", key="auth_login_btn_safe"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("❌ Authentication failed. Verify credentials.")

    with tab2:
        n_reg = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="auth_reg_name_safe")
        e_reg = st.text_input("Email", key="auth_reg_email_safe")
        p_reg = st.text_input("Security Password", type="password", key="auth_reg_pass_safe")
        if st.button("Initialize Pro Account", key="auth_reg_btn_safe"):
            try:
                auth_res = supabase.auth.sign_up({"email": e_reg, "password": p_reg, "options": {"data": {"full_name": n_reg}}})
                # Add usage entry to fix PGRST205 error
                supabase.table("users_usage").insert({"email": e_reg, "is_pro": True}).execute()
                st.success("✅ Account created! Please login.")
            except Exception as e: st.error(f"❌ Error: {e}")

# --- 4. MAIN LABORATORY (Fixed 404 Model Error) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="sidebar_logout_safe"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown('<p class="gemini-title">Formula AI Pro</p>', unsafe_allow_html=True)

    # Solve the 404 error by using the stable model string
    # We use a TRY block to catch issues before they crash the UI
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # Fixed stable identifier
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Enter your manufacturing query...", key="main_chat_input_safe"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Professional engineer response
                    response = model.generate_content(f"Expert Chemical Engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as ai_e:
                    st.error(f"⚠️ AI Core Busy. Error: {ai_e}")
    except Exception as e:
        st.error(f"🛑 Critical Model Error: {e}")

# --- 5. ROUTING ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
