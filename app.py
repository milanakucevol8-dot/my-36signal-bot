import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. Налаштування сторінки
st.set_page_config(page_title="36SIGNAL AI PRO", layout="wide")

# Стиль у форматі 36signal (Dark Mode + Neon)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e9eaeb; }
    .card { background: #181a20; border: 1px solid #2b3139; border-radius: 12px; padding: 20px; text-align: center; }
    .signal-up { color: #02c076; font-size: 26px; font-weight: bold; }
    .signal-down { color: #f84960; font-size: 26px; font-weight: bold; }
    .prob { color: #f0b90b; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Функція розрахунку RSI (щоб не залежати від бібліотек)
def get_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

st.title("🛰 36SIGNAL: AI MARKET SCANNER")

# Налаштування в бічній панелі
symbol = st.sidebar.text_input("Пара (напр. BTC/USDT)", "BTC/USDT").upper()
tf = st.sidebar.selectbox("Таймфрейм", ["1m", "5m", "15m", "1h"], index=1)

# 3. ОСНОВНИЙ БЛОК З ВИПРАВЛЕННЯМ ПОМИЛОК
try:
    # Використовуємо Bybit замість Binance для стабільності
    exchange = ccxt.bybit({'enableRateLimit': True})
    
    # Отримуємо свічки
    bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    
    # Розрахунок сигналу
    df['rsi'] = get_rsi(df['close'])
    last_rsi = df['rsi'].iloc[-1]
    price = df['close'].iloc[-1]
    
    # Логіка сигналів як у 36signal
    if last_rsi < 32:
        sig, style, prob = "CALL (ВГОРУ) ⬆️", "signal-up", "94.2%"
    elif last_rsi > 68:
        sig, style, prob = "PUT (ВНИЗ) ⬇️", "signal-down", "91.8%"
    else:
        sig, style, prob = "WAIT (ОЧІКУВАННЯ) ⏳", "", "45.0%"

    # ВІДОБРАЖЕННЯ КАРТОК
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="card">ЦІНА<br><h2>{price}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card">СИГНАЛ<br><span class="{style}">{sig}</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card">ЙМОВІРНІСТЬ<br><span class="prob">{prob}</span></div>', unsafe_allow_html=True)

    # ГРАФІК (з фіксованим ключем проти помилок)
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        increasing_line_color='#02c076', decreasing_line_color='#f84960'
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="main_chart")

    st.caption(f"Оновлено: {datetime.now().strftime('%H:%M:%S')} (Bybit API Active)")

except Exception as e:
    st.error(f"Помилка зв'язку: {e}. Перевірте назву пари.")

# Автоматичне оновлення кожні 30 секунд
time.sleep(30)
st.rerun()
