import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import time

# --- 1. PAGE CONFIGURATION & THEME ---
# Updated Title: Only "Formula AI"
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

# Professional UI Styling with Pricing Cards
st.markdown("""
<style>
    /* Styling for the main clean titles */
    .main-title { font-size: 3rem; font-weight: 800; text-align: center; color: #0F172A; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
    
    /* Elegant styling for buttons */
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
    
    /* Sidebar name & badge styling (No Email Shown) */
    .sidebar-name { font-size: 1.5rem; font-weight: 700; color: #1E293B; margin-top: 5px; }
    .premium-badge { background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 5px; }
    
    /* Pricing Table design */
    .pricing-card { background-color: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 12px; padding: 20px; text-align: center; height: 100%;}
    .pricing-header { font-size: 1.5rem; font-weight: 700; color: #1E293B; }
    .price { font-size: 2.2rem; font-weight: 800; color: #2563EB; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
@st.cache_resource
def init_db() -> Client:
    # Safely connect to Supabase
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Database Config Missing: {e}")
        return None

try:
    supabase = init_db()
except:
    supabase = None

# --- 3. SESSION STATE ---
if "user_email" not in st.session_state: 
    st.session_state.user_email = None

# --- 4. AUTHENTICATION & PRICING UI ---
def render_auth_page():
    # Title: Clean "Formula AI"
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Advanced chemical formulation intelligence for professionals.</p>', unsafe_allow_html=True)
    
    # Pricing Table to encourage registration
    st.markdown("### 💎 Choose Your Plan")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="pricing-card">
            <div class="pricing-header">Guest Preview</div>
            <div class="price">$0</div>
            <p>• View Interface<br>• No AI Interaction<br>• Limited Preview</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="pricing-card" style="border-color: #2563EB;">
            <div class="pricing-header">Premium PRO</div>
            <div class="price">$29/mo</div>
            <p>• Unlimited AI Formulas<br>• GHS Cost Analysis<br>• Technical Support</p>
        </div>""", unsafe_allow_html=True)
    
    st.divider()
    
    # Login & Register Tabs
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Pro Account"])

    with tab1:
        l_email = st.text_input("Email", key="l_email")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Authenticate & Access"):
            if not supabase: return
            try:
                res = supabase.auth.sign_in_with_password({"email": l_email, "password": l_pass})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: 
                st.error("❌ Invalid credentials. Please try again.")

    with tab2:
        s_name = st.text_input("Full Name (Official)", placeholder="Jamil Abduljalil", key="s_name")
        s_email = st.text_input("Email Address", key="s_email")
        s_pass = st.text_input("Create Secure Password", type="password", key="s_pass")
        if st.button("Register & Initialize PRO Account"):
            if not supabase: return
            if len(s_pass) < 6 or not s_name or not s_email: 
                st.warning("⚠️ Full Name, Email, and 6-char password are required.")
            else:
                try:
                    res = supabase.auth.sign_up({
                        "email": s_email, "password": s_pass,
                        "options": {"data": {"full_name": s_name}}
                    })
                    if res.user:
                        # Auto-login after registration
                        st.session_state.user_email = res.user.email
                        st.success(f"✅ Welcome aboard, {s_name}!")
                        time.sleep(1.5)
                        st.rerun()
                except Exception as e: 
                    st.error(f"❌ Error during registration: {e}")

# --- 5. PREMIUM LABORATORY (MAIN APP) ---
def render_lab():
    # Fetch user's Full Name from Supabase Metadata
    try:
        user_data = supabase.auth.get_user()
        display_name = user_data.user.user_metadata.get("full_name", "Valued Client")
    except: 
        display_name = "Premium Operator"

    # Sidebar: Personalized, clean, showing NAME ONLY
    with st.sidebar:
        st.markdown(f"**Operator:**\n<div class='sidebar-name'>{display_name} <span class='premium-badge'>PRO</span></div>", unsafe_allow_html=True)
        st.success("🟢 Connection: SECURE")
        st.divider()
        if st.button("Clear Lab Records 🧹"):
            st.session_state.msg = []
            if "chat" in st.session_state: del st.session_state.chat
            st.rerun()
        if st.button("Secure Logout 🚪"):
            st.session_state.user_email = None
            st.rerun()

    # Title: Clean "Formula AI"
    st.title("🧪 Formula AI")
    st.markdown(f"Greetings, **{display_name}**. The AI laboratory is ready for your parameters.")

    # --- AI CHAT CORE (Only for PRO Users) ---
    try:
        MY_API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=MY_API_KEY)
        
        @st.cache_resource
        def init_ai_model():
            # Injecting system identity as a Senior Engineer
            instr = "You are Formula AI Expert. You are a senior chemical engineer. Reply in user's language. Provide precise formulas and cost analysis in GHS. Ask for Sector, Objective, Batch Size, Currency (if not GHS)."
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return genai.GenerativeModel(model_name=models[0], system_instruction=instr)
            
        ai_engine = init_ai_model()
        
        # Initialize Chat History
        if "msg" not in st.session_state: st.session_state.msg = []
        if "chat" not in st.session_state: st.session_state.chat = ai_engine.start_chat(history=[])

        # Display Chat History
        for m in st.session_state.msg:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # Input & Response Logic
        if prompt := st.chat_input("Enter formula query or goals..."):
            st.session_state.msg.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.msg.append({"role": "assistant", "content": response.text})
                
    except Exception as e: 
        st.error(f"⚠️ AI Core is offline. Please check secrets/API Key. Details: {e}")

# --- 6. ROUTING ENGINE ---
if st.session_state.user_email is None:
    render_auth_page()
else:
    # Routing requires active supabase connection
    if supabase:
        render_lab()
    else:
        st.error("Database connection failed. App cannot load.")
