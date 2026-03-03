import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. SETTINGS & GEMINI UI ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# Eliminating white patches and forcing the professional Dark theme
st.markdown("""
<style>
    .stApp { background-color: #131314 !important; color: #e3e3e3 !important; }
    section[data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid rgba(255,255,255,0.05); }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #444746 !important; border-radius: 28px !important; }
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & AI INIT ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

def get_ai_model():
    genai.configure(api_key=st.secrets["API_KEY"])
    # Using stable model to avoid 404 errors
    return genai.GenerativeModel("gemini-1.5-flash")

# --- 3. AUTHENTICATION MODULE (Safe Version) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        email = st.text_input("Professional Email", key="login_email_final")
        password = st.text_input("Password", type="password", key="login_pass_final")
        if st.button("Access Laboratory", key="login_btn_final"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Authentication failed. Please check credentials.")

    with tab2:
        reg_email = st.text_input("Professional Email", key="reg_email_final")
        reg_pass = st.text_input("Password", type="password", key="reg_pass_final")
        if st.button("Create Account", key="reg_btn_final"):
            try:
                # Basic registration without extra table requirements
                supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                st.success("Account created! You can now login.")
            except Exception as e: st.error(f"Registration Error: {e}")

# --- 4. MAIN INTERFACE ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"User: {st.session_state.user_email}")
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    
    model = get_ai_model()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about chemical formulation..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Engineering expert persona
                response = model.generate_content(f"Expert Engineer: {prompt}")
                answer = response.text
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"AI System Error. Check API Key. Details: {e}")

# --- 5. ROUTING ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
