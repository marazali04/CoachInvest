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
    st.markdown(f"<h1 style='color:#00ff88; font-size: 24px;'>🛡️ COACHINVEST</h1>", unsafe_allow_html=True)
    st.caption("v11.0 Elite Terminal | AI Mentor Powered")
    st.markdown("---")
    
    # Navigasyon
    nav_items = ["🏠 Dashboard", "📡 BIST Radar", "📈 Portföy Analizi", "🕒 İşlem Merkezi"]
    for item in nav_items:
        if st.button(item, type="primary" if st.session_state.page == item else "secondary"):
            st.session_state.page = item
            st.session_state.selected_stock = None
            st.rerun()

    st.markdown("---")
    
    # Auth Sistemi
    if not st.session_state.user:
        auth_tab1, auth_tab2 = st.tabs(["Giriş", "Kayıt"])
        with auth_tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sisteme Gir"):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.user = u
                    st.rerun()
        with auth_tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Hesap Oluştur"):
                st.session_state.users[nu] = np
                st.success("Kayıt başarılı!")
    else:
        st.write(f"Operatör: **{st.session_state.user}**")
        if st.button("🚪 Terminali Kapat"):
            st.session_state.user = None
            st.rerun()

# ==========================================
# 5. SAYFA MANTIKLARI
# ==========================================

# --- ÜST BAR (Global Market) ---
m1, m2, m3, m4 = st.columns(4)
idx_data = {"BIST 100": "XU100.IS", "USD/TRY": "USDTRY=X", "Altın/Ons": "GC=F", "Bitcoin": "BTC-USD"}
for col, (name, sym) in zip([m1, m2, m3, m4], idx_data.items()):
    val = yf.Ticker(sym).fast_info
    ch = ((val.last_price / val.previous_close) - 1) * 100
    col.metric(name, f"{val.last_price:,.2f}", f"{ch:.2f}%")

st.markdown("---")

# --- 1. DASHBOARD ---
if st.session_state.page == "🏠 Dashboard":
    st.subheader("🏠 Piyasa Panoraması")
    
    c_heat, c_milestone = st.columns([2, 1])
    
    with c_heat:
        st.write("🔥 **BIST Isı Haritası (Hacim & Performans)**")
        map_html = '<div style="height: 500px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
        components.html(map_html, height=520)
        
    with c_milestone:
        st.write("🎯 **Hedef Yolculuğu (100.000 TL)**")
        # Örnek hesaplama
        current_val = 22656.99 + sum([i['Miktar'] for i in st.session_state.history])
        progress = (current_val / 100000)
        st.progress(min(progress, 1.0))
        st.metric("Güncel Portföy", f"{current_val:,.2f} TL", f"%{progress*100:.1f}")
        
        st.markdown("---")
        st.write("🚩 **Mermi Durakları**")
        stops = {25000: "Bronz", 50000: "Gümüş", 75000: "Altın", 100000: "Elmas"}
        for stop_val, label in stops.items():
            check = "✅" if current_val >= stop_val else "⏳"
            st.write(f"{check} **{label}:** {stop_val:,.0f} TL")

# --- 2. BIST RADAR (FINTABLES STYLE) ---
elif st.session_state.page == "📡 BIST Radar":
    if st.session_state.selected_stock:
        # HİSSE DETAY (DEEP ANALYSIS)
        s = st.session_state.selected_stock
        st.header(f"📊 {s} Analiz Terminali")
        if st.button("⬅️ Radara Geri Dön", use_container_width=False):
            st.session_state.selected_stock = None
            st.rerun()
            
        tick = yf.Ticker(f"{s}.IS")
        
        # Fintables Tarzı Rasyolar
        r1, r2, r3, r4, r5 = st.columns(5)
        info = tick.info
        r1.metric("F/K", info.get('trailingPE', 'N/A'))
        r2.metric("PD/DD", info.get('priceToBook', 'N/A'))
        r3.metric("FD/FAVÖK", info.get('enterpriseToEbitda', 'N/A'))
        r4.metric("Özsermaye Kar.", f"%{info.get('returnOnEquity', 0)*100:.1f}")
        r5.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.1f}B TL")
        
        t_chart, t_fin, t_bal, t_cash = st.tabs(["📉 Grafik", "🧾 Gelir Tablosu", "🏦 Bilanço", "💸 Nakit Akışı"])
        with t_chart:
            ch_code = f'<div style="height:500px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{s}", "theme": "dark", "locale": "tr", "container_id": "tv"}});</script></div>'
            components.html(ch_code, height=520)
        with t_fin: st.dataframe(tick.financials, use_container_width=True)
        with t_bal: st.dataframe(tick.balance_sheet, use_container_width=True)
        with t_cash: st.dataframe(tick.cashflow, use_container_width=True)
        
    else:
        st.header("📡 BIST Akıllı Radar")
        search = st.text_input("🔍 Hisse Ara (Fintables Radar)...", "").upper()
        df = fetch_radar_data()
        
        if search: df = df[df['Hisse'].str.contains(search)]
        
        # Custom Table Design
        st.markdown("---")
        head = st.columns([2, 2, 2, 2, 1])
        head[0].write("**Hisse**")
        head[1].write("**Fiyat**")
        head[2].write("**Gün %**")
        head[3].write("**Hacim**")
        
        for _, row in df.iterrows():
            c = st.columns([2, 2, 2, 2, 1])
            c[0].write(f"**{row['Hisse']}**")
            c[1].write(row['Fiyat'])
            color = "profit-up" if row['Değişim %'] > 0 else "profit-down"
            c[2].markdown(f"<span class='{color}'>%{row['Değişim %']:.2f}</span>", unsafe_allow_html=True)
            c[3].write(row['Hacim'])
            if c[4].button("İncele", key=f"btn_{row['Hisse']}"):
                st.session_state.selected_stock = row['Hisse']
                st.rerun()
            st.markdown("<hr style='margin:0; opacity:0.1;'>", unsafe_allow_html=True)

