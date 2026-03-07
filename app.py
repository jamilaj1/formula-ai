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
# GEMINI STYLE UI
# ------------------------------

st.markdown("""
<style>

.stApp{
background-color:#131314;
color:#e3e3e3;
font-family:system-ui;
}

.block-container{
max-width:900px;
margin:auto;
}

[data-testid="stSidebar"]{
background-color:#1e1f20;
border-right:1px solid rgba(255,255,255,0.08);
}

.title-gradient{
font-size:40px;
font-weight:700;
background:linear-gradient(90deg,#4285f4,#9b72cb,#d96570);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:5px;
}

.subtitle{
color:#b4b4b4;
margin-bottom:25px;
}

.user-msg{
background:#2b2c2e;
padding:14px;
border-radius:14px;
margin-bottom:15px;
}

.ai-msg{
background:#1f2022;
padding:20px;
border-radius:14px;
margin-bottom:20px;
line-height:1.7;
}

table{
width:100%;
border-collapse:collapse;
margin-top:10px;
}

th{
background:#2a2b2e;
padding:10px;
text-align:left;
}

td{
padding:10px;
border-bottom:1px solid rgba(255,255,255,0.06);
}

</style>
""", unsafe_allow_html=True)

# ------------------------------
# GEMINI API
# ------------------------------

API_KEY = st.secrets["API_KEY"]
client = genai.Client(api_key=API_KEY)

# ------------------------------
# SESSION MEMORY
# ------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------------
# SIDEBAR
# ------------------------------

with st.sidebar:

    st.markdown("### 🧪 Formula AI")

    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("#### Example Requests")

    st.write("• Liquid laundry detergent")
    st.write("• Lemon dishwashing liquid")
    st.write("• Face cream formulation")
    st.write("• Acrylic wall paint")
    st.write("• NPK fertilizer")

# ------------------------------
# HEADER
# ------------------------------

st.markdown('<div class="title-gradient">Formula AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Chemical Formulation Platform</div>', unsafe_allow_html=True)

# ------------------------------
# CHAT HISTORY
# ------------------------------

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    else:
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# ------------------------------
# INPUT
# ------------------------------

prompt = st.chat_input("Describe the chemical product you want to formulate...")

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Designing formulation..."):

        ai_prompt = f"""
You are an industrial formulation chemist.

User request:
{prompt}

Rules:

- Ingredient names must be in English
- Formula must be returned as a Markdown table

Format:

### FORMULA

| Ingredient | Percentage | Function |
|-----------|-----------|-----------|

### MANUFACTURING STEPS
Explain clearly.

### pH
Recommended pH.

Language rule:
Explanation language must match the user language.
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
