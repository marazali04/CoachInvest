import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Pro", layout="wide")

# 2. Hafıza (Session State)
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

st.title("🛡️ CoachInvest: 100K Strateji Terminali")

# --- YAN PANEL: HEDEF VE NAKİT ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
b_hisse = 9008.50  # Başlangıç Hisse
b_fon = 9947.37    # Başlangıç TP2 Fonu

with st.sidebar.form("mermi_paneli"):
    st.write("📥 Nakit Yönetimi")
    ekle = st.number_input("Ekle (TL)", value=0.0)
    cek = st.number_input("Çek (TL)", value=0.0)
    onay = st.form_submit_button("İşlemi Onayla")
    if onay:
        simdi = datetime.now().strftime("%d/%m %H:%M")
        if ekle > 0: st.session_state.history.append({"Zaman": simdi, "Tip": "Ekle", "Miktar": round(ekle, 2)})
        if cek > 0: st.session_state.history.append({"Zaman": simdi, "Tip": "Çek", "Miktar": round(-cek, 2)})

# Dinamik Hesaplamalar
ekstra = sum([i['Miktar'] for i in st.session_state.history])
c_cash = b_fon + ekstra
toplam_v = b_hisse + c_cash
oran = (toplam_v / target) * 100

st.sidebar.metric("Toplam Varlık", f"{toplam_v:,.2f} TL")
st.sidebar.progress(min(toplam_v/target, 1.0))
st.sidebar.write(f"**Hedef İlerleme:** %{oran:.2f}")

# --- TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal (A-Z)", "🕒 İşlem Tarihçesi"])

with t1:
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("BIST Portföy")
        h_names = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        h_lots = [85, 25, 12]
        p_rows = []
        for i, (h, l) in enumerate(zip(h_names, h_lots), 1):
            try:
                p = yf.Ticker(h).history(period="1d")['Close'].iloc[-1]
                p_rows.append({"No": i, "Varlık": h.replace(".IS",""), "Fiyat/Değer": f"{p:.2f} TL", "Toplam": round(p*l, 2)})
            except:
                p_rows.append({"No": i, "Varlık": h.replace(".IS",""), "Fiyat/Değer": "0.00", "Toplam": 0.0})
        
        # Fonu da tabloya ekleme
        p_rows.append({"No": len(p_rows)+1, "Varlık": "TP2 (Yatırım Fonu)", "Fiyat/Değer": "Fon Bakiyesi", "Toplam": round(c_cash, 2)})
        
        st.dataframe(pd.DataFrame(p_rows), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
        
        st.info(f"💡 **Not:** Fon bakiyen eklediğin/çektiğin paralara göre anlık güncellenir.")

    with col_b:
        st.subheader("📈 Toplam Varlık Grafiği")
        st.area_chart(pd.DataFrame({'V': [toplam_v*0.97, toplam_v*0.985, toplam_v]}), color="#29b5e8")

with t2:
    st.subheader("📈 Detaylı Analiz & Arama")
    bist_list = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "HEKTS", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL", "PETKM", "KONTR", "YEOTK", "REEDR"])
    
    sel = st.selectbox("Hisse Ara veya Seç (Örn: ASEL...):", [""] + bist_list)
    
    if sel != "":
        try:
            t = yf.Ticker(f"{sel}.IS")
            h = t.history(period="2d")
            price = h['Close'].iloc[-1]
            change = ((price - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            
            c_x, c_y, c_z = st.columns(3)
            c_x.metric("Seçili Hisse", sel)
            c_y.metric("Fiyat", f"{price:.2f} TL")
            c_z.metric("Günlük Değişim", f"%{change:.2f}", delta=f"{change:.2f}%")
            
            tv_chart = f"""
            <div style="height:500px;"><div id="tv_chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>
            new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark", "style": "1", "locale": "tr", "container_id": "tv_chart"}});
            </script></div>"""
            components.html(tv_chart, height=520)
        except:
            st.error("Veri çekilemedi.")

    st.markdown("---")
    st.subheader("🔍 Canlı Borsa Ekranı (Tam Sayfa)")
    # Screener Widget (Yüksekliği artırıldı ve daha ferah bir görünüm sağlandı)
    screener_full = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {
      "width": "100%", "height": 600, "defaultColumn": "overview", "defaultScreen": "most_capitalized",
      "market": "turkey", "showToolbar": true, "colorTheme": "dark", "locale": "tr"
      }
      </script>
    </div>
    """
    components.html(screener_full, height=620)

with t3:
    st.subheader("🕒 İşlem Tarihçesi")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)[::-1]
        df_hist.insert(0, 'No', range(1, len(df_hist) + 1))
        st.dataframe(df_hist, hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    else:
        st.info("Henüz bir işlem kaydı bulunmuyor.")

st.markdown("---")
st.caption("CoachInvest Terminal v2.3 | Birim birim zafere!")
