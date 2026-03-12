import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="collapsed")

# 2. Hafıza ve Giriş Sistemi
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS: Fintables Karanlık Tema ve Profesyonel Tablo Tasarımı
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161a1e; border-radius: 5px; }
    .stDataFrame { border: 1px solid #2f363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST BAR (GİRİŞ OPSİYONU) ---
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
        c2.success(f"Hoş geldin, Admin")
        if c2.button("Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

# --- YAN PANEL: KOMUTA MERKEZİ ---
target = 100000
b_hisse_toplam = 0.0 # Canlı hesaplanacak
b_fon = 9947.37 # Başlangıç TP2

if st.session_state.logged_in:
    st.sidebar.header("🎯 Portföy Yönetimi")
    with st.sidebar.form("para_formu"):
        ekle = st.number_input("Para Ekle (TL)", value=0.0)
        cek = st.number_input("Para Çek (TL)", value=0.0)
        if st.form_submit_button("Onayla"):
            z = datetime.now().strftime("%d/%m %H:%M")
            if ekle > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": round(ekle, 2)})
            if cek > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": round(-cek, 2)})

# --- ANA SAYFA TABS ---
t_home, t_term, t_hist = st.tabs(["🏠 Dashboard", "🔍 Hisse Analiz (Radar)", "🕒 İşlem Geçmişi"])

with t_home:
    st.subheader("📊 Piyasa ve Varlıklarım")
    
    # Portföy Verileri (Maliyetlerinle)
    portfolio_data = [
        {"Hisse": "GENKM", "Lot": 85, "Maliyet": 13.00},
        {"Hisse": "NUHCM", "Lot": 25, "Maliyet": 280.00},
        {"Hisse": "TOASO", "Lot": 12, "Maliyet": 300.00}
    ]

    p_list = []
    total_hisse_value = 0.0
    
    for item in portfolio_data:
        t = yf.Ticker(f"{item['Hisse']}.IS")
        current_price = t.history(period="1d")['Close'].iloc[-1]
        value = current_price * item['Lot']
        total_hisse_value += value
        
        # Kar/Zarar Hesabı
        profit_tl = value - (item['Maliyet'] * item['Lot'])
        profit_perc = (profit_tl / (item['Maliyet'] * item['Lot'])) * 100
        
        status_color = "🟢" if profit_tl >= 0 else "🔴"
        p_list.append({
            "Hisse": item['Hisse'],
            "Fiyat": f"{current_price:.2f} TL",
            "Maliyet": f"{item['Maliyet']:.2f} TL",
            "Değer": f"{value:,.2f} TL",
            "Kar / Zarar (TL & %)": f"{status_color} {profit_tl:,.2f} TL (%{profit_perc:.2f})"
        })

    # Genel Durum Kartları
    ekstra = sum([i['Miktar'] for i in st.session_state.history])
    current_cash = b_fon + ekstra
    total_assets = total_hisse_value + current_cash
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Varlık", f"{total_assets:,.2f} TL")
    m2.metric("Nakit Gücü (TP2 + Nakit)", f"{current_cash:,.2f} TL")
    m3.metric("Hedef İlerleme", f"%{(total_assets/target)*100:.2f}")

    st.markdown("---")
    st.subheader("💼 Portföy Detayları")
    st.dataframe(pd.DataFrame(p_list), hide_index=True, use_container_width=True)

with t_term:
    st.subheader("🔍 BIST Radar (A-Z Tüm Hisseler)")
    
    # Fintables Radar Görünümü (Tüm Hisseler Tablosu)
    # Burada en popüler 50+ hisseyi varsayılan tablo olarak getiriyoruz
    bist_all_tickers = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "HEKTS", "GENKM", "NUHCM", "TOASO", "MIATK", "KONTR", "ASTOR", "KOZAL", "PETKM", "ASTOR", "SMRTG", "SDTTR", "REEDR", "TABGD", "CMENT", "FROTO", "TTKOM", "TCELL"])
    
    # Hisse Arama Çubuğu (En Üstte)
    search_q = st.text_input("Radar'da Hisse Ara (Örn: THY, ASE...)", "").upper()
    
    if search_q:
        filtered_tickers = [s for s in bist_all_tickers if search_q in s]
        if filtered_tickers:
            st.write(f"🔍 '{search_q}' için sonuçlar:")
            sel = st.selectbox("Detaylı incelemek için seçin:", [""] + filtered_tickers)
            if sel:
                # Hisse Detayları (F/K, PD/DD vs.)
                t_info = yf.Ticker(f"{sel}.IS").info
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("F/K", f"{t_info.get('trailingPE', 'N/A')}")
                c2.metric("PD/DD", f"{t_info.get('priceToBook', 'N/A')}")
                c3.metric("Piyasa Değeri", f"{t_info.get('marketCap', 0)/1e9:.2f} Mr TL")
                c4.metric("Temettü Verimi", f"%{t_info.get('dividendYield', 0)*100:.2f}")
                
                # TradingView Grafik
                chart_html = f'<div style="height:500px;"><div id="tv_chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "theme": "dark", "locale": "tr", "container_id": "tv_chart"}});</script></div>'
                components.html(chart_html, height=520)
    
    st.markdown("---")
    st.write("📈 **Canlı Piyasa Radarı**")
    # TradingView Screener - Fintables Radar havası için
    screener_html = """
    <div style="height: 600px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
    {
      "width": "100%", "height": "100%", "defaultColumn": "overview", "defaultScreen": "most_capitalized",
      "market": "turkey", "showToolbar": true, "colorTheme": "dark", "locale": "tr"
    }
    </script></div>"""
    components.html(screener_html, height=620)

with t_hist:
    st.subheader("🕒 İşlem Tarihçesi")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)[::-1]
        # Kuruş hanesini 2'ye sabitleme ve No sütunu
        df_hist['Miktar'] = df_hist['Miktar'].map('{:,.2f} TL'.format)
        df_hist.insert(0, 'No', range(1, len(df_hist) + 1))
        st.dataframe(df_hist, hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    else:
        st.info("Henüz bir işlem kaydı bulunmuyor.")

st.caption(f"CoachInvest v5.0 | {datetime.now().strftime('%d-%m-%Y %H:%M')} | Strateji her şeydir.")
