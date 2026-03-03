import streamlit as st
import google.generativeai as genai
from supabase import create_client
from datetime import datetime
import uuid

# =========================
# 1. CONFIGURATION
# =========================
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# =========================
# 2. CSS THEMES
# =========================
dark_css = """
<style>
.stApp { background-color: #131314; color: #e3e3e3; }
section[data-testid="stSidebar"] { background-color: #1e1f20; }
.gemini-title {
    font-size: 3rem; font-weight: 700;
    background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
</style>
"""

light_css = """
<style>
.stApp { background-color: #f5f5f5; color: #000; }
section[data-testid="stSidebar"] { background-color: #ffffff; }
</style>
"""

# =========================
# 3. DATABASE INIT
# =========================
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# =========================
# 4. SESSION INIT
# =========================
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# =========================
# 5. THEME
# =========================
if st.session_state.dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    st.markdown(light_css, unsafe_allow_html=True)

# =========================
# 6. SIDEBAR
# =========================
with st.sidebar:

    st.title("⚙️ Control Panel")

    st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)

    st.divider()

    if st.session_state.user_email:
        st.success(f"Logged in as {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()
    else:
        st.warning("Not Authenticated")

# =========================
# 7. AUTH MODULE
# =========================
def auth_page():
    st.title("🔐 Pro Authentication")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user_email = res.user.email
                st.rerun()
            except:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register"):
            try:
                res = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {"data": {"full_name": name}}
                })

                # create usage record
                supabase.table("users_usage").insert({
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "usage_count": 0,
                    "is_pro": True
                }).execute()

                st.success("Account created")
            except Exception as e:
                st.error(str(e))

# =========================
# 8. USAGE CONTROL
# =========================
def check_usage(email):
    data = supabase.table("users_usage").select("*").eq("email", email).execute()

    if not data.data:
        return False

    user = data.data[0]
    return user["is_pro"]

def increment_usage(email):
    data = supabase.table("users_usage").select("*").eq("email", email).execute()
    user = data.data[0]

    supabase.table("users_usage").update({
        "usage_count": user["usage_count"] + 1
    }).eq("email", email).execute()

# =========================
# 9. AI ENGINE
# =========================
def get_ai_model():
    genai.configure(api_key=st.secrets["API_KEY"])

    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction="""
        You are a senior industrial chemical engineer.
        Always provide:
        1) Structured formula
        2) Batch size example
        3) Cost calculation placeholder
        4) Safety notes
        """
    )

# =========================
# 10. SAVE FORMULA
# =========================
def save_formula(email, title, content):
    supabase.table("saved_formulas").insert({
        "id": str(uuid.uuid4()),
        "email": email,
        "formula_title": title,
        "formula_content": content,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

# =========================
# 11. MAIN APP
# =========================
def main_app():

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)

    if not check_usage(st.session_state.user_email):
        st.error("Access restricted")
        return

    model = get_ai_model()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about chemical formulation..."):

        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing industrial parameters..."):
                response = model.generate_content(prompt)
                answer = response.text

                st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        increment_usage(st.session_state.user_email)

        if st.button("Save This Formula"):
            save_formula(st.session_state.user_email, prompt[:50], answer)
            st.success("Formula Saved")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# =========================
# 12. ROUTING
# =========================
if not st.session_state.user_email:
    auth_page()
else:
    main_app()
