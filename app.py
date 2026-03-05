import streamlit as st
import google.generativeai as genai
from supabase import create_client

st.set_page_config(page_title="Formula AI", layout="wide")

# secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["API_KEY"]

# connect supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# connect gemini
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash-latest")

st.title("Industrial Formula AI")

product = st.selectbox(
    "Product Type",
    ["Detergent", "Shampoo", "Paint", "Adhesive", "Cosmetics"]
)

requirements = st.text_area("Describe your product")

if st.button("Generate Formula"):

    prompt = f"""
You are a senior chemical engineer.

Generate an industrial formulation.

Product type:
{product}

Requirements:
{requirements}

Return:

1. Ingredients
2. Percentages
3. Manufacturing Process
4. Safety Notes
"""

    response = model.generate_content(prompt)

    st.subheader("Generated Formula")

    st.markdown(response.text)
