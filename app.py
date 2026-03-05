import streamlit as st
from supabase import create_client
from google import genai

# ---------------------
# Page setup
# ---------------------
st.set_page_config(
    page_title="Industrial Formula AI",
    layout="wide"
)

# ---------------------
# Secrets
# ---------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
API_KEY = st.secrets["API_KEY"]

# ---------------------
# Supabase
# ---------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------
# Gemini client
# ---------------------
client = genai.Client(api_key=API_KEY)

# ---------------------
# UI
# ---------------------
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

# ---------------------
# Generate
# ---------------------
if st.button("Generate Formula"):

    if requirements.strip() == "":
        st.warning("Please describe the product")
    else:

        prompt = f"""
You are a professional chemical engineer.

Create an industrial formulation.

Product:
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

        try:

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            result = response.text

            st.subheader("Generated Formula")
            st.markdown(result)

            data = {
                "product_type": product,
                "requirements": requirements,
                "formula": result
            }

            supabase.table("formulas").insert(data).execute()

        except Exception as e:
            st.error("AI generation error")
            st.write(e)
