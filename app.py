import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Ultra", layout="wide")

# Session State
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .stock-card { background-color: #262730; padding: 10px; border-radius: 5px; margin-bottom: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Merkezi")
st.markdown("---")

# --- YAN PANEL ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

eklenen = st.sidebar.number_input("📥 Para Ekle (TL)", value=0.0)
cekilen = st.sidebar.number_input("📤 Para Çek (TL)", value=0.0)

if st.sidebar.button("İşlemi Onayla"):
    simdi = datetime.now().strftime("%d/%m/%Y %H:%M")
    if eklenen > 0: st.session_state.history.append({"Zaman": simdi, "İşlem": "Ekleme", "Miktar": f"+{eklenen} TL"})
    if cekilen > 0: st.session_state.history.append({"Zaman": simdi, "İşlem": "Çekme", "Miktar": f"-{cekilen} TL"})
    st.sidebar.success("Kaydedildi!")

current_cash = baslangic_fon + eklenen - cekilen
toplam_varlik = baslangic_hisse + current_cash
gunluk_net = current_cash * (0.60 / 365) * 0.90

st.sidebar.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
st.sidebar.progress(min(toplam_varlik / target, 1.0))

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Portföyüm", "🔍 Gelişmiş Hisse Ara", "🕒 İşlem Tarihçesi"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("BIST Portföy")
        hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        lotlar = [85, 25, 12] 
        p_data = []
        for i, (h, l) in enumerate(zip(hisseler, lotlar), 1):
            t = yf.Ticker(h)
            p = t.history(period="1d")['Close'].iloc[-1]
            p_data.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": p*l})
        st.dataframe(pd.DataFrame(p_data), hide_index=True, use_container_width=True)
    
    with col_b:
        st.subheader("📈 Varlık Grafiği")
        chart_data = pd.DataFrame({'Varlık': [toplam_varlik*0.98, toplam_varlik*0.99, toplam_varlik]})
        st.area_chart(chart_data)

with tab2:
    st.subheader("🔍 Tüm Hisselerde Ara")
    
    # Kapsamlı BIST Listesi (En çok işlem gören 100+ hisse)
    bist_full = [
        "THYAO.IS", "EREGL.IS", "SASA.IS", "ASELS.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS", 
        "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "YKBNK.IS", "HEKTS.IS", "PGRS.IS", "EKGYO.IS", "KOZAL.IS",
        "ARCLK.IS", "FROTO.IS", "TOASO.IS", "TCELL.IS", "TTKOM.IS", "GUBRF.IS", "ENKAI.IS", "BGTOL.IS",
        "NUHCM.IS", "GENKM.IS", "MIATK.IS", "KONTR.IS", "YEOTK.IS", "EUPWR.IS", "ALARK.IS", "PETKM.IS"
        # ... Liste böyle uzayıp gidebilir, mantığı anlaman için ana kağıtları ekledim
    ]
    
    search_query = st.text_input("Hisse Adı veya Kodu Yaz (Örn: THY, NUH...)", "").upper()
    
    if search_query:
        # Arama sorgusuna göre filtreleme
        filtered_
