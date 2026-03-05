import streamlit as st
from google import genai

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Formula AI",
    page_icon="🧪",
    layout="wide"
)

# ----------------------------------
# DARK STYLE (مثل ChatGPT / Gemini)
# ----------------------------------

st.markdown("""
<style>

.stApp{
background-color:#131314;
color:white;
}

[data-testid="stSidebar"]{
background-color:#1e1f20;
}

.chat-title{
font-size:34px;
font-weight:700;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# API KEY
# ----------------------------------

API_KEY = st.secrets["API_KEY"]

client = genai.Client(api_key=API_KEY)

# ----------------------------------
# SESSION STATE
# ----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------
# SIDEBAR
# ----------------------------------

with st.sidebar:

    st.markdown("## 🧪 Formula AI")

    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("### Example Prompts")

    st.write("• Liquid dishwashing detergent")
    st.write("• Laundry powder formula")
    st.write("• Industrial cleaner")

# ----------------------------------
# TITLE
# ----------------------------------

st.markdown('<div class="chat-title">Formula AI</div>', unsafe_allow_html=True)
st.write("AI system specialized in industrial chemical formulations")

# ----------------------------------
# CHAT HISTORY
# ----------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------
# CHAT INPUT
# ----------------------------------

prompt = st.chat_input("Ask for a formula...")

if prompt:

    # user message
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI response
    with st.chat_message("assistant"):

        with st.spinner("Designing formula..."):

            full_prompt = f"""
You are a professional industrial chemist.

Design a full industrial formulation for:

{prompt}

Provide:

1. Raw materials
2. Percentage
3. Function
4. Manufacturing steps
5. pH recommendation
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )

            answer = response.text

            st.markdown(answer)

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })
