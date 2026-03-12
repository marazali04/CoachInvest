import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Pro", layout="wide")

# Session State: Para hareketlerini ve tarihçeyi tutmak için
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_assets_log' not in st.session_state:
    st.session_state.total_assets_log = pd.DataFrame(columns=['Zaman', 'Toplam TL'])

# CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Yolculuğu")
st.markdown("---")

# --- YAN PANEL: PARA GİRİŞ/ÇIKIŞ ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000

# Sabit Başlangıç Değerleri (Midas fotoğraflarından gelen)
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

st.sidebar.subheader("Para Hareketleri")
eklenen = st.sidebar.number_input("📥 Para Ekle (TL)", value=0.0, step=100.0)
cekilen = st.sidebar.number_input("📤 Para Çek (TL)", value=0.0, step=100.0)

if st.sidebar.button("İşlemi Onayla"):
    simdi = datetime.now().strftime("%d/%m/%Y %H:%M")
    if eklenen > 0:
        st.session_state.history.append({"Zaman": simdi, "İşlem": "Ekleme", "Miktar": f"+{eklenen} TL"})
    if cekilen > 0:
        st.session_state.history.append({"Zaman": simdi, "İşlem": "Çekme", "Miktar": f"-{cekilen} TL"})
    st.sidebar.success("İşlem Tarihçeye Eklendi!")

current_cash = baslangic_fon + eklenen - cekilen

# --- ÜST METRİKLER ---
m1, m2, m3 = st.columns(3)
toplam_varlik = baslangic_hisse + current_cash
gunluk_net = current_cash * (0.60 / 365) * 0.90

m1.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
m2.metric("Günlük Pasif Kazanç", f"{gunluk_net:.2f} TL", "Nakit Koruması")
m3.metric("Nakit Gücü", f"{current_cash:,.2f} TL", f"%{(current_cash/toplam_varlik*100):.1f} Ağırlık")

st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**100k Hedefine Ulaşma:** %{((toplam_varlik/target) * 100):.2f}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Portföyüm & Grafik", "📂 Genel Durum (Tarihçe)", "🔍 Hisse Ara & İşlem"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("BIST Portföy Detayları")
        hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        lotlar = [85, 25, 12] 
        p_data = []
        for i, (h, l) in enumerate(zip(hisseler, lotlar), 1):
            try:
                t = yf.Ticker(h)
                p = t.history(period="1d")['Close'].iloc[-1]
                p_data.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": p*l})
            except: pass
        df_p = pd.DataFrame(p_data)
        st.dataframe(df_p, hide_index=True, use_container_width=True) # 0,1,2 SILINDI
    
    with col_b:
        st.subheader("📈 Toplam Varlık Seyri")
        # Simülasyon grafik (Gerçek veri girdikçe bu grafik evrilecek)
        chart_data = pd.DataFrame({'Varlık': [toplam_varlik*0.98, toplam_varlik*0.99, toplam_varlik]})
        st.area_chart(chart_data)

with tab2:
    st.subheader("🕒 Para Hareketleri Tarihçesi")
    if st.session_state.history:
        st.table(st.session_state.history)
    else:
        st.info("Henüz bir para hareketi kaydedilmedi.")

with tab3:
    st.subheader("🔍 Akıllı Hisse Arama")
    # A-Z için popüler BIST listesi (Burayı istediğin gibi genişletebiliriz)
    bist_list = ["THYAO.IS", "EREGL.IS", "SASA.IS", "ASELS.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS"]
    selected_stock = st.selectbox("İncelemek istediğin hisseyi seç veya yaz:", sorted(bist_list))
    
    if selected_stock:
        t_search = yf.Ticker(selected_stock)
        s_price = t_search.history(period="1d")['Close'].iloc[-1]
        st.metric(f"{selected_stock} Güncel", f"{s_price:.2f} TL")
        st.line_chart(t_search.history(period="1mo")['Close'])
        
        ca, cb = st.columns(2)
        ca.button("Sanal AL (Portföye Ekle)")
        cb.button("Sanal SAT (Portföyden Çıkar)")

st.markdown("---")
st.info("💡 **CoachInvest:** 100K hedefinde her mermi (para) değerlidir. Saatlik tarihçe ile disiplini koru.")
