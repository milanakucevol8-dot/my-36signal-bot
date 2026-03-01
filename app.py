import streamlit as st
import pandas as pd
import ccxt
import plotly.graph_objects as go

st.set_page_config(page_title="AI Signal PRO", layout="wide")

# Дизайн карток
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .card { background: #1a1c24; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #30363d; }
    .up { color: #00ff88; font-size: 24px; font-weight: bold; }
    .down { color: #ff4b4b; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🛰 36SIGNAL CLONE: AI SCANNER")

# Отримання ціни
try:
    ex = ccxt.binance()
    data = ex.fetch_ohlcv('BTC/USDT', timeframe='5m', limit=50)
    df = pd.DataFrame(data, columns=['t', 'o', 'h', 'l', 'c', 'v'])
    price = df['c'].iloc[-1]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card">ЦІНА<br><h2>{price}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card">СИГНАЛ<br><span class="up">CALL (ВГОРУ) ⬆️</span></div>', unsafe_allow_html=True)
        
    fig = go.Figure(data=[go.Candlestick(x=df['t'], open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error("Помилка зв'язку з біржею")
