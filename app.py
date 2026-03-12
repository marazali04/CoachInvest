import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PLATFORM AYARLARI & FINTABLES CSS
# ==========================================
st.set_page_config(page_title="CoachInvest Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    /* Premium Koyu Tema */
    .main { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Metrik Kartları (Fintables Style) */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Tab Menüleri */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 600; font-size: 16px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { color: #00ADB5 !important; border-bottom: 3px solid #00ADB5 !important; }
    
    /* Tablolar */
    .stDataFrame { border: 1px solid #333; border-radius: 8px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #181818; border-right: 1px solid #222; }
    
    /* Renk Sınıfları */
    .text-green { color: #00E676; font-weight: 600; }
    .text-red { color: #FF1744; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. VERİ MOTORU (Güvenli & Önbellekli)
# ==========================================
@st.cache_data(ttl=3600)
def get_stock_profile(symbol):
    try:
        t = yf.Ticker(f"{symbol}.IS")
        info = t.info
        hist = t.history(period="6mo")
        return info, hist, t
    except:
        return None, None, None

def format_large_numbers(num):
    if pd.isna(num) or num is None: return "N/A"
    if num >= 1e9: return f"{num/1e9:.2f} Milyar TL"
    if num >= 1e6: return f"{num/1e6:.2f} Milyon TL"
    return f"{num:,.2f} TL"

# ==========================================
# 3. STATE YÖNETİMİ
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "Piyasalar"
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []

# ==========================================
# 4. NAVİGASYON (SOL PANEL)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#00ADB5; text-align:center;'>COACHINVEST</h2>", unsafe_allow_html=True)
    st.caption("<div style='text-align:center;'>Finansal Analiz Platformu</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = ["Piyasalar", "Hisse Analiz Terminali", "Portföy & Yönetim"]
    for m in menu:
        if st.button(m, use_container_width=True):
            st.session_state.page = m
            st.rerun()
            
    st.markdown("---")
    if st.session_state.user:
        st.success(f"Oturum: {st.session_state.user}")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        st.write("🔑 **Sistem Girişi**")
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş", use_container_width=True):
            if u == "admin" and p == "admin":  # Basit auth
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Hatalı giriş.")

# ==========================================
# 5. SAYFA İÇERİKLERİ
# ==========================================

# --- SAYFA 1: PİYASALAR (DASHBOARD) ---
if st.session_state.page == "Piyasalar":
    st.header("🌐 Küresel ve Yerel Piyasalar")
    
    # Üst Endeks Kartları
    c1, c2, c3, c4 = st.columns(4)
    indices = {"BIST 100": "XU100.IS", "S&P 500": "^GSPC", "Dolar/TL": "USDTRY=X", "Altın (Ons)": "GC=F"}
    
    for col, (name, symbol) in zip([c1, c2, c3, c4], indices.items()):
        try:
            t = yf.Ticker(symbol).fast_info
            last = t.last_price
            prev = t.previous_close
            pct = ((last - prev) / prev) * 100
            col.metric(name, f"{last:,.2f}", f"{pct:.2f}%")
        except:
            col.metric(name, "Veri Yok", "0%")
            
    st.markdown("---")
    st.subheader("🔥 BIST 30 Özet Ekranı")
    st.info("Piyasanın lokomotif hisselerinin anlık durumları (Native Tablo)")
    
    # Hızlı BIST 30 Çekimi
    bist30 = ["THYAO", "EREGL", "TUPRS", "KCHOL", "AKBNK", "ISCTR", "SAHOL", "BIMAS", "ASELS", "SISE"]
    market_data = []
    for s in bist30:
        try:
            t = yf.Ticker(f"{s}.IS").fast_info
            chg = ((t.last_price / t.previous_close) - 1) * 100
            market_data.append({"Sembol": s, "Fiyat": f"{t.last_price:.2f}", "Değişim (%)": chg, "Hacim": t.last_volume})
        except: continue
        
    if market_data:
        df_m = pd.DataFrame(market_data)
        # Renklendirme
        def color_pct(val):
            color = '#00E676' if val > 0 else '#FF1744'
            return f'color: {color}; font-weight: bold;'
            
        st.dataframe(df_m.style.applymap(color_pct, subset=['Değişim (%)']).format({'Değişim (%)': '{:.2f}%', 'Hacim': '{:,.0f}'}), 
                     use_container_width=True, hide_index=True)

# --- SAYFA 2: HİSSE ANALİZ (FINTABLES CORE) ---
elif st.session_state.page == "Hisse Analiz Terminali":
    st.header("🔍 Kapsamlı Şirket Analizi")
    
    # Dev Arama Çubuğu
    search = st.text_input("Şirket Kodunu Girin (Örn: GENKM, THYAO, FROTO):", "THYAO").upper()
    
    if search:
        info, hist, ticker = get_stock_profile(search)
        
        if info and not hist.empty:
            # 1. Şirket Başlığı ve Ana Fiyat
            st.markdown(f"## {info.get('longName', search)}")
            st.markdown(f"Sektör: **{info.get('sector', 'Bilinmiyor')}** | Endeks: **BIST**")
            
            # 2. Ana Metrikler (Rasyolar)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Son Fiyat", f"{hist['Close'].iloc[-1]:.2f} TL")
            m2.metric("Piyasa Değeri", format_large_numbers(info.get('marketCap')))
            m3.metric("F/K Oranı", info.get('trailingPE', 'N/A'))
            m4.metric("PD/DD", info.get('priceToBook', 'N/A'))
            m5.metric("FD/FAVÖK", info.get('enterpriseToEbitda', 'N/A'))
            
            st.markdown("---")
            
            # 3. FINTABLES STİLİ TABLAR
            t_ozet, t_grafik, t_bilanco, t_gelir, t_nakit = st.tabs([
                "📋 Özet Rapor", "📉 Teknik Grafik", "🏦 Bilanço", "📊 Gelir Tablosu", "💸 Nakit Akım"
            ])
            
            with t_ozet:
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.subheader("Şirket Profili")
                    st.write(info.get('longBusinessSummary', 'Açıklama bulunamadı.')[:800] + "...")
                with col_b:
                    st.subheader("Kârlılık Oranları")
                    st.write(f"- **Brüt Kâr Marjı:** %{info.get('grossMargins', 0)*100:.2f}")
                    st.write(f"- **FAVÖK Marjı:** %{info.get('ebitdaMargins', 0)*100:.2f}")
                    st.write(f"- **Net Kâr Marjı:** %{info.get('profitMargins', 0)*100:.2f}")
                    st.write(f"- **Özsermaye Kârlılığı (ROE):** %{info.get('returnOnEquity', 0)*100:.2f}")
                    st.write(f"- **Temettü Verimi:** %{info.get('dividendYield', 0)*100:.2f}")
            
            with t_grafik:
                # Plotly Native Candlestick (TradingView Değil)
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name="Fiyat"
                ))
                # 20 Günlük Ortalama
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(20).mean(), line=dict(color='#00ADB5', width=1.5), name="20G Ort"))
                
                fig.update_layout(
                    title=f"{search} - 6 Aylık Fiyat Hareketi",
                    template="plotly_dark",
                    xaxis_rangeslider_visible=False,
                    height=500,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
                [Image of an interactive candlestick stock chart with moving average lines and price volume bars]
                
            with t_bilanco:
                st.subheader("Dönemsel Bilanço")
                bs = ticker.balance_sheet
                if not bs.empty: st.dataframe(bs, use_container_width=True)
                else: st.info("Bilanço verisi çekilemedi.")
                
            with t_gelir:
                st.subheader("Gelir Tablosu")
                fin = ticker.financials
                if not fin.empty: st.dataframe(fin, use_container_width=True)
                else: st.info("Gelir tablosu verisi çekilemedi.")
                
            with t_nakit:
                st.subheader("Nakit Akım Tablosu")
                cf = ticker.cashflow
                if not cf.empty: st.dataframe(cf, use_container_width=True)
                else: st.info("Nakit akım verisi çekilemedi.")
                
        else:
            st.error("⚠️ Geçersiz hisse kodu veya veri sağlayıcı (Yahoo Finance) geçici olarak yanıt vermiyor.")

# --- SAYFA 3: PORTFÖY & YÖNETİM (ADMIN) ---
elif st.session_state.page == "Portföy & Yönetim":
    if not st.session_state.user:
        st.error("🔒 Bu sayfayı görüntülemek için giriş yapmalısınız.")
    else:
        st.header("💼 Stratejik Portföy Yönetimi")
        
        # Mermi Yönetimi
        with st.expander("💰 Mermi (Nakit) Girişi Yap", expanded=False):
            with st.form("add_cash"):
                miktar = st.number_input("Eklenecek Tutar (TL)", min_value=0.0)
                if st.form_submit_button("Sisteme İşle"):
                    st.session_state.history.append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Miktar": miktar})
                    st.success("Mermi eklendi!")
                    st.rerun()
        
        # Portföy Hesaplamaları
        eklenen_nakit = sum([i['Miktar'] for i in st.session_state.history])
        tp2_bakiye = 9959.49 + eklenen_nakit
        
        # Senin Hisselerin
        portfoy = [
            {"Hisse": "GENKM", "Lot": 85, "Maliyet": 13.00},
            {"Hisse": "NUHCM", "Lot": 25, "Maliyet": 280.00},
            {"Hisse": "TOASO", "Lot": 12, "Maliyet": 300.00}
        ]
        
        toplam_hisse_degeri = 0
        analiz_tablosu = []
        
        for p in portfoy:
            try:
                son_fiyat = yf.Ticker(f"{p['Hisse']}.IS").fast_info.last_price
                guncel_deger = son_fiyat * p['Lot']
                toplam_hisse_degeri += guncel_deger
                kar_tl = guncel_deger - (p['Maliyet'] * p['Lot'])
                kar_yuzde = (kar_tl / (p['Maliyet'] * p['Lot'])) * 100
                
                analiz_tablosu.append({
                    "Varlık": p['Hisse'],
                    "Maliyet": f"{p['Maliyet']:.2f} TL",
                    "Güncel Fiyat": f"{son_fiyat:.2f} TL",
                    "Toplam Değer": f"{guncel_deger:,.2f} TL",
                    "Kâr/Zarar": f"{kar_tl:,.2f} TL (%{kar_yuzde:.2f})"
                })
            except: continue
            
        toplam_varlik = toplam_hisse_degeri + tp2_bakiye
        
        # Üst Özet
        st.markdown(f"### 🎯 100K Hedef İlerlemesi: %{(toplam_varlik/100000)*100:.2f}")
        st.progress(min(toplam_varlik/100000, 1.0))
        
        col_v1, col_v2, col_v3 = st.columns(3)
        col_v1.metric("Toplam Net Varlık", f"{toplam_varlik:,.2f} TL")
        col_v2.metric("Hisse Senedi Büyüklüğü", f"{toplam_hisse_degeri:,.2f} TL")
        col_v3.metric("Yatırım Fonu (TP2)", f"{tp2_bakiye:,.2f} TL")
        
        st.markdown("---")
        
        # Varlık Dağılımı (Donut Chart) ve Tablo
        col_tab, col_grafik = st.columns([1.5, 1])
        
        with col_tab:
            st.subheader("Açık Pozisyonlar")
            df_port = pd.DataFrame(analiz_tablosu)
            if not df_port.empty:
                # Renklendirme fonksiyonu
                def color_pnl(val):
                    if isinstance(val, str) and 'TL' in val and '%' in val:
                        color = '#00E676' if not '-' in val else '#FF1744'
                        return f'color: {color}; font-weight: bold;'
                    return ''
                st.dataframe(df_port.style.applymap(color_pnl, subset=['Kâr/Zarar']), use_container_width=True, hide_index=True)
                
        with col_grafik:
            st.subheader("Dağılım")
            fig = px.pie(values=[toplam_hisse_degeri, tp2_bakiye], names=['Hisseler', 'Fon (TP2)'], 
                         hole=0.6, color_discrete_sequence=['#00ADB5', '#333333'])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            [Image of a financial portfolio treemap visualization showing stock weights and performance]
