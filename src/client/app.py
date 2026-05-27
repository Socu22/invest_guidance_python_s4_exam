import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.title("Invest Guidance")

st.write("Go to InvestingGuidance for my exam assignment")

st.page_link("pages/InvestingGuidance.py", label="Go to InvestingGuidance")

