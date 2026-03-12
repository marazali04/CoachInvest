import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Pro", layout="wide")

# Session State: Tarihçe ve mermi hesabı için
if 'history' not in st.session_state:
    st.session_state.history = []

# Görsel İyileştirmeler (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Merkezi")

# --- YAN PANEL: KOMUTA VE PARA ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000

# Sabit Midas Verilerin
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

st.sidebar.subheader("📥 Para Giriş/Çıkış")
with st.sidebar.form("islem_formu"):
    ekle = st.number_input("Ekle (TL)", value=0.0, step=100.0)
    cek = st.number_input("Çek (TL)", value=0.0, step=100.0)
    onay = st.form_submit_button("İşlemi Onayla")
    
    if onay:
        zaman = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if ekle > 0:
            st.session_state.history.append({"Zaman": zaman, "İşlem": "Ekleme", "Miktar": f"+{ekle} TL"})
        if cek > 0:
            st.session_state.history.append({"Zaman": zaman, "İşlem": "Çekme", "Miktar": f"-{cek} TL"})

# Toplam nakit hesaplaması (Tarihçeden gelen)
t_in = sum([float(h['Miktar'].replace(' TL','').replace('+','')) for h in st.session_state.history if 'Ekleme' in h['İşlem']])
t_out = sum([float(h['Miktar'].replace(' TL','').replace('-','')) for h in st.session_state.history if 'Çekme' in h['İşlem']])

current_cash = baslangic_fon + t_in - t_out
