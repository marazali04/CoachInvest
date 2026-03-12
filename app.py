import streamlit as st
import yfinance as yf
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="CoachInvest Pro", layout="wide")

# CSS ile Görsel İyileştirme (Hatayı burada düzelttim: unsafe_allow_html)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 CoachInvest: Strateji ve Birim Merkezi")
st.write(f"Son Güncelleme: {pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')}")
st.markdown("---")

# YAN PANEL (SIDEBAR)
st.sidebar.header("🎯 15 Nisan Hedefi")
target = 20000
hisse_hesabi = st.sidebar.number_input("Hisse Portföy Değeri (TL)", value=9800)
# Toplam Nakit: 18k + 1.1k + Gelecek 7k = 26.1k
nakit_fon = st.sidebar.number_input("Fon + Nakit (TL)", value=26100) 

toplam = hisse_hesabi + nakit_fon
progress = min(hisse_hesabi / target, 1.0)

st.sidebar.metric("Saha (Hisse) Durumu", f"{hisse_hesabi:,} TL", f"{hisse_hesabi - target} TL")
st.sidebar.progress(progress)
st.sidebar.write(f"**20k Hedefine Ulaşma:** %{((progress) * 100):.2f}")

# ÜST ÖZET KARTLARI
m1, m2, m3 = st.columns(3)
gunluk_net = nakit_fon * (0.60 / 365) * 0.90
m1.metric("Toplam Varlık", f"{toplam:,.2f} TL")
m2.metric("Günlük Pasif Kazanç", f"{gunluk_net:.2f} TL", "Nakit Koruması")
m3.metric("Nakit Gücü", f"{nakit_fon:,.2f} TL", f"%{(nakit_fon/toplam*100):.1f} Ağırlık")

# ANA İÇERİK
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Portföy Detayları")
    hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
    lotlar = [85, 25, 12] 
    
    p_data = []
    for h, l in zip(hisseler, lotlar):
        try:
            t = yf.Ticker(h)
            p = t.history(period="1d")['Close'].iloc[-1]
            p_data.append({"Hisse": h, "Fiyat": f"{p:.2f}", "Senin Payın": f"{p*l:,.2f} TL"})
        except:
            p_data.append({"Hisse": h, "Fiyat": "Hata", "Senin Payın": "0 TL"})
    st.table(p_data)

with col2:
    st.subheader("📈 GENKM Performans (Vur-Kaç Takibi)")
    try:
        genkm_data = yf.Ticker("GENKM.IS").history(period="1mo")
        st.line_chart(genkm_data['Close'])
    except:
        st.write("Grafik verisi şu an çekilemiyor.")

st.markdown("---")
st.info("💡 **Mentor Notu:** Saha (hisse) hesabındaki o bar %100 olduğunda 20k hedefine ulaşmış olacaksın. Stajda uykun gelirse bu bara bak!")
