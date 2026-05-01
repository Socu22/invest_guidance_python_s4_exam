import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np  # Tilføjet NumPy
import httpx
import asyncio
from client.utills.data_analysis import analyze_stock_data, plot_stock_trends
#from client.utills.llm_integration import get_investment_advice

# Load environment variables
load_dotenv()

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8080")

st.title("📈 Invest Guidance")
st.markdown("Get stock insights and investment advice powered by AI.")

# Sidebar for user input
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA):", "AAPL")
    analyze_btn = st.button("Analyze Stock")
    advice_btn = st.button("Get AI Investment Advice")

# Main content
if analyze_btn and ticker:
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            async def fetch_data():
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{FASTAPI_URL}/stocks/{ticker}")
                    response.raise_for_status()
                    return response.json()

            stock_data = asyncio.run(fetch_data())

            if stock_data:
                st.success(f"Fetched data for {ticker}")
                df = pd.DataFrame(stock_data["data"])

                # --- Eksempel på brug af NumPy ---
                # Beregn logaritmisk afkast og årlig volatilitet
                close_prices = df['close'].to_numpy(dtype=float)
                log_returns = np.log((close_prices[1:]) / (close_prices[:-1]))
                volatility = np.std(log_returns) * np.sqrt(252)  # 252 handelsdage
                
                st.metric("Annualized Volatility (NumPy)", f"{volatility:.2%}")
                # --------------------------------

                with st.expander("📊 Raw Data"):
                    st.dataframe(df)

                analysis = analyze_stock_data(df)
                st.subheader("📈 Stock Analysis")
                st.json(analysis)

                fig = plot_stock_trends(df)
                st.pyplot(fig)

                st.session_state["stock_data"] = stock_data
                st.session_state["analysis"] = analysis
            else:
                st.error("No data found for this ticker.")

        except Exception as e:
            st.error(f"Error fetching data: {e}")

if advice_btn and "stock_data" in st.session_state:
    with st.spinner("Generating AI advice..."):
        try:
            advice = 0  # get_investment_advice(ticker,st.session_state["stock_data"],st.session_state["analysis"]            )
            st.subheader("🤖 AI Investment Advice")
            st.markdown(advice)
        except Exception as e:
            st.error(f"Error generating advice: {e}")

