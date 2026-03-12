import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. GLOBAL KONFİGÜRASYON & TEMA
# ==========================================
st.set_page_config(
    page_title="CoachInvest | Professional Financial Terminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Profesyonel CSS (Dark Premium UI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #090b0f;
        color: #e1e4e8;
    }
    
    .stApp { background-color: #090b0f; }
    
    /* Kart Yapıları */
    div[data-testid="stMetric"] {
        background-color: #111418;
        border: 1px solid #1f242d;
        border-radius: 12px;
        padding: 20px !important;
        transition: 0.3s all ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #26a69a;
        transform: translateY(-2px);
    }
    
    /* Sidebar Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1f242d;
    }
    
    /* Tab ve Menü Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #26a69a !important;
        color: white !important;
    }
    
    /* Dataframe & Table */
    .stDataFrame { border: 1px solid #1f242d; border-radius: 10px; }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background: #0d1117;
        color: #8b949e;
        font-size: 12px;
        border-top: 1px solid #1f242d;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. STATE YÖNETİMİ
# ==========================================
if 'user' not in st.session_state: st.session_state.user = None
if 'users' not in st.session_state: st.session_state.users = {"admin": "admin"}
if 'history' not in st.session_state: st.session_state.history = []
if 'nav' not in st.session_state: st.session_state.nav = "🏠 Dashboard"
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = None

# ==========================================
# 3. YARDIMCI FONKSİYONLAR (VERİ & ANALİZ)
# ==========================================
@st.cache_data(ttl=600)
def get_market_summary():
    symbols = {"XU100.IS": "BIST 100", "USDTRY=X": "Dolar/TL", "GC=F": "Altın (Ons)", "BTC-USD": "Bitcoin"}
    data = []
    for sym, name in symbols.items():
        t = yf.Ticker(sym).fast_info
        change = ((t.last_price / t.previous_close) - 1) * 100
        data.append({"Name": name, "Price": t.last_price, "Change": change})
    return data

def render_tv_chart(symbol):
    html = f"""
    <div style="height:550px;">
        <div id="tradingview_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "width": "100%", "height": 550, "symbol": "BIST:{symbol}",
            "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark",
            "style": "1", "locale": "tr", "toolbar_bg": "#f1f3f6",
            "enable_publishing": false, "allow_symbol_change": true, "container_id": "tradingview_chart"
        }});
        </script>
    </div>"""
    components.html(html, height=560)

# ==========================================
# 4. SOL NAVİGASYON (PREMIUM SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3258/3258440.png", width=80)
    st.title("COACHINVEST")
    st.caption("Elite Financial Terminal v10.0")
    st.markdown("---")
    
    # Navigasyon Menüsü
    nav_options = ["🏠 Dashboard", "📡 BIST Radar", "📈 Portföy Analizi", "🕒 İşlem Merkezi"]
    for opt in nav_options:
        if st.button(opt, use_container_width=True, type="secondary" if st.session_state.nav != opt else "primary"):
            st.session_state.nav = opt
            st.rerun()

    st.markdown("---")
    
    # Auth Bölümü
    if not st.session_state.user:
        with st.expander("👤 Üye Girişi / Kayıt"):
            tab_login, tab_reg = st.tabs(["Giriş", "Kayıt"])
            with tab_login:
                u = st.text_input("Kullanıcı Adı", key="login_u")
                p = st.text_input("Şifre", type="password", key="login_p")
                if st.button("Giriş Yap", use_container_width=True):
                    if u in st.session_state.users and st.session_state.users[u] == p:
                        st.session_state.user = u
                        st.rerun()
            with tab_reg:
                nu = st.text_input("Yeni Kullanıcı")
                np = st.text_input("Yeni Şifre", type="password")
                if st.button("Kayıt Ol", use_container_width=True):
                    st.session_state.users[nu] = np
                    st.success("Kayıt başarılı!")
    else:
        st.write(f"Sistem Operatörü: **{st.session_state.user}**")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()

# ==========================================
# 5. ÜST GLOBAL BAR (LIVE TICKER)
# ==========================================
m_data = get_market_summary()
cols = st.columns(len(m_data))
for i, item in enumerate(m_data):
    cols[i].metric(item['Name'], f"{item['Price']:,.2f}", f"{item['Change']:.2f}%")

st.markdown("---")

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================

# --- DASHBOARD ---
if st.session_state.nav == "🏠 Dashboard":
    st.header("🏠 Piyasa Panoraması")
    
    col_map, col_news = st.columns([2, 1])
    
    with col_map:
        st.subheader("🔥 BIST Isı Haritası")
        heatmap = '<div style="height: 500px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
        components.html(heatmap, height=520)
        
    with col_news:
        st.subheader("📰 Son Haberler (KAP)")
        # Simüle edilmiş haber akışı
        news = [
            {"t": "04:15", "h": "GENKM: Yeni üretim tesisi onayı alındı."},
            {"t": "03:50", "h": "BIST100: Küresel piyasalarda pozitif ayrışma."},
            {"t": "02:10", "h": "TOASO: Mart ayı üretim verileri açıklandı."}
        ]
        for n in news:
            st.markdown(f"**{n['t']}** | {n['h']}")
            st.markdown("---")

# --- BIST RADAR (FINTABLES STYLE) ---
elif st.session_state.nav == "📡 BIST Radar":
    if st.session_state.active_ticker:
        # DETAYLI ANALİZ SAYFASI
        ticker = yf.Ticker(f"{st.session_state.active_ticker}.IS")
        
        c_head, c_back = st.columns([8, 2])
        c_head.title(f"📊 {st.session_state.active_ticker} Analiz Terminali")
        if c_back.button("⬅️ Listeye Dön"):
            st.session_state.active_ticker = None
            st.rerun()
            
        # KPI Kartları
        info = ticker.info
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("F/K Oranı", info.get('trailingPE', 'N/A'))
        k2.metric("PD/DD", info.get('priceToBook', 'N/A'))
        k3.metric("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}")
        k4.metric("Özsermaye Karlılığı", f"%{info.get('returnOnEquity', 0)*100:.2f}")
        k5.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.1f}B TL")
        
        tab_chart, tab_fin, tab_bal, tab_cash = st.tabs(["📉 İnteraktif Grafik", "🧾 Gelir Tablosu", "🏦 Bilanço", "💸 Nakit Akışı"])
        
        with tab_chart:
            render_tv_chart(st.session_state.active_ticker)
        with tab_fin: st.dataframe(ticker.financials, use_container_width=True)
        with tab_bal: st.dataframe(ticker.balance_sheet, use_container_width=True)
        with tab_cash: st.dataframe(ticker.cashflow, use_container_width=True)
        
    else:
        st.header("📡 BIST Akıllı Radar")
        st.write("A-Z tüm hisseler ve anlık performans verileri.")
        
        search_q = st.text_input("🔍 Hisse Ara (Örn: THYAO, NUH...)", "").upper()
        
        # BIST Veri Çekimi (Simülasyon / Hızlı Çekim)
        all_stocks = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "GENKM", "NUHCM", "TOASO", "ASTOR", "MIATK", "KONTR"]
        radar_data = []
        for s in all_stocks:
            if search_q in s:
                t = yf.Ticker(f"{s}.IS").fast_info
                ch = ((t.last_price / t.previous_close) - 1) * 100
                radar_data.append({"Hisse": s, "Fiyat": f"{t.last_price:.2f} TL", "Değişim": ch})
        
        # Profesyonel Liste Görünümü
        for row in radar_data:
            col_s, col_p, col_c, col_a = st.columns([2, 2, 2, 1])
            col_s.markdown(f"**{row['Hisse']}**")
            col_p.write(row['Fiyat'])
            color = "#26a69a" if row['Değişim'] > 0 else "#ef5350"
            col_c.markdown(f"<span style='color:{color}'>%{row['Değişim']:.2f}</span>", unsafe_allow_html=True)
            if col_a.button("İncele", key=f"btn_{row['Hisse']}"):
                st.session_state.active_ticker = row['Hisse']
                st.rerun()
            st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

