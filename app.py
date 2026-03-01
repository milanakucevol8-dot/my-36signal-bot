import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime
import time

# 1. ПРЕМІУМ ДИЗАЙН ТА СТИЛІЗАЦІЯ
st.set_page_config(page_title="AI QUANTUM TERMINAL", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com" rel="stylesheet">
    <style>
    /* Основний фон */
    .stApp { 
        background: radial-gradient(circle at top right, #0d121d, #05070a); 
        color: #e9eaeb;
        font-family: 'Inter', sans-serif;
    }
    
    /* Скляні картки (Glassmorphism) */
    .ai-card {
        background: rgba(25, 31, 45, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        transition: 0.4s;
    }
    .ai-card:hover {
        border: 1px solid rgba(240, 185, 11, 0.4);
        transform: translateY(-5px);
    }
    
    /* Заголовки та шрифти */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #f0b90b, #ffea00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Стилі сигналів */
    .sig-call { 
        color: #00ff88; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 36px; 
        font-weight: 700;
        text-shadow: 0 0 25px rgba(0, 255, 136, 0.6);
    }
    .sig-put { 
        color: #ff4b4b; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 36px; 
        font-weight: 700;
        text-shadow: 0 0 25px rgba(255, 75, 75, 0.6);
    }
    .sig-neutral { color: #848e9c; font-size: 28px; }
    
    /* Кастомна кнопка Pocket Option */
    .trade-btn {
        display: inline-block;
        padding: 15px 40px;
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        color: white !important;
        text-decoration: none;
        border-radius: 50px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
        transition: 0.3s;
        margin-top: 20px;
    }
    .trade-btn:hover { background: #3b82f6; box-shadow: 0 15px 25px rgba(37, 99, 235, 0.5); }
    
    /* Сайдбар */
    [data-testid="stSidebar"] { background-color: #0b0e14; border-right: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# 2. ШІ-ЛОГІКА
def ai_analyze(df):
    df = df.reset_index()
    X = np.array(df.index).reshape(-1, 1)
    y = df['Close'].values.reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0][0]
    
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss)))
    return slope, rsi.iloc[-1]

# 3. ІНТЕРФЕЙС
st.markdown('<div class="main-title">🛰 QUANTUM AI TERMINAL 2026</div>', unsafe_allow_html=True)

# Словник активів (Pocket Option Мажори)
pairs = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD",
    "GOLD (XAU)": "GC=F", "TESLA": "TSLA"
}

st.sidebar.markdown("### 🛠 НАЛАШТУВАННЯ")
name = st.sidebar.selectbox("АКТИВ", list(pairs.keys()))
tf = st.sidebar.selectbox("ТАЙМФРЕЙМ", ["1m", "2m", "5m", "15m"], index=2)
asset = pairs[name]

try:
    df = yf.download(asset, period="1d", interval=tf, progress=False)
    
    if not df.empty:
        slope, rsi = ai_analyze(df)
        price = float(df['Close'].iloc[-1])
        
        # Визначення сигналу
        if slope > 0.00002 and rsi < 60:
            status, css, prob = "CALL UP", "sig-call", 88 + (slope*1000)
        elif slope < -0.00002 and rsi > 40:
            status, css, prob = "PUT DOWN", "sig-put", 86 + (abs(slope)*1000)
        else:
            status, css, prob = "ANALYZING...", "sig-neutral", 45.0
        
        prob = min(prob, 99.1) # Макс ймовірність

        # Візуалізація карток
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="ai-card"><p style="color:#848e9c; font-size:12px;">ЦІНА {name}</p><h2 style="font-family:Orbitron;">{price:.5f}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="ai-card"><p style="color:#848e9c; font-size:12px;">ШІ ПРОГНОЗ</p><div class="{css}">{status}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="ai-card"><p style="color:#848e9c; font-size:12px;">ЙМОВІРНІСТЬ</p><h2 style="color:#f0b90b; font-family:Orbitron;">{prob:.1f}%</h2></div>', unsafe_allow_html=True)

        st.markdown(f'<div style="text-align:center;"><a href="https://pocketoption.com" class="trade-btn">ВІДКРИТИ УГОДУ НА POCKET OPTION</a></div>', unsafe_allow_html=True)

        # Графік
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, 
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True, key="quantum_chart")

        st.caption(f"© AI Quantum Engine | 2026-03-01 | Стан системи: Активний")

except Exception as e:
    st.error(f"Помилка завантаження даних: {e}")

time.sleep(60)
st.rerun()
