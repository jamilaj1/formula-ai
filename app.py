import streamlit as st
import google.generativeai as genai
from supabase import create_client

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Industrial Formula AI",
    layout="wide"
)

# -------------------------
# Secrets
# -------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["API_KEY"]

# -------------------------
# Connect Supabase
# -------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Configure Gemini
# -------------------------
genai.configure(api_key=API_KEY)

# النموذج الصحيح حالياً
model = genai.GenerativeModel("gemini-1.5-pro")

# -------------------------
# UI
# -------------------------
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

# -------------------------
# Generate Formula
# -------------------------
if st.button("Generate Formula"):

    if requirements.strip() == "":
        st.warning("Please describe the product first.")
    else:

        prompt = f"""
You are a professional chemical engineer.

Create an industrial formulation.

Product type:
{product}

Requirements:
{requirements}

Return:

1. Ingredients
2. Percentage of each ingredient
3. Manufacturing process
4. Safety notes
5. Estimated pH
"""

        with st.spinner("Generating formula..."):

            try:

                response = model.generate_content(prompt)

                formula = response.text

                st.subheader("Generated Formula")

                st.markdown(formula)

                # Save to database
                data = {
                    "product_type": product,
                    "requirements": requirements,
                    "formula": formula
                }

                supabase.table("formulas").insert(data).execute()

            except Exception as e:
                st.error("AI generation error")
                st.write(e)
