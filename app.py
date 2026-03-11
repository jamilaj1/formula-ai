import streamlit as st
from google import genai

# -----------------------
# PAGE CONFIG
# -----------------------

st.set_page_config(
    page_title="Formula AI",
    page_icon="🧪",
    layout="wide"
)

# -----------------------
# STYLE
# -----------------------

st.markdown("""
<style>

.stApp{
background:#131314;
color:#e3e3e3;
}

.block-container{
max-width:1000px;
margin:auto;
}

[data-testid="stSidebar"]{
background:#1e1f20;
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

.ai-msg{
background:#1f2022;
padding:20px;
border-radius:14px;
margin-bottom:25px;
}

.score-box{
background:#232426;
padding:15px;
border-radius:12px;
margin-top:10px;
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

# -----------------------
# GEMINI API
# -----------------------

API_KEY = st.secrets["API_KEY"]
client = genai.Client(api_key=API_KEY)

# -----------------------
# HEADER
# -----------------------

st.markdown('<div class="title-gradient">Formula AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Chemical Formulation Platform</div>', unsafe_allow_html=True)

# -----------------------
# INPUT
# -----------------------

prompt = st.chat_input("Describe the chemical product you want to formulate...")

# -----------------------
# AI GENERATION
# -----------------------

if prompt:

    with st.spinner("Designing multiple formulations..."):

        ai_prompt = f"""
You are a professional industrial chemist.

User request:
{prompt}

Create FOUR formulation options:

1 Economy Formula
2 Balanced Formula
3 High Performance Formula
4 Premium Formula

Each formula must include:

FORMULA TABLE

| Ingredient | Percentage | Function |

Then include:

Estimated cost per kg

Performance scores from 1 to 10:

Cleaning Power
Foam
Stability
Skin Safety
Cost Efficiency

Explain advantages of each formula.

Language rule:
Explanations must use the same language as the user.
Ingredient names must always be English.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ai_prompt
        )

        result = response.text

    st.markdown(f'<div class="ai-msg">{result}</div>', unsafe_allow_html=True)
