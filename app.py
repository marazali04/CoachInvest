import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest Terminal", layout="wide")

# Session State: Tarihçe ve işlemler için hafıza
if 'history' not in st.session_state:
    st.session_state.history = []

# CSS: Arayüz iyileştirme
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 10px; border-radius: 10px; border: 1px solid #3e4255; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1e2130; border-radius: 5px; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Terminal")

# --- YAN PANEL: PARA HAREKETLERİ ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

st.sidebar.subheader("📥 Para Giriş/Çıkış")
with st.sidebar.form("para_formu"):
    eklenen = st.number_input("Ekle (TL)", value=0.0, step=100.0)
    cekilen = st.number_input("Çek (TL)", value=0.0, step=100.0)
    onayla = st.form_submit_button("İşlemi Onayla")
    
    if onayla:
        simdi = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if eklenen > 0:
            st.session_state.history.append({"Zaman": simdi, "İşlem": "Ekleme", "Miktar": f"+{eklenen} TL"})
        if cekilen > 0:
            st.session_state.history.append({"Zaman": simdi, "İşlem": "Çekme", "Miktar": f"-{cekilen} TL"})
        st.success(f"İşlem Kaydedildi!")

# Toplam nakit hesabı
total_in = sum([float(i['Miktar'].replace(' TL','').replace('+','')) for i in st.session_state.history if 'Ekleme' in i['İşlem']])
total_out = sum([float(i['Miktar'].replace(' TL','').replace('-','')) for i in st.session_state.history if 'Çekme' in i['İşlem']])

current_cash = baslangic_fon + total_in - total_out
toplam_varlik = baslangic_hisse + current_cash
gunluk_pasif = current_cash * (0.60 / 365) * 0.90

st.sidebar.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{((toplam_varlik/target
