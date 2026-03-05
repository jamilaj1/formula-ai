import streamlit as st
from google import genai

# ----------------------------------
# Page Configuration
# ----------------------------------

st.set_page_config(
    page_title="Industrial Formula AI",
    page_icon="🧪",
    layout="centered"
)

st.title("Industrial Formula AI")
st.write("AI system for generating industrial product formulations.")

# ----------------------------------
# Load API Key
# ----------------------------------

try:
    API_KEY = st.secrets["API_KEY"]
except:
    st.error("API key not found. Please add it in Streamlit Secrets.")
    st.stop()

# ----------------------------------
# Gemini Client
# ----------------------------------

client = genai.Client(api_key=API_KEY)

# ----------------------------------
# Product Selection
# ----------------------------------

product_type = st.selectbox(
    "Product Type",
    [
        "Detergent",
        "Dishwashing Liquid",
        "Shampoo",
        "Liquid Soap",
        "Fabric Softener",
        "Industrial Cleaner"
    ]
)

description = st.text_area(
    "Describe your product",
    height=200,
    placeholder="Example:\nHigh foam dishwashing liquid\nLemon fragrance\nStrong grease removal\nSkin friendly"
)

generate = st.button("Generate Formula")

# ----------------------------------
# AI Generation
# ----------------------------------

if generate:

    if description.strip() == "":
        st.warning("Please describe your product first.")
        st.stop()

    prompt = f"""
You are an expert industrial chemist.

Create a professional formulation for the following product.

Product type:
{product_type}

Description:
{description}

Provide:

1. Raw materials
2. Percentage of each ingredient
3. Function of each ingredient
4. Manufacturing steps
5. Notes about pH and stability
"""

    try:

        with st.spinner("Generating formulation..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text

        st.success("Formula generated successfully")

        st.markdown("## 🧪 Generated Formula")

        st.markdown(result)

        st.download_button(
            label="Download Formula",
            data=result,
            file_name="formula.txt",
            mime="text/plain"
        )

        st.code(result)

    except Exception as e:

        st.error("AI generation error")
        st.write(e)
