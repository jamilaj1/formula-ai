import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime
import uuid

# =========================
# 1. PAGE CONFIGURATION
# =========================
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# =========================
# 2. SESSION & THEME INIT
# =========================
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"

# Force Gemini Dark aesthetics and fix white background issues
if st.session_state.theme_mode == "Dark":
    bg, side, txt, card = "#131314", "#1e1f20", "#e3e3e3", "#1e1f20"
    border = "#444746"
else:
    bg, side, txt, card = "#ffffff", "#f0f4f9", "#1f1f1f", "#f8fafd"
    border = "#c4c7c5"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {side} !important; border-right: 1px solid rgba(255,255,255,0.05); }}
    .gemini-title {{
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}
    .stChatInputContainer {{ background-color: {card} !important; border: 1px solid {border} !important; border-radius: 28px !important; }}
    header {{ visibility: hidden !important; }}
</style>
""", unsafe_allow_html=True)

# =========================
# 3. DATABASE & AI CORE
# =========================
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

def get_ai_model():
    genai.configure(api_key=st.secrets["API_KEY"])
    # Fixing 404 error by using the standard stable model string
    return genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 4. SAFETY & USAGE LOGIC
# =========================
def check_pro_status(email):
    try:
        # Handling the missing table issue with a try-except
        res = supabase.table("users_usage").select("is_pro").eq("email", email).execute()
        return res.data[0]["is_pro"] if res.data else True # Default to True for now
    except:
        return True

def save_formula_record(email, title, content):
    try:
        supabase.table("saved_formulas").insert({
            "id": str(uuid.uuid4()),
            "email": email,
            "formula_title": title,
            "formula_content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return True
    except: return False

# =========================
# 5. AUTHENTICATION MODULE
# =========================
def render_auth():
    st.markdown("<p class='gemini-title'>Pro Authentication</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        # Added unique keys to prevent DuplicateElementId error
        email_login = st.text_input("Professional Email", key="auth_login_email_unique")
        pass_login = st.text_input("Password", type="password", key="auth_login_pass_unique")
        if st.button("Access Laboratory", key="auth_login_btn_unique"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Authentication failed. Please verify credentials.")

    with tab2:
        name_reg = st.text_input("Full Name", key="auth_reg_name_unique")
        email_reg = st.text_input("Professional Email", key="auth_reg_email_unique")
        pass_reg = st.text_input("Security Password", type="password", key="auth_reg_pass_unique")
        if st.button("Initialize Pro Account", key="auth_reg_btn_unique"):
            try:
                # User Auth Signup
                res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg, "options": {"data": {"full_name": name_reg}}})
                st.success("Account created successfully. Please login to continue.")
            except Exception as e: st.error(f"Error: {e}")

# =========================
# 6. MAIN APPLICATION
# =========================
def render_main():
    with st.sidebar:
        st.markdown("### ⚙️ Workspace")
        theme = st.toggle("Dark Mode ✨", value=(st.session_state.theme_mode == "Dark"))
        st.session_state.theme_mode = "Dark" if theme else "Light"
        st.divider()
        if st.session_state.user_email:
            st.success(f"Verified: {st.session_state.user_email}")
            if st.button("Logout 🚪"):
                st.session_state.user_email = None
                st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.markdown("Advanced Chemical Engineering Assistant")

    model = get_ai_model()

    # Display Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Chat Interaction
    if prompt := st.chat_input("Enter formulation query..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Calculating industrial parameters..."):
                try:
                    response = model.generate_content(f"Expert Engineer: {prompt}")
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    
                    # Option to save the result
                    if st.button("💾 Save Result"):
                        if save_formula_record(st.session_state.user_email, prompt[:50], answer):
                            st.toast("Formula saved to database.")
                        else:
                            st.toast("Error saving. Table may not be ready.")
                except Exception as e:
                    st.error(f"AI System Error: {e}")

    if st.button("Clear Workspace"):
        st.session_state.chat_history = []
        st.rerun()

# =========================
# 7. ROUTING
# =========================
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
