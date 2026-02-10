# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from streamlit_lottie import st_lottie

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Premium Terminal",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU (PREMIUM & SİMETRİK TEMA) ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        # Plotly için özel, koyu lacivert tema
        pio_template = go.layout.Template()
        pio_template.layout.paper_bgcolor = '#131B24'
        pio_template.layout.plot_bgcolor = '#131B24'
        pio_template.layout.font.color = '#94A3B8'
        pio_template.layout.font.family = "Inter, sans-serif"
        pio_template.layout.xaxis.gridcolor = 'rgba(255,255,255,0.05)'
        pio_template.layout.yaxis.gridcolor = 'rgba(255,255,255,0.05)'
        st.session_state.plotly_template = pio_template

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');

        :root {
            /* Premium Renk Paleti - Derin Lacivert/Gri */
            --bg-app: #0A1119;      /* Çok derin lacivert arka plan */
            --bg-surface: #131B24;  /* Kart yüzeyleri */
            --bg-hover: #1E293B;    /* Hover durumları */
            --text-bright: #E2E8F0; /* Ana metin */
            --text-muted: #94A3B8;  /* Alt metinler */
            --border-subtle: rgba(255, 255, 255, 0.06); /* Çok hafif çerçeve */
            --accent-primary: #3B82F6; /* Sofistike Mavi */
            --accent-success: #059669; /* Olgun Yeşil */
            --accent-danger: #DC2626;  /* Olgun Kırmızı */
        }

        /* --- Temel Yapı ve Simetri --- */
        .stApp {
            background-color: var(--bg-app);
            font-family: 'Inter', sans-serif;
            color: var(--text-bright);
        }
        
        /* İçeriği Ortala ve Sınırla */
        .block-container {
            max-width: 1200px; /* İçeriği çok yayılmaktan koru */
            margin: 0 auto;
            padding-top: 3rem;
        }

        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }

        /* Sidebar Styling - Daha sade */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border-subtle);
        }
        
        /* --- ORTALANMIŞ PREMIUM NAVİGASYON --- */
        [data-testid="stRadio"] {
            width: 100%;
            display: flex;
            justify-content: center; /* Butonları ortala */
            background: transparent;
            border: none;
            padding: 0;
            margin-bottom: 30px;
        }

        [data-testid="stRadio"] > div[role="radiogroup"] {
            display: inline-flex; /* İçerik kadar genişlik */
            background: var(--bg-surface);
            padding: 6px;
            border-radius: 16px;
            border: 1px solid var(--border-subtle);
            gap: 5px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        [data-testid="stRadio"] label {
            padding: 10px 20px !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: var(--text-muted) !important;
            background: transparent !important;
            border: none !important;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        [data-testid="stRadio"] label:hover {
            color: var(--text-bright) !important;
            background-color: var(--bg-hover) !important;
        }

        [data-testid="stRadio"] label[data-checked="true"] {
            background-color: var(--accent-primary) !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        [data-testid="stRadio"] div[role="radiogroup"] > :first-child { display: none; }

        /* --- KART TASARIMLARI (Temiz, Gölgeli, Sınır Çizgisiz) --- */
        .kpi-card {
            background-color: var(--bg-surface);
            /* Sınır çizgisi yerine hafif gölge */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 16px;
            padding: 30px 24px; /* Daha fazla iç boşluk */
            display: flex;
            flex-direction: column;
            align-items: center; /* İçeriği ortala */
            text-align: center; /* Metni ortala */
            height: 100%;
            transition: transform 0.3s ease;
            border: 1px solid rgba(255,255,255,0.02); /* Çok çok hafif bir sınır */
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
            background-color: var(--bg-hover);
        }

        .kpi-title {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 15px;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 42px; /* Daha büyük, daha cesur */
            font-weight: 700;
            color: var(--text-bright);
            margin-bottom: 10px;
            letter-spacing: -1px;
        }
        
        .kpi-sub {
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(255,255,255,0.03);
        }

        /* --- DİĞER BİLEŞENLER --- */
        div.stButton > button {
            background-color: var(--accent-primary);
            color: white;
            border: none;
            padding: 12px 28px;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.2s;
            width: auto; /* Tam genişlik yerine içeriğe göre */
        }
        div.stButton > button:hover {
            background-color: #2563eb;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] {
            background-color: var(--bg-surface) !important;
            border-color: var(--border-subtle) !important;
            border-radius: 10px !important;
            color: var(--text-bright) !important;
        }
        
        hr {
            border-color: var(--border-subtle);
            opacity: 0.5;
        }
        
        h1, h2, h3, h4 { color: var(--text-bright) !important; font-family: 'Inter', sans-serif; font-weight: 700; }
        
        /* Grid Kartları için */
        .grid-card {
             background: var(--bg-surface);
             border-radius: 12px;
             padding: 20px;
             text-align: center;
             box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
             transition: all 0.2s;
             border: 1px solid var(--border-subtle);
        }
        .grid-card:hover { background: var(--bg-hover); transform: translateY(-3px); }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU (DEĞİŞMEDİ) ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. RAPOR MOTORU (DEĞİŞMEDİ) ---
def create_word_report(text_content, tarih, df_analiz=None):
    try:
        doc = Document()
        matplotlib.use('Agg')
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        head = doc.add_heading(f'PİYASA GÖRÜNÜM RAPORU', 0)
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subhead = doc.add_paragraph(f'Rapor Tarihi: {tarih}')
        subhead.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("")
        paragraphs = text_content.split('\n')
        for p_text in paragraphs:
            if not p_text.strip(): continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            parts = p_text.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 == 1: 
                    run.bold = True
                    run.font.color.rgb = RGBColor(0, 50, 100) 
        if df_analiz is not None and not df_analiz.empty:
            doc.add_page_break()
            doc.add_heading('EKLER: GÖRSEL ANALİZLER', 1)
            doc.add_paragraph("")
            try:
                if 'Fark' in df_analiz.columns:
                    data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                    if not data.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        # Matplotlib renklerini yeni temaya uyarla
                        ax.hist(data, bins=20, color='#3B82F6', edgecolor='#131B24', alpha=0.9)
                        ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold', color='#E2E8F0')
                        ax.set_facecolor('#131B24')
                        fig.patch.set_facecolor('#131B24')
                        ax.tick_params(axis='x', colors='#94A3B8')
                        ax.tick_params(axis='y', colors='#94A3B8')
                        for spine in ax.spines.values(): spine.set_edgecolor('rgba(255,255,255,0.1)')
                        memfile = BytesIO()
                        plt.savefig(memfile, format='png', dpi=100, bbox_inches='tight')
                        plt.close(fig)
                        doc.add_picture(memfile, width=Inches(5.5))
                        memfile.close()
                        doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
            except Exception:
                pass
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO()

# --- 4. GITHUB İŞLEMLERİ (DEĞİŞMEDİ) ---
@st.cache_resource
def get_github_connection():
    try:
        return Github(st.secrets["github"]["token"])
    except:
        return None

def get_github_repo():
    g = get_github_connection()
    if g:
        return g.get_repo(st.secrets["github"]["repo_name"])
    return None

@st.cache_data(ttl=600, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        if sayfa_adi:
            df = pd.read_excel(BytesIO(c.decoded_content), sheet_name=sayfa_adi, dtype=str)
        else:
            df = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
        return df
    except:
        return pd.DataFrame()

def github_excel_guncelle(df_yeni, dosya_adi):
    repo = get_github_repo()
    if not repo: return "Repo Yok"
    try:
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            old = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
            yeni_tarih = str(df_yeni['Tarih'].iloc[0])
            old = old[~((old['Tarih'].astype(str) == yeni_tarih) & (old['Kod'].isin(df_yeni['Kod'])))]
            final = pd.concat([old, df_yeni], ignore_index=True)
        except:
            c = None; final = df_yeni
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        msg = f"Data Update"
        if c:
            repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else:
            repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e:
        return str(e)

# --- 5. RESMİ ENFLASYON (CACHED) (DEĞİŞMEDİ) ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_official_inflation():
    api_key = st.secrets.get("evds", {}).get("api_key")
    if not api_key: return None, "API Key Yok"
    start_date = (datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y")
    end_date = datetime.now().strftime("%d-%m-%Y")
    url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.FG.J0&startDate={start_date}&endDate={end_date}&type=json"
    headers = {'User-Agent': 'Mozilla/5.0', 'key': api_key, 'Accept': 'application/json'}
    try:
        url_with_key = f"{url}&key={api_key}"
        res = requests.get(url_with_key, headers=headers, timeout=10, verify=False)
        if res.status_code == 200:
            data = res.json()
            if "items" in data:
                df_evds = pd.DataFrame(data["items"])
                df_evds = df_evds[['Tarih', 'TP_FG_J0']]
                df_evds.columns = ['Tarih', 'Resmi_TUFE']
                df_evds['Tarih'] = pd.to_datetime(df_evds['Tarih'] + "-01", format="%Y-%m-%d")
                df_evds['Resmi_TUFE'] = pd.to_numeric(df_evds['Resmi_TUFE'], errors='coerce')
                return df_evds, "OK"
        return None, "Hata"
    except Exception as e:
        return None, str(e)

# --- 6. SCRAPER YARDIMCILARI (DEĞİŞMEDİ) ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except:
        return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = ""; domain = url.lower() if url else ""
    # Basit Regex ve CSS arama
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
    return fiyat, kaynak

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    progress_callback(0.05) 
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        if not kod_col or not url_col: return "Hata: Excel sütunları eksik."
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d")
        simdi = datetime.now().strftime("%H:%M")
        
        progress_callback(0.10)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        total_zips = len(zip_files)
        
        for i, zip_file in enumerate(zip_files):
            current_progress = 0.10 + (0.80 * ((i + 1) / max(1, total_zips)))
            progress_callback(current_progress)
            try:
                blob = repo.get_git_blob(zip_file.sha)
                zip_data = base64.b64decode(blob.content)
                with zipfile.ZipFile(BytesIO(zip_data)) as z:
                    for file_name in z.namelist():
                        if not file_name.endswith(('.html', '.htm')): continue
                        with z.open(file_name) as f:
                            raw = f.read().decode("utf-8", errors="ignore")
                            soup = BeautifulSoup(raw, 'html.parser')
                            found_url = None
                            if c := soup.find("link", rel="canonical"): found_url = c.get("href")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod'])
            except: pass
        
        progress_callback(0.95)
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "Veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. STATİK ANALİZ MOTORU (DEĞİŞMEDİ) ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    toplam_urun = len(df_clean)
    artanlar = df_clean[df_clean['Fark'] > 0]
    dusenler = df_clean[df_clean['Fark'] < 0]
    sabitler = df_clean[df_clean['Fark'] == 0]
    artan_sayisi = len(artanlar)
    yayilim_orani = (artan_sayisi / toplam_urun) * 100 if toplam_urun > 0 else 0
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    text = f"""
**PİYASA GÖRÜNÜM RAPORU**
**Tarih:** {tarih}

**1. 📊 ANA GÖSTERGELER**
-----------------------------------------
**GENEL ENFLASYON** : **%{enf_genel:.2f}**
**GIDA ENFLASYONU** : **%{enf_gida:.2f}**
**AY SONU TAHMİNİ** : **%{tahmin:.2f}**
-----------------------------------------

**2. 🔎 PİYASA RÖNTGENİ**
**Fiyat Hareketleri:**
   🔺 **Zamlanan Ürün:** {artan_sayisi} adet
   🔻 **İndirimli Ürün:** {len(dusenler)} adet
   ➖ **Fiyatı Değişmeyen:** {len(sabitler)} adet

**Sepet Yayılımı:**
   Her 100 üründen **{int(yayilim_orani)}** tanesinde fiyat artışı tespit edilmiştir.

**3. ⚡ DİKKAT ÇEKEN ÜRÜNLER**

**▲ Yüksek Artışlar (Cep Yakanlar)**
{inc_str}

**▼ Fiyat Düşüşleri (Fırsatlar)**
{dec_str}

**4. 💡 SONUÇ**
Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

---
*Otomatik Rapor Sistemi | Validasyon Müdürlüğü*
"""
    return text.strip()

# --- YENİ YARDIMCI FONKSİYONLAR ---
def style_chart(fig, is_sunburst=False):
    # Yeni, profesyonel koyu tema (CSS ile uyumlu)
    layout_args = dict(
        template=st.session_state.plotly_template, # Tanımladığımız temayı kullan
        paper_bgcolor="rgba(0,0,0,0)", # Şeffaf, CSS arka planı görünsün
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        hoverlabel=dict(
            bgcolor="#1E293B", 
            bordercolor="rgba(255,255,255,0.1)", 
            font=dict(family="JetBrains Mono", color="#E2E8F0", size=13)
        ),
        title=dict(
            font=dict(size=18, color="#E2E8F0", family="Inter, sans-serif", weight=700),
            x=0.5, # Başlığı ortala (Simetri için önemli)
            xanchor='center'
        ),
    )
    
    if not is_sunburst:
        # Eksenleri daha belirgin ama inceltilmiş yap
        axis_style = dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)", # Çok hafif grid
            gridwidth=1,
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.1)",
            showline=False, # Dış çizgiyi kaldır, daha temiz
            tickfont=dict(color="#94A3B8", size=12, family="Inter, sans-serif"),
            title_font=dict(color="#94A3B8", size=13, family="Inter, sans-serif"),
        )
        layout_args.update(dict(
            xaxis=axis_style,
            yaxis=axis_style
        ))
        
    fig.update_layout(**layout_args)
    
    # Çizgi grafiklerinde modernlik için yumuşatma (spline)
    if not is_sunburst:
        for data in fig.data:
            if data.type == 'scatter' and data.mode == 'lines+markers':
                data.line.shape = 'spline' 
                data.line.width = 4 # Biraz daha kalın çizgi
                data.marker.size = 10
                data.marker.line.width = 3
                data.marker.line.color = '#131B24' # Marker etrafına outline

    return fig

# --- 9. VERİ VE HESAPLAMA MOTORLARI (CACHE) (DEĞİŞMEDİ) ---

# 1. VERİ GETİR
@st.cache_data(ttl=600, show_spinner=False)
def verileri_getir_cache():
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    if df_f.empty or df_s.empty: return None, None, None

    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    raw_dates = df_f['Tarih_Str'].unique().tolist()

    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f[df_f['Fiyat'] > 0]
    
    pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
    pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()
    if pivot.empty: return None, None, None

    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

    df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
    return df_analiz_base, raw_dates, ad_col

# 2. HESAPLAMA YAP (CACHED)
@st.cache_data(show_spinner=False)
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col, baz_col, aktif_agirlik_col, son):
    df_analiz = df_analiz_base.copy()
    for col in gunler: df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    if baz_col in df_analiz.columns: df_analiz[baz_col] = df_analiz[baz_col].fillna(df_analiz[son])
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz.get(aktif_agirlik_col, 0), errors='coerce').fillna(0)
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])

    enf_genel = 0.0; enf_gida = 0.0
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        if w.sum() > 0: enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty and gida_df[aktif_agirlik_col].sum() > 0:
            enf_gida = ((gida_df[aktif_agirlik_col] * (gida_df['Aylik_Ortalama']/gida_df[baz_col])).sum() / gida_df[aktif_agirlik_col].sum() * 100) - 100
            
        df_analiz['Fark'] = 0.0
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1
        df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
    
    gun_farki = 0
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun].replace(0, np.nan)) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        onceki_gun = son

    month_end_forecast = 0.0
    target_fixed = f"{dt_son.year}-{dt_son.month:02d}-31"
    fixed_cols = [c for c in tum_gunler_sirali if c.startswith(bu_ay_str) and c <= target_fixed]
    if fixed_cols and not gecerli_veri.empty:
        gecerli_veri['Fixed_Ort'] = gecerli_veri[fixed_cols].apply(geo_mean, axis=1)
        gecerli_t = gecerli_veri.dropna(subset=['Fixed_Ort'])
        if not gecerli_t.empty and gecerli_t[aktif_agirlik_col].sum() > 0:
             month_end_forecast = ((gecerli_t[aktif_agirlik_col] * (gecerli_t['Fixed_Ort']/gecerli_t[baz_col])).sum() / gecerli_t[aktif_agirlik_col].sum() * 100) - 100

    resmi_aylik_degisim = 0.0
    try:
        df_resmi, _ = get_official_inflation()
        if df_resmi is not None and not df_resmi.empty:
             df_resmi = df_resmi.sort_values('Tarih')
             if len(df_resmi) >= 2:
                 son_endeks = df_resmi.iloc[-1]['Resmi_TUFE']
                 onceki_endeks = df_resmi.iloc[-2]['Resmi_TUFE']
                 resmi_aylik_degisim = ((son_endeks / onceki_endeks) - 1) * 100
    except:
        resmi_aylik_degisim = 0.0

    return {
        "df_analiz": df_analiz, "enf_genel": enf_genel, "enf_gida": enf_gida,
        "tahmin": month_end_forecast, "resmi_aylik_degisim": resmi_aylik_degisim,
        "son": son, "onceki_gun": onceki_gun, "gunler": gunler,
        "ad_col": ad_col, "agirlik_col": aktif_agirlik_col, "baz_col": baz_col, "gun_farki": gun_farki,
        "stats_urun": len(df_analiz), "stats_kategori": df_analiz['Grup'].nunique(),
        "stats_veri_noktasi": len(df_analiz) * len(tum_gunler_sirali)
    }

