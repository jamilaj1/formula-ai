import streamlit as st
from supabase import create_client
from google import genai
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Formula AI | Premium", page_icon="🧪", layout="centered")

st.markdown("""
<style>
.main-title { font-size: 3rem; font-weight: 800; text-align: center; }
.sub-title { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px; }
.stButton>button { border-radius: 8px; font-weight: 600; width: 100%; padding: 12px 0; }
.sidebar-name { font-size: 1.3rem; font-weight: 700; margin-top: 5px; }
.premium-badge { background-color: #FACC15; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# --- 3. SESSION ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. AUTH PAGE ---
def render_auth_page():
    st.markdown('<p class="main-title">Formula AI Global 🌍</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Industrial Chemical Intelligence Platform</p>', unsafe_allow_html=True)

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
                st.error("Invalid credentials.")

    with tab2:
        name = st.text_input("Full Name")
        reg_email = st.text_input("Email Address")
        reg_pass = st.text_input("Password (Min 6 chars)", type="password")

        if st.button("Register"):
            if len(reg_pass) < 6 or not name:
                st.warning("Please complete all fields.")
            else:
                try:
                    supabase.auth.sign_up({
                        "email": reg_email,
                        "password": reg_pass,
                        "options": {"data": {"full_name": name}}
                    })
                    st.success("Account created. Please login.")
                except Exception as e:
                    st.error(str(e))

# --- 5. MAIN LAB ---
def render_lab():

    client = genai.Client(api_key=st.secrets["API_KEY"])

    with st.sidebar:
        st.success(f"Operator: {st.session_state.user_email}")
        if st.button("Clear History"):
            st.session_state.messages = []
            st.rerun()
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()

    st.title("🧪 Formula AI Studio")
    st.markdown("Ask for industrial formulations, cost analysis, or scaling calculations.")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New prompt
    if prompt := st.chat_input("Enter your manufacturing query..."):

        st.session_state.messages.append({"role": "user", "content": prompt})

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

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"AI Error: {e}")

# --- 6. ROUTING ---
if st.session_state.user_email is None:
    render_auth_page()
else:
    render_lab()
