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
# 2. SESSION INITIALIZATION
# =========================
if "user_email" not in st.session_state: st.session_state.user_email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "dark_mode" not in st.session_state: st.session_state.dark_mode = True

# =========================
# 3. CSS THEMES (GEMINI STYLE)
# =========================
# We use !important to force the colors and prevent white patches
if st.session_state.dark_mode:
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
# 4. DATABASE & AI INIT
# =========================
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

def get_ai_model():
    genai.configure(api_key=st.secrets["API_KEY"])
    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction="""
        You are Formula AI, a senior industrial chemical engineer. 
        User: Jamil Abduljalil.
        Response Requirements:
        1) Professional English only.
        2) Structured formula with batch size examples.
        3) Safety protocols and industrial cost placeholders.
        """
    )

# =========================
# 5. USAGE & STORAGE LOGIC
# =========================
def check_usage(email):
    try:
        data = supabase.table("users_usage").select("*").eq("email", email).execute()
        return data.data[0]["is_pro"] if data.data else False
    except: return False

def increment_usage(email):
    try:
        data = supabase.table("users_usage").select("*").eq("email", email).execute()
        if data.data:
            new_count = data.data[0]["usage_count"] + 1
            supabase.table("users_usage").update({"usage_count": new_count}).eq("email", email).execute()
    except: pass

def save_formula(email, title, content):
    supabase.table("saved_formulas").insert({
        "id": str(uuid.uuid4()),
        "email": email,
        "formula_title": title,
        "formula_content": content,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

# =========================
# 6. AUTHENTICATION MODULE
# =========================
def auth_page():
    st.markdown("<p class='gemini-title'>Pro Authentication</p>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        email = st.text_input("Professional Email", key="log_email_id")
        password = st.text_input("Password", type="password", key="log_pass_id")
        if st.button("Access Laboratory", key="log_btn_id"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user_email = res.user.email
                st.rerun()
            except: st.error("Authentication failed. Check credentials.")

    with tab2:
        name = st.text_input("Full Name", key="reg_name_id")
        email_reg = st.text_input("Email", key="reg_email_id")
        pass_reg = st.text_input("Password", type="password", key="reg_pass_id")
        if st.button("Initialize Pro Account", key="reg_btn_id"):
            try:
                res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg, "options": {"data": {"full_name": name}}})
                supabase.table("users_usage").insert({
                    "id": str(uuid.uuid4()), "email": email_reg, "usage_count": 0, "is_pro": True
                }).execute()
                st.success("Account initialized! Please login.")
            except Exception as e: st.error(f"Registration error: {e}")

# =========================
# 7. MAIN LABORATORY
# =========================
def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")
        st.session_state.dark_mode = st.toggle("Dark Mode ✨", value=st.session_state.dark_mode)
        st.divider()
        st.success(f"Verified Operator: {st.session_state.user_email}")
        if st.button("Logout 🚪", key="logout_btn_id"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    
    if not check_usage(st.session_state.user_email):
        st.error("Access restricted. No Pro license found.")
        return

    model = get_ai_model()

    # Chat Display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about chemical formulation..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing parameters..."):
                response = model.generate_content(prompt)
                answer = response.text
                st.markdown(answer)
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        increment_usage(st.session_state.user_email)

        if st.button("💾 Save Formula"):
            save_formula(st.session_state.user_email, prompt[:50], answer)
            st.toast("Formula Saved Successfully!")

    if st.button("Clear Workspace"):
        st.session_state.chat_history = []
        st.rerun()

# =========================
# 8. ROUTING
# =========================
if not st.session_state.user_email:
    auth_page()
else:
    main_app()
