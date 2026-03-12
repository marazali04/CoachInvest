import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K", layout="wide")

# 2. Hafıza (Session State) Kontrolü
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Görsel Tasarım
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Terminal")

# --- YAN PANEL: KOMUTA ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

with st.sidebar.form("mermi_paneli"):
    st.write("📥 Para Giriş/Çıkış")
    ekle = st.number_input("Ekle (TL)", value=0.0)
    cek = st.number_input("Çek (TL)", value=0.0)
    submit = st.form_submit_button("Onayla")
    
    if submit:
        simdi = datetime.now().strftime("%d/%m/%Y %H:%M")
        if ekle > 0:
            st.session_state.history.append({"Zaman": simdi, "İşlem": "Ekleme", "Miktar": ekle})
        if cek > 0:
            st.session_state.history.append({"Zaman": simdi, "İşlem": "Çekme", "Miktar": -cek})

# Dinamik Hesaplama
toplam_mermi = sum([item['Miktar'] for item in st.session_state.history])
current_cash = baslangic_fon + toplam_mermi
toplam_varlik = baslangic_hisse + current_cash
ilerleme = (toplam_varlik / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{ilerleme:.2f}")

# --- ANA SAYFA TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal", "🕒 Tarihçe"])

with t1:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.subheader("BIST Portföy")
        hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        lotlar = [85, 25, 12]
        p_list = []
        for i, (h, l) in enumerate(zip(hisseler, lotlar), 1):
            try:
                p = yf.Ticker(h).history(period="1d")['Close'].iloc[-1]
                p_list.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": round(p*l, 2)})
            except:
                p_list.append({"No": i, "Hisse": h, "Fiyat": "0.00", "Değer": 0.0})
        
        st.dataframe(pd.DataFrame(p_list), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    
    with c2:
        st.subheader("📈 Toplam Varlık")
        chart_data = pd.DataFrame({'Varlık': [toplam_varlik*0.97, toplam_varlik*0.99, toplam_varlik]})
        st.area_chart(chart_data, color="#29b5e8")

with t2:
    st.subheader("🔍 Tüm Hisseler ve TradingView")
    bist_liste =
