import streamlit as st
from google import genai

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Formula AI",
    page_icon="🧪",
    layout="wide"
)

# ---------------------------
# STYLE
# ---------------------------

st.markdown("""
<style>

.stApp{
background:#0f0f0f;
color:white;
}

.block-container{
max-width:900px;
margin:auto;
}

[data-testid="stSidebar"]{
background:#171717;
border-right:1px solid #2a2a2a;
}

.chat-title{
font-size:36px;
font-weight:700;
margin-bottom:5px;
}

.chat-sub{
color:#9aa0a6;
margin-bottom:30px;
}

.user-msg{
background:#2a2a2a;
padding:14px;
border-radius:12px;
margin-bottom:15px;
}

.ai-msg{
background:#1b1b1b;
padding:20px;
border-radius:12px;
margin-bottom:20px;
}

table{
width:100%;
border-collapse:collapse;
margin-top:10px;
}

th{
background:#262626;
padding:10px;
text-align:left;
}

td{
padding:10px;
border-bottom:1px solid #2a2a2a;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# GEMINI API
# ---------------------------

API_KEY = st.secrets["API_KEY"]

client = genai.Client(api_key=API_KEY)

# ---------------------------
# SESSION
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# SIDEBAR
# ---------------------------

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

# ---------------------------
# HEADER
# ---------------------------

st.markdown('<div class="chat-title">Formula AI</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-sub">AI specialized in industrial chemical formulations</div>', unsafe_allow_html=True)

# ---------------------------
# SHOW CHAT
# ---------------------------

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    else:
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# ---------------------------
# INPUT
# ---------------------------

prompt = st.chat_input("Describe the product you want to formulate...")

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Designing formula..."):

        ai_prompt = f"""
You are a professional industrial chemist.

User request:
{prompt}

IMPORTANT RULES:

1. The FORMULA table must ALWAYS be in English.
2. Ingredient names must ALWAYS be in English.
3. Table headers must be:
Ingredient | Percentage | Function

4. All explanations, manufacturing steps, and comments must be written in the SAME LANGUAGE as the user request.

Example:
If the user writes Arabic → explanations Arabic.
If the user writes English → explanations English.

Return format:

### FORMULA

| Ingredient | Percentage | Function |
|-----------|-----------|-----------|

### MANUFACTURING STEPS

Explain steps.

### pH

Explain recommended pH.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ai_prompt
        )

        answer = response.text

    st.markdown(f'<div class="ai-msg">{answer}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })
