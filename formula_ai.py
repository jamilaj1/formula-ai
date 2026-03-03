import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. GLOBAL THEME & UI OVERRIDE ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

st.markdown("""
<style>
    /* Absolute Dark Mode Force */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR (Personalized) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace", unsafe_allow_html=True)
    theme_toggle = st.toggle("Dark Mode ✨", value=True, key="unique_theme_toggle")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_info = supabase.auth.get_user()
            display_name = user_info.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except: display_name = "Jamil Abduljalil"
        st.markdown(f"**Operator:**\n### {display_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="unique_logout_btn"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free usage: {st.session_state.free_usage}/2")
        if st.button("Unlock Full Access 🔓", key="unique_unlock_btn"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        e = st.text_input("Email", key="auth_login_email")
        p = st.text_input("Password", type="password", key="auth_login_pass")
        if st.button("Enter Laboratory", key="auth_login_submit"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as e:
                st.error("❌ Invalid credentials.")

    with tab2:
        n = st.text_input("Full Name", key="auth_reg_name")
        e_s = st.text_input("Email", key="auth_reg_email")
        p_s = st.text_input("Password", type="password", key="auth_reg_pass")
        if st.button("Create Pro Account", key="auth_reg_submit"):
            try:
                res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as ex:
                st.error(f"❌ Error: {ex}")

# --- 5. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free usage limit reached. Please register to continue.")
        return

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        ai_model = genai.GenerativeModel("gemini-1.5-flash") # Fixed model name
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask anything..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat.send_message(f"Expert Engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_e:
                    st.error(f"AI Core Busy: {ai_e}")
    except Exception as e:
        st.error(f"System Load Error: {e}")

# --- 6. ROUTING ENGINE ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Lab", key="unique_back_btn"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
