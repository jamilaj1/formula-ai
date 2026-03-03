import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. FORCE THEME & UI INJECTION ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# CSS to override Streamlit default white backgrounds
st.markdown("""
<style>
    /* Force main background to Gemini Dark */
    .stApp {
        background-color: #131314 !format;
        color: #e3e3e3 !important;
    }
    
    /* Force Sidebar to Deep Charcoal */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Force Header to disappear or match */
    header {background: rgba(0,0,0,0) !important;}
    
    /* Gemini-style Title with Gradient */
    .gemini-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    /* Elegant Chat Input */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border-radius: 28px !important;
        border: 1px solid #444746 !important;
    }
    
    /* Buttons Styling */
    .stButton>button {
        border-radius: 50px;
        background-color: #1e1f20;
        color: #e3e3e3;
        border: 1px solid #444746;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #4285f4;
        background-color: #2a2b2c;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# Session State for User and Quota
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Workspace")
    
    is_pro = st.session_state.user_email is not None
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            name = user_data.user.user_metadata.get("full_name", "Member")
        except: name = "Member"
        
        st.markdown(f"**Verified Pro**\n### {name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM ACCESS</span>", unsafe_allow_html=True)
        if st.button("Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Free usage: {st.session_state.free_usage}/2")
        if st.button("Get Full Access 🔓"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.5rem; margin-top:-20px;'>How can I help you today?</p>", unsafe_allow_html=True)

    # Restriction for non-pro
    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue.")
        return

    # Chat Engine (Gemini)
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your request..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = model.generate_content(f"You are Formula AI expert. Answer: {prompt}")
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"System Error: {e}")

# --- 5. AUTHENTICATION ---
def render_auth():
    st.markdown('<p class="gemini-title">Join Formula AI</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("Enter Lab"):
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user_email = res.user.email
            st.rerun()
    with tab2:
        n = st.text_input("Full Name")
        e_s = st.text_input("Email")
        p_s = st.text_input("Password", type="password")
        if st.button("Create Pro Account"):
            res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
            st.session_state.user_email = res.user.email
            st.rerun()

# --- 6. ROUTING ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Lab"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
