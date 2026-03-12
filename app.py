import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K", layout="wide")

# Session State: Alım-Satım ve Para Hareketleri için hafıza oluşturma
if 'gecmis_veriler' not in st.session_state:
    st.session_state.gecmis_veriler = []
if 'islemler' not in st.session_state:
    st.session_state.islemler = []

# CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Yolculuğu")
st.markdown("---")

# --- YAN PANEL: HEDEF VE PARA YÖNETİMİ ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000

# Fotoğraftaki güncel verilerin
baslangic_hisse = 9008.50
baslangic_fon = 9947.37

eklenen_para = st.sidebar.number_input("📥 Para Ekle (TL)", value=0.0)
cekilen_para = st.sidebar.number_input("📤 Para Çek (TL)", value=0.0)

current_cash = baslangic_fon + eklenen_para - cekilen_para
st.sidebar.markdown(f"**Güncel Fon Gücü:** {current_cash:,.2f} TL")

# --- ÜST ÖZET KARTLARI ---
m1, m2, m3 = st.columns(3)
toplam_varlik = baslangic_hisse + current_cash
gunluk_pasif = current_cash * (0.60 / 365) * 0.90

m1.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
m2.metric("Günlük Pasif Kazanç", f"{gunluk_net:.2f} TL", "Nakit Koruması")
m3.metric("Hedef İlerleme", f"%{(toplam_varlik/target*100):.2f}", f"Kalan: {target-toplam_varlik:,.0f} TL")

st.sidebar.progress(min(toplam_varlik / target, 1.0))

# --- ANA İÇERİK: PORTFÖY VE GRAFİK ---
tab1, tab2, tab3 = st.tabs(["📊 Portföyüm", "📈 Genel Durum", "🔍 Hisse Ara & İşlem Yap"])

with tab1:
    st.subheader("BIST Portföy Detayları")
    hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
    lotlar = [85, 25, 12] 
    
    p_data = []
    for i, (h, l) in enumerate(zip(hisseler, lotlar), 1): # 1'den başlatma
        t = yf.Ticker(h)
        p = t.history(period="1d")['Close'].iloc[-1]
        p_data.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": f"{p*l:,.2f} TL"})
    
    st.table(p_data)

with tab2:
    st.subheader("📈 Toplam Varlık Değişimi")
    # Bu kısım gerçek geçmiş veri için veritabanı ister, şimdilik simülasyon yapıyoruz
    chart_data = pd.DataFrame({
        'Gün': range(1, 11),
        'Toplam TL': [toplam_varlik * (1 + (i*0.01)) for i in range(10)]
    })
    st.line_chart(chart_data.set_index('Day'))

with tab3:
    st.subheader("🔍 Piyasa Analizi ve Sanal İşlem")
    search_symbol = st.text_input("Hisse Kodu Gir (Örn: THYAO.IS)", "THYAO.IS")
    if search_symbol:
        ticker_search = yf.Ticker(search_symbol)
        s_price = ticker_search.history(period="1d")['Close'].iloc[-1]
        st.write(f"**Güncel Fiyat:** {s_price:.2f} TL")
        st.line_chart(ticker_search.history(period="1mo")['Close'])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"AL: {search_symbol}"):
                st.success(f"{search_symbol} alım emri simüle edildi.")
        with c2:
            if st.button(f"SAT: {search_symbol}"):
                st.warning(f"{search_symbol} satış emri simüle edildi.")

st.markdown("---")
st.info("💡 **CoachInvest Notu:** 100K hedefi disiplin ister. Sahadaki hisselerin skor üretsin, fonların kalkanın olsun.")
