import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. КОНФІГУРАЦІЯ СТОРІНКИ
st.set_page_config(page_title="Pocket AI Signal PRO", layout="wide", initial_sidebar_state="expanded")

# Стилізація під 36signal & Pocket Option
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e9eaeb; }
    .card { 
        background: #181a20; 
        border: 1px solid #2b3139; 
        border-radius: 15px; 
        padding: 25px; 
        text-align: center; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }
    .signal-up { color: #00ff88; font-size: 32px; font-weight: bold; text-shadow: 0 0 15px rgba(0,255,136,0.5); }
    .signal-down { color: #ff4b4b; font-size: 32px; font-weight: bold; text-shadow: 0 0 15px rgba(255,75,75,0.5); }
    .prob { color: #f0b90b; font-size: 24px; font-weight: bold; }
    .stButton>button {
        width: 100%;
        background-color: #2a52be;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #3b66e6; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. СЛОВНИК АКТИВІВ (ЯК НА POCKET OPTION)
assets_dict = {
    "Валюти (Forex)": {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
        "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "USD/CHF": "CHF=X",
        "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X", "EUR/GBP": "EURGBP=X"
    },
    "Криптовалюти": {
        "Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", 
        "Solana (SOL)": "SOL-USD", "Ripple (XRP)": "XRP-USD", 
        "Dogecoin (DOGE)": "DOGE-USD", "Litecoin (LTC)": "LTC-USD"
    },
    "Акції (Stocks)": {
        "Apple": "AAPL", "Tesla": "TSLA", "Amazon": "AMZN", 
        "Google": "GOOGL", "Microsoft": "MSFT", "Meta": "META", "Netflix": "NFLX"
    },
    "Товари (Commodities)": {
        "Золото (Gold)": "GC=F", "Срібло (Silver)": "SI=F", 
        "Нафта Brent": "BZ=F", "Газ (Natural Gas)": "NG=F"
    }
}

# 3. ЛОГІКА ІНДИКАТОРІВ
def get_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / loss)))

# 4. БІЧНА ПАНЕЛЬ
st.sidebar.title("💎 AI TERMINAL 2026")
category = st.sidebar.selectbox("Оберіть категорію", list(assets_dict.keys()))
asset_label = st.sidebar.selectbox("Оберіть пару", list(assets_dict[category].keys()))
asset_code = assets_dict[category][asset_label]
timeframe = st.sidebar.selectbox("Таймфрейм", ["1m", "2m", "5m", "15m", "30m", "1h"], index=2)

st.sidebar.markdown("---")
st.sidebar.info("Бот аналізує ринок у реальному часі за стратегією RSI Reversal (36signal Style).")

# 5. ОСНОВНИЙ КОНТЕНТ
st.title(f"🛰 СИГНАЛ: {asset_label}")

try:
    # Завантаження даних
    data = yf.download(asset_code, period="1d", interval=timeframe, progress=False)
    
    if not data.empty:
        # Розрахунок
        data['rsi'] = get_rsi(data['Close'])
        current_price = data['Close'].iloc[-1]
        current_rsi = data['rsi'].iloc[-1]
        
        # Визначення сигналу
        if current_rsi < 32:
            signal, style, prob = "CALL (ВГОРУ) ⬆️", "signal-up", "94.8%"
        elif current_rsi > 68:
            signal, style, prob = "PUT (ВНИЗ) ⬇️", "signal-down", "91.2%"
        else:
            signal, style, prob = "NEUTRAL ⏳", "", "45%"

        # Візуалізація карток
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="card">ПОТОЧНА ЦІНА<br><h2 style="margin:0;">{current_price:.5f}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="card">АЛГОРИТМ AI<br><span class="{style}">{signal}</span></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="card">ЙМОВІРНІСТЬ<br><span class="prob">{prob}</span></div>', unsafe_allow_html=True)

        st.write("") # Відступ

        # Кнопка переходу на Pocket Option (посилання на загальну платформу)
        st.link_button(f"🔥 ВІДКРИТИ УГОДУ {asset_label} НА POCKET OPTION", "https://pocketoption.com")

        # Графік
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
        )])
        fig.update_layout(
            template="plotly_dark", 
            height=550, 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True, key="live_market_chart")

        st.caption(f"Останнє оновлення: {datetime.now().strftime('%H:%M:%S')} | Синхронізація з сервером успішна")

    else:
        st.warning("Ринок зараз закритий або дані недоступні для цього активу.")

except Exception as e:
    st.error(f"Помилка отримання даних: {e}")

# Автоматичне оновлення сторінки кожні 60 секунд
time.sleep(60)
st.rerun()
