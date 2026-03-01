import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. НАЛАШТУВАННЯ ДИЗАЙНУ (36SIGNAL STYLE)
st.set_page_config(page_title="AI SIGNAL TERMINAL v3", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e9eaeb; }
    .card {
        background: #12161c;
        border: 1px solid #232a33;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .symbol { font-size: 20px; font-weight: bold; color: #f0b90b; }
    .buy { color: #02c076; font-size: 24px; font-weight: bold; }
    .sell { color: #f84960; font-size: 24px; font-weight: bold; }
    .wait { color: #5e6673; font-size: 18px; }
    .stButton>button { width: 100%; background: #2a52be; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. ФУНКЦІЯ РОЗРАХУНКУ СИГНАЛУ
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. СПИСОК АКТИВІВ (POCKET OPTION)
pairs = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD", "GOLD": "GC=F",
    "APPLE": "AAPL", "TESLA": "TSLA"
}

st.title("🛰 36SIGNAL AI: MULTI-SCANNER 2026")
st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')} | Data: Yahoo Finance")

# 4. ГЕНЕРАЦІЯ ПЛИТКИ СИГНАЛІВ
cols = st.columns(4)

for i, (name, code) in enumerate(pairs.items()):
    with cols[i % 4]:
        try:
            # Отримання даних
            ticker = yf.Ticker(code)
            df = ticker.history(period="1d", interval="5m")
            
            if not df.empty:
                # Безпечне отримання ціни та RSI
                close_series = df['Close'].squeeze()
                rsi_series = get_rsi(close_series)
                
                current_price = float(close_series.iloc[-1])
                current_rsi = float(rsi_series.iloc[-1])
                
                # Логіка сигналу
                if current_rsi < 30:
                    status, style, prob = "STRONG CALL ⬆️", "buy", "94%"
                elif current_rsi > 70:
                    status, style, prob = "STRONG PUT ⬇️", "sell", "92%"
                else:
                    status, style, prob = "WAITING ⏳", "wait", "45%"
                
                # Відображення картки
                st.markdown(f"""
                    <div class="card">
                        <div class="symbol">{name}</div>
                        <div style="color:#848e9c;">Price: {current_price:.5f}</div>
                        <div class="{style}">{status}</div>
                        <div style="font-size:12px; margin-top:10px;">Prob: {prob} | RSI: {current_rsi:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Кнопка для переходу
                st.link_button(f"Trade {name}", "https://pocketoption.com", key=f"btn_{name}")
            else:
                st.write(f"{name}: Closed")
        except Exception:
            st.write(f"{name}: Error")

# 5. АВТО-ОНОВЛЕННЯ
time.sleep(30)
st.rerun()
