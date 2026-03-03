import streamlit as st
from supabase import create_client
from google import genai

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
                st.error("Authentication failed.")

    with tab2:
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({
                    "email": reg_email,
                    "password": reg_pass
                })
                st.success("Account created. Please login.")
            except Exception as e:
                st.error(str(e))

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

    # ✅ استخدام API الحديثة
    client = genai.Client(api_key=st.secrets["API_KEY"])

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"You are a senior industrial chemical engineer. Answer professionally:\n{prompt}"
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
