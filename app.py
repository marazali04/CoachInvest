import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Sayfa Ayarları
st.set_page_config(page_title="CoachInvest 100K Ultra", layout="wide")

# 2. Hafıza (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Görsel Stil (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    [data-testid="stDataFrame"] { border: 1px solid #3e4255; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CoachInvest: 100K Strateji Terminali")

# --- YAN PANEL: HEDEF TAKİBİ ---
st.sidebar.header("🎯 Hedef: 100.000 TL")
target = 100000
b_hisse = 9008.50 # Midas'tan gelen
b_fon = 9947.37   # Midas'tan gelen

with st.sidebar.form("mermi_formu"):
    st.write("📥 Nakit Hareketi")
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

# --- ANA SAYFA TABS ---
t1, t2, t3 = st.tabs(["📊 Portföyüm", "🔍 BIST Terminal (A-Z)", "🕒 İşlem Tarihçesi"])

with t1:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.subheader("BIST Portföy")
        h_names = ["GENKM.IS", "NUHCM.IS", "TOASO.IS"]
        h_lots = [85, 25, 12]
        p_rows = []
        for i, (h, l) in enumerate(zip(h_names, h_lots), 1):
            try:
                p = yf.Ticker(h).history(period="1d")['Close'].iloc[-1]
                p_rows.append({"No": i, "Hisse": h.replace(".IS",""), "Fiyat": f"{p:.2f}", "Değer": round(p*l, 2)})
            except:
                p_rows.append({"No": i, "Hisse": h, "Fiyat": "0.00", "Değer": 0.0})
        
        # 'No' sütunu daraltıldı
        st.dataframe(pd.DataFrame(p_rows), hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    
    with c2:
        st.subheader("📈 Toplam Varlık Grafiği")
        st.area_chart(pd.DataFrame({'V': [toplam_v*0.97, toplam_v*0.99, toplam_v]}), color="#29b5e8")

with t2:
    st.subheader("🔍 Canlı Borsa Ekranı (Tüm Hisseler)")
    
    # 1. TradingView Market Overview Widget (Tüm BIST, Logolar ve % Değişimlerle)
    screener_html = """
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {
      "width": "100%", "height": 400, "defaultColumn": "overview", "defaultScreen": "most_capitalized",
      "market": "turkey", "showToolbar": true, "colorTheme": "dark", "locale": "tr"
      }
      </script>
    </div>
    """
    components.html(screener_html, height=420)

    st.markdown("---")
    st.subheader("📈 Detaylı Analiz & Arama")
    
    # Kapsamlı Arama (Search as you type için Selectbox kullanıyoruz, en hızlısı budur)
    bist_full = sorted(["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GARAN", "ISCTR", "YKBNK", "HEKTS", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL", "PETKM", "ASTOR", "SMRTG", "KONTR", "YEOTK", "REEDR", "TABGD", "CMENT"])
    
    sel = st.selectbox("İncelemek istediğin hisseyi yaz veya seç (Örn: ASEL...):", [""] + bist_full)
    
    if sel != "":
        try:
            t = yf.Ticker(f"{sel}.IS")
            h = t.history(period="2d")
            price = h['Close'].iloc[-1]
            change = ((price - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            
            c_a, c_b, c_c = st.columns(3)
            c_a.metric("Hisse", sel)
            c_b.metric("Fiyat", f"{price:.2f} TL")
            c_c.metric("Günlük Değişim", f"%{change:.2f}", delta=f"{change:.2f}%")
            
            # TradingView Advanced Chart
            tv_chart = f"""
            <div style="height:500px;"><div id="tv_chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>
            new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{sel}", "interval": "D", "timezone": "Europe/Istanbul", "theme": "dark", "style": "1", "locale": "tr", "container_id": "tv_chart"}});
            </script></div>"""
            components.html(tv_chart, height=520)
        except:
            st.error("Hisse verisi çekilemedi. Lütfen kodu kontrol edin.")

with t3:
    st.subheader("🕒 İşlem Tarihçesi")
    if st.session_state.history:
        # No sütununu 1'den başlatmak için dataframe düzenleme
        df_hist = pd.DataFrame(st.session_state.history)[::-1]
        df_hist.insert(0, 'No', range(1, len(df_hist) + 1))
        st.dataframe(df_hist, hide_index=True, use_container_width=True,
                     column_config={"No": st.column_config.Column(width="small")})
    else:
        st.info("Henüz bir işlem kaydı yok.")

st.markdown("---")
st.caption("CoachInvest Terminal v2.2 | Sabaha kadar nöbetteyiz.")
