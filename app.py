import streamlit as st
from google import genai

# ------------------------------
# PAGE CONFIG
# ------------------------------

st.set_page_config(
    page_title="Formula AI",
    page_icon="🧪",
    layout="wide"
)

# ------------------------------
# STYLE (ChatGPT Style)
# ------------------------------

st.markdown("""
<style>

.stApp{
background-color:#0f0f0f;
color:white;
}

[data-testid="stSidebar"]{
background-color:#171717;
}

.chat-title{
font-size:36px;
font-weight:700;
margin-bottom:5px;
}

.chat-sub{
color:#9aa0a6;
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------
# API KEY
# ------------------------------

API_KEY = st.secrets["API_KEY"]

client = genai.Client(api_key=API_KEY)

# ------------------------------
# SESSION
# ------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------------
# SIDEBAR
# ------------------------------

with st.sidebar:

    st.markdown("## 🧪 Formula AI")

    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("### Examples")

    st.write("Dishwashing liquid")
    st.write("Laundry powder")
    st.write("Liquid detergent")

# ------------------------------
# TITLE
# ------------------------------

st.markdown('<div class="chat-title">Formula AI</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-sub">AI specialized in industrial chemical formulations</div>', unsafe_allow_html=True)

# ------------------------------
# CHAT HISTORY
# ------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------------------
# USER INPUT
# ------------------------------

prompt = st.chat_input("Describe the product you want to formulate...")

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Designing formula..."):

            ai_prompt = f"""
You are a professional industrial chemist.

Create a CLEAN and SIMPLE formulation.

Product:
{prompt}

Rules:
- Do NOT generate large tables
- Use bullet points
- Keep it clean and readable

Return in this format:

FORMULA

Ingredient – percentage – function

MANUFACTURING

Step 1
Step 2
Step 3

PH

Recommended pH
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_prompt
            )

            answer = response.text

            st.markdown(answer)

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })
