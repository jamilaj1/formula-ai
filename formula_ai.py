import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE SETUP & GLOBAL STYLING ---
st.set_page_config(page_title="Formula AI | Industrial Laboratory", page_icon="🧪", layout="centered")

# Professional Corporate CSS
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
    .sidebar-name { font-size: 1.4rem; font-weight: 700; color: #1E293B; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Critical Connection Error: {e}")

# Master Administrative Account
ADMIN_EMAIL = "jamilaj1@gmail.com"

# --- 3. SESSION STATE TRACKING ---
if "user_email" not in st.session_state: 
    st.session_state.user_email = None
if "is_admin" not in st.session_state: 
    st.session_state.is_admin = False

# --- 4. AUTHENTICATION MODULE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Providing elite AI intelligence for professional chemical manufacturing.</p>', unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    with tab1:
        st.markdown('<div class="auth-header">Authorized Access</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Please enter your credentials to access the laboratory workspace.</div>', unsafe_allow_html=True)
        
        l_email = st.text_input("Professional Email", placeholder="name@company.com", key="login_email")
        l_pass = st.text_input("Secure Password", type="password", key="login_pass")
        
        if st.button("Authenticate & Access"):
            try:
                response = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = response.user.email
                st.session_state.is_admin = (response.user.email == ADMIN_EMAIL)
                st.rerun()
            except Exception:
                st.error("❌ Authentication Denied: Verify your email and password.")

    with tab2:
        st.markdown('<div class="auth-header">Professional Registration</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Create your industrial profile for full access to formulation tools.</div>', unsafe_allow_html=True)
        
        s_name = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="signup_name")
        s_email = st.text_input("Professional Email Address", placeholder="name@company.com", key="signup_email")
        s_phone = st.text_input("Contact Number", placeholder="+233 ...", key="signup_phone")
        s_pass = st.text_input("Access Password", type="password", placeholder="Minimum 6 characters", key="signup_pass")
        
        if st.button("Initialize & Enter Laboratory"):
            if not s_name or not s_email:
                st.warning("⚠️ Action Required: Please provide your Full Name and Email.")
            elif len(s_pass) < 6:
                st.warning("⚠️ Security Alert: Password must be at least 6 characters.")
            else:
                try:
                    # Sign up with metadata for Name and Phone
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
                        st.success(f"✅ Registration successful! Welcome, {s_name}.")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ System Error: Account creation failed. {e}")

# --- 5. EXECUTIVE DASHBOARD (ADMIN) ---
def render_admin_dashboard():
    with st.sidebar:
        st.error("🛡️ EXECUTIVE SYSTEM ADMIN")
        st.write(f"Identity: {st.session_state.user_email}")
        if st.button("Global Logout 🚪", key="admin_logout"):
            st.session_state.user_email = None
            st.session_state.is_admin = False
            st.rerun()

    st.title("🛡️ System Administration")
    st.markdown("Global Control Console: Monitor platform metrics and secure database links.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="card"><div class="stat-value">Active</div><div class="stat-label">System Node</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="card"><div class="stat-value">v4.0</div><div class="stat-label">Global Version</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="card"><div class="stat-value">Secured</div><div class="stat-label">DB Clusters</div></div>', unsafe_allow_html=True)

    st.markdown("### 👥 User Registry")
    st.info("Complete client profiles including Full Names and phone numbers are securely vaulted in your Supabase Auth Dashboard.")

# --- 6. CLIENT LABORATORY INTERFACE ---
def render_client_app():
    # Attempt to retrieve user's Full Name from Supabase Metadata
    try:
        user_response = supabase.auth.get_user()
        client_name = user_response.user.user_metadata.get("full_name", "Valued Client")
    except:
        client_name = st.session_state.user_email

    with st.sidebar:
        st.success("🟢 Online - Premium Session")
        st.markdown(f"**Welcome,**\n<div class='sidebar-name'>{client_name}</div>", unsafe_allow_html=True)
        st.caption(f"Account Email: {st.session_state.user_email}")
        st.divider()
        if st.button("Refresh Workspace 🧹"):
            st.session_state.msg = []
            if "chat" in st.session_state: del st.session_state.chat
            st.rerun()
        if st.button("Secure Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown(f"Industrial Intelligence Workspace. The laboratory is prepared for your parameters, **{client_name}**.")
    
    try:
        API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=API_KEY)
        
        @st.cache_resource
        def init_ai():
            instr = "You are 'Formula AI', a senior chemical engineer. Provide precise formulations and industrial cost analysis. Ask for: 1) Industry Sector, 2) Batch Objective, 3) Production Size, 4) Local Currency."
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return genai.GenerativeModel(model_name=models[0], system_instruction=instr)
            
        ai_engine = init_ai()
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_engine.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if user_prompt := st.chat_input("Enter your manufacturing inquiry..."):
            st.session_state.msg.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"): st.markdown(user_prompt)
            
            with st.chat_message("assistant"):
                ai_response = st.session_state.chat.send_message(user_prompt)
                st.markdown(ai_response.text)
                st.session_state.msg.append({"role": "assistant", "content": ai_response.text})
                
    except Exception as e:
        st.error(f"⚠️ System Alert: Unable to reach AI core. Details: {e}")

# --- 7. ROUTING ENGINE ---
if st.session_state.user_email is None:
    render_auth_page()
elif st.session_state.is_admin:
    render_admin_dashboard()
else:
    render_client_app()
