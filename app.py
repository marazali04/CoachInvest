import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları (Her zaman en üstte olmalı)
st.set_page_config(page_title="CoachInvest 100K Pro", layout="wide")

# 2. Session State Başlatma (Hata payını sıfırlamak için)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Görsel Tasarım (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Merkezi")

# --- YAN PANEL: HESAPLAMALAR ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000

# Midas'tan gelen sabit veriler
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

st.sidebar.subheader("📥 Para Giriş/Çıkış")
with st.sidebar.form("para_giris_formu"):
    ekle = st.number_input("Ekle (TL)", value=0.0, step=100.0)
    cek = st.number_input("Çek (TL)", value=0.0, step=100.0)
    onay = st.form_submit_button("İşlemi Onayla")
    
    if onay:
        zaman = datetime.now().strftime("%d/%m/%Y %H:%M")
        if ekle > 0:
            st.session_state.history.append({"Zaman": zaman, "İşlem": "Ekleme", "Miktar": ekle})
        if cek > 0:
            st.session_state.history.append({"Zaman": zaman, "İşlem": "Çekme", "Miktar": -cek})
        st.success("Kaydedildi!")

# Nakit Hesabı (Daha güvenli döngü)
ekstra_nakit = 0.0
for h in st.session_state.history:
    ekstra_nakit += h['Miktar']

current_cash = baslangic_fon + ekstra_nakit
toplam_varlik = baslangic_hisse + current_cash
ilerleme = (toplam_varlik / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{ilerleme:.2f}")

# --- ANA SAYFA: TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal", "🕒 İşlem Tarihçesi"])

with t1:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("BIST Portföy")
        hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        lotlar = [85, 25, 12]
        p_list = []
        for idx, (h, l) in enumerate(zip(hisseler, lotlar), 1):
            try:
                t = yf.Ticker(h)
                p = t.history(period="1d")['Close'].iloc[-1]
                p_list.append({"No": idx, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": round(p*l, 2)})
            except:
                p_list.append({"No": idx, "Hisse": h, "Fiyat": "0.00", "Değer": 0.0})
        
        st.dataframe(pd.DataFrame(p_list), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    
    with col2:
        st.subheader("📈 Varlık Grafiği")
        # Grafik için veri hazırlığı
        g_data = pd.DataFrame({'Varlık': [toplam_varlik*0.96, toplam_varlik*0.98, toplam_varlik]})
        st.area_chart(g_data, color="#29b5e8")

with t2:
    st.subheader("🔍 Tüm Hisseler ve TradingView")
    bist_all = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "HEKTS", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "SMRTG"])
    
    s_input = st.text_input("Hisse Ara (Yazdıkça filtrelenir)...", "").upper()
    filtered = [s for s in bist_all if s_input in s] if s_input else bist_all
    
    sel = st.selectbox("Grafiğini görmek için seçin:", filtered)
    if sel:
        tv_html = f"""
        <div style="height:500px;">
          <div id="tv_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark", "style": "1", "locale": "tr", "container_id": "tv_chart"}});
          </script>
        </div>"""
        components.html(tv_html, height=520)

with t3:
    st.subheader("🕒 İşlem Tarihçesi")
    if st.session_state.history:
