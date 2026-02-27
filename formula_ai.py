import streamlit as st
import google.generativeai as genai

# --- 1. PAGE SETUP & DESIGN ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

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

# --- 2. AUTHENTICATION ---
USERS = {"admin": "123", "jamil": "123"}

if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    # --- LANDING PAGE ---
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Intelligent Agent for Industrial Chemistry & Production Economics</p>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Account Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("❌ Invalid credentials.")
    
    st.markdown('<p class="pricing-header">Subscription Plans</p>', unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.markdown('<div class="card"><div class="card-title">Weekly</div><div class="card-price">$9.99</div></div>', unsafe_allow_html=True)
        if st.button("Subscribe Weekly"): st.info("Gateway Pending...")
    with p_col2:
        st.markdown('<div class="card" style="border: 2px solid #2563EB;"><div class="card-title">Monthly (Pro)</div><div class="card-price">$29.99</div></div>', unsafe_allow_html=True)
        if st.button("Subscribe Monthly"): st.info("Gateway Pending...")
    with p_col3:
        st.markdown('<div class="card"><div class="card-title">Yearly</div><div class="card-price">$249.99</div></div>', unsafe_allow_html=True)
        if st.button("Subscribe Yearly"): st.info("Gateway Pending...")

else:
    # --- 3. MAIN APP (PREMIUM DASHBOARD) ---
    with st.sidebar:
        st.success("🟢 Online - Premium")
        if st.button("New Session 🧹", use_container_width=True):
            st.session_state.msg = []
            if "chat" in st.session_state:
                del st.session_state.chat
            st.rerun()
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown("Welcome to the premium formulation lab. Enter your parameters below.")
    st.divider()
    
    try:
        # Load AI safely
        MY_API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=MY_API_KEY)
        
        @st.cache_resource
        def load_ai_model():
            instr = "You are 'Formula AI'. Reply in user's language. Technical data in English. Ask for: 1) Sector, 2) Objective, 3) Mode, 4) Batch Size, 5) Currency."
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return genai.GenerativeModel(model_name=models[0], system_instruction=instr)
            
        ai_model = load_ai_model()
        
        # Chat Interface
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
        st.error(f"⚠️ System Alert: Could not connect to AI. Please check your API Key in Settings. Error: {e}")
