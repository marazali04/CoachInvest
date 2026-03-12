import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Hafıza ve Giriş Sistemi (Daha stabil yapı)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS: Fintables Karanlık Tema ve Kart Yapısı
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161a1e; border-radius: 5px; }
    .stDataFrame { border: 1px solid #2f363d; }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST BAR (LOGIN OPSİYONU) ---
with st.container():
    c1, c2 = st.columns([8, 2])
    c1.title("🛡️ CoachInvest: Profesyonel Yatırım Terminali")
    if not st.session_state.logged_in:
        with c2.popover("👤 Giriş / Kayıt Ol"):
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                if user == "admin" and pw == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Hata!")
    else:
        c2.success(f"Hoş geldin, Admin")
        if c2.button("Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

# --- YAN PANEL: SADECE LOGGED IN KULLANICIYA ÖZEL ---
target = 100000
b_hisse = 9008.50
b_fon = 9947.37

if st.session_state.logged_in:
    st.sidebar.header("🎯 Portföy Yönetimi")
    with st.sidebar.form("para_y"):
        ekle = st.number_input("Para Ekle (TL)", value=0.0)
        cek = st.number_input("Para Çek (TL)", value=0.0)
        if st.form_submit_button("İşlemi Kaydet"):
            z = datetime.now().strftime("%d/%m %H:%M")
            if ekle > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": ekle})
            if cek > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -cek})
    
    ekstra = sum([i['Miktar'] for i in st.session_state.history])
    c_cash = b_fon + ekstra
    toplam_v = b_hisse + c_cash
    st.sidebar.metric("Toplam Varlık", f"{toplam_v:,.2f} TL")
    st.sidebar.progress(min(toplam_v/target, 1.0))
else:
    toplam_v = b_hisse + b_fon # Preview için
    st.sidebar.info("Özel portföy verilerini görmek için giriş yapmalısınız.")

# --- ANA SAYFA TABS ---
t_home, t_term, t_hist = st.tabs(["🏠 Dashboard", "🔍 Hisse Analiz (Fintables)", "🕒 İşlem Geçmişi"])

with t_home:
    st.subheader("📊 Piyasa Genel Bakış")
    # Canlı Isı Haritası ve Endeks Özetleri
    overview_html = """
    <div style="height: 450px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
    {
      "colorTheme": "dark", "dateRange": "12M", "showChart": true, "locale": "tr", "width": "100%", "height": "100%",
      "symbolsGroups": [
        { "name": "Endeksler", "originalName": "Indices", "symbols": [
            { "name": "BIST:XU100", "displayName": "BIST 100" },
            { "name": "BIST:XU030", "displayName": "BIST 30" }
        ]}
      ]
    }
    </script></div>"""
    components.html(overview_html, height=460)

    if st.session_state.logged_in:
        st.markdown("---")
        st.subheader("💼 Mevcut Varlıklarım")
        h_data = [
            {"Varlık": "GENKM", "Lot": 85, "Maliyet": "13.00"},
            {"Varlık": "NUHCM", "Lot": 25, "Maliyet": "280.00"},
            {"Varlık": "TOASO", "Lot": 12, "Maliyet": "300.00"}
        ]
        st.table(pd.DataFrame(h_data))

with t_term:
    st.subheader("🔍 Fintables Tarzı Temel Analiz")
    bist_pop = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GENKM", "NUHCM", "MIATK", "KONTR", "ASTOR"])
    sel = st.selectbox("Hisse Seçin", [""] + bist_pop)

    if sel:
        tick = yf.Ticker(f"{sel}.IS")
        info = tick.info
        
        # Üst Metrikler (Fintables Style)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("F/K", f"{info.get('trailingPE', 'N/A')}")
        m2.metric("PD/DD", f"{info.get('priceToBook', 'N/A')}")
        m3.metric("FD/FAVÖK", f"{info.get('enterpriseToEbitda', 'N/A')}")
        m4.metric("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}")
        m5.metric("Özsermaye Karlılığı", f"%{info.get('returnOnEquity', 0)*100:.2f}")

        # Sekmeli Detay Analiz
        s_t1, s_t2, s_t3, s_t4 = st.tabs(["📉 Teknik Grafik", "📊 Gelir Tablosu", "🏦 Bilanço", "💸 Nakit Akışı"])
        
        with s_t1:
            chart_html = f'<div style="height:500px;"><div id="tv_chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "theme": "dark", "locale": "tr", "container_id": "tv_chart"}});</script></div>'
            components.html(chart_html, height=520)
        
        with s_t2: st.dataframe(tick.financials)
        with s_t3: st.dataframe(tick.balance_sheet)
        with s_t4: st.dataframe(tick.cashflow)

with t_hist:
    if st.session_state.logged_in:
        st.subheader("🕒 İşlem Tarihçesi")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history)[::-1])
        else: st.info("Henüz işlem yok.")
    else: st.warning("Bu bölümü görmek için giriş yapmalısınız.")

st.caption("CoachInvest v4.0 | Strateji her şeydir.")
