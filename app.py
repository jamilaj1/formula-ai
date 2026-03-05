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
margin-top:15px;
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
# GEMINI
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
    st.write("Hand soap")
    st.write("Shampoo")

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

    with st.spinner("Designing industrial formula..."):

        ai_prompt = f"""
You are an industrial formulation chemist.

User request:
{prompt}

RULES:

1. Ingredient names MUST always be in English.
2. Formula table MUST always be in English.
3. Explanations must be in the SAME language used by the user.

Return result using this format.

### PRODUCT TYPE
Identify product type.

### CONCENTRATION LEVEL
Economy / Standard / Premium

### FORMULA

| Ingredient | Percentage | Function |
|-----------|-----------|-----------|

### MANUFACTURING STEPS

Explain steps clearly.

### RECOMMENDED pH

Explain ideal pH.

### ESTIMATED COST

Estimate raw material cost per kg.

### SUGGESTED MARKET PRICE

Suggested selling price.
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
