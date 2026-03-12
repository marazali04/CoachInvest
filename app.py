import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# 1. KONFİGÜRASYON
st.set_page_config(page_title="CoachInvest Elite", layout="wide")

# CSS: Terminal Estetiği
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #0d1117; border: 1px solid #1f242d; border-radius: 10px; padding: 15px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; }
    .stTabs [aria-selected="true"] { color: #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. ÖNBELLEKLEME (API Kısıtı Çözümü)
@st.cache_data(ttl=3600) # Veriyi 1 saat boyunca hafızada saklar
def get_stock_data(symbol):
    try:
        df = yf.download(f"{symbol}.IS", period="1y", interval="1d", progress=False)
        if df.empty: return None
        return df
    except: return None

# 3. TEKNİK ANALİZ HESAPLAMALARI (RSI & SMA)
def calculate_indicators(df):
    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # Hareketli Ortalamalar
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    return df

# 4. STATE YÖNETİMİ
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

# 5. NATIVE GRAFİK MOTORU (Price + RSI)
def plot_advanced_chart(df, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # Mum Grafiği (Row 1)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Fiyat"
    ), row=1, col=1)

    # Ortalamalar
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#00ff88', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="SMA 50", line=dict(color='#ff3333', width=1)), row=1, col=1)

    # RSI (Row 2)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI (14)", line=dict(color='#29b5e8', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False,
                      margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- SIDEBAR & NAVİGASYON ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    if st.button("🏠 Dashboard"): st.session_state.page = "🏠 Dashboard"
    if st.button("📡 BIST Radar"): st.session_state.page = "📡 BIST Radar"
    if st.button("📈 Portföyüm"): st.session_state.page = "📈 Portföyüm"

# --- SAYFA MANTIKLARI ---
if st.session_state.page == "📡 BIST Radar":
    st.header("📡 Gelişmiş BIST Terminal")
    
    symbol = st.text_input("🔍 Hisse Ara (Örn: THYAO, SASA):", "THYAO").upper()
    
    df_raw = get_stock_data(symbol) # Validasyon & Önbellek burada çalışıyor
    
    if df_raw is not None:
        df = calculate_indicators(df_raw)
        
        # Grafik
        plot_advanced_chart(df, symbol)
        
        # Kıyaslama Modülü (Peer Comparison)
        st.subheader("📊 Sektörel Kıyaslama")
        peer_list = ["THYAO", "PGSUS", "EREGL", "KRDMD", "SASA", "HEKTS"] # Örnek havuz
        comparison = []
        for p in peer_list[:3]: # Performans için ilk 3
            t_data = yf.Ticker(f"{p}.IS").info
            comparison.append({
                "Hisse": p,
                "Fiyat": f"{t_data.get('currentPrice', 0):.2f}",
                "F/K": t_data.get('trailingPE', 'N/A'),
                "PD/DD": t_data.get('priceToBook', 'N/A')
            })
        st.table(pd.DataFrame(comparison))
    else:
        st.error(f"⚠️ '{symbol}' kodu geçerli bir BIST hissesi değil. Lütfen kontrol edin.")

elif st.session_state.page == "🏠 Dashboard":
    st.header("🚀 Piyasa Özeti")
    map_html = '<div style="height: 600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    components.html(map_html, height=620)

st.sidebar.caption("v13.0 | Resilient Terminal")
