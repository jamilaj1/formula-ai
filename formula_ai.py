import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Formula AI | Professional", page_icon="🧪", layout="centered")

# Professional UI Styling
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
    .sidebar-name { font-size: 1.4rem; font-weight: 700; color: #1E293B; margin-top: 5px; }
    .premium-badge { background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 5px; }
    .quota-info { font-size: 0.9rem; color: #64748B; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Database Connection Error: {e}")

# --- 3. SESSION STATE MANAGEMENT ---
if "user_email" not in st.session_state: st.session_state.user_email = None
if "free_usage_count" not in st.session_state: st.session_state.free_usage_count = 0

# --- 4. AUTHENTICATION MODULE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">The global intelligence for chemical manufacturing.</p>', unsafe_allow_html=True)
    st.divider()

    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Pro Account"])

    with tab1:
        st.markdown("### Access Your Workspace")
        l_email = st.text_input("Professional Email", key="login_email")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Authenticate & Enter"):
            try:
                res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        st.markdown("### Join Formula AI Pro")
        s_name = st.text_input("Full Name", placeholder="e.g. Jamil Abduljalil")
        s_email = st.text_input("Email Address")
        s_pass = st.text_input("Secure Password (Min 6 chars)", type="password")
        if st.button("Register & Unlock Pro Access"):
            if len(s_pass) < 6 or not s_name: st.warning("⚠️ Full Name and 6-char password are required.")
            else:
                try:
                    res = supabase.auth.sign_up({
                        "email": s_email, "password": s_pass,
                        "options": {"data": {"full_name": s_name}}
                    })
                    if res.user:
                        st.session_state.user_email = res.user.email
                        st.success(f"✅ Welcome, {s_name}! Initializing Pro environment...")
                        time.sleep(1.5)
                        st.rerun()
                except Exception as e: st.error(f"❌ Error: {e}")

# --- 5. MAIN LABORATORY INTERFACE ---
def render_lab():
    # User Identification
    is_pro = st.session_state.user_email is not None
    display_name = "Guest User"
    
    if is_pro:
        try:
            user_data = supabase.auth.get_user()
            display_name = user_data.user.user_metadata.get("full_name", "Premium Operator")
        except: display_name = "Premium Operator"

    # Sidebar Navigation
    with st.sidebar:
        if is_pro:
            st.markdown(f"<div class='sidebar-name'>{display_name} <span class='premium-badge'>PRO</span></div>", unsafe_allow_html=True)
            st.success("🟢 Connection: SECURE")
        else:
            st.markdown(f"<div class='sidebar-name'>Guest Access</div>", unsafe_allow_html=True)
            st.markdown(f"<p class='quota-info'>Free Formulas: {st.session_state.free_usage_count} / 2</p>", unsafe_allow_html=True)
            if st.button("Login to Unlock Pro 🔓"):
                render_auth_page()
                return

        st.divider()
        if st.button("New Session 🧹"):
            st.session_state.msg = []
            if "chat" in st.session_state: del st.session_state.chat
            st.rerun()
        if is_pro and st.button("Secure Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI")
    st.markdown(f"Greetings, **{display_name}**. The laboratory is ready for your parameters.")

    # --- RESTRICTION LOGIC ---
    can_use_ai = True
    if not is_pro and st.session_state.free_usage_count >= 2:
        can_use_ai = False
        st.error("⚠️ Free usage limit reached. Please register a Pro account to continue.")
        if st.button("Go to Registration Page"):
             st.session_state.show_auth = True
             st.rerun()
        return

    # --- AI ENGINE CORE ---
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash", 
            system_instruction="You are Formula AI Expert. Provide precise chemical formulas and GHS cost analysis. Ask for Sector, Batch Size, and Currency.")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = model.start_chat(history=[])

        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter your formulation query..."):
            if not is_pro:
                st.session_state.free_usage_count += 1
            
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e: st.error(f"⚠️ AI Core Error: {e}")

# --- 6. ROUTING ---
if st.session_state.user_email is None and st.session_state.get('show_auth', True):
    if st.session_state.free_usage_count < 2 and not st.session_state.get('force_auth', False):
        # Allow guest to see the lab first
        if st.button("Enter as Guest (Limited)"):
            st.session_state.show_auth = False
            st.rerun()
        render_auth_page()
    else:
        render_auth_page()
else:
    render_lab()
