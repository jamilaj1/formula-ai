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
                st.warning("⚠️ Full Name and Professional Email are required fields.")
            else:
                try:
                    # Register user and save Name & Phone in metadata
                    response = supabase.auth.sign_up({
                        "email": s_email, 
                        "password": s_pass,
                        "options": {
                            "data": {
                                "full_name": s_name,
                                "phone_number": s_phone
                            }
                        }
                    })
                    
                    # Auto-Login and personalized greeting
                    if response.user:
                        st.session_state.user_email = response.user.email
                        st.session_state.is_admin = (response.user.email == ADMIN_EMAIL)
                        
                        # Elegant success message
                        st.success(f"✅ Welcome aboard, {s_name}! Provisioning your secure lab environment...")
                        time.sleep(1.5) # A brief, elegant pause before redirecting
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Account creation failed. Error: {e}")

# --- 5. ADMIN DASHBOARD ---
def render_admin_dashboard():
    with st.sidebar:
        st.error("🛡️ ADMIN MODE")
        st.write(f"Logged in as: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="admin_logout"):
            st.session_state.user_email = None
            st.session_state.is_admin = False
            st.rerun()

    st.title("🛡️ Executive Administration")
    st.markdown("Welcome to the master control panel. Monitor platform metrics below.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><div class="stat-value">Active</div><div class="stat-label">System Status</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><div class="stat-value">v3.0</div><div class="stat-label">Platform Version</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><div class="stat-value">Secured</div><div class="stat-label">Database Link</div></div>', unsafe_allow_html=True)

    st.markdown("### 👥 Client Management")
    st.info("Client details (Names, Emails, Phone Numbers) are securely stored. Access the 'Authentication' tab in your Supabase Dashboard to view complete profiles.")

# --- 6. MAIN APPLICATION (CLIENT LAB) ---
def render_client_app():
    with st.sidebar:
        st.success("🟢 Online - Premium Account")
        st.write(f"User: {st.session_state.user_email}")
        st.divider()
        if st.button("New Session 🧹"):
            st.session_state.msg = []
            if "chat" in st.session_state: del st.session_state.chat
            st.rerun()
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown("Welcome to the premium formulation lab. Enter your production parameters below.")
    
    try:
        MY_API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=MY_API_KEY)
        
        @st.cache_resource
        def load_ai_model():
            instr = "You are 'Formula AI', an expert chemical engineer. Reply in the user's language. Keep technical terms and formulas in Professional English. Ask for: 1) Sector, 2) Objective, 3) Batch Size, 4) Local Currency."
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return genai.GenerativeModel(model_name=models[0], system_instruction=instr)
            
        ai_model = load_ai_model()
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your formulation parameters..."):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                res = st.session_state.chat.send_message(prompt)
                st.markdown(res.text)
                st.session_state.msg.append({"role": "assistant", "content": res.text})
                
    except Exception as e:
        st.error(f"⚠️ System Alert: Could not connect to AI Engine. Error: {e}")

# --- 7. ROUTING ENGINE ---
if st.session_state.user_email is None:
    render_auth_page()
elif st.session_state.is_admin:
    render_admin_dashboard()
else:
    render_client_app()
