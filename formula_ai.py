import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

# Professional UI Styling
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
    .sidebar-name { font-size: 1.5rem; font-weight: 700; color: #1E293B; margin-top: 5px; }
    .premium-badge { background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Database offline: {e}")

# --- 3. SESSION STATE ---
if "user_email" not in st.session_state: st.session_state.user_email = None

# --- 4. AUTHENTICATION MODULE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">The world\'s most advanced chemical formulation engine.</p>', unsafe_allow_html=True)
    
    # Guest Access Preview
    st.warning("🔒 **Limited Access:** Please login or register to unlock full formulation capabilities and AI consultation.")
    
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])

    with tab1:
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Access Laboratory"):
            try:
                res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Invalid credentials.")

    with tab2:
        s_name = st.text_input("Full Name", placeholder="Jamil Abduljalil")
        s_email = st.text_input("Email Address")
        s_pass = st.text_input("Password (Min 6 chars)", type="password")
        if st.button("Register & Get Full Access"):
            if len(s_pass) < 6 or not s_name: st.warning("Please fill all fields correctly.")
            else:
                try:
                    res = supabase.auth.sign_up({
                        "email": s_email, "password": s_pass,
                        "options": {"data": {"full_name": s_name}}
                    })
                    if res.user:
                        st.session_state.user_email = res.user.email
                        st.success(f"Account Created! Welcome {s_name}.")
                        time.sleep(1)
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

# --- 5. MAIN APPLICATION (LABORATORY) ---
def render_lab():
    # Identify User
    is_logged_in = st.session_state.user_email is not None
    display_name = "Guest User"
    
    if is_logged_in:
        try:
            user_info = supabase.auth.get_user()
            display_name = user_info.user.user_metadata.get("full_name", "Valued Client")
        except: display_name = "Premium Member"

    # Sidebar Navigation
    with st.sidebar:
        if is_logged_in:
            st.markdown(f"**Current User:**\n<div class='sidebar-name'>{display_name} <span class='premium-badge'>PRO</span></div>", unsafe_allow_html=True)
            st.divider()
            if st.button("Clear History 🧹"):
                st.session_state.msg = []
                st.rerun()
            if st.button("Logout 🚪"):
                st.session_state.user_email = None
                st.rerun()
        else:
            st.markdown("**Status:**\n<div class='sidebar-name'>Guest Access</div>", unsafe_allow_html=True)
            if st.button("Login to Unlock Full AI 🔓"):
                st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown(f"Welcome to the laboratory, **{display_name}**.")

    # --- RESTRICTION LOGIC ---
    if not is_logged_in:
        st.info("💡 **Experience the power of AI:** Register now to generate unlimited formulas, calculate costs in GHS, and get technical support.")
        # Visual preview of what they are missing
        st.image("https://via.placeholder.com/800x400.png?text=Register+to+Unlock+AI+Formulations", use_container_width=True)
        return

    # --- AI CHAT (ONLY FOR REGISTERED USERS) ---
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask for a formula or cost analysis..."):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e: st.error(f"AI System busy: {e}")

# --- 6. ROUTING ---
if st.session_state.user_email is None:
    # Check if they want to browse as guest or go to auth
    render_auth_page()
else:
    render_lab()
