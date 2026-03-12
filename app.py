import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Konfigürasyon
st.set_page_config(page_title="CoachInvest Terminal", layout="wide", initial_sidebar_state="expanded")

# 2. Gelişmiş State Yönetimi (Kullanıcı Veritabanı Simülasyonu)
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "admin"} # Varsayılan admin
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Ana Sayfa"

# 3. Görsel Stil ve Renk Kodları
st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; }
    div[data-testid="stMetric"] { background-color: #161a1e; padding: 15px; border-radius: 8px; border: 1px solid #2f363d; }
    .profit-pos { color: #26a69a; font-weight: bold; }
    .profit-neg { color: #ef5350; font-weight: bold; }
    .profit-neu { color: #9ea1a6; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- YAN PANEL: NAVİGASYON VE AUTH ---
with st.sidebar:
    st.title("🛡️ CoachInvest")
    st.markdown("---")
    
    # Giriş/Kayıt Bölümü
    if not st.session_state.logged_in_user:
        auth_mode = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"])
        with st.container():
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if auth_mode == "Kayıt Ol":
                if st.button("Kayıt İşlemini Tamamla"):
                    if u and p:
                        st.session_state.users[u] = p
                        st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                    else: st.error("Eksik bilgi!")
            else:
                if st.button("Giriş Yap"):
                    if u in st.session_state.users and st.session_state.users[u] == p:
                        st.session_state.logged_in_user = u
                        st.rerun()
                    else: st.error("Hatalı bilgiler!")
    else:
        st.success(f"Hoş geldin, **{st.session_state.logged_in_user}**")
        pages = ["🏠 Ana Sayfa", "📡 BIST Radar", "📈 Portföyüm", "🕒 İşlem Geçmişi"]
        for pg in pages:
            if st.button(pg, key=f"nav_{pg}"):
                st.session_state.page = pg
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.logged_in_user = None
            st.rerun()

# --- ÜST BAR (STRATEJİK BUTONLAR) ---
col_head, col_btn = st.columns([8, 2])
with col_btn:
    if st.session_state.logged_in_user:
        with st.popover("💰 Mermi Yönetimi"):
            e = st.number_input("Ekle (TL)", value=0.0)
            c = st.number_input("Çıkar (TL)", value=0.0)
            if st.button("Onayla"):
                z = datetime.now().strftime("%d/%m %H:%M")
                if e > 0: st.session_state.history.append({"Zaman": z, "Tip": "Ekle", "Miktar": e})
                if c > 0: st.session_state.history.append({"Zaman": z, "Tip": "Çek", "Miktar": -c})
                st.rerun()

# --- SAYFA MANTIKLARI ---

def get_safe_price(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        data = t.history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1], data['Open'].iloc[-1]
        return 0.0, 0.0
    except: return 0.0, 0.0

if st.session_state.page == "🏠 Ana Sayfa":
    st.header("📈 Borsa İstanbul'un Nabzı")
    # Piyasa Isı Haritası
    map_html = '<div style="height: 600px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"container_id": "heatmap", "hasButtons": false, "colorTheme": "dark", "market": "turkey", "locale": "tr", "width": "100%", "height": "100%"}</script></div>'
    components.html(map_html, height=620)

elif st.session_state.page == "📡 BIST Radar":
    st.header("📡 BIST Tüm Hisseler")
    # Hata önleyici: Daha az hisse ve güvenli çekim
    tickers = ["THYAO", "EREGL", "SASA", "ASELS", "TUPRS", "KCHOL", "SISE", "BIMAS", "AKBNK", "GENKM", "NUHCM", "TOASO"]
    radar_list = []
    for s in tickers:
        price, open_p = get_safe_price(f"{s}.IS")
        change = ((price/open_p)-1)*100 if open_p != 0 else 0
        radar_list.append({"Hisse": s, "Fiyat": f"{price:.2f} TL", "Gün %": f"{change:.2f}%"})
    st.table(pd.DataFrame(radar_list))

elif st.session_state.page == "📈 Portföyüm":
    if not st.session_state.logged_in_user:
        st.warning("🔒 Lütfen giriş yapın.")
    else:
        st.header("📊 Varlık Dağılımı")
        
        # 1. HİSSELAR BÖLÜMÜ
        st.subheader("💼 Hisse Senetleri")
        assets = [
            {"H": "GENKM", "L": 85, "M": 13.0},
            {"H": "NUHCM", "L": 25, "M": 280.0},
            {"H": "TOASO", "L": 12, "M": 300.0}
        ]
        total_h = 0.0
        p_rows = []
        for a in assets:
            cur, _ = get_safe_price(f"{a['H']}.IS")
            val = cur * a['L']
            total_h += val
            diff = val - (a['M'] * a['L'])
            perc = (diff / (a['M'] * a['L'])) * 100
            
            # Renk Belirleme
            color = "profit-pos" if diff > 0 else "profit-neg" if diff < 0 else "profit-neu"
            p_rows.append({
                "Varlık": a['H'],
                "Değer": f"{val:,.2f} TL",
                "Kar / Zarar": f'<span class="{color}">{diff:,.2f} TL (%{perc:.2f})</span>'
            })
        st.write(pd.DataFrame(p_rows).to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("---")
        
        # 2. FONLAR BÖLÜMÜ
        st.subheader("💰 Yatırım Fonları")
        c_cash = 9947.37 + sum([i['Miktar'] for i in st.session_state.history])
        f_data = [{"Fon Adı": "TP2 - Serbest Fon", "Bakiye": f"{c_cash:,.2f} TL", "Durum": "Aktif"}]
        st.table(pd.DataFrame(f_data))

        # Genel Özet Kartları
        total = total_h + c_cash
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Portföy", f"{total:,.2f} TL")
        m2.metric("Nakit Gücü", f"{c_cash:,.2f} TL")
        m3.metric("Hedef Yolculuğu", f"%{(total/100000)*100:.2f}")

elif st.session_state.page == "🕒 İşlem Geçmişi":
    if st.session_state.logged_in_user:
        st.header("🕒 Nakit Hareketleri")
        if st.session_state.history:
            df_h = pd.DataFrame(st.session_state.history)[::-1]
            df_h['Miktar'] = df_h['Miktar'].map('{:,.2f} TL'.format)
            st.table(df_h)
        else: st.info("İşlem yok.")

st.sidebar.markdown("---")
st.sidebar.caption(f"CoachInvest v7.0 | {datetime.now().year}")
