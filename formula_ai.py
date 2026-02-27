import streamlit as st
import google.generativeai as genai

# --- 1. PAGE SETUP & DESIGN (CSS) ---
st.set_page_config(page_title="Formula AI | Premium Formulation", page_icon="🧪", layout="centered")

# Custom CSS for a beautiful, clean, and modern UI
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.2rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .pricing-header { font-size: 1.5rem; font-weight: bold; text-align: center; margin-top: 40px; margin-bottom: 20px; color: #334155; }
    .card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .card-title { font-size: 1.2rem; font-weight: 700; color: #0F172A; }
    .card-price { font-size: 2rem; font-weight: 800; color: #2563EB; margin: 10px 0; }
    .card-features { color: #475569; font-size: 0.95rem; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION & LANDING PAGE ---
# Placeholder for database users
USERS = {"admin": "123", "client": "pass"}

def render_landing_page():
    # Hero Section
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Your Intelligent Agent for Industrial Chemistry & Production Economics</p>', unsafe_allow_html=True)
    
    st.divider()

    # Login Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Account Login")
        u = st.text_input("Username / Email")
        p = st.text_input("Password", type="password")
        
        if st.button("Access Platform"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("❌ Invalid credentials. Please try again or subscribe below.")
    
    # Pricing Section
    st.markdown('<p class="pricing-header">Choose Your Subscription Plan</p>', unsafe_allow_html=True)
    
    p_col1, p_col2, p_col3 = st.columns(3)
    
    with p_col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Weekly Pass</div>
            <div class="card-price">$9.99</div>
            <div class="card-features">
                ✔️ 7 Days Access<br>
                ✔️ Basic Formulas<br>
                ✔️ Standard Support
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Weekly"): st.info("Payment Gateway Integration Pending...")

    with p_col2:
        st.markdown("""
        <div class="card" style="border: 2px solid #2563EB;">
            <div class="card-title">Monthly Pro (Popular)</div>
            <div class="card-price">$29.99</div>
            <div class="card-features">
                ✔️ 30 Days Access<br>
                ✔️ Advanced Formulas<br>
                ✔️ Cost Calculator
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Monthly"): st.info("Payment Gateway Integration Pending...")

    with p_col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Yearly Enterprise</div>
            <div class="card-price">$249.99</div>
            <div class="card-features">
                ✔️ 365 Days Access<br>
                ✔️ Premium Features<br>
                ✔️ Priority 24/7 Support
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Yearly"): st.info("Payment Gateway Integration Pending...")

def check_auth():
    if "auth" not in st.session_state: 
        st.session_state.auth = False
    if not st.session_state.auth:
        render_landing_page()
        return False
    return True

# --- 3. MAIN APP (AFTER LOGIN) ---
if check_auth():
    # Secure API Key retrieval
    MY_API_KEY = st.secrets["API_KEY"]
    
    @st.cache_resource
    def init_ai(key):
        genai.configure(api_key=key)
        instr = """
        You are 'Formula AI'. Detect user language and reply in it. 
        CRITICAL: All technical data, chemical names, formulas, and financial tables MUST be in Professional English. 
        Ask for: 1) Sector, 2) Objective, 3) Mode (A-F), 4) Batch Size, 5) Local Currency.
        """
        m_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return genai.GenerativeModel(model_name=m_list[0], system_instruction=instr)

    try:
        ai_model = init_ai(MY_API_KEY)
    except Exception as e:
        st.error(f"AI Initialization Error: {e}")
    
    # Sidebar
    with st.sidebar:
        st.success("🟢 Online - Premium Account")
        if st.button("New Session 🧹", use_container_width=True):
            st.session_state.msg = []
            st.session_state.chat = ai_model.start_chat(history=[])
            st.rerun()
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state.auth = False
