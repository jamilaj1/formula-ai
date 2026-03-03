import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. SETTINGS & CSS INJECTION (The "White Background" Killer) ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

st.markdown("""
<style>
    /* Absolute force for Dark Mode colors */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stCanvas"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    
    /* Force Sidebar Style */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Style titles & inputs */
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border-radius: 28px !important;
        border: 1px solid #444746 !important;
    }

    /* Hide standard header */
    header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & SESSION ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

supabase = init_db()

if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR (Personalized Profile) ---
with st.sidebar:
    st.markdown("<br>### ⚙️ Workspace Settings", unsafe_allow_html=True)
    # Simple toggle for mode
    is_dark = st.toggle("Dark Mode ✨", value=True, key="sidebar_theme_toggle_key")
    st.divider()
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            # Fetching Jamil Abduljalil from metadata
            full_name = user_data.user.user_metadata.get("full_name", "Jamil Abduljalil")
        except:
            full_name = "Jamil Abduljalil"
            
        st.markdown(f"**Operator:**\n### {full_name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM PRO ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪", key="sidebar_logout_btn_key"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free usage: {st.session_state.free_usage}/2")
        if st.button("Unlock Full Access 🔓", key="sidebar_unlock_pro_btn_key"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. AUTHENTICATION MODULE (Fixed Duplicate IDs) ---
def render_auth():
    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
    
    with tab1:
        email_in = st.text_input("Professional Email", key="login_email_unique_id")
        pass_in = st.text_input("Security Password", type="password", key="login_pass_unique_id")
        if st.button("Authenticate & Enter", key="login_submit_btn_unique_id"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        name_in = st.text_input("Full Name", placeholder="e.g., Jamil Abduljalil", key="reg_name_unique_id")
        email_s = st.text_input("Professional Email", key="reg_email_unique_id")
        pass_s = st.text_input("New Password (6+ chars)", type="password", key="reg_pass_unique_id")
        if st.button("Initialize Pro Account", key="reg_submit_btn_unique_id"):
            try:
                res = supabase.auth.sign_up({
                    "email": email_s, 
                    "password": pass_s, 
                    "options": {"data": {"full_name": name_in}}
                })
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error during registration: {e}")

# --- 5. MAIN APP INTERFACE ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.2rem;'>Next-Gen Industrial Intelligence</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to unlock unlimited formulas.")
        return

    # Chat Engine Configuration
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        # Fix: Using the stable model name directly
        ai_engine = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_engine.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter formula query or batch requirements..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat.send_message(f"Chemical Engineering Expert Response: {prompt}")
                    st.markdown(response.text)
                    st.session_state.msg.append({"role": "assistant", "content": response.text})
                except Exception as ai_err:
                    st.error(f"AI Engine Error: {ai_err}")
    except Exception as e:
        st.error(f"System Configuration Error: {e}")

# --- 6. GLOBAL ROUTING ENGINE ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Laboratory", key="global_back_nav_btn_id"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
