import streamlit as st
import google.generativeai as genai

# --- 1. STABLE PAGE CONFIG & DESIGN ---
st.set_page_config(page_title="Formula AI | Premium Formulation", page_icon="🧪", layout="centered")

# Professional Clean UI (The version you liked)
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
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

# --- 2. SECURE AUTHENTICATION (NO DB ERRORS) ---
# We use a stable local list to avoid PGRST205 database errors
USERS = {"admin": "123", "jamil": "2026", "client": "pass"}

def render_landing_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Your Intelligent Agent for Industrial Chemistry & Production Economics</p>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Account Login")
        # Unique keys assigned to prevent DuplicateElementId error
        u = st.text_input("Username / Email", key="unique_user_login")
        p = st.text_input("Password", type="password", key="unique_pass_login")
        
        if st.button("Access Platform", key="main_access_btn"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.session_state.user_name = u.capitalize()
                st.rerun()
            else: 
                st.error("❌ Invalid credentials. Please verify your access.")
    
    # Pricing Visualization
    st.markdown('<p class="pricing-header">Choose Your Subscription Plan</p>', unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)
    
    plans = ["Weekly Pass", "Monthly Pro", "Yearly Enterprise"]
    prices = ["$9.99", "$29.99", "$249.99"]
    
    for i, col in enumerate([p_col1, p_col2, p_col3]):
        with col:
            st.markdown(f'<div class="card"><div class="card-title">{plans[i]}</div><div class="card-price">{prices[i]}</div></div>', unsafe_allow_html=True)
            if st.button(f"Select {plans[i]}", key=f"plan_selector_{i}"): st.info("Payment Integration Pending...")

# --- 3. MAIN LABORATORY (SECURE WORKSPACE) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    render_landing_page()
else:
    # Sidebar control
    with st.sidebar:
        st.success(f"🟢 Verified Account: {st.session_state.user_name}")
        if st.button("New Session 🧹", use_container_width=True, key="new_session_sidebar"):
            st.session_state.msg = []
            st.rerun()
        if st.button("Logout 🚪", use_container_width=True, key="logout_sidebar"):
            st.session_state.auth = False
            st.rerun()
            
    st.title("🧪 Formula AI Studio")
    
    
    # Stable AI Core
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # Standard stable model identifier to prevent 404 errors
        ai_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are 'Formula AI'. Provide expert industrial chemical formulations. All technical data MUST be in Professional English."
        )
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        # Render conversation
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # Workspace Input
        if prompt := st.chat_input("Enter formulation parameters...", key="workspace_chat_input"):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    res = st.session_state.chat.send_message(prompt)
                    st.markdown(res.text)
                    st.session_state.msg.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"AI Core Busy. Error: {e}")
                    
    except Exception as e:
        st.error(f"Configuration System Error: {e}")
