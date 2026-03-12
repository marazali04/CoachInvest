import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K", layout="wide")

# 2. Hafıza (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Görsel Tasarım
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Merkezi")

# --- YAN PANEL: KOMUTA ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
# Midas'tan gelen sabit başlangıç değerlerin
b_hisse = 9008.50
b_fon = 9947.37

with st.sidebar.form("para_yonetimi"):
    st.write("📥 Nakit Hareketi")
    e_tl = st.number_input("Ekle (TL)", value=0.0)
    c_tl = st.number_input("Çek (TL)", value=0.0)
    onay = st.form_submit_button("İşlemi Onayla")
    if onay:
        z = datetime.now().strftime("%H:%M")
        if e_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": e_tl})
        if c_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -c_tl})

# Hesaplamalar
ekstra = sum([i['Miktar'] for i in st.session_state.history])
current_cash = b_fon + ekstra
toplam = b_hisse + current_cash
oran = (toplam / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam:,.2f} TL")
st.sidebar.progress(min(toplam/target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{oran:.2f}")

# --- ANA SAYFA: TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Analiz", "🕒 Tarihçe"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("BIST Detay")
        h_names = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        h_lots = [85, 25, 12]
        p_rows = []
        for i, (h, l) in enumerate(zip(h_names, h_lots), 1):
            try:
                p = yf.Ticker
