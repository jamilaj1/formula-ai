import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import uuid
import time

# -----------------------------
# 1. Page Config
# -----------------------------
st.set_page_config(
    page_title="Formula AI Pro",
    page_icon="🧪",
    layout="wide"
)

# -----------------------------
# 2. Dark Theme UI
# -----------------------------
st.markdown("""
<style>

.stApp {
background-color:#131314;
color:#e3e3e3;
}

section[data-testid="stSidebar"]{
background:#1e1f20;
border-right:1px solid rgba(255,255,255,0.05);
}

.gemini-title{
font-size:3.5rem;
font-weight:700;
background:linear-gradient(90deg,#4285f4,#9b72cb,#d96570);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:5px;
}

.stChatInputContainer{
background-color:#1e1f20;
border:1px solid #444746;
border-radius:28px;
}

header{
visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. Session Init
# -----------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# 4. Init Connections
# -----------------------------
@st.cache_resource
def init_connections():

    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

    genai.configure(
        api_key=st.secrets["API_KEY"]
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config={
            "temperature":0.6,
            "top_p":1,
            "max_output_tokens":2048
        }
    )

    return supabase, model


supabase, model = init_connections()

# -----------------------------
# 5. Save Chat to DB
# -----------------------------
def save_chat(email, user_msg, ai_msg):

    try:

        supabase.table("saved_formulas").insert({

            "id":str(uuid.uuid4()),
            "email":email,
            "formula_title":user_msg[:60],
            "formula_content":ai_msg

        }).execute()

    except Exception as e:
        pass


# -----------------------------
# 6. Authentication UI
# -----------------------------
def render_auth():

    st.markdown('<p class="gemini-title">Pro Access</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login","Create Account"])

    # -----------------
    # LOGIN
    # -----------------

    with tab1:

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):

            try:

                res = supabase.auth.sign_in_with_password({
                    "email":email,
                    "password":password
                })

                st.session_state.user_email = res.user.email
                st.rerun()

            except Exception:
                st.error("Login failed")


    # -----------------
    # REGISTER
    # -----------------

    with tab2:

        name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Create Account"):

            try:

                supabase.auth.sign_up({
                    "email":email,
                    "password":password,
                    "options":{
                        "data":{
                            "full_name":name
                        }
                    }
                })

                supabase.table("users_usage").insert({

                    "email":email,
                    "is_pro":True

                }).execute()

                st.success("Account created. Please login.")

            except Exception as e:

                st.error("Registration error")


# -----------------------------
# 7. AI Streaming
# -----------------------------
def stream_ai(prompt):

    response = model.generate_content(
        f"""
You are a senior industrial chemical engineer.

Provide professional and structured answers.

Question:
{prompt}
""",
        stream=True
    )

    full_text=""

    for chunk in response:

        if chunk.text:
            full_text+=chunk.text
            yield full_text


# -----------------------------
# 8. Main App
# -----------------------------
def render_main():

    with st.sidebar:

        st.markdown("### Workspace Settings")

        st.success(
            f"Operator: {st.session_state.user_email}"
        )

        if st.button("Logout"):
            st.session_state.user_email=None
            st.rerun()

    st.markdown('<p class="gemini-title">Formula AI Pro</p>', unsafe_allow_html=True)

    st.markdown(
        "Advanced Industrial Intelligence Laboratory"
    )

    # -----------------
    # Show History
    # -----------------

    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])


    # -----------------
    # Chat Input
    # -----------------

    if prompt := st.chat_input("Enter manufacturing query..."):

        st.session_state.chat_history.append({
            "role":"user",
            "content":prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            placeholder = st.empty()

            full_response=""

            try:

                for chunk in stream_ai(prompt):

                    full_response = chunk
                    placeholder.markdown(full_response)

                st.session_state.chat_history.append({

                    "role":"assistant",
                    "content":full_response

                })

                save_chat(
                    st.session_state.user_email,
                    prompt,
                    full_response
                )

            except Exception as e:

                st.error("AI system busy")


# -----------------------------
# 9. Router
# -----------------------------
if not st.session_state.user_email:

    render_auth()

else:

    render_main()
