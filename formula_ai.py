import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# --- 1. THE ULTIMATE VISUAL OVERRIDE (Killing the White Background) ---
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# This block forces EVERY element to adopt the Gemini Dark theme
st.markdown("""
<style>
    /* Force main background and text colors */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }

    /* Force Sidebar specific styling */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* Gemini Title with Gradient */
    .gemini-title {
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Professional Chat Input box */
    .stChatInputContainer {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }

    /* Hide standard Streamlit elements that cause white bars */
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION & DATABASE ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_db()

# --- 3. AUTHENTICATION (Safe & Unique IDs) ---
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Access</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        email = st.text_input("Professional Email", key="final_login_email")
        password = st.text_input("Password", type="password", key="final_login_pass")
        if st.button("Access Laboratory", key="final_login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Authentication failed. Please verify credentials.")

    with tab2:
        reg_email = st.text_input("Professional Email", key="final_reg_email")
        reg_pass = st.text_input("Create Password", type="password", key="final_reg_pass")
        if st.button("Initialize Account", key="final_reg_btn"):
            try:
                supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                st.success("Account created! You can now login.")
            except Exception as e:
                st.error(f"Registration Error: {e}")

# --- 4. MAIN LABORATORY (Gemini Engine) ---
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="final_logout_btn"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    
    # AI Config
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Display history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if prompt := st.chat_input("Enter manufacturing query...", key="final_chat_input"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(f"Expert Industrial Engineer: {prompt}")
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"AI System Error: {e}")
    except Exception as sys_e:
        st.error(f"System Load Error: {sys_e}")

# --- 5. ROUTING ---
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
