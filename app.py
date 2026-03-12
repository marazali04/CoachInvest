import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. ELITE TERMINAL KONFİGÜRASYONU
# ==========================================
st.set_page_config(
    page_title="CoachInvest Terminal v11",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark UI & Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Public+Sans:wght@300;400;600;700&display=swap');
    
    :root {
        --primary-color: #00ff88;
        --bg-color: #05070a;
        --card-bg: #0d1117;
        --border-color: #1f242d;
    }

    html, body, [class*="css"] {
        font-family: 'Public Sans', sans-serif;
        background-color: var(--bg-color);
        color: #e1e4e8;
    }

    /* Kart ve Metrik Tasarımı */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Navigasyon Paneli */
    [data-testid="stSidebar"] {
        background-color: #080a0d;
        border-right: 1px solid var(--border-color);
    }
    
    /* Buton Estetiği */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        background-color: #161b22;
        color: #c9d1d9;
        transition: 0.2s all;
    }
    .stButton>button:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        background-color: #1f242d;
    }

    /* Pozitif/Negatif Renkleri */
    .profit-up { color: #00ff88; font-weight: bold; }
    .profit-down { color: #ff3333; font-weight: bold; }
    
    /* Tablo Düzenlemeleri */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. STATE YÖNETİMİ (Persistent Session)
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'users' not in st.session_state: st.session_state.users = {"admin": "admin"}
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# ==========================================
# 3. VERİ MOTORU (YFINANCE OPTİMİZASYONU)
# ==========================================
@st.cache_data(ttl=300)
def fetch_radar_data():
    # En aktif BIST 30/100 örneklemi
    tickers = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL"]
    data = []
    for s in tickers:
        try:
            t = yf.Ticker(f"{s}.IS").fast_info
            change = ((t.last_price / t.previous_close) - 1) * 100
            data.append({
                "Hisse": s, "Fiyat": f"{t.last_price:.2f} TL", 
                "Değişim %": change, "Hacim": f"{t.last_volume/1e6:.1f}M"
            })
        except: continue
    return pd.DataFrame(data)

# ==========================================
# 4. YAN PANEL: KOMUTA ZİNCİRİ
# ==========================================
with st.sidebar:
    st.markdown(f"<h1 style='color:#00ff88; font-size: 24px;'>🛡️ COACH
