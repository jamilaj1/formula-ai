import streamlit as st
import google.generativeai as genai
from supabase import create_client

# -----------------------------------
# 1. PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="Formula AI Pro", page_icon="🧪", layout="wide")

# -----------------------------------
# 2. DARK UI
# -----------------------------------
st.markdown("""
<style>
.stApp { background-color: #131314; color: #e3e3e3; }
section[data-testid="stSidebar"] { background-color: #1e1f20; }
.gemini-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# 3. SESSION STATE
# -----------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------
# 4. SUPABASE INIT
# -----------------------------------
@st.cache_resource
def init_db():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = init_db()

# -----------------------------------
# 5. AUTH PAGE
# -----------------------------------
def render_auth():
    st.markdown("<h1 class='gemini-title'>Pro Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user_email = res.user.email
                st.rerun()
            except Exception:
                st.error("Authentication failed. Check email or password.")

    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({
                    "email": reg_email,
                    "password": reg_pass
                })
                st.success("Account created successfully. Please login.")
            except Exception as e:
                st.error(f"Registration error: {e}")

# -----------------------------------
# 6. MAIN APP
# -----------------------------------
def render_main():

    with st.sidebar:
        st.success(f"Operator: {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("<h1 class='gemini-title'>Formula AI Pro</h1>", unsafe_allow_html=True)
    st.write("Advanced Industrial Intelligence Laboratory")

    # AI CONFIG
    genai.configure(api_key=st.secrets["API_KEY"])

    # 🔥 موديل مستقر
    model = genai.GenerativeModel("gemini-1.5-pro")

    # عرض المحادثة السابقة
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # إدخال جديد
    if prompt := st.chat_input("Enter your manufacturing query..."):

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing formulation parameters..."):
                try:
                    response = model.generate_content(
                        f"You are a senior industrial chemical engineer. Answer professionally:\n{prompt}"
                    )
                    answer = response.text

                    st.markdown(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"AI Error: {e}")

# -----------------------------------
# 7. ROUTING
# -----------------------------------
if not st.session_state.user_email:
    render_auth()
else:
    render_main()