# --- 3. PORTFÖYÜM ---
elif st.session_state.page == "📈 Portföy Analizi":
    if not st.session_state.user:
        st.warning("🔒 Bu sayfa sadece admin yetkisine sahiptir.")
    else:
        st.header("📈 Portföy Performans & Analiz")
        
        # Veri ve Kar/Zarar
        assets = [
            {"H": "GENKM", "L": 85, "M": 13.0, "S": "Teknoloji"},
            {"H": "NUHCM", "L": 25, "M": 280.0, "S": "Çimento"},
            {"H": "TOASO", "L": 12, "M": 300.0, "S": "Otomotiv"}
        ]
        
        total_h_val = 0
        p_rows = []
        for a in assets:
            curr = yf.Ticker(f"{a['H']}.IS").fast_info.last_price
            val = curr * a['L']
            total_h_val += val
            k_tl = val - (a['M'] * a['L'])
            k_p = (k_tl / (a['M'] * a['L'])) * 100
            p_rows.append({"Hisse": a['H'], "Sektör": a['S'], "Değer": val, "KarZarar": f"{k_tl:,.2f} TL (%{k_p:.2f})", "Color": k_tl >= 0})
            
        extra = sum([i['Miktar'] for i in st.session_state.history])
        tp2_val = 9959.49 + extra
        total_port = total_h_val + tp2_val
        
        # Donut Chart (Varlık Dağılımı)
        c_stats, c_chart = st.columns([1, 1])
        with c_stats:
            st.metric("Net Portföy Değeri", f"{total_port:,.2f} TL")
            st.metric("TP2 Likidite", f"{tp2_val:,.2f} TL")
            
            st.subheader("💼 Pozisyonlar")
            for p in p_rows:
                st.markdown(f"**{p['Hisse']}** | {p['Değer']:,.2f} TL | <span class='{'profit-up' if p['Color'] else 'profit-down'}'>{p['KarZarar']}</span>", unsafe_allow_html=True)
                st.markdown("---")
                
        with c_chart:
            fig = px.pie(values=[total_h_val, tp2_val], names=['Hisseler', 'Yatırım Fonu (TP2)'], 
                         hole=.5, color_discrete_sequence=['#00ff88', '#161b22'])
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# --- 4. İŞLEM MERKEZİ ---
elif st.session_state.page == "🕒 İşlem Merkezi":
    if st.session_state.user:
        st.header("🕒 Nakit Akışı ve Mermi Kaydı")
        
        c_form, c_hist = st.columns([1, 2])
        with c_form:
            with st.form("mermi"):
                t_amt = st.number_input("İşlem Tutarı (TL)", min_value=0.0)
                t_type = st.selectbox("İşlem", ["Ekleme", "Çekme"])
                if st.form_submit_button("Sisteme İşle"):
                    z = datetime.now().strftime("%d/%m %H:%M")
                    val = t_amt if t_type == "Ekleme" else -t_amt
                    st.session_state.history.append({"Zaman": z, "Tip": t_type, "Miktar": val})
                    st.success("İşlem onaylandı!")
                    st.rerun()
                    
        with c_hist:
            if st.session_state.history:
                df_h = pd.DataFrame(st.session_state.history)[::-1]
                st.table(df_h)
            else: st.info("Henüz mermi eklenmedi.")

st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
st.sidebar.info("Yatırım tavsiyesi değildir. CoachInvest v11.0")
