import streamlit as st
import yfinance as yf

st.set_page_config(page_title="CoachInvest", layout="wide")

st.title("🚀 CoachInvest: Strateji ve Birim Merkezi")
st.markdown("---")

# SOL PANEL: HEDEF VE NAKİT
target = 20000
st.sidebar.header("🎯 15 Nisan Hedefi")
hisse_hesabi = st.sidebar.number_input("Hisse Portföy Değeri (TL)", value=9800)
# Mevcut 18k + 1.1k + Gelecek 7k (İstediğin gibi güncelleyebilirsin)
nakit_fon = st.sidebar.number_input("Fon + Nakit (TL)", value=19100) 

toplam = hisse_hesabi + nakit_fon
progress = min(hisse_hesabi / target, 1.0)

st.sidebar.metric("Hedef Yolculuğu", f"{hisse_hesabi:,} TL", f"{hisse_hesabi - target} TL")
st.sidebar.progress(progress)
st.sidebar.write(f"**Hedefe Ulaşma Oranı:** %{((progress) * 100):.2f}")

# ANA PANEL: CANLI TAKİP
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Canlı Hisse İzleme")
    hisseler = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
    lotlar = [85, 25, 12] 
    
    for hisse, lot in zip(hisseler, lotlar):
        ticker = yf.Ticker(hisse)
        price = ticker.history(period="1d")['Close'].iloc[-1]
        st.write(f"**{hisse}:** {price:.2f} TL (Senin Payın: {price*lot:.2f} TL)")

with col2:
    st.subheader("💰 Pasif Gelir (Fon)")
    gunluk_net = nakit_fon * (0.60 / 365) * 0.90
    st.success(f"Fonun sana günlük **{gunluk_net:.2f} TL** kazandırıyor.")
    st.info("Bu para her sabah uyandığında cebinde.")

st.markdown("---")
st.write("📝 *CoachInvest: Stratejiye sadık kal, birimleri topla.*")
