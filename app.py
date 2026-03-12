import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="expanded")

# 2. State Yönetimi (Veritabanı Simülasyonu)
if 'users' not in st.session_state: st.session_state.users = {"admin": "admin"}
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Ana Sayfa"
if 'selected_stock' not in st.session_state: st.session_state.selected_stock = None

# 3. Görsel Mimari (CSS)
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    .stButton>button { border-radius: 5px; transition: 0.3s; }
    .stButton>button:hover { background-color: #26a69a; color: white; }
    [data-testid="stSidebar"] { background-color: #161a1e; border-right: 1px solid #2f363d; }
    .fintable-header { color: #26a69a; font-weight: bold; border-bottom: 2px solid #26a69a; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def get_bist_data():
    # Bu liste örnek, gerçekte 600+ hisseyi bir kerede çekmek için loop kullanılır
    pop_tickers = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL"]
    data = []
    for s in pop_tickers:
        try:
            t = yf.Ticker(f"{s}.IS").fast_info
            change = ((t.last_price / t.previous_close) - 1) * 100
            data.append({
                "Hisse": s, "Fiyat": f"{t.last_price:.2f} TL", 
                "Değişim": f"{'+' if change > 0 else ''}{change:.2f}%",
                "Hacim": f"{t.last_volume/1e6:.1f}M"
            })
        except: continue
    return pd.DataFrame(data)

# --- SOL NAVİGASYON ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    
    if st.button("🏠 Ana Sayfa"): 
        st.session_state.page = "🏠 Ana Sayfa"
        st.session_state.selected_stock = None
    if st.button("📡 BIST Radar"): 
        st.session_state.page = "📡 BIST Radar"
        st.session_state.selected_stock = None
    
    if st.session_state.user:
        if st.button("📈 Portföyüm"): st.session_state.page = "📈 Portföyüm"
        if st.button("🕒 İşlem Geçmişi"): st.session_state.page = "🕒 İşlem Geçmişi"
        st.markdown("---")
        st.success(f"Kullanıcı: {st.session_state.user}")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.user = None
            st.rerun()
    else:
        st.markdown("---")
        if st.button("🔑 Giriş Yap"): st.session_state.page = "🔑 Giriş"
        if st.button("📝 Kayıt Ol"): st.session_state.page = "📝 Kayıt"

# --- ÜST BAR (STRATEJİK) ---
if st.session_state.user:
    _, col_m = st.columns([8, 2])
    with col_m:
        with st.popover("💰 Mermi Yönetimi"):
            ekle = st.number_input("Ekle (TL)", value=0.0)
            cek = st.number_input("Çek (TL)", value=0.0)
            if st.button("Onayla"):
                z = datetime.now().strftime("%d/%m %H:%M")
                if ekle > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": ekle})
                if cek > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -cek})
                st.rerun()

# --- SAYFALAR ---

if st.session_state.page == "🔑 Giriş":
    st.header("🔑 Üye Girişi")
    u = st.text_input("Kullanıcı Adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.user = u
            st.session_state.page = "🏠 Ana Sayfa"
            st.rerun()
        else: st.error("Hatalı bilgiler!")

elif st.session_state.page == "📝 Kayıt":
    st.header("📝 CoachInvest'e Katıl")
    st.markdown("##### Portföyünü profesyonelce yönetmek için ücretsiz hesabını oluştur.")
    c1, c2 = st.columns(2)
    new_u = c1.text_input("Kullanıcı Adı Belirle")
    new_p = c2.text_input("Şifre Belirle", type="password")
    email = st.text_input("E-Posta Adresi (Opsiyonel)")
    st.checkbox("Kullanım koşullarını ve gizlilik politikasını kabul ediyorum.")
    if st.button("Hesabımı Oluştur"):
        if new_u and new_p:
            st.session_state.users[new_u] = new_p
            st.balloons()
            st.success("Kaydın tamamlandı! Şimdi giriş yapabilirsin.")
        else: st.error("Gerekli alanları doldur!")

elif st.session_state.page == "📡 BIST Radar":
    if st.session_state.selected_stock:
        # HİSSE DETAY SAYFASI (FINTABLES STYLE)
        s = st.session_state.selected_stock
        st.header(f"📊 {s} - Analiz Merkezi")
        if st.button("⬅️ Radara Geri Dön"):
            st.session_state.selected_stock = None
            st.rerun()
        
        tick = yf.Ticker(f"{s}.IS")
        
        # Üst Metrikler
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fiyat", f"{tick.fast_info.last_price:.2f} TL")
        m2.metric("P/K", f"{tick.info.get('trailingPE', 'N/A')}")
        m3.metric("PD/DD", f"{tick.info.get('priceToBook', 'N/A')}")
        m4.metric("Özsermaye Karlılığı", f"%{tick.info.get('returnOnEquity', 0)*100:.1f}")
        
        # İçerik Sekmeleri
        tab_ozet, tab_bilanzo, tab_gelir, tab_nakit = st.tabs(["📉 Özet Rapor & Grafik", "🏦 Bilanço", "🧾 Gelir Tablosu", "💸 Nakit Akışı"])
        
        with tab_ozet:
            ch_html = f'<div style="height:500px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 500, "symbol": "BIST:{s}", "theme": "dark", "locale": "tr", "container_id": "tv"}});</script></div>'
            components.html(ch_html, height=520)
            st.markdown("---")
            st.subheader("Şirket Bilgileri")
            st.write(tick.info.get('longBusinessSummary', 'Bilgi bulunamadı.'))

        with tab_bilanzo:
            st.markdown("<p class='fintable-header'>Dönemsel Bilanço (Milyon TL)</p>", unsafe_allow_html=True)
            st.dataframe(tick.balance_sheet, use_container_width=True)
        
        with tab_gelir:
            st.markdown("<p class='fintable-header'>Gelir Tablosu (Milyon TL)</p>", unsafe_allow_html=True)
            st.dataframe(tick.financials, use_container_width=True)
            
        with tab_nakit:
            st.markdown("<p class='fintable-header'>Nakit Akım Tablosu (Milyon TL)</p>", unsafe_allow_html=True)
            st.dataframe(tick.cashflow, use_container_width=True)

    else:
        # RADAR LİSTE SAYFASI
        st.header("📡 BIST Piyasa Radarı")
        search = st.text_input("🔍 Hisse Ara (Örn: THYAO, SASA...)", "").upper()
        df = get_bist_data()
        
        if search:
            df = df[df['Hisse'].str.contains(search)]
        
        st.markdown("---")
        # Custom Table with Selection
        st.write("Hisse detayları için ismine tıklayabilirsiniz:")
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            if col1.button(row['Hisse'], key=f"sel_{row['Hisse']}"):
                st.session_state.selected_stock = row['Hisse']
                st.rerun()
            col2.write(row['Fiyat'])
            # Değişim Rengi
            color = "#26a69a" if "+" in row['Değişim'] else "#ef5350"
            col3.markdown(f"<span style='color:{color}'>{row['Değişim']}</span>", unsafe_allow_html=True)
            col4.write(row['Hacim'])
            col5.write("Detay ➡️")
            st.markdown("<hr style='margin:0; opacity:0.1;'>", unsafe_allow_html=True)

elif st.session_state.page == "📈 Portföyüm":
    if not st.session_state.user:
        st.warning("🔒 Portföyünüzü görmek için giriş yapmalısınız.")
    else:
        st.header("📈 Varlıklarım")
        # Portföy Mantığı
        baslangic_nakit = 18956.11
        extra_mermi = sum([i['Miktar'] for i in st.session_state.history])
        current_cash = baslangic_nakit + extra_mermi
        
        m1, m2 = st.columns(2)
        m1.metric("Toplam Varlık", f"{current_cash + 9008.50:,.2f} TL")
        m2.metric("TP2 Fon Bakiye", f"{current_cash:,.2f} TL")

        st.subheader("💼 Hisse Pozisyonları")
        h_data = [
            {"Hisse": "GENKM", "Değer": "1,368.50 TL", "Kâr": "+%23.85"},
            {"Hisse": "NUHCM", "Değer": "7,675.00 TL", "Kâr": "+%9.64"},
            {"Hisse": "TOASO", "Değer": "3,654.00 TL", "Kâr": "+%1.50"}
        ]
        st.table(h_data)

elif st.session_state.page == "🏠 Ana Sayfa":
    st.header("🚀 CoachInvest Dashboard")
    st.markdown("##### Piyasanın nabzını buradan takip edin.")
    map_html = '<div style="height: 600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    components.html(map_html, height=620)

st.sidebar.markdown("---")
st.sidebar.caption("CoachInvest v9.0 | Pro Terminal")
