import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Konfigürasyonu (En üstte kalmalı)
st.set_page_config(page_title="CoachInvest 100K", layout="wide")

# 2. Veri Hafızası (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Görsel Stil (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .stDataFrame { border: 1px solid #3e4255; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Merkezi")

# --- YAN PANEL: HEDEF VE NAKİT ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
# Midas'tan gelen başlangıç değerlerin
b_hisse = 9008.50
b_fon = 9947.37

with st.sidebar.form("para_formu"):
    st.write("📥 Nakit Yönetimi")
    e_tl = st.number_input("Ekle (TL)", value=0.0, step=100.0)
    c_tl = st.number_input("Çek (TL)", value=0.0, step=100.0)
    submit = st.form_submit_button("İşlemi Onayla")
    if submit:
        z = datetime.now().strftime("%d/%m %H:%M")
        if e_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": e_tl})
        if c_tl > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -c_tl})

# Hesaplamalar
ekstra_nakit = sum([item['Miktar'] for item in st.session_state.history])
current_cash = b_fon + ekstra_nakit
# Portföy değerini canlı çekmek için aşağıda güncelleyeceğiz, şimdilik sabit
toplam_v = b_hisse + current_cash 
ilerleme_oranı = (toplam_v / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam_v:,.2f} TL")
st.sidebar.progress(min(toplam_v/target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{ilerleme_oranı:.2f}")

# --- ANA SAYFA TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal", "🕒 İşlem Tarihçesi"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("BIST Portföy")
        h_names = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        h_lots = [85, 25, 12]
        rows = []
        for i, (h, l) in enumerate(zip(h_names, h_lots), 1):
            try:
                p_val = yf.Ticker(h).history(period="1d")['Close'].iloc[-1]
                rows.append({"No": i, "Hisse": h, "Fiyat": f"{p_val:.2f}", "Değer": round(p_val*l, 2)})
            except:
                rows.append({"No": i, "Hisse": h, "Fiyat": "N/A", "Değer": 0.0})
        
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    
    with col_b:
        st.subheader("📈 Toplam Varlık Seyri")
        # Grafik için 3 noktalı gelişim simülasyonu
        chart_df = pd.DataFrame({'Varlık': [toplam_v*0.97, toplam_v*0.99, toplam_v]})
        st.area_chart(chart_df, color="#29b5e8")

with t2:
    st.subheader("🔍 Tüm Hisseler & TradingView Analiz")
    
    # Kapsamlı BIST listesi (Arama için anahtar)
    bist_all = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "HEKTS", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL", "PETKM", "ASTOR", "SMRTG", "KONTR", "YEOTK"])
    
    search_q = st.text_input("Hisse Ara (Yazmaya başlayınca filtreler...):").upper()
    
    if search_q:
        matches = [s for s in bist_all if search_q in s]
        if matches:
            cols = st.columns(4)
            for idx, stock in enumerate(matches):
                with cols[idx % 4]:
                    if st.button(f"📊 {stock}", key=f"btn_{stock}"):
                        st.session_state.active_stock = stock
        else:
            st.warning("Hisse bulunamadı.")
    
    # Seçili hissenin TradingView grafiği
    if 'active_stock' in st.session_state:
        st.markdown(f"### {st.session_state.active_stock} Canlı Grafik")
        s = st.session_state.active_stock
        tv_html = f"""
        <div style="height:500px;">
          <div id="tv_chart"></div>
          <script src="https://s3.tradingview.com/tv.js"></script>
          <script>
          new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{s}", "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark", "style": "1", "locale": "tr", "toolbar_bg": "#f1f3f6", "enable_publishing": false, "allow_symbol_change": true, "container_id": "tv_chart"}});
          </script>
        </div>"""
        components.html(tv_html, height=520)
    else:
        st.info("Grafiğini görmek istediğin hisseyi yukarıdan aratıp tıkla.")

with t3:
    st.subheader("🕒 Para Hareketleri Tarihçesi")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history)[::-1])
    else:
        st.info("Henüz bir işlem kaydı bulunmuyor.")

st.markdown("---")
st.caption("CoachInvest Terminal v2.1 | Birim birim zafere!")
