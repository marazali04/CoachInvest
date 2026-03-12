import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="expanded")

# 2. Login Sistemi (Admin Girişi)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.markdown("""<h2 style='text-align: center;'>🛡️ CoachInvest Giriş</h2>""", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
                if user == "admin" and pw == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")

if not st.session_state.logged_in:
    login()
    st.stop()

# 3. Veri Hafızası
if 'history' not in st.session_state:
    st.session_state.history = []

# 4. Görsel Tasarım (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- YAN PANEL: KOMUTA ---
st.sidebar.title("🛡️ CoachInvest Pro")
st.sidebar.write(f"Hoş geldin, **Admin**")
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
target = 100000
b_hisse = 9008.50
b_fon = 9947.37

with st.sidebar.form("nakit_formu"):
    st.write("📥 Nakit Yönetimi")
    e_tl = st.number_input("Ekle (TL)", value=0.0)
    c_tl = st.number_input("Çek (TL)", value=0.0)
    if st.form_submit_button("Onayla"):
        z = datetime.now().strftime("%d/%m %H:%M")
        if e_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": e_tl})
        if c_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -c_tl})

# Hesaplamalar
ekstra = sum([i['Miktar'] for i in st.session_state.history])
c_cash = b_fon + ekstra
toplam_v = b_hisse + c_cash
oran = (toplam_v / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam_v:,.2f} TL")
st.sidebar.progress(min(toplam_v/target, 1.0))
st.sidebar.write(f"Hedef İlerleme: %{oran:.2f}")

# --- ANA SAYFA TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 Hisse Terminali (Fintables Style)", "🕒 İşlem Tarihçesi"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("Aktif Varlıklar")
        h_names = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        h_lots = [85, 25, 12]
        p_rows = []
        for i, (h, l) in enumerate(zip(h_names, h_lots), 1):
            try:
                p = yf.Ticker(h).history(period="1d")['Close'].iloc[-1]
                p_rows.append({"No": i, "Varlık": h.replace(".IS",""), "Fiyat": f"{p:.2f}", "Toplam": round(p*l, 2)})
            except:
                p_rows.append({"No": i, "Varlık": h, "Fiyat": "0.00", "Toplam": 0.0})
        p_rows.append({"No": len(p_rows)+1, "Varlık": "TP2 FON", "Fiyat": "-", "Toplam": round(c_cash, 2)})
        st.dataframe(pd.DataFrame(p_rows), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    with col_b:
        st.subheader("Stratejik Varlık Dağılımı")
        st.area_chart(pd.DataFrame({'V': [toplam_v*0.97, toplam_v*0.99, toplam_v]}), color="#29b5e8")

with t2:
    st.subheader("🔍 Temel ve Teknik Analiz Merkezi")
    bist_all = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "GENKM", "NUHCM", "TOASO", "MIATK", "KONTR", "YEOTK", "REEDR", "TABGD"])
    
    sel = st.selectbox("Analiz edilecek hisseyi seçin:", [""] + bist_all)
    
    if sel:
        ticker = yf.Ticker(f"{sel}.IS")
        
        # Fintables Tarzı Başlık Metrikleri
        c1, c2, c3, c4 = st.columns(4)
        info = ticker.fast_info
        last_price = info.last_price
        c1.metric("Son Fiyat", f"{last_price:.2f} TL")
        c2.metric("Piyasa Değeri", f"{info.market_cap/1e9:.2f} Milyar")
        c3.metric("Günlük Hacim", f"{info.last_volume/1e6:.1f} Milyon")
        c4.metric("52 Haftalık Zirve", f"{info.year_high:.2f} TL")

        # Fintables Tarzı Tablo Menüsü
        sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs(["📉 Grafik", "🧾 Gelir Tablosu", "🏦 Bilanço", "💸 Nakit Akışı"])
        
        with sub_t1:
            tv_html = f'<div style="height:500px;"><div id="tv_chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark", "style": "1", "locale": "tr", "container_id": "tv_chart", "hide_side_toolbar": false, "allow_symbol_change": true, "save_image": false}});</script></div>'
            components.html(tv_html, height=520)
        
        with sub_t2:
            st.dataframe(ticker.financials, use_container_width=True)
        with sub_t3:
            st.dataframe(ticker.balance_sheet, use_container_width=True)
        with sub_t4:
            st.dataframe(ticker.cashflow, use_container_width=True)

with t3:
    st.subheader("🕒 İşlem Kayıtları")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)[::-1]
        df_hist.insert(0, 'No', range(1, len(df_hist) + 1))
        st.table(df_hist)
    else:
        st.info("Henüz onaylanmış bir işlem yok.")

st.markdown("---")
st.caption("CoachInvest v3.0 | Kurumsal Altyapı | Mentor: Gemini")