# --- PORTFÖY ANALİZİ (ADMIN ONLY) ---
elif st.session_state.nav == "📈 Portföy Analizi":
    if not st.session_state.user:
        st.warning("🔒 Bu alan yalnızca yetkili kullanıcılar içindir. Lütfen giriş yapın.")
    else:
        st.header("📈 Stratejik Portföy Yönetimi")
        
        # Veri Hazırlama
        mermiler = sum([i['Miktar'] for i in st.session_state.history])
        tp2_bakiye = 9947.37 + mermiler
        
        assets = [
            {"H": "GENKM", "Lot": 85, "Cost": 13.0},
            {"H": "NUHCM", "Lot": 25, "Cost": 280.0},
            {"H": "TOASO", "Lot": 12, "Cost": 300.0}
        ]
        
        total_hisse_value = 0
        p_list = []
        for a in assets:
            cur = yf.Ticker(f"{a['H']}.IS").fast_info.last_price
            val = cur * a['Lot']
            total_hisse_value += val
            pnl = val - (a['Cost'] * a['Lot'])
            pnl_p = (pnl / (a['Cost'] * a['Lot'])) * 100
            p_list.append({"Varlık": a['H'], "Miktar": a['Lot'], "Değer": val, "PnL": pnl, "PnL%": pnl_p})
            
        total_v = total_hisse_value + tp2_bakiye
        
        # Üst Panel
        c1, c2, c3 = st.columns(3)
        c1.metric("Net Varlık Değeri", f"{total_v:,.2f} TL")
        c2.metric("Likidite (TP2)", f"{tp2_bakiye:,.2f} TL")
        c3.metric("Hedef Yolculuğu (100k)", f"%{(total_v/100000)*100:.2f}")
        
        # Detaylı Tablo
        st.subheader("💼 Pozisyon Detayları")
        df_p = pd.DataFrame(p_list)
        st.table(df_p.style.format({'Değer': '{:,.2f} TL', 'PnL': '{:,.2f} TL', 'PnL%': '%{:.2f}'}))
        
        # Dağılım Grafiği
        st.subheader("📊 Varlık Dağılımı")
        fig = px.pie(values=[total_hisse_value, tp2_bakiye], names=['Hisse Senetleri', 'Yatırım Fonları (TP2)'], hole=.4, color_discrete_sequence=['#26a69a', '#1f242d'])
        st.plotly_chart(fig, use_container_width=True)

