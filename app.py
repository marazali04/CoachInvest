import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFİGÜRASYON (En üstte olmalı)
st.set_page_config(page_title="CoachInvest Elite", layout="wide", page_icon="🛡️")

# CSS: Terminal Estetiği (Daha Keskin ve Kurumsal)
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #0d1117; border: 1px solid #1f242d; border-radius: 10px; padding: 15px; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 5px; }
    .stTabs [aria-selected="true"] { color: #00ff88 !important; border-bottom: 2px solid #00ff88 !important; }
    .stDataFrame { border-radius: 10px; border: 1px solid #1f242d; }
    </style>
    """, unsafe_allow_html=True)

# 2. ÖNBELLEKLEME (API Kısıtı & Hız İçin)
@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    try:
        df = yf.download(f"{symbol}.IS", period="1y", interval="1d", progress=False)
        return df if not df.empty else None
    except:
        return None

# 3. TEKNİK ANALİZ MOTORU (RSI & SMA)
def apply_indicators(df):
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # SMA
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    return df

# 4. NATIVE GRAFİK (TradingView Alternatifi - Plotly)
def draw_native_chart(df, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, row_heights=[0.75, 0.25])
    
    # Mumlar & Ortalamalar
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Fiyat"
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name="SMA 20", line=dict(color='#00ff88', width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="SMA 50", line=dict(color='#ff3333', width=1.2)), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI (14)", line=dict(color='#29b5e8', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    fig.update_layout(template="plotly_dark", height=650, xaxis_rangeslider_visible=False,
                      margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# 5. STATE YÖNETİMİ
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"
if 'history' not in st.session_state: st.session_state.history = []

# --- NAVİGASYON (SOL PANEL) ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    if st.button("🏠 Dashboard"): st.session_state.page = "🏠 Dashboard"
    if st.button("📡 BIST Radar"): st.session_state.page = "📡 BIST Radar"
    if st.button("📈 Portföyüm"): st.session_state.page = "📈 Portföyüm"
    st.markdown("---")
    st.caption("v14.0 Elite Terminal")

# --- SAYFA MANTIKLARI ---

if st.session_state.page == "🏠 Dashboard":
    st.header("🏠 Piyasa Panoraması")
    
    # Global Değişken Tanımlama (NameError Çözümü)
    heatmap_code = '<div style="height: 600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    
    m1, m2, m3 = st.columns(3)
    # Endeks Özetleri
    for col, tick, label in zip([m1, m2, m3], ["XU100.IS", "USDTRY=X", "GC=F"], ["BIST 100", "Dolar/TL", "Altın (Ons)"]):
        info = yf.Ticker(tick).fast_info
        change = ((info.last_price / info.previous_close) - 1) * 100
        col.metric(label, f"{info.last_price:,.2f}", f"{change:.2f}%")
        
    st.markdown("---")
    st.subheader("🔥 BIST Isı Haritası")
    components.html(heatmap_code, height=620)

elif st.session_state.page == "📡 BIST Radar":
    st.header("📡 Gelişmiş BIST Terminal")
    
    # Radar Başlangıç Listesi (İlk başta çıkan hisseler sorunu çözüldü)
    default_watchlist = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS"]
    
    tab_search, tab_list = st.tabs(["🔍 Hisse Analiz", "📂 İzleme Listesi"])
    
    with tab_search:
        symbol = st.text_input("Hisse Ara (Örn: GENKM, NUHCM):", "THYAO").upper()
        if symbol:
            df = fetch_stock_data(symbol)
            if df is not None:
                df = apply_indicators(df)
                draw_native_chart(df, symbol)
                
                # Temel Veriler
                t_info = yf.Ticker(f"{symbol}.IS").info
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Son Fiyat", f"{t_info.get('currentPrice', 0):.2f} TL")
                c2.metric("F/K Oranı", t_info.get('trailingPE', 'N/A'))
                c3.metric("PD/DD", t_info.get('priceToBook', 'N/A'))
                c4.metric("ROE", f"%{t_info.get('returnOnEquity', 0)*100:.2f}")
            else:
                st.error(f"⚠️ '{symbol}' için veri bulunamadı.")

    with tab_list:
        st.subheader("Popüler BIST Takibi")
        watchlist_data = []
        for s in default_watchlist:
            try:
                p = yf.Ticker(f"{s}.IS").fast_info.last_price
                watchlist_data.append({"Hisse": s, "Fiyat": f"{p:.2f} TL"})
            except: continue
        st.table(pd.DataFrame(watchlist_data))

elif st.session_state.page == "📈 Portföyüm":
    st.header("📈 Portföy Durumu")
    # Mevcut mermi durumu (Dinamik)
    st.metric("Toplam Varlık (Simüle)", "22,656.99 TL")
    st.info("Kalıcı veritabanı bağlantısı yakında eklenecek.")
