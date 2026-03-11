import streamlit as st
import pandas as pd
from google import genai
from cost_engine import calculate_formula_cost

st.set_page_config(
    page_title="Formula AI Studio",
    page_icon="🧪",
    layout="wide"
)

API_KEY = st.secrets["API_KEY"]
client = genai.Client(api_key=API_KEY)

st.title("🧪 Formula AI Studio")

st.sidebar.header("Formulation Settings")

product = st.sidebar.text_input("Product Type")

performance = st.sidebar.selectbox(
    "Performance Level",
    ["Economy","Balanced","High Performance","Premium"]
)

generate = st.sidebar.button("Generate Formula")

if generate:

    with st.spinner("Designing formulation..."):

        prompt = f"""
Create an industrial chemical formulation.

Product:
{product}

Performance level:
{performance}

Return table:

Ingredient | Percentage | Function
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text

    st.subheader("Generated Formula")

    st.markdown(result)

    # Example structure for cost calculation
    formula = [
        {"ingredient":"SLES","percentage":12},
        {"ingredient":"CAPB","percentage":5},
        {"ingredient":"Water","percentage":80}
    ]

    cost = calculate_formula_cost(formula)

    st.subheader("Estimated Production Cost")

    st.metric("Cost per kg", f"{cost} $")

st.sidebar.markdown("---")

st.sidebar.write("AI Chemical Formulation Platform")
