# app.py

import streamlit as st
import google.generativeai as genai
from supabase import create_client

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Industrial Formula AI",
    layout="wide"
)

# -----------------------------
# Secrets
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["API_KEY"]

# -----------------------------
# Supabase connection
# -----------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Gemini configuration
# -----------------------------
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

# -----------------------------
# UI
# -----------------------------
st.title("Industrial Formula AI")

st.write("AI system for generating industrial product formulations.")

product = st.selectbox(
    "Product Type",
    [
        "Detergent",
        "Shampoo",
        "Paint",
        "Adhesive",
        "Cosmetics"
    ]
)

requirements = st.text_area(
    "Describe your product",
    height=200
)

# -----------------------------
# Generate button
# -----------------------------
if st.button("Generate Formula"):

    if requirements.strip() == "":
        st.warning("Please describe the product first.")
    else:

        prompt = f"""
You are a senior chemical engineer.

Generate a professional industrial formulation.

Product type:
{product}

Requirements:
{requirements}

Return the answer in this structure:

1. Ingredients list
2. Percentage of each ingredient
3. Manufacturing process
4. Safety notes
5. Estimated pH
"""

        with st.spinner("Generating formula..."):

            try:

                response = model.generate_content(prompt)

                result = response.text

                st.subheader("Generated Formula")

                st.markdown(result)

                # -----------------------------
                # Save to Supabase
                # -----------------------------
                data = {
                    "product_type": product,
                    "requirements": requirements,
                    "formula": result
                }

                supabase.table("formulas").insert(data).execute()

            except Exception as e:
                st.error("AI generation error")
                st.exception(e)
