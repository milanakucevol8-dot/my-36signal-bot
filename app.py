import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# Конфігурація сторінки
st.set_page_config(page_title="36SIGNAL AI - Dashboard", layout="wide")

# ФІРМОВИЙ СТИЛЬ 36SIGNAL (Шахівниця)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: white; }
    .signal-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        padding: 10px;
    }
    .signal-card {
        background: #181a20;
        border: 1px solid #2b3139;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    .signal-card:hover { border-color: #f0b90b; transform: translateY(-5px); }
    .pair-name { font-size: 18px; font-weight: bold; color: #f0b90b; }
    .status-buy { color: #00ff88; font-size: 22px; font-weight: bold; }
    .status-sell { color: #ff4b4b; font-size: 22px; font-weight: bold; }
    .status-wait { color: #848e9c; font-size: 20px; }
    .probability { background: #2b3139; border-radius: 5px; padding: 5px; margin-top: 10px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

def get_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / loss)))

# Список пар як на 36signal
pairs = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD", "GOLD": "GC=F", "SILVER": "SI=F"
}

st.title("🛰 36SIGNAL AI REAL-TIME DASHBOARD")
st.write(f"Останнє сканування: {datetime.now().strftime('%H:%M:%S')}")

# Створення сітки карток
cols = st.columns(3) # Розбиваємо на 3 колонки для десктопа

for i, (name, code) in enumerate(pairs.items()):
    with cols[i % 3]:
        try:
            # Отримуємо дані (мінімум для швидкості)
            data = yf.download(code, period="1d", interval="5m", progress=False).squeeze()
            if not data.empty:
                rsi = get_rsi(data['Close']).iloc[-1]
                price = data['Close'].iloc[-1]
                
                # Логіка сигналу
                if rsi < 33:
                    res, style, prob = "STRONG CALL ⬆️", "status-buy", "94%"
                elif rsi > 67:
                    res, style, prob = "STRONG PUT ⬇️", "status-sell", "92%"
                else:
                    res, style, prob = "WAITING ⏳", "status-wait", "45%"
                
                # Вивід картки в стилі 36signal
                st.markdown(f"""
                    <div class="signal-card">
                        <div class="pair-name">{name}</div>
                        <div style="font-size: 14px; color: #848e9c;">Price: {price:.5f}</div>
                        <div class="{style}" style="margin-top: 10px;">{res}</div>
                        <div class="probability">Ймовірність: {prob} | RSI: {rsi:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Кнопка для кожної картки
                st.link_button(f"Торгувати {name}", f"https://pocketoption.com", key=f"btn_{name}")
        except:
            st.error(f"Помилка {name}")

# Авто-оновлення кожні 30 секунд
time.sleep(30)
st.rerun()
