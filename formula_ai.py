import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE SETUP & DESIGN ---
st.set_page_config(page_title="Formula AI | Platform", page_icon="🧪", layout="centered")

st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;}
    .stat-value { font-size: 2.5rem; font-weight: 800; color: #2563EB; }
    .stat-label { font-size: 1rem; color: #475569; font-weight: 600; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 10px 0; }
    .auth-header { font-size: 1.5rem; font-weight: 700; color: #1E293B; margin-bottom: 5px; }
    .auth-sub { font-size: 0.95rem; color: #64748B; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONFIGURATION ---
@st.cache_resource
def init_db() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Database Initialization Error: {e}")

ADMIN_EMAIL = "jamilaj1@gmail.com"

# --- 3. SESSION STATE MANAGEMENT ---
if "user_email" not in st.session_state: 
    st.session_state.user_email = None
if "is_admin" not in st.session_state: 
    st.session_state.is_admin = False

# --- 4. AUTHENTICATION (LOGIN & SIGN UP) ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sign in or create an account to access the advanced formulation laboratory.</p>', unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    # --- LOGIN TAB ---
    with tab1:
        st.markdown('<div class="auth-header">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Please enter your credentials to access your workspace.</div>', unsafe_allow_html=True)
        
        l_email = st.text_input("Professional Email", placeholder="name@company.com", key="login_email")
        l_pass = st.text_input("Secure Password", type="password", key="login_pass")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Access Workspace"):
            try:
                response = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = response.user.email
                st.session_state.is_admin = (response.user.email == ADMIN_EMAIL)
                st.rerun()
            except Exception as e:
                st.error("❌ Authentication failed. Please verify your email and password.")

    # --- SIGN UP TAB (ELEGANT DESIGN WITH NAME & PHONE) ---
    with tab2:
        st.markdown('<div class="auth-header">Create Your Professional Account</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Join the ultimate AI-driven formulation laboratory.</div>', unsafe_allow_html=True)
        
        s_name = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="signup_name")
        s_email = st.text_input("Professional Email", placeholder="name@company.com", key="signup_email")
        s_phone = st.text_input("Contact Number (Optional)", placeholder="+233 ...", key="signup_phone")
        s_pass = st.text_input("Secure Password", type="password", placeholder="Minimum 6 characters strictly required", key="signup_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Create Account & Initialize Lab"):
            if len(s_pass) < 6:
                st.warning("⚠️ For your security, the password must be at least 6 characters.")
            elif not s_email or not s_name:
                st.warning("⚠️ Full Name and Professional Email are required fields