# --- İŞLEM MERKEZİ ---
elif st.session_state.nav == "🕒 İşlem Merkezi":
    if not st.session_state.user:
        st.warning("🔒 Giriş gerekli.")
    else:
        st.header("🕒 Nakit Akış Kontrolü")
        
        col_form, col_hist = st.columns([1, 2])
        
        with col_form:
            st.subheader("Yeni Mermi Ekle/Çıkar")
            with st.form("transaction"):
                amt = st.number_input("Tutar (TL)", min_value=0.0)
                type_t = st.selectbox("İşlem Tipi", ["Ekleme", "Çekme"])
                if st.form_submit_button("Sisteme İşle"):
                    z = datetime.now().strftime("%d/%m %H:%M")
                    val = amt if type_t == "Ekleme" else -amt
                    st.session_state.history.append({"Zaman": z, "Tip": type_t, "Miktar": val})
                    st.success("Kayıt eklendi.")
                    st.rerun()
                    
        with col_hist:
            st.subheader("İşlem Tarihçesi")
            if st.session_state.history:
                st.table(pd.DataFrame(st.session_state.history)[::-1])
            else:
                st.info("Henüz bir işlem kaydı bulunmuyor.")

# ==========================================
# 7. FOOTER & DISCLAIMER
# ==========================================
st.markdown("""
    <div class="footer">
        CoachInvest Terminal © 2026 | Tüm veriler 15 dk gecikmelidir. Yatırım tavsiyesi değildir.
    </div>
    """, unsafe_allow_html=True)
