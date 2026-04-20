import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:3000")

st.title("Invest Guidance")