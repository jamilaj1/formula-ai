import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. THEME ENGINE & GLOBAL CSS OVERRIDE ---
st.set_page_config(page_title="Formula AI", page_icon="🧪", layout="wide")

# This CSS uses !important to force Streamlit to ignore its internal light-mode settings
st.markdown("""
<style>
    /* 1. Force the entire app background */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }

    /* 2. Force Sidebar to Deep Charcoal */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* 3. Eliminate the white header and footer entirely */
    header, footer, [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        visibility: hidden !important;
    }

    /* 4. Gemini Title Styling with Gradient */
    .gemini-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }

    /* 5. Fix Chat Input (Remove the white bar at the bottom) */
    [data-testid="stChatInputContainer"] {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }

    /* 6. Professional Rounded Buttons */
    .stButton>button {
        border-radius: 50px !important;
        background-color: #1e1f20 !important;
        color: #e3e3e3 !important;
        border: 1px solid #444746 !important;
        transition: 0.3s ease !important;
    }
    .stButton>button:hover {
        border-color: #4285f4 !important;
        background-color: #2a2b2c !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_db()

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
        
        st.markdown(f"**Verified Pro Account**\n### {name}")
        st.markdown("<span style='color:#4285f4; font-weight:700;'>PREMIUM ACCESS</span>", unsafe_allow_html=True)
        if st.button("Secure Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.info(f"Usage: {st.session_state.free_usage}/2 Formulas")
        if st.button("Unlock Full Access 🔓"):
            st.session_state.show_auth = True
            st.rerun()

# --- 4. MAIN LABORATORY ---
def render_main():
    st.markdown('<p class="gemini-title">Formula AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#b4b4b4; font-size:1.5rem; margin-top:-20px;'>How can I help you today?</p>", unsafe_allow_html=True)

    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue using the industrial engine.")
        return

    # Chat Engine
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask your chemical engineering question..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = st.session_state.chat.send_message(f"Expert Formula AI: {prompt}")
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"System Error: {e}")

# --- 5. AUTHENTICATION MODULE ---
def render_auth():
    st.markdown('<p class="gemini-title">Join Formula AI</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        e = st.text_input("Professional Email")
        p = st.text_input("Password", type="password")
        if st.button("Enter Laboratory"):
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user_email = res.user.email
            st.rerun()
    with tab2:
        n = st.text_input("Full Name")
        e_s = st.text_input("Professional Email")
        p_s = st.text_input("Security Password", type="password")
        if st.button("Initialize Pro Account"):
            res = supabase.auth.sign_up({"email": e_s, "password": p_s, "options": {"data": {"full_name": n}}})
            st.session_state.user_email = res.user.email
            st.rerun()

# --- 6. ROUTING ---
if not is_pro and st.session_state.get('show_auth', False):
    render_auth()
    if st.button("← Back to Workspace"):
        st.session_state.show_auth = False
        st.rerun()
else:
    render_main()
