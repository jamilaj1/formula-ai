import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. SETTINGS & STABLE UI ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# Static Dark Theme (Professional & Stable)
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    section[data-testid="stSidebar"] { background-color: #1e1f20; }
    .gemini-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .stChatInputContainer { background-color: #1e1f20; border-radius: 28px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & SESSION INITIALIZATION ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- 3. AUTHENTICATION (Fixed Duplicate ID Errors) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        # Unique keys assigned to prevent DuplicateElementId error
        e_log = st.text_input("Professional Email", key="login_email_unique")
        p_log = st.text_input("Password", type="password", key="login_pass_unique")
        if st.button("Access Laboratory", key="login_submit_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Check credentials.")

    with tab2:
        # Unique keys assigned to prevent DuplicateElementId error
        e_reg = st.text_input("Professional Email", key="reg_email_unique")
        p_reg = st.text_input("Password", type="password", key="reg_pass_unique")
        if st.button("Initialize Account", key="reg_submit_btn"):
            try:
                supabase.auth.sign_up({"email": e_reg, "password": p_reg})
                st.success("Account created! Please login.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. MAIN LABORATORY (Gemini 1.5 Flash Stable) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"User: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="logout_btn_unique"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.write("Advanced Industrial Intelligence Laboratory")

    # AI Config - Fixed model to ensure generateContent support
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Enter manufacturing query...", key="chat_input_unique"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = model.generate_content(f"As a Senior Chemical Engineer: {prompt}")
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                
    except Exception as e:
        st.error(f"AI System Error: {e}")

# --- 5. ROUTING ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
