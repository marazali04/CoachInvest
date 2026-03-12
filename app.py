import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Terminal", layout="wide")

# Session State: Tarihçeyi ve verileri tutmak için
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS: Tablo ve kart tasarımları
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 10px; border-radius: 10px; border: 1px solid #3e4255; }
    [data-testid="stDataFrame"] { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Terminali")

# --- YAN PANEL: PARA HAREKETLERİ ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

st.sidebar.subheader("📥 Para Giriş/Çıkış")
eklenen = st.sidebar.number_input("Ekle (TL)", value=0.0)
cekilen = st.sidebar.number_input("Çek (TL)", value=0.0)

if st.sidebar.button("İşlemi Onayla"):
    simdi = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if eklenen > 0:
        st.session_state.history.append({"Zaman": simdi, "İşlem": "Ekleme", "Miktar": f"+{eklenen} TL"})
    if cekilen > 0:
        st.session_state.history.append({"Zaman": simdi, "İşlem": "Çekme", "Miktar": f"-{cekilen} TL"})
    st.sidebar.success(f"İşlem kaydedildi: {simdi}")

current_cash = baslangic_fon + eklenen - cekilen
toplam_varlik = baslangic_hisse + current_cash
gunluk_net = current_cash * (0.60 / 365) * 0.90

st.sidebar.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{((toplam_varlik/target) * 100):.2f}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal (A-Z)", "🕒 İşlem Tarihçesi"])

with tab1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("BIST Portföy")
        hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        lotlar = [85, 25, 12] 
        p_data = []
        for i, (h, l) in enumerate(zip(hisseler, lotlar), 1):
            t = yf.Ticker(h)
            p = t.history(period="1d")['Close'].iloc[-1]
            p_data.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": round(p*l, 2)})
        
        # 'No' sütununu daraltmak için column_config kullandım
        st.dataframe(pd.DataFrame(p_data), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.
