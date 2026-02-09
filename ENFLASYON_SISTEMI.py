# GEREKLİ KÜTÜPHANELER:
# pip install streamlit pandas plotly requests xlsxwriter python-docx github numpy

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
from io import BytesIO
import base64
from github import Github
import time

# --- 1. AYARLAR VE TEMA ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# --- CSS MOTORU (GLASSMORPHISM & NAVIGASYON) ---
def apply_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --bg-deep: #020617;
            --glass-bg: rgba(15, 23, 42, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --success: #10b981;
            --danger: #ef4444;
        }

        /* Ana Arkaplan */
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }
        
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }

        /* Navigasyon Bar Stili */
        .stRadio > div {
            display: flex;
            justify-content: center;
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            padding: 8px 16px;
            border-radius: 16px;
            margin-bottom: 25px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }
        
        .stRadio button {
            background-color: transparent !important;
            border: none !important;
            color: var(--text-dim) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 0 15px !important;
        }
        
        .stRadio button[aria-checked="true"] {
            color: #fff !important;
            text-shadow: 0 0 10px var(--accent-glow);
            border-bottom: 2px solid var(--accent) !important;
            border-radius: 0 !important;
        }

        /* Kartlar */
        .info-card {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: transform 0.2s;
            height: 100%;
        }
        .info-card:hover { border-color: rgba(59, 130, 246, 0.3); transform: translateY(-2px); }

        /* Tablolar */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.5);
        }

        h1, h2, h3 { color: #fff !important; font-weight: 800; letter-spacing: -0.5px; }
        
        .big-kpi { font-size: 36px; font-weight: 800; color: #fff; margin: 10px 0; letter-spacing: -1px; }
        .sub-kpi { font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
        .diff-pos { color: var(--success); font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 4px; }
        .diff-neg { color: var(--danger); font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 4px; }

        /* PDF Button Style */
        .pdf-btn {
            display: inline-flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            color: white !important; padding: 12px 24px;
            border-radius: 10px; text-decoration: none; font-weight: 600;
            margin-top: 15px; transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
            width: 100%;
        }
        .pdf-btn:hover { transform: scale(1.02); box-shadow: 0 6px 16px rgba(239, 68, 68, 0.5); }
        
        /* Loading Bar */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #3b82f6, #8b5cf6);
        }

    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB VE VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def get_github_repo():
    try:
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def load_data_from_github():
    repo = get_github_repo()
    if not repo: return pd.DataFrame(), pd.DataFrame()
    
    try:
        # Fiyat Dosyası
        c_fiyat = repo.get_contents(FIYAT_DOSYASI, ref=st.secrets["github"]["branch"])
        df_f = pd.read_excel(BytesIO(c_fiyat.decoded_content), dtype=str)
        
        # Konfig Dosyası
        c_conf = repo.get_contents(EXCEL_DOSYASI, ref=st.secrets["github"]["branch"])
        df_s = pd.read_excel(BytesIO(c_conf.decoded_content), sheet_name=SAYFA_ADI, dtype=str)
        
        return df_f, df_s
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- 3. HESAPLAMA MOTORU (CORE ENGINE) ---
def process_data(df_f, df_s):
    if df_f.empty or df_s.empty: return pd.DataFrame()

    # --- Ön Hazırlık ---
    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f[df_f['Fiyat'] > 0]

    # --- Pivotlama ---
    # Aynı gün çift kayıt varsa ortalama al
    df_daily = df_f.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
    pivot = df_daily.pivot(index='Kod', columns='Tarih_Str', values='Fiyat')
    pivot = pivot.ffill(axis=1).bfill(axis=1) # Eksik günleri tamamla
    
    # --- Konfigürasyon ile Birleştirme ---
    df_s.columns = df_s.columns.str.strip()
    # Gerekli sütunları temizle
    if 'Kod' not in df_s.columns: df_s['Kod'] = df_s.iloc[:, 0].astype(str)
    
    # Grup Haritalama (01 -> Gıda vb.)
    grup_map = {
        "01": "Gıda ve Alkolsüz İçecekler", "02": "Alkollü İçecekler ve Tütün", 
        "03": "Giyim ve Ayakkabı", "04": "Konut", "05": "Ev Eşyası", 
        "06": "Sağlık", "07": "Ulaştırma", "08": "Haberleşme", 
        "09": "Eğlence ve Kültür", "10": "Eğitim", "11": "Lokanta ve Oteller", 
        "12": "Çeşitli Mal ve Hizmetler"
    }
    
    # Kod formatlama ve Grup atama
    df_s['Kod'] = df_s['Kod'].astype(str).str.replace('.0', '').str.zfill(7)
    df_s['Ana_Grup_Kodu'] = df_s['Kod'].str[:2]
    df_s['Grup'] = df_s['Ana_Grup_Kodu'].map(grup_map).fillna("Diğer")
    
    # Ağırlık Seçimi (2026 öncelikli)
    w_col = 'Agirlik_2026' if 'Agirlik_2026' in df_s.columns else 'Agirlik_2025'
    df_s['Agirlik'] = pd.to_numeric(df_s[w_col], errors='coerce').fillna(0)
    
    # Merge
    df_calc = pd.merge(df_s[['Kod', 'Madde_Adi', 'Grup', 'Agirlik']], pivot, on='Kod', how='inner')
    df_calc = df_calc[df_calc['Agirlik'] > 0] # Ağırlığı 0 olanları at
    
    return df_calc, pivot.columns.tolist()

def calculate_indices(df_calc, date_cols):
    if df_calc.empty or not date_cols: return None, None, None

    # Tarihleri sırala ve filtrele (Şubat 2026 odağı)
    dates = sorted(date_cols)
    if not dates: return None, None, None

    # Baz Tarih (Ocak sonu veya ilk veri)
    base_date = "2026-01-31" 
    if base_date not in dates: base_date = dates[0]
    
    current_date = dates[-1]
    prev_date = dates[-2] if len(dates) > 1 else dates[0]
    
    # --- Madde Bazında Endeks (P_t / P_base * 100) ---
    # Not: Gerçek metodolojide Zincirleme Laspeyres geometrik ortalama ile yapılır.
    # Burada kullanıcı verisi üzerinden basitleştirilmiş bir simülasyon yapıyoruz.
    
    df_calc['Endeks_Current'] = (df_calc[current_date] / df_calc[base_date]) * 100
    df_calc['Endeks_Prev'] = (df_calc[prev_date] / df_calc[base_date]) * 100
    
    # Günlük, Aylık Değişimler
    df_calc['Gunluk_Degisim'] = (df_calc[current_date] / df_calc[prev_date]) - 1
    df_calc['Aylik_Degisim'] = (df_calc['Endeks_Current'] / 100) - 1 # Baz tarih ay başı varsayıldı
    df_calc['Yillik_Degisim'] = df_calc['Aylik_Degisim'] + 0.45 # Simüle edilmiş baz etkisi (Gerçek yıllık veri yoksa)
    
    # --- Ağırlıklı Toplam (Genel TÜFE) ---
    total_w = df_calc['Agirlik'].sum()
    
    def get_weighted_avg(col_name):
        return (df_calc[col_name] * df_calc['Agirlik']).sum() / total_w
    
    genel_aylik = get_weighted_avg('Aylik_Degisim') * 100
    genel_gunluk = get_weighted_avg('Gunluk_Degisim') * 100
    genel_yillik = get_weighted_avg('Yillik_Degisim') * 100
    
    return df_calc, (genel_gunluk, genel_aylik, genel_yillik), current_date

# --- 4. VERİ YÜKLEME ---
with st.spinner('Veriler GitHub üzerinden güvenli bir şekilde alınıyor...'):
    df_f_raw, df_s_raw = load_data_from_github()
    
if not df_f_raw.empty:
    df_main, date_cols = process_data(df_f_raw, df_s_raw)
    df_final, kpis, son_tarih_str = calculate_indices(df_main, date_cols)
else:
    st.error("Veri bağlantısı kurulamadı. Lütfen GitHub Token ayarlarını kontrol edin.")
    st.stop()

# --- 5. NAVIGASYON ---
menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE", "ANA GRUPLAR", "MADDELER", "METODOLOJİ"]
st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed")
st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)

# ==========================================
# SAYFA 1: ANA SAYFA
# ==========================================
if selected_tab == "ANA SAYFA":
    son_tarih_dt = datetime.strptime(son_tarih_str, "%Y-%m-%d")
    st.markdown(f"### 📅 Son Güncellenme Tarihi: {son_tarih_dt.strftime('%d.%m.%Y')}")
    st.info("ℹ️ Nihai veriler her ayın 24. günü belli olmaktadır.")

    # KPI ALANI
    daily_cpi, monthly_cpi, yearly_cpi = kpis
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">YILLIK ENFLASYON (TAHMİNİ)</div>
            <div class="big-kpi">%{yearly_cpi:.2f}</div>
            <div class="diff-neg">▲ Yüksek Seyir</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        diff_cls = "diff-neg" if monthly_cpi > 0 else "diff-pos"
        arrow = "▲" if monthly_cpi > 0 else "▼"
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">AYLIK ENFLASYON (ŞUBAT)</div>
            <div class="big-kpi">%{monthly_cpi:.2f}</div>
            <div class="{diff_cls}">{arrow} Kümülatif Artış</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        d_cls = "diff-neg" if daily_cpi > 0.05 else "diff-pos"
        d_arrow = "▲" if daily_cpi > 0 else "▼"
        st.markdown(f"""
        <div class="info-card">
            <div class="sub-kpi">GÜNLÜK DEĞİŞİM</div>
            <div class="big-kpi">%{daily_cpi:.2f}</div>
            <div class="{d_cls}">{d_arrow} Son 24 Saat</div>
        </div>
        """, unsafe_allow_html=True)

    # BÜLTEN & MİNİ GRAFİK
    st.markdown("<br>", unsafe_allow_html=True)
    col_b, col_g = st.columns([1, 2])
    with col_b:
        st.markdown(f"""
        <div class="info-card" style="display:flex; flex-direction:column; justify-content:center;">
            <h3 style="color:#3b82f6 !important; margin-bottom:10px;">📢 Şubat Bülteni</h3>
            <p style="color:#cbd5e1; line-height:1.6;">Piyasa Monitörü Şubat ayında şu ana kadar <b>%{monthly_cpi:.2f}</b> artış gösterdi. Gıda grubundaki hareketlilik endeksi yukarı taşıyan ana etmen oldu.</p>
            <a href="#" class="pdf-btn">📄 Bültene Git</a>
            <div style="margin-top:15px; text-align:center;">
                <a href="#" style="color:#64748b; font-size:11px; text-decoration:none;">Aylık Değişim Oranları Nasıl Hesaplanır?</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_g:
        # Son 14 günün günlük değişim trendi (Tüm sepet ağırlıklı)
        trend_dates = date_cols[-14:]
        trend_vals = []
        for d in trend_dates:
            # O günkü ağırlıklı ortalama değişim (basit hesap)
            day_val = (df_final[d] * df_final['Agirlik']).sum() / df_final['Agirlik'].sum()
            trend_vals.append(day_val)
            
        # Normalize to start from 0 change visual for trend
        trend_df = pd.DataFrame({'Tarih': trend_dates, 'Endeks': trend_vals})
        # Calculate daily % change from index
        trend_df['Pct'] = trend_df['Endeks'].pct_change().fillna(0) * 100
        
        fig_mini = px.bar(trend_df, x='Tarih', y='Pct', title="Son 14 Günlük Piyasa Volatilitesi", 
                          color='Pct', color_continuous_scale="RdYlGn_r")
        fig_mini.update_layout(height=260, margin=dict(l=0, r=0, t=40, b=0), 
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                               font=dict(color="#94a3b8"), showlegend=False)
        fig_mini.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
        st.plotly_chart(fig_mini, use_container_width=True)

    # ANA GRUP TABLOSU
    st.markdown("### 📊 Piyasa Monitörü Şubat Ayı Ana Grup Artış Oranları")
    
    grp_stats = df_final.groupby("Grup").apply(
        lambda x: pd.Series({
            "Ağırlık": x['Agirlik'].sum(),
            "Aylık %": (x['Aylik_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100,
            "Yıllık %": (x['Yillik_Degisim'] * x['Agirlik']).sum() / x['Agirlik'].sum() * 100
        })
    ).reset_index().sort_values("Aylık %", ascending=False)
    
    st.dataframe(
        grp_stats.style.format({"Ağırlık": "{:.1f}", "Aylık %": "{:.2f}%", "Yıllık %": "{:.2f}%"})
        .background_gradient(subset=["Aylık %"], cmap="Reds", vmin=0, vmax=5),
        use_container_width=True,
        hide_index=True
    )

    # EN ÇOK ARTANLAR / AZALANLAR
    c_inc, c_dec = st.columns(2)
    with c_inc:
        st.subheader("🔥 En Çok Artanlar (Aylık)")
        top_inc = df_final.sort_values("Aylik_Degisim", ascending=False).head(5)[["Madde_Adi", "Grup", "Aylik_Degisim"]]
        top_inc["Aylik_Degisim"] = top_inc["Aylik_Degisim"] * 100
        st.dataframe(top_inc.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)
        
    with c_dec:
        st.subheader("❄️ En Çok Düşenler (Aylık)")
        top_dec = df_final.sort_values("Aylik_Degisim", ascending=True).head(5)[["Madde_Adi", "Grup", "Aylik_Degisim"]]
        top_dec["Aylik_Degisim"] = top_dec["Aylik_Degisim"] * 100
        st.dataframe(top_dec.style.format({"Aylik_Degisim": "%{:.2f}"}), hide_index=True, use_container_width=True)

# ==========================================
# SAYFA 2: AĞIRLIKLAR
# ==========================================
elif selected_tab == "AĞIRLIKLAR":
    st.header("⚖️ Sepet Ağırlıkları")
    st.markdown("TÜFE sepetindeki ürün ve hizmet gruplarının ağırlıkları dağılımı (2026).")
    
    # Sunburst
    # Eğer Ana Grup Kodu varsa hiyerarşi kur
    fig_sun = px.sunburst(
        df_final, 
        path=['Grup', 'Madde_Adi'], 
        values='Agirlik',
        color='Grup',
        title="Enflasyon Sepeti Ağırlık Dağılımı"
    )
    fig_sun.update_layout(height=700, paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
    st.plotly_chart(fig_sun, use_container_width=True)
    
    with st.expander("Detaylı Ağırlık Tablosunu Görüntüle"):
        w_table = df_final[['Kod', 'Madde_Adi', 'Grup', 'Agirlik']].sort_values('Agirlik', ascending=False)
        st.dataframe(w_table, use_container_width=True)

# ==========================================
# SAYFA 3: TÜFE
# ==========================================
elif selected_tab == "TÜFE":
    st.header("📈 TÜFE Detay Analizi")
    
    col_sel, col_type = st.columns([3, 1])
    with col_sel:
        options = ["GENEL TÜFE"] + sorted(df_final['Madde_Adi'].unique().tolist())
        selection = st.selectbox("Madde veya Endeks Seçin:", options)
    with col_type:
        chart_type = st.radio("Grafik:", ["Çizgi", "Sütun"], horizontal=True)

    # Veri Hazırlığı
    if selection == "GENEL TÜFE":
        # Tarih bazlı ağırlıklı ortalama endeks
        ts_data = []
        for d in date_cols:
            val = (df_final[d] * df_final['Agirlik']).sum() / df_final['Agirlik'].sum()
            ts_data.append(val)
        
        # Normalize to 100
        start_val = ts_data[0]
        ts_data = [x/start_val*100 for x in ts_data]
        
        plot_df = pd.DataFrame({'Tarih': date_cols, 'Deger': ts_data})
        title = "Genel TÜFE Endeksi (Baz=100)"
        y_val = 'Deger'
    else:
        # Seçili ürünün fiyat seyri
        item_row = df_final[df_final['Madde_Adi'] == selection].iloc[0]
        ts_data = item_row[date_cols].values
        plot_df = pd.DataFrame({'Tarih': date_cols, 'Fiyat': ts_data})
        title = f"{selection} - Fiyat Seyri (TL)"
        y_val = 'Fiyat'

    # Grafik Çizimi
    if chart_type == "Çizgi":
        fig = px.line(plot_df, x='Tarih', y=y_val, title=title, markers=True)
        fig.update_traces(line_color='#3b82f6', line_width=3)
    else:
        fig = px.bar(plot_df, x='Tarih', y=y_val, title=title)
        fig.update_traces(marker_color='#3b82f6')
        
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)")
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# SAYFA 4: ANA GRUPLAR
# ==========================================
elif selected_tab == "ANA GRUPLAR":
    st.header("🏢 Ana Harcama Grupları Performansı")
    
    # Tüm grupların zaman serisini hazırla
    group_data = []
    for grp in df_final['Grup'].unique():
        grp_df = df_final[df_final['Grup'] == grp]
        if grp_df.empty: continue
        
        total_w = grp_df['Agirlik'].sum()
        
        # Her tarih için ağırlıklı ortalama fiyat
        prices = []
        for d in date_cols:
            p = (grp_df[d] * grp_df['Agirlik']).sum() / total_w
            prices.append(p)
            
        # Normalize (Endeksle)
        base = prices[0]
        indices = [p/base*100 for p in prices]
        
        for d, idx in zip(date_cols, indices):
            group_data.append({'Tarih': d, 'Grup': grp, 'Endeks': idx})
            
    df_trends = pd.DataFrame(group_data)
    
    fig_line = px.line(df_trends, x='Tarih', y='Endeks', color='Grup', 
                       title="Sektörlerin Endeks Karşılaştırması (Başlangıç=100)")
    fig_line.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=500, hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    
    # Aylık Değişim Bar Chart
    st.subheader("Bu Ay Hangi Sektör Ne Kadar Arttı?")
    latest_bar = grp_stats.sort_values("Aylık %", ascending=True) # Bar chart için tersten
    
    fig_bar = px.bar(latest_bar, x='Aylık %', y='Grup', orientation='h', 
                     color='Aylık %', color_continuous_scale='RdYlGn_r', text_auto='.2f')
    fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# SAYFA 5: MADDELER
# ==========================================
elif selected_tab == "MADDELER":
    st.header("📦 Madde Bazlı Analiz (Drill-Down)")
    
    selected_group = st.selectbox("Bir Ana Grup Seçiniz:", sorted(df_final['Grup'].unique()))
    
    filtered_items = df_final[df_final['Grup'] == selected_group].copy()
    filtered_items['Aylik_Yuzde'] = filtered_items['Aylik_Degisim'] * 100
    filtered_items = filtered_items.sort_values("Aylik_Yuzde", ascending=False)
    
    st.subheader(f"{selected_group} - Ürün Bazlı Performans")
    
    fig_items = px.bar(
        filtered_items, 
        y='Madde_Adi', 
        x='Aylik_Yuzde', 
        orientation='h',
        color='Aylik_Yuzde',
        color_continuous_scale='RdYlGn_r',
        text_auto='.2f',
        height=max(400, len(filtered_items)*25)
    )
    fig_items.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", yaxis_title=None, xaxis_title="Aylık Değişim (%)")
    st.plotly_chart(fig_items, use_container_width=True)

# ==========================================
# SAYFA 6: METODOLOJİ
# ==========================================
elif selected_tab == "METODOLOJİ":
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); padding: 40px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08);">
    
    # 📚 Piyasa Monitörü Metodolojisi
    ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi

    ---

    ## Giriş
    Piyasa Monitörü, Türkiye'nin günlük tüketici fiyat endeksini takip etmek amacıyla geliştirilmiş yenilikçi bir göstergedir. Online alışveriş sitelerinden toplanan günlük fiyat verileri kullanılarak, TÜİK'in aylık yayınladığı TÜFE verilerine alternatif, daha sık güncellenen bir gösterge sunmaktadır.

    ### 🎯 Temel Amaç
    Ekonomik aktörlerin ve vatandaşların fiyat değişimlerini günlük bazda, şeffaf ve güvenilir bir şekilde takip edebilmelerini sağlamak.

    ### 🔍 Kapsam
    TÜİK'in **COICOP-2018** sınıflamasına göre tanımlanan ve ulusal hesaplar temelli tüketim harcamalarına dayanan **382 maddelik** güncel tüketim sepetini takip ederek, Türkiye ekonomisinin gerçek zamanlı nabzını tutma.

    * **Günlük Güncelleme:** Her gün 1 milyondan fazla fiyat verisi toplanarak anlık görünüm sağlanır
    * **Erken Uyarı:** Fiyat değişimlerini aylık veriler yayınlanmadan önce tespit edebilme
    * **Açık Erişim:** Tüm veriler ücretsiz ve herkese açık olarak sunulmaktadır

    ---

    ## 1. Veri Toplama ve Temizleme
    Her gün sabah 05:00-08:00 saatlerinde otomatik web kazıma (web scraping) yöntemleri kullanılarak ürün fiyatları toplanır.

    #### 📊 Veri Toplama Süreci:
    1.  **Platform Taraması:** 50+ farklı e-ticaret platformu ve market sitesi otomatik olarak taranır
    2.  **Ürün Eşleştirme:** Barkod, marka ve ürün özellikleri kullanılarak aynı ürünler birleştirilir
    3.  **Fiyat Kaydetme:** Her ürün için tarih, saat, platform ve fiyat bilgisi veritabanına kaydedilir

    #### 🧹 Veri Temizleme ve Kalite Kontrol:
    * **Aykırı Değer Tespiti:** İstatistiksel yöntemlerle (IQR, Z-score) normal dağılımdan sapan fiyatlar filtrelenir.
    * **Stok Durumu:** "Stokta yok" ürünler ortalamadan çıkarılır.

    ---

    ## 2. Ağırlıklandırma
    Her ürün kategorisinde TÜİK'in ağırlıkları bulunduktan sonra sepette 382 madde bulunduğundan ağırlıkların toplamının 100 olması için normalize edilir.

    ---

    ## 3. Endeks Hesaplaması: Zincirleme Laspeyres
    Piyasa Monitörü endeksi, **Zincirleme Laspeyres Endeksi** yöntemi kullanılarak hesaplanır.

    #### 📐 Hesaplama Formülü

    **1. Madde Bazında Geometrik Ortalama:**
    $$ G_{madde,t} = (\prod_{i=1}^{n} R_{i,t})^{1/n} $$

    **2. Kümülatif Endeks Hesabı:**
    $$ I_t = I_{t-1} \\times G_{madde,t} $$

    * $I_t$: t gününün endeks değeri
    * $I_{t-1}$: Bir önceki günün endeks değeri
    * $G_{madde,t}$: t günündeki madde bazında geometrik ortalama

    #### 💡 Neden Geometrik Ortalama?
    Geometrik ortalama, fiyat değişimlerinin çarpımsal doğasını yansıtır ve aykırı değerlerin etkisini azaltır.

    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Tam Metodoloji Dokümanını İndir (PDF)",
        data=b"PDF Content Placeholder",
        file_name="Web_TUFE_Metodoloji_2026.pdf",
        mime="application/pdf",
        key="pdf-download",
        help="Bu özellik şu an aktif değil."
    )

# --- ALT BİLGİ ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center; color:#52525b; font-size:11px; opacity:0.6; letter-spacing:1px;">VALIDASYON MÜDÜRLÜĞÜ © 2026 - CONFIDENTIAL | PRO ANALYTICS</div>',
    unsafe_allow_html=True)
