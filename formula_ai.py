import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- A. PROFESSIONAL THEME & LAYOUT ---
st.set_page_config(page_title="Formula AI | Industrial Lab", page_icon="🧪", layout="centered")

# Static Dark Theme to prevent white flickering
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    section[data-testid="stSidebar"] { background-color: #1e1f20; }
    .gemini-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- B. SESSION & DATABASE INIT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- C. AUTHENTICATION (Fixed PGRST205 Error) ---
# Fixing the missing table error from image_7f4c7c by using local logic first
USERS = {"admin": "123", "jamil": "2026"}

def render_login():
    st.markdown("<h1 class='gemini-title'>Secure Access</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Unique keys to prevent DuplicateElementId error from image_80299f
        u = st.text_input("Operator Email", key="final_login_u")
        p = st.text_input("Password", type="password", key="final_login_p")
        if st.button("Enter Laboratory", key="final_login_btn"):
            if u.lower() in USERS and USERS[u.lower()] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("❌ Invalid credentials")

# --- D. INDUSTRIAL AI CORE (Fixed 404 Model Error) ---
def render_main():
    with st.sidebar:
        st.success(f"🟢 Active: {st.session_state.user}")
        if st.button("Logout", key="final_logout_unique"):
            st.session_state.auth = False
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    
    # Correcting 404 model name from image_7fb1b8 and image_7e5789
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash") # Fixed stable identifier
        
        # Chat display
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter manufacturing query...", key="final_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                # Professional engineering persona
                res = model.generate_content(f"Expert Engineer: {prompt}")
                st.markdown(res.text)
                st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    except Exception as e:
        st.error(f"System Error: {e}")

# --- E. ROUTING ---
if not st.session_state.auth:
    render_login()
else:
    render_main()