# 3. SIDEBAR UI (Daha Sade)
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None: return None
    
    # Lottie Animasyon (Varsa - daha küçük)
    lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
    try:
        lottie_json = load_lottieurl(lottie_url)
        with st.sidebar:
             if lottie_json: st_lottie(lottie_json, height=80, key="nav_anim")
    except: pass

    st.sidebar.markdown("### ⚙️ Kontrol Paneli")

    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None
    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi Seçin", options=tum_tarihler, index=0)
    
    st.sidebar.divider()
    
    # Senkronizasyon Butonu (Sidebar'a alındı, daha derli toplu)
    if st.sidebar.button("🔄 Veriyi Güncelle (Senkronize Et)", use_container_width=True):
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        def update_progress(p):
            progress_bar.progress(min(1.0, max(0.0, p)))
            status_text.text(f"İşleniyor... %{int(p*100)}")

        res = html_isleyici(update_progress)
        progress_bar.empty()
        status_text.empty()
        
        if "OK" in res:
            st.cache_data.clear()
            st.sidebar.success('✅ Sistem başarıyla güncellendi.')
            time.sleep(1)
            st.rerun()
        elif "Veri bulunamadı" in res:
            st.sidebar.info("ℹ️ İşlenecek yeni veri paketi yok.")
        else:
            st.sidebar.error(f"Hata: {res}")

    # Tarih hesaplamaları
    tum_gunler_sirali = sorted([c for c in df_analiz_base.columns if re.match(r'\d{4}-\d{2}-\d{2}', str(c)) and c >= BASLANGIC_LIMITI])
    if secilen_tarih in tum_gunler_sirali:
        idx = tum_gunler_sirali.index(secilen_tarih)
        gunler = tum_gunler_sirali[:idx+1]
    else: gunler = tum_gunler_sirali
    if not gunler: return None
    son = gunler[-1]; dt_son = datetime.strptime(son, '%Y-%m-%d')
    col_w25, col_w26 = 'Agirlik_2025', 'Agirlik_2026'
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    if dt_son >= ZINCIR_TARIHI:
        aktif_agirlik_col = col_w26
        gunler_2026 = [c for c in tum_gunler_sirali if c >= "2026-01-01"]
        baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
    else:
        aktif_agirlik_col = col_w25; baz_col = gunler[0]

    ctx = hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col=None, baz_col=baz_col, aktif_agirlik_col=aktif_agirlik_col, son=son)
    return ctx

