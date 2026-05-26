import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import httpx
import asyncio
from datetime import datetime

# Import af dine egne hjælpefunktioner
from client.utills.data_analysis import analyze_stock_data, plot_stock_trends
from client.utills.llm_integration import get_investment_advice

# --- KONFIGURATION ---
load_dotenv()

# FastAPI Port
FASTAPI_PORT = os.getenv("FASTAPI_PORT",8000)

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:"+str(FASTAPI_PORT))

st.set_page_config(
    page_title="Invest Guidance",
    page_icon="📈",
    layout="wide"
)

# Initialiser session state
if "stock_data" not in st.session_state:
    st.session_state["stock_data"] = None
if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

# --- SMART API LOGIK ---
async def get_smart_stock_data(ticker):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            db_res = await client.get(f"{FASTAPI_URL}/stocks/{ticker}")
            
            if db_res.status_code == 404:
                return await (await client.post(f"{FASTAPI_URL}/stocks/", json={"ticker": ticker})).json()
            
            db_data = db_res.json()
            raw_data = db_data.get("data", [])
            
            # 1. Tjek om det er en "Seed" (f.eks. hvis der er færre end 10 dages data)
            
            # 2. Tjek om den er forældet
            db_dates = [item["date"] for item in raw_data]
            latest_date = max(db_dates) if db_dates else "1900-01-01"
            today = datetime.now().strftime("%Y-%m-%d")
            
            # TVING opdatering hvis det er en lille seed-entry ELLER den er forældet
            if latest_date < today:
                st.info("🔄 Forældet data. Synkroniserer fuld historik...")
                put_res = await client.put(f"{FASTAPI_URL}/stocks/", json={"ticker": ticker})
                return put_res.json()

            return db_data

        except Exception as e:
            st.error(f"Fejl: {e}")
            return None

# --- UI STRUKTUR ---
st.title("📈 Invest Guidance")
st.markdown("Få AI-drevet indsigt i dine yndlingsaktier.")

with st.sidebar:
    st.header("Indstillinger")
    ticker_input = st.text_input("Indtast Ticker:", "AAPL").upper().strip()
    
    analyze_btn = st.button("🔍 Analyser Aktie", use_container_width=True)
    
    # AI knappen er kun aktiv hvis vi har analyseret data først
    advice_ready = st.session_state["stock_data"] is not None
    advice_btn = st.button("🤖 Få AI Investeringsråd", use_container_width=True, disabled=not advice_ready)

    st.divider()
    st.markdown("### Om appen")
    st.caption("Data hentes via FastAPI og analyseres med NumPy & Mistral AI.")

# --- HOVEDLOGIK (ANALYSE) ---
if analyze_btn and ticker_input:
    with st.spinner(f"Henter data for {ticker_input}..."):
        result = asyncio.run(get_smart_stock_data(ticker_input))

        if result and "data" in result:
            st.session_state["stock_data"] = result
            df = pd.DataFrame(result["data"])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # NumPy Beregninger (Volatilitet & Kurs)
            close_prices = df['close'].to_numpy(dtype=float)
            log_returns = np.log(close_prices[1:] / close_prices[:-1])
            volatility = np.std(log_returns) * np.sqrt(252)

            # Vis Nøgletal
            c1, c2, c3 = st.columns(3)
            c1.metric("Aktuel Kurs", f"${close_prices[-1]:.2f}")
            c2.metric("Årlig Volatilitet", f"{volatility:.2%}")
            c3.metric("Sidste Opdatering", df['date'].iloc[-1].strftime('%d. %b %Y'))

            # Teknisk Analyse
            st.session_state["analysis"] = analyze_stock_data(df)
            
            # Grafer
            st.subheader(f"Kursudvikling: {ticker_input}")
            st.pyplot(plot_stock_trends(df))
            
            with st.expander("Se rå data og analyse"):
                st.json(st.session_state["analysis"])
                st.dataframe(df.tail(10))
            
            if "message" in result:
                st.toast(result["message"])
        else:
            st.error("Kunne ikke hente data. Prøv en anden ticker.")

# --- HOVEDLOGIK (AI RÅDGIVNING) ---
if advice_btn and st.session_state["stock_data"]:
    with st.spinner("🤖 Mistral AI analyserer markedet..."):
        try:
            # Her kaldes din LLM-integration direkte (synkront)
            advice = get_investment_advice(
                ticker=ticker_input,
                stock_data=st.session_state["stock_data"],
                analysis=st.session_state["analysis"]
            )
            
            st.markdown("---")
            st.subheader("🤖 AI Investment Advice")
            st.markdown(advice)
            
            st.download_button(
                "📥 Download Rapport",
                data=advice,
                file_name=f"invest_advice_{ticker_input}.txt"
            )
        except Exception as e:
            st.error(f"Fejl under AI-generering: {e}")

# Footer
st.divider()
st.markdown("<center><small>Invest Guidance © 2026</small></center>", unsafe_allow_html=True)
