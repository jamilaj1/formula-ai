import streamlit as st
import google.generativeai as genai

# --- 1. PROFESSIONAL UI CONFIG ---
st.set_page_config(page_title="Formula AI | Industrial Lab", page_icon="🧪", layout="centered")

# Clean, professional style that worked before
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 10px; }
    .sub-title { font-size: 1.2rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; height: 3em; background-color: #2563EB; color: white; }
    .stTextInput>div>div>input { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SECURE ACCESS (STATIC VERSION) ---
# Fixing PGRST205 by using local auth until DB tables are ready
USERS = {"admin": "123", "jamil": "2026", "client": "pass"}

def render_landing_page():
    st.markdown('<p class="main-title">Formula AI Studio 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Advanced Industrial Chemistry & Production Intelligence</p>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Secure Login")
        # FIXED: Unique keys prevent DuplicateElementId error
        u = st.text_input("Username / Email", key="unique_login_user")
        p = st.text_input("Password", type="password", key="unique_login_pass")
        
        if st.button("Enter Laboratory", key="main_entry_btn"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.session_state.user_name = u.capitalize()
                st.rerun()
            else: 
                st.error("❌ Invalid credentials. Please verify your access.")

# --- 3. THE INDUSTRIAL LABORATORY (AI CORE) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    render_landing_page()
else:
    # Sidebar
    with st.sidebar:
        st.success(f"🟢 Verified: {st.session_state.user_name}")
        if st.button("Clear Lab 🧹", key="sidebar_clear_btn"):
            st.session_state.msg = []
            st.rerun()
        if st.button("Logout 🚪", key="sidebar_logout_btn"):
            st.session_state.auth = False
            st.rerun()
            
    st.title("🧪 Formula AI Workspace")
    
    # FIXED: AI Config with stable model name to avoid 404
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        ai_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are 'Formula AI'. Detect user language but provide all chemical and cost data in Professional English."
        )
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        # Render workspace messages
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # FIXED: Unique key for input to prevent crashes
        if prompt := st.chat_input("Ask about chemical formulation or batch costs...", key="workspace_input"):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    res = st.session_state.chat.send_message(prompt)
                    st.markdown(res.text)
                    st.session_state.msg.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"AI Core Busy: {e}")
                    
    except Exception as e:
        st.error(f"System Load Error: {e}")
