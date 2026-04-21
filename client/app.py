import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8080")

st.title("Invest Guidance")