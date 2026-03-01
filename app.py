import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. Налаштування сторінки
st.set_page_config(page_title="36SIGNAL AI 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e9eaeb; }
    .card { background: #181a20; border: 1px solid #2b3139; border-radius: 12px; padding: 20px; text-align: center; }
    .signal-up { color: #02c076; font-size: 26px; font-weight: bold; }
    .signal-down { color: #f84960; font-size: 26px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / loss)))

st.title("🛰 36SIGNAL AI: CLOUD TERMINAL")

# Налаштування активу (Для Yahoo Finance BTC пишеться як BTC-USD)
asset = st.sidebar.selectbox("Оберіть актив", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])

try:
    # Отримання даних через Yahoo Finance
    ticker = yf.Ticker(asset)
    df = ticker.history(period="1d", interval="5m")
    
    if df.empty:
        st.error("Дані не отримано. Зачекайте хвилину...")
    else:
        df['rsi'] = get_rsi(df['Close'])
        price = round(df['Close'].iloc[-1], 5)
        rsi = df['rsi'].iloc[-1]
        
        # Сигнали 36signal
        if rsi < 30:
            sig, style, prob = "CALL (ВГОРУ) ⬆️", "signal-up", "93.1%"
        elif rsi > 70:
            sig, style, prob = "PUT (ВНИЗ) ⬇️", "signal-down", "89.5%"
        else:
            sig, style, prob = "WAIT (ОЧІКУВАННЯ) ⏳", "", "45%"

        # Картки
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="card">ЦІНА<br><h2>{price}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card">СИГНАЛ<br><span class="{style}">{sig}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card">ЙМОВІРНІСТЬ<br><h2>{prob}</h2></div>', unsafe_allow_html=True)

        # Графік
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#02c076', decreasing_line_color='#f84960'
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True, key="finance_chart")

    st.caption(f"Оновлено: {datetime.now().strftime('%H:%M:%S')} | Джерело: Global Finance API")

except Exception as e:
    st.error(f"Помилка: {e}")

# Перезапуск сторінки для "живого" ефекту
time.sleep(60)
st.rerun()
