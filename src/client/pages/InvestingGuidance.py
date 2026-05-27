import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import httpx
import asyncio
from datetime import datetime

from client.utills.data_analysis import analyze_stock_data, plot_stock_trends
from client.utills.llm_integration import get_investment_advice

# --- CONFIGURATION ---
load_dotenv()

# FastAPI Port
FASTAPI_PORT = os.getenv("FASTAPI_PORT", 8000)

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:" + str(FASTAPI_PORT))

st.set_page_config(
    page_title="Invest Guidance",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if "stock_data" not in st.session_state:
    st.session_state["stock_data"] = None

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

# --- SMART API LOGIC ---
async def get_smart_stock_data(ticker):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            db_res = await client.get(f"{FASTAPI_URL}/stocks/{ticker}")

            if db_res.status_code == 404:
                create_res = await client.post(
                    f"{FASTAPI_URL}/stocks/",
                    json={"ticker": ticker}
                )
                return create_res.json()

            db_data = db_res.json()
            raw_data = db_data.get("data", [])

            # Check if data is outdated
            db_dates = [item["date"] for item in raw_data]
            latest_date = max(db_dates) if db_dates else "1900-01-01"
            today = datetime.now().strftime("%Y-%m-%d")

            # Force update if outdated
            if latest_date < today:
                st.info("🔄 Outdated data detected. Synchronizing full history...")

                put_res = await client.put(
                    f"{FASTAPI_URL}/stocks/",
                    json={"ticker": ticker}
                )

                return put_res.json()

            return db_data

        except Exception as e:
            st.error(f"Error: {e}")
            return None

# --- UI STRUCTURE ---
st.title("📈 Invest Guidance")
st.markdown("Get AI-powered insights into your favorite stocks.")

with st.sidebar:
    st.header("Settings")

    ticker_input = st.text_input(
        "Enter Ticker:",
        "AAPL"
    ).upper().strip()

    analyze_btn = st.button(
        "🔍 Analyze Stock",
        use_container_width=True
    )

    # AI button only enabled after analysis
    advice_ready = st.session_state["stock_data"] is not None

    advice_btn = st.button(
        "🤖 Get AI Investment Advice",
        use_container_width=True,
        disabled=not advice_ready
    )

    st.divider()

    st.markdown("### About the App")
    st.caption(
        "Data is fetched through FastAPI and analyzed with NumPy & Mistral AI."
    )

# --- MAIN ANALYSIS LOGIC ---
if analyze_btn and ticker_input:

    with st.spinner(f"Fetching data for {ticker_input}..."):

        result = asyncio.run(get_smart_stock_data(ticker_input))

        if result and "data" in result:

            st.session_state["stock_data"] = result

            df = pd.DataFrame(result["data"])

            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            # NumPy calculations
            close_prices = df["close"].to_numpy(dtype=float)

            log_returns = np.log(
                close_prices[1:] / close_prices[:-1]
            )

            volatility = np.std(log_returns) * np.sqrt(252)

            # Metrics
            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Current Price",
                f"${close_prices[-1]:.2f}"
            )

            c2.metric(
                "Annual Volatility",
                f"{volatility:.2%}"
            )

            c3.metric(
                "Last Updated",
                df["date"].iloc[-1].strftime("%d %b %Y")
            )

            # Technical analysis
            st.session_state["analysis"] = analyze_stock_data(df)

            # Charts
            st.subheader(f"Price Development: {ticker_input}")

            st.pyplot(plot_stock_trends(df))

            with st.expander("View raw data and analysis"):
                st.json(st.session_state["analysis"])
                st.dataframe(df.tail(10))

            if "message" in result:
                st.toast(result["message"])

        else:
            st.error("Could not fetch data. Try another ticker.")

# --- AI ADVICE LOGIC ---
if advice_btn and st.session_state["stock_data"]:

    with st.spinner("🤖 Mistral AI is analyzing the market..."):

        try:
            advice = get_investment_advice(
                ticker=ticker_input,
                stock_data=st.session_state["stock_data"],
                analysis=st.session_state["analysis"]
            )

            st.markdown("---")

            st.subheader("🤖 AI Investment Advice")

            st.markdown(advice)

            st.download_button(
                "📥 Download Report",
                data=advice,
                file_name=f"invest_advice_{ticker_input}.txt"
            )

        except Exception as e:
            st.error(f"Error during AI generation: {e}")

# Footer
st.divider()

st.markdown(
    "<center><small>Invest Guidance © 2026</small></center>",
    unsafe_allow_html=True
)