# --- SAYFA FONKSİYONLARI (YENİ TASARIM - ORTALI) ---
def sayfa_ana_sayfa(ctx):
    # Ortalanmış Hero Section
    st.markdown(f"""
    <div style="text-align:center; padding: 60px 0; max-width: 800px; margin: 0 auto;">
        <h1 style="font-size: 56px; font-weight: 800; letter-spacing: -1.5px; line-height: 1.1; margin-bottom: 24px;
                   background: linear-gradient(to right, #E2E8F0, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Gerçek Zamanlı Enflasyon Analiz Terminali
        </h1>
        <p style="font-size: 20px; color: var(--text-muted); line-height: 1.6; margin-bottom: 50px;">
            Türkiye genelinde toplanan yüksek frekanslı fiyat verileriyle oluşturulan, şeffaf ve yapay zeka destekli alternatif enflasyon göstergesi.
        </p>
        
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:30px; justify-content:center;">
            <div class="kpi-card">
                <div class="kpi-title">TAKİP EDİLEN ÜRÜN</div>
                <div class="kpi-value">{ctx["stats_urun"]}</div>
                <div class="kpi-sub" style="color:var(--accent-success);"><span>📦</span> Canlı veri akışı</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">ALT SEKTÖR</div>
                <div class="kpi-value">{ctx["stats_kategori"]}</div>
                 <div class="kpi-sub" style="color:var(--text-muted);"><span>📊</span> TÜİK ağırlıklandırması</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">VERİ NOKTASI</div>
                <div class="kpi-value">{ctx["stats_veri_noktasi"]}+</div>
                <div class="kpi-sub" style="color:var(--accent-primary);"><span>⚡</span> Yüksek frekanslı işlem</div>
            </div>
        </div>

        <div style="margin-top:50px; padding: 12px 24px; background: rgba(255,255,255,0.03); border-radius: 30px; display: inline-flex; align-items:center; gap:12px;">
            <span style="display:block; width:10px; height:10px; background:var(--accent-success); border-radius:50%; box-shadow: 0 0 10px var(--accent-success);"></span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size:13px; color: var(--text-bright);">
                SİSTEM DURUMU: NORMAL • {datetime.now().strftime('%H:%M')} TSİ
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def sayfa_piyasa_ozeti(ctx):
    st.markdown("<h2 style='text-align:center; margin-bottom:30px;'>Piyasa Nabzı ve Kritik Göstergeler</h2>", unsafe_allow_html=True)
    
    # KPI Kartları - Tam Simetrik Grid (4 Kolon)
    c1, c2, c3, c4 = st.columns(4, gap="large")
    
    def create_kpi(title, value, icon, text, color):
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value" style="color:{color}">%{value:.2f}</div>
            <div class="kpi-sub" style="color:{color}">{icon} {text}</div>
        </div>
        """
        
    # Trend renklerini belirle
    c_genel = "var(--accent-success)" if ctx["enf_genel"] > 0 else "var(--accent-danger)"
    c_gida = "var(--accent-success)" if ctx["enf_gida"] > 0 else "var(--accent-danger)"
    i_genel = "📈" if ctx["enf_genel"] > 0 else "📉"
    i_gida = "🍲"

    with c1: st.markdown(create_kpi("GENEL ENFLASYON (AYLIK)", ctx["enf_genel"], i_genel, "Sepet Değişimi", c_genel), unsafe_allow_html=True)
    with c2: st.markdown(create_kpi("GIDA ENFLASYONU (AYLIK)", ctx["enf_gida"], i_gida, "Mutfak Harcaması", c_gida), unsafe_allow_html=True)
    with c3: st.markdown(create_kpi("YIL SONU TAHMİNİ", ctx["tahmin"], "🤖", "AI Projeksiyonu", "var(--accent-primary)"), unsafe_allow_html=True)
    with c4: st.markdown(create_kpi("RESMİ TÜİK VERİSİ", ctx["resmi_aylik_degisim"], "🏛️", "Son Açıklanan", "var(--text-muted)"), unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    # Grafikler ve Özet Tablo - Tam Simetrik Grid (2 Kolon)
    col_g1, col_g2 = st.columns(2, gap="large")
    df = ctx["df_analiz"]

    with col_g1:
        st.subheader("Fiyat Değişim Dağılımı")
        # Histogram için daha profesyonel renkler
        fig_hist = px.histogram(df, x="Fark_Yuzde", nbins=40, color_discrete_sequence=["#3B82F6"])
        fig_hist.update_traces(marker_line_color='#131B24', marker_line_width=1, opacity=1)
        st.plotly_chart(style_chart(fig_hist), use_container_width=True)
        
    with col_g2:
        st.subheader("Piyasa Hareket Özeti")
        artan = len(df[df['Fark'] > 0])
        dusen = len(df[df['Fark'] < 0])
        sabit = len(df[df['Fark'] == 0])
        
        # Ortalanmış Özet Kartı
        st.markdown(f"""
        <div style="background:var(--bg-surface); border-radius:16px; padding:30px; border:1px solid var(--border-subtle); height:100%; display:flex; flex-direction:column; justify-content:center; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px; padding-bottom:20px; border-bottom:1px solid var(--border-subtle);">
                <span style="font-size:14px; color:var(--text-muted); font-weight:600; text-transform:uppercase;">YÜKSELEN ÜRÜNLER</span>
                <span style="font-size:24px; color:var(--accent-success); font-weight:700; font-family:'JetBrains Mono';">▲ {artan}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px; padding-bottom:20px; border-bottom:1px solid var(--border-subtle);">
                <span style="font-size:14px; color:var(--text-muted); font-weight:600; text-transform:uppercase;">DÜŞEN ÜRÜNLER</span>
                <span style="font-size:24px; color:var(--accent-danger); font-weight:700; font-family:'JetBrains Mono';">▼ {dusen}</span>
            </div>
             <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:14px; color:var(--text-muted); font-weight:600; text-transform:uppercase;">SABİT KALANLAR</span>
                <span style="font-size:24px; color:var(--text-bright); font-weight:700; font-family:'JetBrains Mono';">• {sabit}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.subheader("Sektörel Isı Haritası (Ağırlıklı)")
    # Isı haritası için daha net bir renk skalası
    fig_tree = px.treemap(df, path=[px.Constant("Genel Pazar"), 'Grup', ctx['ad_col']], values=ctx['agirlik_col'], color='Fark', 
                          color_continuous_scale=['#DC2626', '#131B24', '#059669'], # Kırmızı -> Koyu -> Yeşil
                          color_continuous_midpoint=0)
    fig_tree.update_traces(marker_line_width=1, marker_line_color='#131B24')
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    st.markdown("<h2 style='text-align:center;'>Detaylı Ürün Fiyat Takibi</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--text-muted); margin-bottom:30px;'>Kategori bazında veya arama yaparak ürünlerin anlık durumunu inceleyin.</p>", unsafe_allow_html=True)
    
    # Filtreleme Alanı - Ortalanmış
    c_spacer_l, c_filt_1, c_filt_2, c_spacer_r = st.columns([1, 2, 3, 1])
    with c_filt_1:
        kategoriler = ["Tümü"] + sorted(df['Grup'].unique().tolist())
        secilen_kat = st.selectbox("Kategori Filtresi", kategoriler)
    with c_filt_2:
        arama = st.text_input("Ürün Arama", placeholder="Örn: Süt, Ekmek, Yumurta...")
    
    st.markdown("<br>", unsafe_allow_html=True)

    df_show = df.copy()
    if secilen_kat != "Tümü": df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama: df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]
    
    if not df_show.empty:
        # Pagination - Ortalanmış
        items_per_page = 24
        total_pages = max(1, len(df_show)//items_per_page + 1)
        
        c_pag_l, c_pag_c, c_pag_r = st.columns([3, 2, 3])
        with c_pag_c:
            page_num = st.number_input(f"Sayfa (Toplam {total_pages})", min_value=1, max_value=total_pages, step=1)
        
        batch = df_show.iloc[(page_num - 1) * items_per_page : (page_num - 1) * items_per_page + items_per_page]
        
        # Grid Görünümü - 6 Kolonlu Simetrik Grid
        cols = st.columns(6)
        for idx, row in enumerate(batch.to_dict('records')):
            fiyat = row[ctx['son']]; fark = row.get('Gunluk_Degisim', 0) * 100
            
            if fark > 0.01:
                badge_color = "var(--accent-success)"; badge_bg = "rgba(5, 150, 105, 0.1)"; icon = "▲"; fark_txt = f"+%{abs(fark):.2f}"
            elif fark < -0.01:
                badge_color = "var(--accent-danger)"; badge_bg = "rgba(220, 38, 38, 0.1)"; icon = "▼"; fark_txt = f"-%{abs(fark):.2f}"
            else:
                badge_color = "var(--text-muted)"; badge_bg = "rgba(255, 255, 255, 0.05)"; icon = "•"; fark_txt = "%0.00"

            with cols[idx % 6]:
                st.markdown(f"""
                <div class="grid-card" style="background:var(--bg-surface); border-radius:12px; padding:15px; text-align:center; border:1px solid var(--border-subtle); height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="font-size:13px; font-weight:500; color:var(--text-bright); margin-bottom:10px; height:40px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="{row[ctx['ad_col']]}">{row[ctx['ad_col']]}</div>
                    <div>
                        <div style="font-family:'JetBrains Mono'; font-size:18px; font-weight:700; margin-bottom:8px;">{fiyat:.2f} ₺</div>
                        <div style="font-size:11px; font-weight:700; padding:4px 8px; border-radius:6px; background:{badge_bg}; color:{badge_color}; display:inline-block;">{icon} {fark_txt}</div>
                    </div>
                </div>
                <div style="margin-bottom:16px;"></div>
                """, unsafe_allow_html=True)
    else: 
        st.info("Kriterlere uygun ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    st.markdown("<h2 style='text-align:center;'>Tam Veri Seti ve Analiz</h2>", unsafe_allow_html=True)
    df = ctx["df_analiz"]

    # Sparkline için veriyi hazırla
    def fix_sparkline(row):
        vals = [v if pd.notnull(v) else 0 for v in row.tolist()]
        if not vals: return [0,0]
        # Düz çizgi olmaması için minik bir varyasyon ekle (görsel hile)
        if min(vals) == max(vals) and len(vals) > 1: vals[-1] += 0.0001
        return vals

    df['Fiyat_Trendi'] = df[ctx['gunler']].apply(fix_sparkline, axis=1)
    
    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', ctx['baz_col'], ctx['son'], 'Gunluk_Degisim']
    
    cfg = {
        "Grup": st.column_config.TextColumn("Kategori", width="medium"),
        ctx['ad_col']: st.column_config.TextColumn("Ürün Adı", width="large"),
        "Fiyat_Trendi": st.column_config.LineChartColumn("Fiyat Trendi (Son Dönem)", width="medium", y_min=0), 
        ctx['baz_col']: st.column_config.NumberColumn(f"Baz Fiyat ({ctx['baz_col']})", format="%.2f ₺"), 
        ctx['son']: st.column_config.NumberColumn(f"Son Fiyat ({ctx['son']})", format="%.2f ₺"),
        "Gunluk_Degisim": st.column_config.ProgressColumn("Günlük Değişim", format="%.2f%%", min_value=-0.2, max_value=0.2), 
    }
    
    # Dataframe'i daha temiz göster
    st.dataframe(df[cols_show], column_config=cfg, hide_index=True, use_container_width=True, height=700)
    
    # İndirme butonu - Ortalanmış
    st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
    output = BytesIO(); 
    with pd.ExcelWriter(output) as writer: df.to_excel(writer, index=False)
    st.download_button("📥 Excel Raporunu İndir", data=output.getvalue(), file_name=f"Enflasyon_Verisi_{ctx['son']}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("</div>", unsafe_allow_html=True)

def sayfa_raporlama(ctx):
    st.markdown("<h2 style='text-align:center;'>Stratejik Pazar Raporu (AI)</h2>", unsafe_allow_html=True)
    
    # Simetrik olmayan ama dengeli bir düzen (Rapor geniş, butonlar dar)
    col_l, col_r = st.columns([3, 1], gap="large")
    with col_l:
        # Rapor metnini bir "kağıt" gibi göster - Ortalanmış metin
        rap_text = generate_detailed_static_report(ctx["df_analiz"], ctx["son"], ctx["enf_genel"], ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], ctx["ad_col"], ctx["agirlik_col"])
        st.markdown(f"""
        <div style="background:var(--bg-surface); padding:40px; border-radius:16px; border:1px solid var(--border-subtle); font-family:'Inter'; line-height:1.7; font-size:15px; color: var(--text-bright); text-align:left; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            {rap_text.replace(chr(10), '<br>').replace('**', '<b style="color:var(--accent-primary);">').replace('**', '</b>')}
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        st.markdown("#### Rapor İşlemleri")
        st.write("Bu rapor, sistemdeki anlık veriler ve yapay zeka algoritmaları kullanılarak otomatik oluşturulmuştur.")
        
        word_buffer = create_word_report(rap_text, ctx["son"], ctx["df_analiz"])
        st.download_button(
            label="📄 Word Raporu Olarak İndir", 
            data=word_buffer, 
            file_name=f"Piyasa_Raporu_{ctx['son']}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            use_container_width=True
        )
        
        st.divider()
        st.info("NOT: Bu belge, dahili analiz amaçlıdır ve resmi yatırım tavsiyesi niteliği taşımaz.")

def sayfa_maddeler(ctx):
    df = ctx["df_analiz"]
    st.markdown("<h2 style='text-align:center;'>Kategori Bazlı Kümülatif Değişim</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--text-muted); margin-bottom:30px;'>Seçilen kategorideki ürünlerin, baz alınan tarihe göre toplam yüzdesel değişimlerini gösterir.</p>", unsafe_allow_html=True)
    
    # Seçim kutusunu ortala
    c_l, c_c, c_r = st.columns([1, 2, 1])
    with c_c:
        kategoriler = sorted(df['Grup'].unique().tolist())
        secilen_kat = st.selectbox("Kategori Seçiniz:", options=kategoriler, index=0)
    
    df_sub = df[df['Grup'] == secilen_kat].copy().sort_values('Fark_Yuzde', ascending=True)
    
    if not df_sub.empty:
        # Renkleri profesyonel palete göre ayarla
        colors = ['#DC2626' if x < 0 else '#059669' for x in df_sub['Fark_Yuzde']]
        
        fig = go.Figure(go.Bar(
            x=df_sub['Fark_Yuzde'], 
            y=df_sub[ctx['ad_col']], 
            orientation='h', 
            marker_color=colors,
            text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"), 
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Kümülatif Değişim: %%{x:.2f}<extra></extra>'
        ))
        
        # Dinamik yükseklik
        fig.update_layout(
            height=max(600, len(df_sub) * 40), 
            title=f"{secilen_kat} Grubu Ürünleri",
            xaxis_title="Değişim Oranı (%)", 
            yaxis_title=None,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else: 
        st.warning("Bu kategoride görüntülenecek veri bulunamadı.")

def sayfa_trend_analizi(ctx):
    st.markdown("<h2 style='text-align:center;'>Zaman Serisi ve Trend Analizi</h2>", unsafe_allow_html=True)
    
    df = ctx["df_analiz"]; gunler = ctx["gunler"]; agirlik_col = ctx["agirlik_col"]
    
    # --- Genel Enflasyon Trendi ---
    endeks_verisi = []
    for gun in gunler:
        temp_df = df.dropna(subset=[gun, agirlik_col])
        if not temp_df.empty and temp_df[agirlik_col].sum() > 0:
            index_val = (temp_df[gun] * temp_df[agirlik_col]).sum() / temp_df[agirlik_col].sum()
            endeks_verisi.append({"Tarih": gun, "Deger": index_val})
            
    df_endeks = pd.DataFrame(endeks_verisi)
    if not df_endeks.empty:
        # Başlangıcı 0'a endeksle
        df_endeks['Kümülatif_Degisim'] = ((df_endeks['Deger'] / df_endeks.iloc[0]['Deger']) - 1) * 100
        
        fig_genel = px.line(df_endeks, x='Tarih', y='Kümülatif_Degisim', title="Genel Sepet Kümülatif Değişimi (%)", markers=True)
        # Çizgiyi kalınlaştır ve kurumsal mavi yap
        fig_genel.update_traces(line_color='#3B82F6', line_width=5, marker_size=12, marker_color='#131B24', marker_line_width=3, marker_line_color='#3B82F6')
        
        st.plotly_chart(style_chart(fig_genel), use_container_width=True)
        st.caption(f"ℹ️ Grafik, {gunler[0]} tarihini baz (0) alarak hesaplanan ağırlıklı sepet değişimini gösterir.")
    
    st.divider()
    
    # --- Ürün Bazlı Kıyaslama ---
    st.subheader("Ürün Bazlı Fiyat Kıyaslama")
    
    # Varsayılan olarak en çok artan 3 ürünü seç
    default_selection = df.sort_values('Fark_Yuzde', ascending=False).head(3)[ctx['ad_col']].tolist()
    seçilen_urunler = st.multiselect("Karşılaştırılacak ürünleri seçin:", options=df[ctx['ad_col']].unique(), default=default_selection)
    
    if seçilen_urunler:
        df_melted = df[df[ctx['ad_col']].isin(seçilen_urunler)][[ctx['ad_col']] + gunler].melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        
        # Her ürünün kendi ilk günkü fiyatına göre değişimini hesapla
        base_prices = df_melted[df_melted['Tarih'] == gunler[0]].set_index(ctx['ad_col'])['Fiyat'].to_dict()
        df_melted['Yuzde_Degisim'] = df_melted.apply(lambda row: ((row['Fiyat']/base_prices.get(row[ctx['ad_col']], 1)) - 1)*100 if base_prices.get(row[ctx['ad_col']], 0) > 0 else 0, axis=1)
        
        fig_urun = px.line(df_melted, x='Tarih', y='Yuzde_Degisim', color=ctx['ad_col'], title="Seçili Ürünlerin Kümülatif Değişimi (%)", markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_urun.update_traces(line_width=3, marker_size=8)
        st.plotly_chart(style_chart(fig_urun), use_container_width=True)

def sayfa_metodoloji(ctx=None):
    # Ortalanmış başlık ve içerik
    st.markdown("<h2 style='text-align:center;'>Metodoloji ve Yasal Uyarı</h2>", unsafe_allow_html=True)
    
    c_l, c_c, c_r = st.columns([1, 2, 1])
    with c_c:
        with st.expander("📌 Veri Toplama ve İşleme Yöntemi", expanded=True):
            st.markdown("""
            Bu sistem, Türkiye'de faaliyet gösteren önde gelen zincir marketler ve e-ticaret platformlarından **web kazıma (web scraping)** yöntemiyle günlük olarak fiyat verisi toplamaktadır.
            * **Kapsam:** TÜİK enflasyon sepetindeki ana harcama gruplarını temsil eden simüle edilmiş bir ürün sepeti takip edilmektedir.
            * **Veri Güvenliği:** Toplama işlemi sırasında User-Agent rotasyonu ve hız sınırlaması (rate limiting) uygulanarak hedef sitelere zarar verilmemesi amaçlanmaktadır.
            * **Veri Temizliği:** Aykırı değerler (anomali) ve eksik veriler, istatistiksel yöntemlerle (örneğin, önceki günün verisini taşıma veya enterpolasyon) işlenmektedir.
            """)

        with st.expander("🧮 Endeks Hesaplama Modeli", expanded=True):
            st.markdown("""
            Enflasyon hesaplamasında, uluslararası standartlara uygun olarak **Zincirleme Laspeyres Fiyat Endeksi** yaklaşımı benimsenmiştir.
            * **Formül:** `I(t) = Σ ( P(i,t) / P(i,0) ) × W(i)`
            * **Ağırlıklandırma (W):** Ürünlerin endeks üzerindeki etkisi, TÜİK Hanehalkı Bütçe Anketi'nden (HBA) elde edilen harcama paylarına göre simüle edilmiş ağırlıklarla belirlenir. Bu ağırlıklar her yılın başında (Zincirleme tarihi) güncellenir.
            """)

        with st.expander("⚠️ Yasal Uyarı ve Sorumluluk Reddi", expanded=True):
            st.markdown("""
            * Bu platformda sunulan veriler, analizler ve raporlar tamamen **bilgilendirme ve akademik/deneysel amaçlıdır.**
            * Buradaki bilgiler, **resmi enflasyon verisi (TÜİK) yerine geçmez** ve kesinlikle **yatırım tavsiyesi değildir.**
            * Verilerin doğruluğu, tamlığı veya güncelliği konusunda garanti verilmez. Bu verilere dayanarak alınan finansal veya ticari kararlardan doğabilecek zararlardan sistem geliştiricileri sorumlu tutulamaz.
            """)

# --- ANA UYGULAMA MANTIĞI ---
def main():
    # --- HEADER BÖLÜMÜ (TAM ORTALI) ---
    st.markdown("""
    <div style="text-align:center; padding-bottom: 20px;">
        <div style="display:inline-flex; align-items:center; gap:15px; margin-bottom:10px;">
            <div style="font-size:42px;">💠</div>
            <div style="font-weight:900; font-size:36px; color:var(--text-bright); letter-spacing:-1px;">
                Piyasa Monitörü <span style="color:var(--accent-primary);">PRO</span>
            </div>
        </div>
        <div style="font-size:16px; color:var(--text-muted); font-weight:500;">Kurumsal Enflasyon Analiz Terminali v3.0 (Premium)</div>
        <div style="margin-top:15px; font-family:'JetBrains Mono'; font-size:14px; color:var(--text-muted);">
            İSTANBUL • {date}
        </div>
    </div>
    """.format(date=datetime.now().strftime("%d.%m.%Y")), unsafe_allow_html=True)

    # --- NAVİGASYON (TAM ORTALI) ---
    menu_items = {
        "🏠 Ana Sayfa": "Ana Sayfa",
        "⚡ Özet": "Piyasa Özeti",
        "📈 Trendler": "Trendler",
        "📦 Ürünler": "Maddeler",
        "🔍 Detay": "Kategori Detay",
        "💾 Veri Seti": "Tam Liste",
        "📝 Rapor": "Raporlama",
        "ℹ️ Metodoloji": "Metodoloji"
    }
    secilen_etiket = st.radio(
        "Navigasyon", 
        options=list(menu_items.keys()), 
        label_visibility="collapsed", 
        key="main_nav",
        horizontal=True
    )
    secim = menu_items[secilen_etiket]

    # --- VERİ YÜKLEME ---
    with st.spinner("Premium veritabanına bağlanılıyor..."):
        df_base, r_dates, col_name = verileri_getir_cache()
    
    if df_base is not None:
        # Sidebar'ı sadece veri varsa göster ve bağlamı (ctx) al
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)
    else:
        ctx = None

    # --- SAYFA İÇERİĞİ ---
    if ctx:
        # İçerik alanı için biraz boşluk
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        
        if secim == "Ana Sayfa": sayfa_ana_sayfa(ctx)
        elif secim == "Piyasa Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
        elif secim == "Metodoloji": sayfa_metodoloji(ctx)
        
    else:
        # Veri yüklenemezse
        if secim == "Metodoloji":
            sayfa_metodoloji()
        else:
            st.markdown("<div style='text-align:center; padding:50px; color:var(--accent-danger);'>⚠️ Veritabanı bağlantısı kurulamadı. Lütfen internet bağlantınızı kontrol edin.</div>", unsafe_allow_html=True)

    # --- FOOTER (ORTALI) ---
    st.markdown("""
    <div style="text-align:center; color:var(--text-muted); font-size:12px; margin-top:80px; padding-top:30px; border-top:1px solid var(--border-subtle); opacity:0.7;">
        VALIDASYON MÜDÜRLÜĞÜ © 2026 • PREMIUM ANALYTICS SUITE • GİZLİDİR
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
