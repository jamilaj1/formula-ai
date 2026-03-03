import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION & THEME ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

# Professional UI Styling with Pricing Cards
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
    .sidebar-name { font-size: 1.5rem; font-weight: 700; color: #1E293B; margin-top: 5px; }
    .premium-badge { background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; }
    .pricing-card { background-color: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center; }
    .pricing-header { font-size: 1.5rem; font-weight: 700; color: #1E293B; }
    .price { font-size: 2rem; font-weight: 800; color: #2563EB; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_db()
except Exception as e:
    st.error(f"Database link broken: {e}")

# --- 3. SESSION STATE ---
if "user_email" not in st.session_state: st.session_state.user_email = None

# --- 4. AUTHENTICATION & PRICING UI ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">The elite intelligence for chemical manufacturing.</p>', unsafe_allow_html=True)
    
    # Pricing Table for Motivation
    st.markdown("### 💎 Choose Your Plan")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="pricing-card">
            <div class="pricing-header">Free Guest</div>
            <div class="price">$0</div>
            <p>• View Interface<br>• No AI Formulas<br>• No Cost Analysis</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="pricing-card" style="border-color: #2563EB;">
            <div class="pricing-header">Premium Pro</div>
            <div class="price">$29/mo</div>
            <p>• Unlimited AI Formulas<br>• Accurate Cost (GHS)<br>• Full Technical Support</p>
        </div>""", unsafe_allow_html=True)
    
    st.divider()
    
    tab1, tab2 = st.tabs(["🔐 Login to Workspace", "📝 Register New Account"])

    with tab1:
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Unlock Laboratory"):
            try:
                res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        s_name = st.text_input("Full Name (Official)", placeholder="Jamil Abduljalil")
        s_email = st.text_input("Email Address")
        s_pass = st.text_input("Create Password", type="password")
        if st.button("Create Pro Account"):
            if len(s_pass) < 6 or not s_name: st.warning("⚠️ Full Name and valid password are required.")
            else:
                try:
                    res = supabase.auth.sign_up({
                        "email": s_email, "password": s_pass,
                        "options": {"data": {"full_name": s_name}}
                    })
                    if res.user:
                        st.session_state.user_email = res.user.email
                        st.success(f"✅ Welcome, {s_name}! Entering Pro Mode...")
                        time.sleep(1.5)
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

# --- 5. PREMIUM LABORATORY (MAIN APP) ---
def render_lab():
    # Identify Professional Name
    try:
        user_info = supabase.auth.get_user()
        display_name = user_info.user.user_metadata.get("full_name", "Valued Client")
    except: display_name = "Premium Member"

    # Sidebar: Clean and Personalized
    with st.sidebar:
        st.markdown(f"**Current Operator:**\n<div class='sidebar-name'>{display_name} <span class='premium-badge'>PRO</span></div>", unsafe_allow_html=True)
        st.success("Status: Secure Connection")
        st.divider()
        if st.button("Clear Lab Records 🧹"):
            st.session_state.msg = []
            st.rerun()
        if st.button("Secure Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown(f"Industrial Intelligence Workspace. The lab is ready, **{display_name}**.")

    # --- AI CHAT CORE ---
    try:
        genai.configure(api_key=st.secrets["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if "msg" not in st.session_state: st.session_state.msg = []
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Enter formula requirements or production goals..."):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                # System instruction injected for high-quality response
                full_prompt = f"As a Senior Chemical Engineer, answer this: {prompt}. Provide formulas in English, costs in GHS."
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
    except Exception as e: st.error(f"AI System Busy: {e}")

# --- 6. ROUTING LOGIC ---
if st.session_state.user_email is None:
    render_auth_page()
else:
    render_lab()
