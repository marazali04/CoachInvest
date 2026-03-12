import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="expanded")

# 2. State Yönetimi
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Ana Sayfa"

# CSS: Fintables Koyu Tema ve Navigasyon Tasarımı
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    [data-testid="stSidebar"] { background-color: #161a1e; border-right: 1px solid #2f363d; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .stDataFrame { border: 1px solid #2f363d; }
    </style>
    """, unsafe_allow_html=True)

# --- SOL NAVİGASYON (FINTABLES STYLE) ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    pages = ["🏠 Ana Sayfa", "📡 BIST Radar", "📈 Portföyüm", "🕒 İşlem Geçmişi"]
    for p in pages:
        if st.button(p, key=f"nav_{p}"):
            st.session_state.page = p
    
    st.markdown("---")
    if not st.session_state.logged_in:
        with st.popover("🔑 Admin Girişi"):
            u = st.text_input("Kullanıcı")
            p = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap"):
                if u == "admin" and p == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
    else:
        st.success("Hoş geldin, Efruz")
        if st.button("Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

# --- ÜST BAR (STRATEJİK BUTONLAR) ---
col_head, col_btn = st.columns([8, 2])
with col_btn:
    if st.session_state.logged_in:
        with st.popover("💰 Mermi Yönetimi"):
            e = st.number_input("Ekle (TL)", value=0.0)
            c = st.number_input("Çıkar (TL)", value=0.0)
            if st.button("Onayla"):
                z = datetime.now().strftime("%d/%m %H:%M")
                if e > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": e})
                if c > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -c})
                st.rerun()

# --- SAYFA MANTIKLARI ---

# 1. ANA SAYFA (LANDING)
if st.session_state.page == "🏠 Ana Sayfa":
    st.header("📈 Borsa İstanbul'un Nabzı")
    c1, c2, c3 = st.columns(3)
    # Endeks Özetleri
    for col, tick, name in zip([c1, c2, c3], ["XU100.IS", "USDTRY=X", "GC=F"], ["BIST 100", "Dolar/TL", "Altın (Ons)"]):
        t = yf.Ticker(tick).fast_info
        col.metric(name, f"{t.last_price:,.2f}", f"{((t.last_price/t.previous_close)-1)*100:.2f}%")
    
    st.markdown("---")
    st.subheader("🔥 Piyasa Isı Haritası")
    map_html = '<div style="height: 500px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"container_id": "heatmap", "hasButtons": false, "colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    components.html(map_html, height=520)

# 2. RADAR (FINTABLES STYLE STOCK LIST)
elif st.session_state.page == "📡 BIST Radar":
    st.header("📡 BIST Tüm Hisseler")
    # A'dan Z'ye Hisse Listesi (Örnek Geniş Liste)
    tickers = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GENKM", "NUHCM", "TOASO", "MIATK", "ASTOR", "KOZAL", "PETKM"]
    
    radar_data = []
    for s in tickers:
        t = yf.Ticker(f"{s}.IS").fast_info
        radar_data.append({
            "Hisse": s,
            "Fiyat": f"{t.last_price:.2f} TL",
            "Gün %": f"{((t.last_price/t.previous_close)-1)*100:.2f}%",
            "Hacim": f"{t.last_volume/1e6:.1f} M"
        })
    
    st.dataframe(pd.DataFrame(radar_data), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔍 Detaylı Hisse Analizi")
    sel = st.selectbox("Hisse Seç", [""] + tickers)
    if sel:
        tick = yf.Ticker(f"{sel}.IS")
        m1, m2, m3 = st.columns(3)
        m1.metric("F/K", f"{tick.info.get('trailingPE', 'N/A')}")
        m2.metric("PD/DD", f"{tick.info.get('priceToBook', 'N/A')}")
        m3.metric("Özsermaye Karlılığı", f"%{tick.info.get('returnOnEquity', 0)*100:.1f}")
        
        tab_g, tab_b = st.tabs(["📉 Grafik", "🏦 Bilanço"])
        with tab_g:
            ch = f'<div style="height:400px;"><div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"width": "100%", "height": 400, "symbol": "BIST:{sel}", "theme": "dark", "locale": "tr", "container_id": "tv"}});</script></div>'
            components.html(ch, height=420)
        with tab_b: st.dataframe(tick.balance_sheet)

# 3. PORTFÖYÜM (SADECE ADMIN)
elif st.session_state.page == "📈 Portföyüm":
    if not st.session_state.logged_in:
        st.warning("🔒 Bu sayfayı görmek için Admin girişi yapmalısınız.")
    else:
        st.header("📈 Dashboard & Varlıklarım")
        # Portföy Hesaplama
        assets = [
            {"H": "GENKM", "L": 85, "M": 13.0},
            {"H": "NUHCM", "L": 25, "M": 280.0},
            {"H": "TOASO", "L": 12, "M": 300.0}
        ]
        total_h = 0.0
        p_list = []
        for a in assets:
            cur = yf.Ticker(f"{a['H']}.IS").fast_info.last_price
            val = cur * a['L']
            total_h += val
            k_tl = val - (a['M'] * a['L'])
            k_p = (k_tl / (a['M'] * a['L'])) * 100
            p_list.append({
                "Varlık": a['H'],
                "Değer": f"{val:,.2f} TL",
                "Kâr / Zarar": f"{k_tl:,.2f} TL (%{k_p:.2f})" # İstenen format
            })
        
        # Üst Metrikler
        c_cash = 9947.37 + sum([i['Miktar'] for i in st.session_state.history])
        total = total_h + c_cash
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Varlık", f"{total:,.2f} TL")
        m2.metric("Nakit Gücü", f"{c_cash:,.2f} TL")
        m3.metric("Hedef İlerleme (100k)", f"%{(total/100000)*100:.2f}")
        
        st.dataframe(pd.DataFrame(p_list), hide_index=True, use_container_width=True)

# 4. TARİHÇE (SADECE ADMIN)
elif st.session_state.page == "🕒 İşlem Geçmişi":
    if not st.session_state.logged_in:
        st.warning("🔒 Admin girişi gereklidir.")
    else:
        st.header("🕒 Nakit Hareketleri")
        if st.session_state.history:
            df_h = pd.DataFrame(st.session_state.history)[::-1]
            df_h['Miktar'] = df_h['Miktar'].map('{:,.2f} TL'.format) # 2 haneli kuruş
            st.table(df_h)
        else: st.info("İşlem yok.")

st.sidebar.markdown("---")
st.sidebar.caption("CoachInvest v6.0 | Strateji her şeydir.")
