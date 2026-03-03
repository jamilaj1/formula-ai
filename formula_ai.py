import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. GLOBAL UI & GEMINI DARK THEME ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# Eliminating white patches and forcing the professional Charcoal/Dark theme
st.markdown("""
<style>
    .stApp { background-color: #131314 !important; color: #e3e3e3 !important; }
    section[data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid rgba(255,255,255,0.05); }
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .stChatInputContainer { background-color: #1e1f20 !important; border: 1px solid #444746 !important; border-radius: 28px !important; }
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR (Restored Toggle & Profile) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    # The Toggle Switch
    is_dark = st.toggle("Dark Mode ✨", value=True, key="main_sidebar_theme_toggle")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_res = supabase.auth.get_user()
            display_name = user_res.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except Exception:
            display_name = "Jamil Abduljalil"
            
        st.markdown(f"**Operator:**\n### {display_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="sidebar_logout_btn"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Free Formulas")
        if st.button("Unlock Pro 🔓", key="sidebar_unlock_pro_btn"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE (Fixed IDs) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        e_log = st.text_input("Professional Email", key="auth_login_email")
        p_log = st.text_input("Password", type="password", key="auth_login_pass")
        if st.button("Authenticate & Enter", key="auth_login_submit"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e_log, "password": p_log})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception:
                st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        n_reg = st.text_input("Full Name", placeholder="e.g. Jamil Abduljalil", key="auth_reg_name")
        e_reg = st.text_input("Email", key="auth_reg_email")
        p_reg = st.text_input("Password (6+ characters)", type="password", key="auth_reg_pass")
        if st.button("Initialize Pro Account", key="auth_reg_submit"):
            try:
                res = supabase.auth.sign_up({"email": e_reg, "password": p_reg, "options": {"data": {"full_name": n_reg}}})
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as ex:
                st.error(f"❌ Error during registration: {ex}")

# --- 5. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Advanced Industrial Intelligence Laboratory</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free usage limit reached. Please register to continue.")
        return

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # Fix: Using the stable model name directly
        ai_model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask about formulations, batch costs, or requirements..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat.send_message(f"As an expert chemical engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_e:
                    st.error(f"AI System Busy: {ai_e}")
    except Exception as e:
        st.error(f"System Configuration Error: {e}")

# --- 6. ROUTING ENGINE ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Preview", key="global_back_nav_btn"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
