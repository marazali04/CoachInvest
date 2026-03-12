import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest 100K Pro", layout="wide", initial_sidebar_state="expanded")

# 2. State Yönetimi
if 'users' not in st.session_state: st.session_state.users = {"admin": "admin"}
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Ana Sayfa"

# 3. Görsel Tasarım ve Renklendirme Fonksiyonu
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    .stDataFrame { border: 1px solid #2f363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def color_df(val):
    if isinstance(val, str) and '%' in val:
        color = '#26a69a' if '+' in val or float(val.strip('%').replace('+','')) > 0 else '#ef5350'
        return f'color: {color}'
    return ''

# --- SOL NAVİGASYON ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    
    # Sayfa Navigasyonu (Herkes görebilir)
    if st.button("🏠 Ana Sayfa"): st.session_state.page = "🏠 Ana Sayfa"
    if st.button("📡 BIST Radar"): st.session_state.page = "📡 BIST Radar"
    
    # Giriş Yapmış Kullanıcı Sayfaları
    if st.session_state.user:
        if st.button("📈 Portföyüm"): st.session_state.page = "📈 Portföyüm"
        if st.button("🕒 İşlem Geçmişi"): st.session_state.page = "🕒 İşlem Geçmişi"
        st.markdown("---")
        st.success(f"Hoş geldin, {st.session_state.user}")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.user = None
            st.rerun()
    else:
        st.markdown("---")
        if st.button("🔑 Giriş Yap"): st.session_state.page = "🔑 Giriş"
        if st.button("📝 Kayıt Ol"): st.session_state.page = "📝 Kayıt"

# --- ÜST BAR (PARA YÖNETİMİ) ---
if st.session_state.user:
    col_h, col_m = st.columns([8, 2])
    with col_m:
        with st.popover("💰 Mermi Yönetimi"):
            ekle = st.number_input("Ekle (TL)", value=0.0)
            cek = st.number_input("Çek (TL)", value=0.0)
            if st.button("Onayla"):
                z = datetime.now().strftime("%d/%m %H:%M")
                if ekle > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": ekle})
                if cek > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -cek})
                st.rerun()

# --- SAYFA İÇERİKLERİ ---

# 1. GİRİŞ VE KAYIT SAYFALARI
if st.session_state.page == "🔑 Giriş":
    st.header("🔑 Giriş Yap")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.user = u
            st.session_state.page = "📈 Portföyüm"
            st.rerun()
        else: st.error("Hatalı kullanıcı adı veya şifre!")

elif st.session_state.page == "📝 Kayıt":
    st.header("📝 Yeni Hesap Oluştur")
    new_u = st.text_input("Kullanıcı Adı")
    new_p = st.text_input("Şifre", type="password")
    if st.button("Kayıt Ol"):
        if new_u and new_p:
            st.session_state.users[new_u] = new_p
            st.success("Kayıt Başarılı! Şimdi giriş yapabilirsiniz.")
        else: st.error("Lütfen alanları doldurun.")

# 2. RADAR (FINTABLES STYLE - 600+ HİSSE)
elif st.session_state.page == "📡 BIST Radar":
    st.header("📡 BIST Piyasa Radarı")
    # TradingView Screener (631 hisse ve anlık performans için en stabil çözüm)
    radar_html = """
    <div style="height: 800px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
    {
      "width": "100%", "height": "100%", "defaultColumn": "overview", "defaultScreen": "most_capitalized",
      "market": "turkey", "showToolbar": true, "colorTheme": "dark", "locale": "tr"
    }
    </script></div>"""
    components.html(radar_html, height=820)
    
    st.markdown("---")
    st.subheader("📊 Performans Analizi (Seçili Hisse)")
    tickers = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "GENKM", "NUHCM", "TOASO"]
    sel = st.selectbox("Analiz için hisse seçin:", tickers)
    if sel:
        t = yf.Ticker(f"{sel}.IS")
        h = t.history(period="1y")
        # Performans hesaplama
        p1m = ((h['Close'].iloc[-1]/h['Close'].iloc[-21])-1)*100
        p3m = ((h['Close'].iloc[-1]/h['Close'].iloc[-63])-1)*100
        p6m = ((h['Close'].iloc[-1]/h['Close'].iloc[-126])-1)*100
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Son Fiyat", f"{h['Close'].iloc[-1]:.2f} TL")
        c2.metric("1 Aylık", f"%{p1m:.2f}")
        c3.metric("3 Aylık", f"%{p3m:.2f}")
        c4.metric("6 Aylık", f"%{p6m:.2f}")

# 3. PORTFÖYÜM
elif st.session_state.page == "📈 Portföyüm":
    st.header("📈 Dashboard & Varlıklarım")
    
    # 26k Hesaplama Güncellemesi
    baslangic_nakit = 18956.11 # image_8bd974'teki bakiye
    extra_mermi = sum([i['Miktar'] for i in st.session_state.history])
    
    assets = [
        {"H": "GENKM", "L": 85, "M": 13.0, "C": 16.10},
        {"H": "NUHCM", "L": 25, "M": 280.0, "C": 307.0},
        {"H": "TOASO", "L": 12, "M": 300.0, "C": 304.5}
    ]
    
    total_h = 0.0
    h_rows = []
    for a in assets:
        val = a['C'] * a['L']
        total_h += val
        kar_tl = val - (a['M'] * a['L'])
        kar_p = (kar_tl / (a['M'] * a['L'])) * 100
        color = "profit-pos" if kar_tl >= 0 else "profit-neg"
        h_rows.append({"Varlık": a['H'], "Değer": f"{val:,.2f} TL", "Kâr/Zarar": f"{kar_tl:,.2f} TL (%{kar_p:.2f})"})

    # Fonlar (TP2 Canlı % Simülasyonu)
    tp2_bakiye = 9959.49 + extra_mermi
    tp2_kar_p = 1.49 # Örnek günlük getiri
    
    # Özet Kartları
    total_portfoy = total_h + tp2_bakiye
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Varlık", f"{total_portfoy:,.2f} TL")
    m2.metric("Nakit Gücü (TP2)", f"{tp2_bakiye:,.2f} TL")
    m3.metric("Hedef Yolculuğu", f"%{(total_portfoy/100000)*100:.2f}")

    st.subheader("💼 Hisse Senetleri")
    st.table(h_rows)
    
    st.subheader("💰 Yatırım Fonları")
    st.table([{"Fon": "TP2 - Serbest Fon", "Bakiye": f"{tp2_bakiye:,.2f} TL", "Günlük Getiri": f"+%{tp2_kar_p}"}])

elif st.session_state.page == "🕒 İşlem Geçmişi":
    st.header("🕒 İşlem Geçmişi")
    if st.session_state.history:
        df_h = pd.DataFrame(st.session_state.history)[::-1]
        df_h['Miktar'] = df_h['Miktar'].map('{:,.2f} TL'.format) # 2 haneli kuruş
        st.table(df_h)
    else: st.info("Henüz mermi eklenmedi.")

# 4. ANA SAYFA (HERKESE AÇIK)
else:
    st.header("🚀 CoachInvest Dashboard")
    map_html = '<div style="height: 600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    components.html(map_html, height=620)

st.sidebar.markdown("---")
st.sidebar.caption("CoachInvest v8.0 | Strateji her şeydir.")
