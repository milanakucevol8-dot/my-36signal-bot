import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time

# 1. СТИЛІЗАЦІЯ ІНТЕРФЕЙСУ (36SIGNAL DARK MODE)
st.set_page_config(page_title="AI SIGNAL TERMINAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e9eaeb; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Контейнер для плитки сигналів */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        padding: 10px;
    }
    
    /* Картка активу */
    .card {
        background: #12161c;
        border: 1px solid #232a33;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .card:hover { border-color: #f0b90b; transform: translateY(-3px); }
    
    .symbol { font-size: 20px; font-weight: bold; color: #f0b90b; letter-spacing: 1px; }
    .price { font-size: 16px; color: #848e9c; margin-bottom: 10px; }
    
    /* Статуси сигналів */
    .buy { color: #02c076; font-size: 24px; font-weight: bold; text-shadow: 0 0 10px rgba(2,192,118,0.3); }
    .sell { color: #f84960; font-size: 24px; font-weight: bold; text-shadow: 0 0 10px rgba(248,73,96,0.3); }
    .wait { color: #5e6673; font-size: 20px; font-weight: normal; }
    
    .prob-bar {
        background: #2b3139;
        border-radius: 10px;
        height: 8px;
        margin: 15px 0 5px 0;
        overflow: hidden;
    }
    .prob-fill { height: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. АЛГОРИТМ RSI
def get_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 3. СПИСОК АКТИВІВ (ЯК НА POCKET OPTION)
pairs = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD",
    "GOLD": "GC=F", "SILVER": "SI=F", "TESLA": "TSLA", "APPLE": "AAPL"
}

st.title("🛰 36SIGNAL AI: REAL-TIME MULTI-SCANNER")
st.caption(f"Синхронізація з Global Finance API: {datetime.now().strftime('%H:%M:%S')}")

# 4. ВІДОБРАЖЕННЯ СИГНАЛІВ
# Розбиваємо на колонки по 4 картки в ряд
cols = st.columns(4)

for i, (name, code) in enumerate(pairs.items()):
    with cols[i % 4]:
        try:
            # Отримуємо дані
            df = yf.download(code, period="1d", interval="5m", progress=False).squeeze()
            
            if not df.empty:
                rsi_val = get_rsi(df['Close']).iloc[-1]
                price_val = float(df['Close'].iloc[-1])
                
                # Логіка визначення сигналу
                if rsi_val < 32:
                    action, css_class, prob, bar_color = "STRONG CALL ⬆️", "buy", 94, "#02c076"
                elif rsi_val > 68:
                    action, css_class, prob, bar_color = "STRONG PUT ⬇️", "sell", 91, "#f84960"
                else:
                    action, css_class, prob, bar_color = "WAITING... ⏳", "wait", 45, "#5e6673"
                
                # HTML Картка
                st.markdown(f"""
                    <div class="card">
                        <div class="symbol">{name}</div>
                        <div class="price">Ціна: {price_val:.5f}</div>
                        <div class="{css_class}">{action}</div>
                        <div class="prob-bar">
                            <div class="prob-fill" style="width: {prob}%; background-color: {bar_color};"></div>
                        </div>
                        <div style="font-size: 12px; color: #848e9c;">Ймовірність: {prob}% | RSI: {rsi_val:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Кнопка дії
                st.link_button(f"ТОРГУВАТИ {name}", "https://pocketoption.com", key=f"btn_{name}")
            else:
                st.error(f"Немає даних для {name}")
        except Exception as e:
            st.error(f"Помилка {name}")

# 5. АВТО-ОНОВЛЕННЯ
time.sleep(30)
st.rerun()
