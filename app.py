import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K", layout="wide")

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

# 7k transferini yapınca 'Para Ekle' kısmına yazabilirsin
current_cash = baslangic_fon + eklenen_para - cekilen_para

# --- ÜST ÖZET KARTLARI ---
m1, m2, m3 = st.columns(3)
toplam_varlik = baslangic_hisse + current_cash
gunluk_net = current_cash * (0.60 / 365) * 0.90 # Hata burada düzeltildi

m1.metric("Toplam Varlık", f"{toplam_varlik:,.2f} TL")
m2.metric("Günlük Pasif Kazanç", f"{gunluk_net:.2f} TL", "Nakit Koruması")
m3.metric("Nakit Gücü", f"{current_cash:,.2f} TL", f"%{(current_cash/toplam_varlik*100):.1f} Ağırlık")

st.sidebar.progress(min(toplam_varlik / target, 1.0))
st.sidebar.write(f"**100k Hedefine Ulaşma:** %{((toplam_varlik/target) * 100):.2f}")

# --- ANA İÇERİK: PORTFÖY VE GRAFİK ---
tab1, tab2, tab3 = st.tabs(["📊 Portföyüm", "📈 Genel Durum", "🔍 Hisse Ara & İşlem Yap"])

with tab1:
    st.subheader("BIST Portföy Detayları")
    hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
    lotlar = [85, 25, 12] 
    
    p_data = []
    for i, (h, l) in enumerate(zip(hisseler, lotlar), 1): # 1'den başlattım
        try:
            t = yf.Ticker(h)
            p = t.history(period="1d")['Close'].iloc[-1]
            p_data.append({"No": i, "Hisse": h, "Fiyat": f"{p:.2f}", "Değer": f"{p*l:,.2f} TL"})
        except:
            p_data.append({"No": i, "Hisse": h, "Fiyat": "Yükleniyor", "Değer": "0 TL"})
    
    st.table(p_data)

with tab2:
    st.subheader("📈 Tahmini Varlık Seyri")
    # Basit bir artış simülasyonu
    chart_data = pd.DataFrame({
        'Gün': range(1, 11),
        'Toplam_TL': [toplam_varlik * (1 + (i*0.005)) for i in range(10)]
    })
    st.line_chart(chart_data.set_index('Gün'))

with tab3:
    st.subheader("🔍 Piyasa Analizi ve Strateji")
    search_symbol = st.text_input("Hisse Kodu Gir (Örn: THYAO.IS)", "THYAO.IS")
    if search_symbol:
        try:
            ticker_search = yf.Ticker(search_symbol)
            s_price = ticker_search.history(period="1d")['Close'].iloc[-1]
            st.metric(f"{search_symbol} Fiyat", f"{s_price:.2f} TL")
            st.line_chart(ticker_search.history(period="1mo")['Close'])
            
            c1, c2 = st.columns(2)
            with c1:
                st.button(f"Sanal AL: {search_symbol}")
            with c2:
                st.button(f"Sanal SAT: {search_symbol}")
        except:
            st.error("Hisse kodu bulunamadı veya veri çekilemiyor.")

st.markdown("---")
st.info("💡 **CoachInvest Notu:** 100K hedefi disiplin ister. Bugün bankadan gelecek 7k ile nakit gücünü tahkim et.")
