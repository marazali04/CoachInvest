import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# 1. KONFİGÜRASYON
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", page_icon="🛡️")

# 2. STATE YÖNETİMİ (Kayıt, Giriş ve Hafıza)
if 'users' not in st.session_state: st.session_state.users = {"admin": "admin"}
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Dashboard"

# 3. ÖNBELLEKLEME & GÜVENLİ VERİ MOTORU
@st.cache_data(ttl=600)
def fetch_bist_summary():
    # En aktif 30 hisseyi çekerek "Native Heatmap" oluşturur
    tickers = ["THYAO.IS", "EREGL.IS", "SASA.IS", "ASELS.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS", 
               "BIMAS.IS", "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "YKBNK.IS", "HEKTS.IS", "EKGYO.IS", 
               "KOZAL.IS", "ARCLK.IS", "FROTO.IS", "TOASO.IS", "TCELL.IS", "TTKOM.IS"]
    data = []
    for t_code in tickers:
        try:
            t = yf.Ticker(t_code)
            hist = t.history(period="2d")
            if len(hist) > 1:
                price = hist['Close'].iloc[-1]
                change = ((price / hist['Close'].iloc[-2]) - 1) * 100
                data.append({"Hisse": t_code.replace(".IS",""), "Fiyat": price, "Değişim": change})
        except: continue
    return pd.DataFrame(data)

# 4. GÖRSEL STİL (CSS)
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #0d1117; border: 1px solid #1f242d; border-radius: 12px; padding: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; border: 1px solid #1f242d; background-color: #161b22; }
    .stButton>button:hover { border-color: #00ff88; color: #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# --- SOL NAVİGASYON VE AUTH ---
with st.sidebar:
    st.markdown("<h1 style='color:#00ff88;'>🛡️ COACHINVEST</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.user:
        st.success(f"Hoş geldin, {st.session_state.user}")
        if st.button("🏠 Dashboard"): st.session_state.page = "🏠 Dashboard"
        if st.button("📡 BIST Radar"): st.session_state.page = "📡 BIST Radar"
        if st.button("📈 Portföyüm"): st.session_state.page = "📈 Portföyüm"
        st.markdown("---")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_choice = st.radio("Sisteme Katıl", ["Giriş Yap", "Kayıt Ol"])
        u_name = st.text_input("Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        if auth_choice == "Giriş Yap":
            if st.button("Giriş"):
                if u_name in st.session_state.users and st.session_state.users[u_name] == u_pass:
                    st.session_state.user = u_name
                    st.rerun()
                else: st.error("Hatalı bilgiler!")
        else:
            if st.button("Hesap Oluştur"):
                st.session_state.users[u_name] = u_pass
                st.success("Kayıt Başarılı! Şimdi giriş yapın.")

# --- SAYFA MANTIKLARI ---

# 1. NATIVE DASHBOARD (TradingView Yerine Plotly)
if st.session_state.page == "🏠 Dashboard":
    st.header("🏠 Piyasa Panoraması (Native)")
    
    # Isı Haritası Verisi
    df_market = fetch_bist_summary()
    
    if not df_market.empty:
        # Plotly Treemap (Native Heatmap)
        fig = px.treemap(df_market, path=['Hisse'], values='Fiyat', color='Değişim',
                         color_continuous_scale=['#ff3333', '#161b22', '#00ff88'],
                         color_continuous_midpoint=0)
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor="rgba(0,0,0,0)", height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Piyasa verileri şu an yüklenemiyor (Rate Limit). Lütfen bekleyin.")

# 2. BIST RADAR (Kapsamlı ve Temiz)
elif st.session_state.page == "📡 BIST Radar":
    st.header("📡 BIST Akıllı Radar")
    st.info("Aşağıdaki arama çubuğuna dilediğiniz hisseyi yazın.")
    
    search_symbol = st.text_input("🔍 Hisse Kodu Ara (Örn: GENKM, NUHCM):", "").upper()
    
    if search_symbol:
        try:
            t = yf.Ticker(f"{search_symbol}.IS")
            hist = t.history(period="1y")
            
            if not hist.empty:
                # Teknik Analiz (SMA & RSI)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                hist['RSI'] = 100 - (100 / (1 + rs))
                
                # Plotly Chart
                fig_stock = go.Figure()
                fig_stock.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="Fiyat"))
                fig_stock.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
                st.plotly_chart(fig_stock, use_container_width=True)
                
                # Performans Tablosu
                perf_data = {
                    "1 Ay": f"%{((hist['Close'].iloc[-1]/hist['Close'].iloc[-21])-1)*100:.2f}",
                    "6 Ay": f"%{((hist['Close'].iloc[-1]/hist['Close'].iloc[-126])-1)*100:.2f}",
                    "F/K": t.info.get('trailingPE', 'N/A'),
                    "PD/DD": t.info.get('priceToBook', 'N/A')
                }
                st.table(pd.DataFrame([perf_data]))
            else: st.error("Hisse bulunamadı.")
        except: st.error("Veri çekme hatası (Rate Limit). Lütfen biraz bekleyin.")

# 3. PORTFÖYÜM
elif st.session_state.page == "📈 Portföyüm":
    if not st.session_state.user:
        st.warning("🔒 Portföyünüzü görmek için lütfen giriş yapın.")
    else:
        st.header(f"💼 {st.session_state.user} - Portföy Analizi")
        # Sabit portföy verileri (Daha sonra DB'ye bağlanacak)
        mermiler = sum([i['Miktar'] for i in st.session_state.history])
        tp2_bakiye = 9959.49 + mermiler
        
        c1, c2 = st.columns(2)
        c1.metric("Toplam Varlık", f"{12695.38 + tp2_bakiye:,.2f} TL")
        c2.metric("Nakit Gücü (TP2)", f"{tp2_bakiye:,.2f} TL")
        
        # Kar/Zarar Tablosu (Renkli)
        st.subheader("Pozisyonlar")
        h_data = [
            {"Varlık": "GENKM", "Kar/Zarar": "263.50 TL (%23.85)", "Tip": "Pozitif"},
            {"Varlık": "NUHCM", "Kar/Zarar": "675.00 TL (%9.64)", "Tip": "Pozitif"},
            {"Varlık": "TOASO", "Kar/Zarar": "54.00 TL (%1.50)", "Tip": "Pozitif"}
        ]
        st.table(h_data)

st.sidebar.caption("v15.0 Elite Terminal | Native Architecture")
