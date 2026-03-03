import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE SETUP & DESIGN ---
st.set_page_config(page_title="Formula AI | Premium Platform", page_icon="🧪", layout="centered")

# Custom Professional CSS
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;}
    .stat-value { font-size: 2.5rem; font-weight: 800; color: #2563EB; }
    .stat-label { font-size: 1rem; color: #475569; font-weight: 600; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
    .auth-header { font-size: 1.5rem; font-weight: 700; color: #1E293B; margin-bottom: 5px; }
    .auth-sub { font-size: 0.95rem; color: #64748B; margin-bottom: 20px; }
    .welcome-text { font-size: 1.2rem; font-weight: 600; color: #1E293B; }
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
    st.error(f"Database Connection Error: {e}")

ADMIN_EMAIL = "jamilaj1@gmail.com"

# --- 3. SESSION STATE MANAGEMENT ---
if "user_email" not in st.session_state: 
    st.session_state.user_email = None
if "is_admin" not in st.session_state: 
    st.session_state.is_admin = False

# --- 4. AUTHENTICATION MODULE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Secure access to the world\'s most advanced chemical formulation engine.</p>', unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    # --- LOGIN TAB ---
    with tab1:
        st.markdown('<div class="auth-header">Authorized Access</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Enter your credentials to access your industrial workspace.</div>', unsafe_allow_html=True)
        
        l_email = st.text_input("Professional Email", placeholder="name@company.com", key="login_email")
        l_pass = st.text_input("Secure Password", type="password", key="login_pass")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Authenticate & Enter"):
            try:
                response = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = response.user.email
                st.session_state.is_admin = (response.user.email == ADMIN_EMAIL)
                st.rerun()
            except Exception:
                st.error("❌ Authentication Failed: Invalid credentials provided.")

    # --- SIGN UP TAB ---
    with tab2:
        st.markdown('<div class="auth-header">Register New Account</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Join the elite network of chemical manufacturers and engineers.</div>', unsafe_allow_html=True)
        
        s_name = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="signup_name")
        s_email = st.text_input("Professional Email", placeholder="name@company.com", key="signup_email")
        s_phone = st.text_input("Contact Number", placeholder="+233 ...", key="signup_phone")
        s_pass = st.text_input("Security Password", type="password", placeholder="Minimum 6 characters", key="signup_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Register & Initialize Workspace"):
            if len(s_pass) < 6:
                st.warning("⚠️ Security Requirement: Password must be at least 6 characters.")
            elif not s_email or not s_name:
                st.warning("⚠️ Mandatory Fields: Full Name and Email are required.")
            else:
                try:
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
                    
                    if response.user:
                        st.session_state.user_email = response.user.email
                        st.session_state.is_admin = (response.user.email == ADMIN_EMAIL)
                        st.success(f"✅ Welcome, {s_name}! Provisioning your secure lab...")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ System Error: Account creation failed. {e}")

# --- 5. EXECUTIVE ADMIN DASHBOARD ---
def render_admin_dashboard():
    with st.sidebar:
        st.error("🛡️ EXECUTIVE ADMIN")
        st.write(f"Identity: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="admin_logout"):
            st.session_state.user_email = None
            st.session_state.is_admin = False
            st.rerun()

    st.title("🛡️ System Administration")
    st.markdown("Global Control Panel: Overseeing platform operations and security.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="card"><div class="stat-value">Active</div><div class="stat-label">System Node</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="card"><div class="stat-value">v3.5</div><div class="stat-label">Core Engine</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="card"><div class="stat-value">Linked</div><div class="stat-label">DB Clusters</div></div>', unsafe_allow_html=True)

    st.markdown("### 👥 User Insights")
    st.info("User metadata including Full Names and Phone Numbers are securely vaulted in your Supabase Auth Dashboard.")

# --- 6. CLIENT LABORATORY (MAIN APP) ---
def render_client_app():
    # Fetch user metadata for personalized UI
    try:
        user_info = supabase.auth.get_user()
        display_name = user_info.user.user_metadata.get("full_name", "Valued Client")
    except:
        display_name = st.session_state.user_email

    with st.sidebar:
        st.success("🟢 Online - Premium Access")
        st.markdown(f"**Welcome back,**\n### {display_name}")
        st.caption(f"Account: {st.session_state.user_email}")
        st.divider()
        if st.button("Clean Laboratory 🧹"):
            st.session_state.msg = []
            if "chat" in st.session_state: del st.session_state.chat
            st.rerun()
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown(f"Greetings, **{display_name}**. The AI Laboratory is ready for your technical parameters.")
    
    try:
        MY_API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=MY_API_KEY)
        
        @st.cache_resource
        def load_ai_model():
            # System Instruction to ensure technical quality
            instr = "You are 'Formula AI Expert'. You assist chemical manufacturers with precise formulations and cost analysis. You MUST ask for: 1. Industrial Sector, 2. Formula Objective, 3. Batch Size, 4. Local Currency (e.g. GHS)."
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return genai.GenerativeModel(model_name=models[0], system_instruction=instr)
            
        ai_model = load_ai_model()
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your manufacturing query here..."):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                res = st.session_state.chat.send_message(prompt)
                st.markdown(res.text)
                st.session_state.msg.append({"role": "assistant", "content": res.text})
