import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

# --- 2. DARK/LIGHT MODE LOGIC ---
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# Dynamic CSS based on theme selection
if st.session_state.theme_mode == "Dark":
    bg_color = "#0F172A"
    text_color = "#F8FAFC"
    card_bg = "#1E293B"
    border_color = "#334155"
    sub_text = "#94A3B8"
else:
    bg_color = "#FFFFFF"
    text_color = "#0F172A"
    card_bg = "#F8FAFC"
    border_color = "#E2E8F0"
    sub_text = "#64748B"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .main-title {{ font-size: 3rem; font-weight: 800; text-align: center; color: {text_color}; margin-bottom: 0px; }}
    .sub-title {{ font-size: 1.1rem; text-align: center; color: {sub_text}; margin-bottom: 30px; }}
    .stButton>button {{ border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }}
    .sidebar-name {{ font-size: 1.4rem; font-weight: 700; color: {text_color}; margin-top: 5px; }}
    .premium-badge {{ background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 5px; }}
    .pricing-card {{ background-color: {card_bg}; border: 2px solid {border_color}; border-radius: 12px; padding: 20px; text-align: center; color: {text_color}; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Database Error: {e}")

# --- 4. SESSION MANAGEMENT ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage" not in st.session_state: st.session_state.free_usage = 0

# --- 5. AUTHENTICATION MODULE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Elite chemical engineering intelligence at your fingertips.</p>', unsafe_allow_html=True)
    
    # Pricing UI
    st.markdown("### 💎 Professional Plans")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="pricing-card"><h3>Guest</h3><p class="price">$0</p><p>2 Free Formulas</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="pricing-card" style="border-color: #2563EB;"><h3>Pro</h3><p class="price">$29/mo</p><p>Unlimited Access</p></div>', unsafe_allow_html=True)
    
    st.divider()
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Access Platform"):
            try:
                res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Invalid credentials.")

    with tab2:
        s_name = st.text_input("Full Name", placeholder="e.g. Jamil Abduljalil")
        s_email = st.text_input("Email Address")
        s_pass = st.text_input("Password", type="password")
        if st.button("Create Account"):
            if len(s_pass) < 6 or not s_name: st.warning("Name and 6-char password required.")
            else:
                try:
                    res = supabase.auth.sign_up({"email": s_email, "password": s_pass, "options": {"data": {"full_name": s_name}}})
                    if res.user:
                        st.session_state.user_email = res.user.email
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

# --- 6. MAIN LABORATORY ---
def render_lab():
    is_pro = st.session_state.user_email is not None
    try:
        user_data = supabase.auth.get_user()
        display_name = user_data.user.user_metadata.get("full_name", "Premium Operator")
    except: display_name = "Premium Operator"

    # Sidebar UI with Theme Toggle
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        # The Toggle Switch
        theme = st.toggle("Dark Mode 🌙", value=(st.session_state.theme_mode == "Dark"))
        st.session_state.theme_mode = "Dark" if theme else "Light"
        
        st.divider()
        if is_pro:
            st.markdown(f"<div class='sidebar-name'>{display_name} <span class='premium-badge'>PRO</span></div>", unsafe_allow_html=True)
            if st.button("Logout 🚪"):
                st.session_state.user_email = None
                st.rerun()
        else:
            st.markdown(f"**Status:** Guest ({st.session_state.free_usage}/2 Free)")
            if st.button("Unlock Pro 🔓"): st.rerun()

    st.title("🧪 Formula AI")
    st.markdown(f"Greetings, **{display_name}**. Workspace mode: **{st.session_state.theme_mode}**.")

    # --- AI CORE ---
    if not is_pro and st.session_state.free_usage >= 2:
        st.error("⚠️ Free limit reached. Please register to continue.")
        return

    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter manufacturing query..."):
            if not is_pro: st.session_state.free_usage += 1
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.msg.append({"role": "assistant", "content": res.text})
    except Exception as e: st.error(f"AI System Offline: {e}")

# --- 7. ROUTING ---
if st.session_state.user_email is None and st.session_state.free_usage >= 2:
    render_auth_page()
else:
    render_lab()
