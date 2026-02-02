# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
import calendar
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import tempfile
import os
import math
import random
import html
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

try:
    import xlsxwriter
except ImportError:
    st.error("Lütfen 'pip install xlsxwriter' komutunu çalıştırın. Excel raporlama modülü için gereklidir.")
    
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st.error("Lütfen 'pip install streamlit-lottie' komutunu çalıştırın.")

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("Lütfen 'pip install python-docx' komutunu çalıştırın.")

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded" # Masaüstünde varsayılan açık gelir
)

# --- CSS MOTORU (MOBİLDE SIDEBAR GİZLEME EKLENDİ) ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {{
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-highlight: rgba(255, 255, 255, 0.15);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --card-radius: 16px;
        }}

        /* --- MOBİL UYUMLULUK VE SIDEBAR GİZLEME --- */
        @media only screen and (max-width: 768px) {{
            /* 1. SIDEBAR'I MOBİLDE TAMAMEN GİZLE */
            section[data-testid="stSidebar"] {{
                display: none !important;
                width: 0px !important;
            }}
            /* Sidebar Açma/Kapama Okunu (Button) da Gizle */
            div[data-testid="stSidebarCollapsedControl"] {{
                display: none !important;
            }}
            
            /* 2. KONTEYNER AYARLARI */
            .block-container {{
                padding-top: 1rem !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                max-width: 100% !important;
            }}
            
            /* 3. HEADER AYARLARI */
            .header-wrapper {{
                flex-direction: column !important;
                align-items: flex-start !important;
                padding: 15px 20px !important;
                height: auto !important;
                gap: 15px !important;
            }}
            .app-title {{ 
                font-size: 24px !important; 
                flex-direction: column !important; 
                align-items: flex-start !important; 
                gap: 5px !important;
            }}
            .clock-container {{ 
                text-align: left !important; 
                width: 100% !important; 
                margin-top: 10px !important;
                padding-top: 10px !important;
                border-top: 1px solid rgba(255,255,255,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            /* 4. KART DÜZENLEMELERİ */
            .kpi-card {{
                margin-bottom: 10px !important;
                padding: 16px !important;
                height: auto !important;
            }}
            .kpi-value {{ font-size: 28px !important; margin-bottom: 4px !important; }}
            .kpi-title {{ font-size: 10px !important; margin-bottom: 8px !important; }}

            /* 5. ÜRÜN KARTLARI (YATAY LİSTE) */
            .pg-card {{
                width: 100% !important;
                height: auto !important;
                min-height: 70px !important;
                margin-bottom: 10px !important;
                flex-direction: row !important;
                justify-content: space-between !important;
                align-items: center !important;
                text-align: left !important;
                padding: 12px 16px !important;
                gap: 10px;
            }}
            .pg-name {{ 
                font-size: 13px !important; 
                -webkit-line-clamp: 1 !important; 
                margin-bottom: 0 !important;
                flex: 1; 
                text-align: left !important;
            }}
            .pg-price {{ font-size: 15px !important; margin: 0 !important; white-space: nowrap; }}
            .pg-badge {{ font-size: 9px !important; padding: 2px 6px !important; }}

            /* 6. TABLO VE GRAFİK */
            .stTabs [data-baseweb="tab-list"] {{
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                justify-content: flex-start !important;
                padding-bottom: 5px !important;
            }}
            .stTabs [data-baseweb="tab"] {{
                flex: 0 0 auto !important;
                padding: 0 15px !important;
            }}
            .stPlotlyChart {{ width: 100% !important; }}
            .ticker-wrap {{ font-size: 10px !important; padding: 8px 0 !important; }}
        }}

        /* --- GENEL STİLLER (DEĞİŞMEDİ) --- */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
                radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px),
                radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 3px);
            background-size: 550px 550px, 350px 350px, 250px 250px;
            background-position: 0 0, 40 60, 130 270;
            opacity: 0.07; z-index: 0; animation: star-move 200s linear infinite; pointer-events: none;
        }}
        @keyframes star-move {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-2000px); }} }}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translate3d(0, 20px, 0); }} to {{ opacity: 1; transform: translate3d(0, 0, 0); }} }}
        @keyframes border-flow {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .animate-enter {{ animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }}
        .delay-1 {{ animation-delay: 0.1s; }} .delay-2 {{ animation-delay: 0.2s; }} .delay-3 {{ animation-delay: 0.3s; }}
        .blink {{ animation: blinker 1s linear infinite; }} @keyframes blinker {{ 50% {{ opacity: 0; }} }}

        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-deep);
            background-image: radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.06), transparent 25%), radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.06), transparent 25%);
            background-attachment: fixed; font-family: 'Inter', sans-serif !important; color: var(--text-main) !important;
        }}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: #02040a; }}
        ::-webkit-scrollbar-thumb {{ background: #3b82f6; border-radius: 4px; }}
        [data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
        [data-testid="stToolbar"] {{ display: none; }}
        
        /* Side bar masaüstü için genel stil */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(5, 5, 10, 0.95) 0%, rgba(0, 0, 0, 0.98) 100%) !important;
            border-right: 1px solid var(--glass-border); backdrop-filter: blur(20px); z-index: 99;
        }}
        
        .stSelectbox > div > div, .stTextInput > div > div {{
            background-color: rgba(255, 255, 255, 0.03) !important; border: 1px solid var(--glass-border) !important;
            color: var(--text-main) !important; border-radius: 10px !important; transition: all 0.3s ease;
        }}
        .stSelectbox > div > div:hover, .stTextInput > div > div:focus-within {{
            border-color: var(--accent-blue) !important; background-color: rgba(255, 255, 255, 0.06) !important;
        }}
        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {{
            border: 1px solid var(--glass-border); border-radius: 12px; background: rgba(10, 10, 15, 0.4) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); animation: fadeInUp 0.8s ease-out;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px; background: rgba(255,255,255,0.02); padding: 8px; border-radius: 12px; border: 1px solid var(--glass-border);
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 40px; border-radius: 8px; padding: 0 20px; color: var(--text-dim) !important; font-weight: 500; border: none !important; transition: all 0.2s ease;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(255,255,255,0.1) !important; color: #fff !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        div.stButton > button {{
            background: linear-gradient(145deg, rgba(40,40,45,0.8), rgba(20,20,25,0.9)); border: 1px solid var(--glass-border);
            color: #fff; border-radius: 10px; font-weight: 600; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        div.stButton > button:hover {{ border-color: var(--accent-blue); box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); transform: translateY(-1px); }}

        .kpi-card {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border); border-radius: var(--card-radius);
            padding: 24px; position: relative; overflow: hidden; backdrop-filter: blur(10px); transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease-out both; z-index: 1;
        }}
        .kpi-card::before, .pg-card::before, .smart-card::before {{
            content: ""; position: absolute; inset: -1px; z-index: -1;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
            background-size: 400% 400%; animation: border-flow 10s ease infinite; border-radius: inherit; opacity: 0; transition: opacity 0.3s ease;
        }}
        .kpi-card:hover::before, .pg-card:hover::before, .smart-card:hover::before {{ opacity: 0.6; filter: blur(10px); }}
        .kpi-card:hover {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.02) 100%);
            border-color: var(--glass-highlight); transform: translateY(-4px);
        }}
        .kpi-bg-icon {{ position: absolute; right: -15px; bottom: -25px; font-size: 100px; opacity: 0.04; transform: rotate(-15deg); filter: blur(1px); pointer-events: none; }}
        .kpi-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 1.5px; margin-bottom: 12px; }}
        .kpi-value {{ font-size: 36px; font-weight: 700; color: #fff; margin-bottom: 8px; letter-spacing: -1.5px; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        .kpi-sub {{ font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--text-dim); background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 6px; width: fit-content; }}

        .pg-card {{
            background: rgba(20, 20, 25, 0.4); border: 1px solid var(--glass-border); border-radius: 12px;
            padding: 16px; height: 150px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            text-align: center; transition: all 0.2s ease; animation: fadeInUp 0.5s ease-out both; position: relative; z-index: 1;
        }}
        .pg-card:hover {{ background: rgba(40, 40, 45, 0.6); border-color: rgba(255,255,255,0.2); transform: scale(1.03); }}
        .pg-name {{ font-size: 12px; font-weight: 500; color: #d4d4d8; line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; min-height: 32px; }}
        .pg-price {{ font-size: 18px; font-weight: 700; color: #fff; margin: 8px 0; }}
        .pg-badge {{ padding: 3px 10px; border-radius: 99px; font-size: 10px; font-weight: 700; border: 1px solid transparent; }}
        .pg-red {{ background: rgba(239, 68, 68, 0.1); color: #fca5a5; border-color: rgba(239, 68, 68, 0.2); }}
        .pg-green {{ background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.2); }}
        .pg-yellow {{ background: rgba(255, 255, 255, 0.05); color: #ffd966; }}

        .ticker-wrap {{ width: 100%; overflow: hidden; background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(20,20,30,0.5) 15%, rgba(20,20,30,0.5) 85%, rgba(0,0,0,0) 100%); border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); padding: 12px 0; margin-bottom: 30px; white-space: nowrap; }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.5px; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        .smart-card {{ background: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; display: flex; flex-direction: column; gap: 5px; transition: all 0.2s; animation: fadeInUp 0.7s ease-out both; position: relative; z-index: 1; }}
        .smart-card:hover {{ border-color: var(--accent-blue); transform: translateY(-2px); }}
        .sc-title {{ font-size: 11px; color: #a1a1aa; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }}
        .sc-val {{ font-size: 20px; color: #fff; font-weight:700; display:flex; align-items:center; gap:8px; }}
        
        .skeleton {{ background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 8px; }}
        @keyframes loading {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

# --- LOTTIE LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. WORD MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
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
        if not p_text.strip(): 
            continue
            
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
            fig, ax = plt.subplots(figsize=(6, 4))
            data = df_analiz['Fark'].dropna() * 100
            ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
            ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
            ax.set_xlabel("Değişim Oranı (%)")
            ax.set_ylabel("Ürün Sayısı")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            
            memfile = BytesIO()
            plt.savefig(memfile, format='png', dpi=100)
            doc.add_picture(memfile, width=Inches(5.5))
            memfile.close()
            plt.close()
            
            doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
            doc.add_paragraph("")

            if 'Grup' in df_analiz.columns and 'Agirlik_2025' in df_analiz.columns:
                df_analiz['Agirlikli_Fark'] = df_analiz['Fark'] * df_analiz['Agirlik_2025']
                sektor_grp = df_analiz.groupby('Grup')['Agirlikli_Fark'].sum().sort_values(ascending=False).head(7)
                
                if not sektor_grp.empty:
                    fig, ax = plt.subplots(figsize=(7, 4))
                    colors = ['#ef4444' if x > 0 else '#10b981' for x in sektor_grp.values]
                    sektor_grp.plot(kind='barh', ax=ax, color=colors)
                    ax.set_title("Enflasyona En Çok Etki Eden Sektörler (Puan)", fontsize=12, fontweight='bold')
                    ax.set_xlabel("Puan Katkısı")
                    ax.invert_yaxis() 
                    plt.tight_layout()

                    memfile2 = BytesIO()
                    plt.savefig(memfile2, format='png', dpi=100)
                    doc.add_picture(memfile2, width=Inches(6.0))
                    memfile2.close()
                    plt.close()
                    
                    doc.add_paragraph("Grafik 2: Genel endeks üzerinde en çok baskı oluşturan ana harcama grupları.")

        except Exception as e:
            doc.add_paragraph(f"[Grafik oluşturulurken teknik bir sorun oluştu: {str(e)}]")

    section = doc.sections[0]
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.text = "Validasyon Müdürlüğü © 2026 - Gizli Belge"
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. GITHUB İŞLEMLERİ ---
def get_github_repo():
    try:
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except:
        return None

def github_json_oku(dosya_adi):
    repo = get_github_repo()
    if not repo: return {}
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        return json.loads(c.decoded_content.decode("utf-8"))
    except:
        return {}

def github_json_yaz(dosya_adi, data, mesaj="Update JSON"):
    repo = get_github_repo()
    if not repo: return False
    try:
        content = json.dumps(data, indent=4)
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            repo.update_file(c.path, mesaj, content, c.sha, branch=st.secrets["github"]["branch"])
        except:
            repo.create_file(dosya_adi, mesaj, content, branch=st.secrets["github"]["branch"])
        return True
    except:
        return False

@st.cache_data(ttl=60, show_spinner=False)
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

# --- 5. RESMİ ENFLASYON & PROPHET ---
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
            else:
                return None, "Boş Veri"
        else:
            return None, f"HTTP {res.status_code}"
    except Exception as e:
        return None, str(e)

# --- 6. SCRAPER (PROGRESS BAR DESTEKLİ) ---
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
    fiyat = 0;
    kaynak = "";
    domain = url.lower() if url else ""
    if "migros" in domain:
        garbage = ["sm-list-page-item", ".horizontal-list-page-items-container", "app-product-carousel",
                   ".similar-products", "div.badges-wrapper"]
        for g in garbage:
            for x in soup.select(g): x.decompose()
        main_wrapper = soup.select_one(".name-price-wrapper")
        if main_wrapper:
            for sel, k in [(".price.subtitle-1", "Migros(N)"), (".single-price-amount", "Migros(S)"),
                           ("#sale-price, .sale-price", "Migros(I)")]:
                if el := main_wrapper.select_one(sel):
                    if val := temizle_fiyat(el.get_text()): return val, k
        if fiyat == 0:
            if el := soup.select_one("fe-product-price .subtitle-1, .single-price-amount"):
                if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(G)"
            if fiyat == 0:
                if el := soup.select_one("#sale-price"):
                    if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(GI)"
    elif "cimri" in domain:
        for sel in ["div.rTdMX", ".offer-price", "div.sS0lR", ".min-price-val"]:
            if els := soup.select(sel):
                vals = [v for v in [temizle_fiyat(e.get_text()) for e in els] if v and v > 0]
                if vals:
                    if len(vals) > 4: vals.sort(); vals = vals[1:-1]
                    fiyat = sum(vals) / len(vals);
                    kaynak = f"Cimri({len(vals)})";
                    break
        if fiyat == 0:
            if m := re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:10000]):
                ff = sorted([temizle_fiyat(x) for x in m if temizle_fiyat(x)])
                if ff: fiyat = sum(ff[:max(1, len(ff) // 2)]) / max(1, len(ff) // 2); kaynak = "Cimri(Reg)"
    if fiyat == 0 and "migros" not in domain:
        for sel in [".product-price", ".price", ".current-price", "span[itemprop='price']"]:
            if el := soup.select_one(sel):
                if v := temizle_fiyat(el.get_text()): fiyat = v; kaynak = "Genel(CSS)"; break
    if fiyat == 0 and "migros" not in domain and "cimri" not in domain:
        if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
            if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
    return fiyat, kaynak

def html_isleyici(progress_callback):
    """
    Log yazısı yerine Progress Bar için float döner (0.0 - 1.0)
    """
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    
    # 1. Aşama: Hazırlık ve Config (0% - 10%)
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
        veriler = [];
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d");
        simdi = datetime.now().strftime("%H:%M")
        
        manuel_col = next((c for c in df_conf.columns if 'manuel' in c.lower()), None)
        ms = 0
        if manuel_col:
            for _, row in df_conf.iterrows():
                if pd.notna(row[manuel_col]) and str(row[manuel_col]).strip() != "":
                    try:
                        fiyat_man = float(row[manuel_col])
                        if fiyat_man > 0:
                            veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": row['Kod'], "Madde_Adi": row[ad_col],
                                            "Fiyat": fiyat_man, "Kaynak": "Manuel", "URL": row[url_col]})
                            islenen_kodlar.add(row['Kod']);
                            ms += 1
                    except:
                        pass
        
        progress_callback(0.10) # Config bitti
        
        # 2. Aşama: ZIP Tarama (10% - 90%)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        
        total_zips = len(zip_files)
        hs = 0
        
        for i, zip_file in enumerate(zip_files):
            # İlerlemeyi ZIP dosyasına göre hesapla
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
                            if not found_url and (m := soup.find("meta", property="og:url")): found_url = m.get(
                                "content")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod']);
                                    hs += 1
            except Exception as e:
                pass # Hataları sessiz geçiyoruz
        
        # 3. Aşama: Kaydetme (90% - 100%)
        progress_callback(0.95)
        
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "Veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. STATİK ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    import numpy as np
    
    df_clean = df_analiz.dropna(subset=['Fark'])
    toplam_urun = len(df_clean)
    
    ortalama_fark = df_clean['Fark'].mean()
    medyan_fark = df_clean['Fark'].median()
    
    piyasa_yorumu = ""
    if ortalama_fark > (medyan_fark * 1.2):
        piyasa_yorumu = "Lokal Şoklar (Belirli Ürünler Endeksi Yükseltiyor)"
    elif ortalama_fark < (medyan_fark * 0.8):
        piyasa_yorumu = "İndirim Ağırlıklı (Kampanyalar Etkili)"
    else:
        piyasa_yorumu = "Genele Yayılım (Fiyat Artışı Homojen)"

    artanlar = df_clean[df_clean['Fark'] > 0]
    dusenler = df_clean[df_clean['Fark'] < 0]
    sabitler = df_clean[df_clean['Fark'] == 0]
    
    artan_sayisi = len(artanlar)
    yayilim_orani = (artan_sayisi / toplam_urun) * 100 if toplam_urun > 0 else 0
    
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    sektor_ozet = ""
    if 'Grup' in df_analiz.columns:
        df_clean['Agirlikli_Etki'] = df_clean['Fark'] * df_clean[agirlik_col]
        sektor_grp = df_clean.groupby('Grup').agg({
            'Agirlikli_Etki': 'sum',
            agirlik_col: 'sum'
        })
        toplam_agirlik = df_clean[agirlik_col].sum()
        sektor_grp['Katki'] = (sektor_grp['Agirlikli_Etki'] / toplam_agirlik) * 100
        sektor_sirali = sektor_grp.sort_values('Katki', ascending=False).head(3)
        
        for sek, row in sektor_sirali.iterrows():
            sektor_ozet += f"   • {sek}: {row['Katki']:+.2f} Puan Etki\n"
    else:
        sektor_ozet = "   (Veri yok)\n"

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
**Durum:** {piyasa_yorumu}

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

**4. 🏭 SEKTÖREL ETKİ**
Enflasyonu yukarı çeken ana gruplar:
{sektor_ozet}

**5. 💡 SONUÇ**
Piyasa verileri, fiyat istikrarının henüz tam sağlanamadığını ve gıda grubunun ana baskı unsuru olduğunu göstermektedir. Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

---
*Otomatik Rapor Sistemi | Validasyon Müdürlüğü*
"""
    return text.strip()

# --- YENİ YARDIMCI FONKSİYONLAR ---
def make_neon_chart(fig):
    new_traces = []
    for trace in fig.data:
        if trace.type == 'scatter' or trace.type == 'line':
            glow_trace = go.Scatter(
                x=trace.x, y=trace.y,
                mode='lines',
                line=dict(width=10, color=trace.line.color), 
                opacity=0.2, 
                hoverinfo='skip', 
                showlegend=False
            )
            new_traces.append(glow_trace)
    
    fig.add_traces(new_traces)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    )
    return fig

def render_skeleton():
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="skeleton" style="height:300px; margin-top:20px;"></div>', unsafe_allow_html=True)

def stream_text(text, container, kutu_rengi, kenar_rengi, durum_emoji, durum_baslik, delay=0.015):
    for i in range(len(text) + 1):
        curr_text = text[:i]
        container.markdown(f"""
        <div class="delay-2 animate-enter" style="
            background: {kutu_rengi}; 
            border-left: 4px solid {kenar_rengi}; 
            border-radius: 12px; 
            padding: 24px; 
            margin-bottom: 30px;
            border-top: 1px solid rgba(255,255,255,0.05);
            border-right: 1px solid rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <span style="font-size:24px;">{durum_emoji}</span>
                <span style="font-weight:700; color:#fff; letter-spacing:1px; font-size:14px; font-family:'Inter', sans-serif;">AI MARKET ANALİSTİ: <span style="color:{kenar_rengi}">{durum_baslik}</span> <span class="blink">|</span></span>
            </div>
            <div style="font-size:14px; color:#d4d4d8; line-height:1.6; font-style:italic; padding-left:42px;">
                "{curr_text}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(delay)

def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
        layout_args = dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
            margin=dict(l=0, r=0, t=40, b=0),
            hoverlabel=dict(bgcolor="#18181b", bordercolor="rgba(255,255,255,0.1)", font=dict(color="#fff")),
        )
        if not is_sunburst:
            layout_args.update(dict(
                xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)",
                           gridcolor='rgba(255,255,255,0.05)', dtick="M1"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False,
                           gridwidth=1)
            ))
        fig.update_layout(**layout_args)
        fig.update_layout(modebar=dict(bgcolor='rgba(0,0,0,0)', color='#71717a', activecolor='#fff'))
    return fig

# --- 8. DASHBOARD MODU (SHOW EDITION) ---
def dashboard_modu():
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        pass 

    with loader_placeholder.container():
        render_skeleton()
    
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    loader_placeholder.empty()
    
    if not df_f.empty:
        df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
        df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
        df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
        
        raw_dates = df_f['Tarih_Str'].unique().tolist()
        BASLANGIC_LIMITI = "2026-01-02"
        tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    else:
        tum_tarihler = []

    # 2. SIDEBAR (MOBİLDE GÖRÜNMEZ, MASAÜSTÜNDE GÖRÜNÜR)
    with st.sidebar:
        lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json" 
        try:
            if 'load_lottieurl' in globals() and 'st_lottie' in globals():
                lottie_json = load_lottieurl(lottie_url)
                if lottie_json:
                      st_lottie(lottie_json, height=180, key="finance_anim")
                else:
                      st.markdown("""<div style="font-size: 50px; text-align:center; padding: 20px;">💎</div>""", unsafe_allow_html=True)
            else:
                 st.markdown("""<div style="font-size: 50px; text-align:center; padding: 20px;">💎</div>""", unsafe_allow_html=True)
        except Exception:
            st.markdown("""<div style="font-size: 50px; text-align:center; padding: 20px;">💎</div>""", unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; padding-bottom: 20px;">
                <div style="font-size: 22px; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin-top: 5px;">PİYASA MONİTÖRÜ</div>
                <div style="font-size: 11px; font-weight: 600; color: #60a5fa; letter-spacing: 3px; text-transform:uppercase; margin-top:4px;">Pro Analytics</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown("<h3 style='color: #e4e4e7; font-size: 14px; font-weight: 600; text-transform:uppercase; letter-spacing:1px; margin-bottom: 15px;'>⏳ Geçmiş Veri</h3>", unsafe_allow_html=True)
        
        if 'tum_tarihler' not in locals(): tum_tarihler = []
        
        if tum_tarihler:
            secilen_tarih = st.selectbox(
                "Geçmiş bir tarihe git:",
                options=tum_tarihler,
                index=0, 
                label_visibility="collapsed"
            )
            
            if secilen_tarih != tum_tarihler[0]:
                st.warning(f"⚠️ Şuan {secilen_tarih} tarihli arşiv kaydı inceleniyor.")
        else:
            secilen_tarih = None
            if 'df_f' in locals() and not df_f.empty:
                st.warning("2026-01-02 tarihinden sonrasına ait veri henüz oluşmadı.")
            else:
                st.error("Veri bulunamadı.")

        st.markdown("---")

        st.markdown("<h3 style='color: #e4e4e7; font-size: 14px; font-weight: 600; text-transform:uppercase; letter-spacing:1px; margin-bottom: 15px;'>🌍 Küresel Piyasalar</h3>", unsafe_allow_html=True)
        tv_theme = "dark"
        symbols = [
            {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"},
            {"s": "FX_IDC:EURTRY", "d": "Euro / TL"},
            {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"},
            {"s": "TVC:UKOIL", "d": "Brent Petrol"},
            {"s": "BINANCE:BTCUSDT", "d": "Bitcoin ($)"}
        ]
        widgets_html = ""
        for sym in symbols:
            widgets_html += f"""
            <div class="tradingview-widget-container" style="margin-bottom: 12px; border:1px solid rgba(255,255,255,0.05); border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
              {{ "symbol": "{sym['s']}", "width": "100%", "height": 110, "locale": "tr", "dateRange": "1D", "colorTheme": "{tv_theme}", "isTransparent": true, "autosize": true, "noTimeScale": true }}
              </script>
            </div>
            """
        components.html(f'<div style="display:flex; flex-direction:column; overflow:hidden;">{widgets_html}</div>',
                        height=len(symbols) * 125)

    # 3. ANA EKRAN HEADER
    header_date = datetime.strptime(secilen_tarih, "%Y-%m-%d").strftime("%d.%m.%Y") if secilen_tarih else "--.--.----"
    
    header_html_code = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            body {{ 
                margin: 0; padding: 0; 
                background: transparent; 
                font-family: 'Inter', sans-serif; 
                overflow: hidden; /* Scrollbar oluşmasını engelle */
            }}
            .header-wrapper {{
                background: linear-gradient(90deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 20px;
                padding: 20px 40px; 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                box-shadow: 0 20px 50px -20px rgba(0,0,0,0.5);
                animation: fadeInUp 0.8s ease-out;
                height: 90px;
                box-sizing: border-box;
            }}
            
            .left-section {{ display: flex; flex-direction: column; justify-content: center; }}
            
            .app-title {{ 
                font-size: 32px; 
                font-weight: 800; 
                color: #fff; 
                letter-spacing: -1.5px; 
                display: flex; 
                align-items: center; 
                gap: 15px; 
                text-shadow: 0 4px 10px rgba(0,0,0,0.5); 
                line-height: 1.1;
            }}
            
            .app-subtitle {{ font-size: 13px; color: #a1a1aa; font-weight: 500; margin-top: 6px; letter-spacing: 0.5px; }}
            
            .live-badge {{ 
                display: inline-flex; align-items: center; background: rgba(59, 130, 246, 0.15); color: #60a5fa; 
                padding: 6px 12px; border-radius: 99px; font-size: 10px; font-weight: 700; 
                border: 1px solid rgba(59, 130, 246, 0.3); letter-spacing: 1px; box-shadow: 0 0 20px rgba(59,130,246,0.15);
                position: relative; overflow: hidden; vertical-align: middle; white-space: nowrap;
            }}
            .live-badge::after {{
                content: ''; position: absolute; top:0; left:0; width:100%; height:100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                animation: shine 3s infinite;
            }}
            @keyframes shine {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(100%); }} }}
            .clock-container {{ text-align: right; min-width: 120px; }}
            .location-tag {{ font-size: 10px; color: #71717a; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px; }}
            #report_date {{ font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 800; color: #e4e4e7; letter-spacing: -1px; line-height: 1; }}

            /* --- MOBİL UYUMLULUK --- */
            @media only screen and (max-width: 600px) {{
                .header-wrapper {{
                    flex-direction: column;
                    align-items: flex-start;
                    padding: 15px 20px;
                    height: auto;
                    gap: 15px;
                }}
                .app-title {{ font-size: 22px; flex-wrap: wrap; }}
                .live-badge {{ margin-top: 5px; }}
                .app-subtitle {{ font-size: 12px; }}
                .clock-container {{ 
                    text-align: left; width: 100%; border-top: 1px solid rgba(255,255,255,0.1);
                    padding-top: 10px; margin-top: 5px; display: flex; justify-content: space-between; align-items: center;
                }}
                .location-tag {{ margin-bottom: 0; }}
                #report_date {{ font-size: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header-wrapper">
            <div class="left-section">
                <div class="app-title">
                    Piyasa Monitörü 
                    <span class="live-badge">SİMÜLASYON</span>
                </div>
                <div class="app-subtitle">Yapay Zeka Destekli Enflasyon & Fiyat Analiz Sistemi</div>
            </div>
            <div class="clock-container">
                <div class="location-tag">RAPOR TARİHİ</div>
                <div id="report_date">{header_date}</div>
            </div>
        </div>
    </body>
    </html>
    """
    components.html(header_html_code, height=165)

    # --- BUTON KONTROL PANELİ (PROGRESS BAR DESTEKLİ) ---
    SHOW_SYNC_BUTTON = True 

    if SHOW_SYNC_BUTTON:
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn2:
            if st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True):
                progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
                
                def progress_updater(percentage):
                    progress_bar.progress(min(1.0, max(0.0, percentage)), text="Senkronizasyon sürüyor...")

                res = html_isleyici(progress_updater)
                
                progress_bar.progress(1.0, text="Tamamlandı!")
                time.sleep(0.5)
                progress_bar.empty()
                
                if "OK" in res:
                    st.cache_data.clear()
                    st.toast('Sistem Senkronize Edildi!', icon='🚀') 
                    st.balloons() 
                    time.sleep(1);
                    st.rerun()
                elif "Veri bulunamadı" in res:
                    st.warning("⚠️ Yeni veri akışı yok.")
                else:
                    st.error(res)
    else:
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # 4. HESAPLAMA MOTORU
    if not df_f.empty and not df_s.empty:
        try:
            df_s.columns = df_s.columns.str.strip()
            kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
            ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde adı')
            agirlik_col = next((c for c in df_s.columns if 'agirlik' in c.lower().replace('ğ', 'g').replace('ı', 'i')),
                               'Agirlik_2025')
            
            df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
            df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
            df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
            df_f = df_f[df_f['Fiyat'] > 0]
            
            pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='last').ffill(
                axis=1).bfill(axis=1).reset_index()

            if not pivot.empty:
                if 'Grup' not in df_s.columns:
                    grup_map = {"01": "Gıda", "02": "Alkol ve Tütünlü İçecekler", "03": "Giyim", "04": "Konut",
                                "05": "Ev Eşyası", "06": "Sağlık", "07": "Ulaşım", "08": "Haberleşme", "09": "Eğlence",
                                "10": "Eğitim", "11": "Lokanta", "12": "Çeşitli"}
                    df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")
                df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')

                if agirlik_col in df_analiz.columns:
                    df_analiz[agirlik_col] = pd.to_numeric(df_analiz[agirlik_col], errors='coerce').fillna(1)
                else:
                    df_analiz['Agirlik_2025'] = 1;
                    agirlik_col = 'Agirlik_2025'

                tum_gunler_sirali = sorted([c for c in pivot.columns if c != 'Kod'])
                
                if secilen_tarih and secilen_tarih in tum_gunler_sirali:
                    idx = tum_gunler_sirali.index(secilen_tarih)
                    gunler = tum_gunler_sirali[:idx+1]
                else:
                    if tum_tarihler:
                        son_tarih = tum_tarihler[0]
                        if son_tarih in tum_gunler_sirali:
                             idx = tum_gunler_sirali.index(son_tarih)
                             gunler = tum_gunler_sirali[:idx+1]
                        else:
                             gunler = tum_gunler_sirali 
                    else:
                        gunler = tum_gunler_sirali 

                if not gunler:
                    st.error("Seçilen tarih için veri oluşturulamadı.")
                    return

                son = gunler[-1];
                dt_son = datetime.strptime(son, '%Y-%m-%d')
                simdi_yil = dt_son.year

                # --- GÜNCELLEME: DİNAMİK REFERANS MANTIĞI ---
                # Eğer içinde bulunduğumuz ay Şubat veya sonrasıysa (Yeni Veriler) -> Baz: OCAK 2026
                # Eğer içinde bulunduğumuz ay Ocak ise (Geçmiş Veriler) -> Baz: ARALIK 2025
                
                target_cols = []
                baz_tanimi_text = ""

                # Şubat 2026 ve sonrası için mantık (Yeni dönem)
                if dt_son.year == 2026 and dt_son.month >= 2:
                    ocak_prefix = f"{simdi_yil}-01"
                    target_cols = [c for c in gunler if c.startswith(ocak_prefix)]
                    baz_tanimi_text = f"Ocak {simdi_yil}"
                
                # Ocak 2026 ve öncesi için mantık (Eski dönem)
                else:
                    onceki_yil_aralik_prefix = f"{simdi_yil - 1}-12"
                    target_cols = [c for c in gunler if c.startswith(onceki_yil_aralik_prefix)]
                    baz_tanimi_text = f"Aralık {simdi_yil - 1}"

                # Sütunu Seçme İşlemi
                if target_cols:
                    baz_col = target_cols[-1] # İlgili ayın en son verisini al
                    baz_tanimi = baz_tanimi_text
                else:
                    # Eğer istenen baz ayı verisi yoksa (örn. yeni yılın ilk günü), listenin en başını al
                    baz_col = gunler[0]
                    baz_tanimi = f"Başlangıç ({baz_col})"
                # ---------------------------------------------

                def geometrik_ortalama_hesapla(row):
                    valid_vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
                    if not valid_vals:
                        return np.nan
                    return np.exp(np.mean(np.log(valid_vals)))

                bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
                bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]

                if not bu_ay_cols: bu_ay_cols = [son]

                df_analiz['Aylik_Ortalama'] = df_analiz[bu_ay_cols].apply(geometrik_ortalama_hesapla, axis=1)
                
                ma3_baslik = "Son 3 Gün Ort."
                if len(gunler) >= 3:
                      last_3_dates = gunler[-3:]
                      start_d = datetime.strptime(last_3_dates[0], '%Y-%m-%d').strftime('%d.%m')
                      end_d = datetime.strptime(last_3_dates[-1], '%Y-%m-%d').strftime('%d.%m')
                      ma3_baslik = f"Ortalama ({start_d} - {end_d})"
                      
                      df_analiz[ma3_baslik] = df_analiz[gunler[-3:]].mean(axis=1)

                gecerli_veri = df_analiz.dropna(subset=['Aylik_Ortalama', baz_col]).copy()
                enf_genel = 0.0
                enf_gida = 0.0

                if not gecerli_veri.empty:
                    w = gecerli_veri[agirlik_col]
                    p_relative = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
                    genel_endeks = (w * p_relative).sum() / w.sum() * 100
                    enf_genel = genel_endeks - 100

                    gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
                    if not gida_df.empty:
                        w_g = gida_df[agirlik_col]
                        p_rel_g = gida_df['Aylik_Ortalama'] / gida_df[baz_col]
                        enf_gida = ((w_g * p_rel_g).sum() / w_g.sum() * 100) - 100

                    df_analiz['Fark'] = (df_analiz['Aylik_Ortalama'] / df_analiz[baz_col]) - 1
                else:
                    df_analiz['Fark'] = 0.0

                enf_onceki = 0.0
                if len(bu_ay_cols) > 1:
                    onceki_cols = bu_ay_cols[:-1] 
                    df_analiz['Onceki_Ortalama'] = df_analiz[onceki_cols].apply(geometrik_ortalama_hesapla, axis=1)
                    gecerli_veri_prev = df_analiz.dropna(subset=['Onceki_Ortalama', baz_col])

                    if not gecerli_veri_prev.empty:
                        w_p = gecerli_veri_prev[agirlik_col]
                        p_rel_p = gecerli_veri_prev['Onceki_Ortalama'] / gecerli_veri_prev[baz_col]
                        genel_endeks_prev = (w_p * p_rel_p).sum() / w_p.sum() * 100
                        enf_onceki = genel_endeks_prev - 100
                    else:
                        enf_onceki = enf_genel 
                else:
                    enf_onceki = enf_genel

                trend_data = []
                analiz_gunleri = bu_ay_cols

                def get_geo_mean_vectorized(df_in, cols):
                    data = df_in[cols].values.astype(float)
                    data[data <= 0] = np.nan
                    with np.errstate(divide='ignore', invalid='ignore'):
                        log_data = np.log(data)
                    mean_log = np.nanmean(log_data, axis=1)
                    return np.exp(mean_log)

                for i in range(1, len(analiz_gunleri) + 1):
                    aktif_gunler = analiz_gunleri[:i]
                    su_anki_tarih = aktif_gunler[-1]

                    df_analiz[f'Geo_Temp_{i}'] = get_geo_mean_vectorized(df_analiz, aktif_gunler)
                    gecerli = df_analiz.dropna(subset=[f'Geo_Temp_{i}', baz_col])
                    
                    if not gecerli.empty:
                        w = gecerli[agirlik_col]
                        p_rel = gecerli[f'Geo_Temp_{i}'] / gecerli[baz_col]
                        idx_val = (w * p_rel).sum() / w.sum() * 100
                        trend_data.append({"Tarih": su_anki_tarih, "TÜFE": idx_val})
                    else:
                        prev_val = trend_data[-1]["TÜFE"] if trend_data else 100.0
                        trend_data.append({"Tarih": su_anki_tarih, "TÜFE": prev_val})

                df_trend = pd.DataFrame(trend_data)
                if not df_trend.empty:
                    df_trend['Tarih'] = pd.to_datetime(df_trend['Tarih'])

                kumu_fark = enf_genel - enf_onceki
                kumu_icon_color = "#ef4444" if kumu_fark > 0 else "#10b981"
                kumu_sub_text = f"Önceki: %{enf_onceki:.2f} ({'+' if kumu_fark > 0 else ''}{kumu_fark:.2f})"

                df_analiz['Max_Fiyat'] = df_analiz[gunler].max(axis=1)
                df_analiz['Min_Fiyat'] = df_analiz[gunler].min(axis=1)

                # --- AY SONU TAHMİNİ (SABİT TARİH: 24.01.2026) ---
                # --- AY SONU TAHMİNİ (SABİT TARİH: 31.01.2026) ---
                target_fixed_date = "2026-01-31"  # <-- TARİH GÜNCELLENDİ
                month_end_forecast = 0.0

                # Pivot tablodaki tüm tarihleri kullanarak 31 Ocak'a kadar olan sütunları bulalım
                fixed_cols = [c for c in tum_gunler_sirali if c.startswith("2026-01") and c <= target_fixed_date]

                if fixed_cols:
                    # 31 Ocak (veya öncesi) için aylık geometrik ortalamayı hesapla
                    df_analiz['Fixed_Ortalama_Target'] = df_analiz[fixed_cols].apply(geometrik_ortalama_hesapla, axis=1)
                    
                    # Enflasyon hesabı
                    gecerli_fixed = df_analiz.dropna(subset=['Fixed_Ortalama_Target', baz_col])
                    
                    if not gecerli_fixed.empty:
                        w_f = gecerli_fixed[agirlik_col]
                        p_rel_f = gecerli_fixed['Fixed_Ortalama_Target'] / gecerli_fixed[baz_col]
                        fixed_endeks = (w_f * p_rel_f).sum() / w_f.sum() * 100
                        month_end_forecast = fixed_endeks - 100
                    else:
                        month_end_forecast = 0.0
                else:
                    month_end_forecast = 0.0

                if len(gunler) >= 2:
                    onceki_gun = gunler[-2]
                    df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun]) - 1
                    gun_farki = (dt_son - datetime.strptime(baz_col, '%Y-%m-%d')).days
                    
                    anomaliler = df_analiz[df_analiz['Gunluk_Degisim'] > 0.05].copy()
                    anomaliler = anomaliler.sort_values('Gunluk_Degisim', ascending=False)
                else:
                    df_analiz['Gunluk_Degisim'] = 0
                    gun_farki = 0
                    anomaliler = pd.DataFrame()

                inc = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(5)
                dec = df_analiz.sort_values('Gunluk_Degisim', ascending=True).head(5)
                items = []

                for _, r in inc.iterrows():
                    if r['Gunluk_Degisim'] > 0:
                        items.append(
                            f"<span style='color:#f87171; font-weight:700;'>▲ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")
                for _, r in dec.iterrows():
                    if r['Gunluk_Degisim'] < 0:
                        items.append(
                            f"<span style='color:#34d399; font-weight:700;'>▼ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")

                ticker_html_content = " &nbsp;&nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;&nbsp; ".join(
                    items) if items else "<span style='color:#71717a'>Piyasada yatay seyir izlenmektedir.</span>"
                st.markdown(f"""<div class="ticker-wrap animate-enter"><div class="ticker-move">{ticker_html_content}</div></div>""",
                            unsafe_allow_html=True)
                
                st.markdown(f"""
                <script>
                    document.title = "🔴 %{enf_genel:.2f} | Piyasa Monitörü";
                </script>
                """, unsafe_allow_html=True)

                df_resmi, msg = get_official_inflation()
                resmi_aylik_enf = 0.0;
                resmi_tarih_str = "-";
                if df_resmi is not None and not df_resmi.empty:
                    df_resmi_filtered = df_resmi[df_resmi['Tarih'] <= dt_son].sort_values('Tarih')
                    
                    if len(df_resmi_filtered) > 1:
                        try:
                            son_veri = df_resmi_filtered.iloc[-1];
                            onceki_veri = df_resmi_filtered.iloc[-2]
                            resmi_aylik_enf = ((son_veri['Resmi_TUFE'] / onceki_veri['Resmi_TUFE']) - 1) * 100
                            aylar = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz',
                                     8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
                            resmi_tarih_str = f"{aylar[son_veri['Tarih'].month]} {son_veri['Tarih'].year}"
                        except:
                            pass

                def kpi_card(title, val, sub, sub_color, accent_color, icon, delay_class=""):
                    sub_html = f"<div class='kpi-sub'><span style='display:inline-block; width:6px; height:6px; background:{sub_color}; border-radius:50%; box-shadow:0 0 5px {sub_color};'></span><span style='color:{sub_color}; filter: brightness(1.2);'>{sub}</span></div>" if sub else ""
                    card_html = f'<div class="kpi-card {delay_class}"><div class="kpi-bg-icon" style="color:{accent_color};">{icon}</div><div class="kpi-content"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div>{sub_html}</div></div>'
                    st.markdown(card_html, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    guncel_tarih_etiket = datetime.strptime(son, '%Y-%m-%d').strftime('%d.%m')
                    kpi_card(f"Enflasyon ({guncel_tarih_etiket})", f"%{enf_genel:.2f}", kumu_sub_text, kumu_icon_color, "#ef4444", "📈", "delay-1")
                with c2:
                    kpi_card("Gıda Enflasyonu", f"%{enf_gida:.2f}", "Mutfak Sepeti", "#fca5a5", "#10b981", "🛒", "delay-2")
                with c3:
                    # 31 OCAK DEĞERİ STATİK OLARAK 4.01 SABİTLENDİ
                    kpi_card("Ocak Tahmini (31.01.2026)", "%4.01", "Nihai Tahmin", "#a78bfa", "#8b5cf6", "🤖", "delay-3")
                with c4:
                    kpi_card("Resmi TÜİK Verisi", f"%{resmi_aylik_enf:.2f}", f"{resmi_tarih_str}", "#fbbf24", "#f59e0b",
                             "🏛️", "delay-3")
                
                if not anomaliler.empty:
                    st.error(f"⚠️ DİKKAT: Piyasadaki {len(anomaliler)} üründe ani fiyat artışı (Şok) tespit edildi!")
                    with st.expander("Şok Yaşanan Ürünleri İncele"):
                        df_show = anomaliler[[ad_col, onceki_gun, son, 'Gunluk_Degisim']].copy()
                    
                        new_columns = {
                            ad_col: "Ürün",
                            onceki_gun: f"Dünkü Fiyat ({onceki_gun})",
                            son: f"Bugünkü Fiyat ({son})",
                            'Gunluk_Degisim': "Şok Olan Üründeki Değişim"
                        }
                        df_show = df_show.rename(columns=new_columns)
                    
                        styled_df = (
                            df_show.style
                            .format({
                                f"Dünkü Fiyat ({onceki_gun})": "{:.4f} ₺", 
                                f"Bugünkü Fiyat ({son})": "{:.4f} ₺",
                                "Şok Olan Üründeki Değişim": lambda x: f"%{x*100:.2f}" 
                            })
                            .set_properties(subset=["Şok Olan Üründeki Değişim"], **{'text-align': 'right'})
                        )
                    
                        st.dataframe(
                            styled_df,
                            hide_index=True,
                            use_container_width=True,
                            height=len(df_show) * 35 + 38 
                        )

                st.markdown("<br>", unsafe_allow_html=True)
                
                durum_mesaji = ""
                if enf_genel > 5:
                    durum_emoji = "🔥"
                    durum_baslik = "YÜKSEK RİSK UYARISI"
                    durum_mesaji = "Piyasada volatilite kritik seviyelerde. Özellikle gıda sepetindeki artış trendi, ay sonu hedeflerini riske atıyor."
                    kutu_rengi = "linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)" 
                    kenar_rengi = "#ef4444"
                elif enf_genel > 2:
                    durum_emoji = "⚠️"
                    durum_baslik = "DİKKATLİ İZLEME"
                    durum_mesaji = "Piyasa beklentilerin hafif üzerinde seyrediyor. Ürün bazlı şoklar gözlemlendi."
                    kutu_rengi = "linear-gradient(90deg, rgba(251, 191, 36, 0.1) 0%, rgba(251, 191, 36, 0.05) 100%)" 
                    kenar_rengi = "#f59e0b"
                else:
                    durum_emoji = "✅"
                    durum_baslik = "STABİL GÖRÜNÜM"
                    durum_mesaji = "Fiyatlamalar olağan seyirde. Piyasa volatilitesi düşük."
                    kutu_rengi = "linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)" 
                    kenar_rengi = "#10b981"

                ai_placeholder = st.empty()
                stream_text(durum_mesaji, ai_placeholder, kutu_rengi, kenar_rengi, durum_emoji, durum_baslik)
                
                def style_chart(fig, is_pdf=False, is_sunburst=False):
                    if is_pdf:
                        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
                    else:
                        layout_args = dict(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
                            margin=dict(l=0, r=0, t=40, b=0),
                            hoverlabel=dict(bgcolor="#18181b", bordercolor="rgba(255,255,255,0.1)", font=dict(color="#fff")),
                        )
                        if not is_sunburst:
                            layout_args.update(dict(
                                xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)",
                                           gridcolor='rgba(255,255,255,0.05)', dtick="M1"),
                                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False,
                                           gridwidth=1)
                            ))
                        fig.update_layout(**layout_args)
                        fig.update_layout(modebar=dict(bgcolor='rgba(0,0,0,0)', color='#71717a', activecolor='#fff'))
                    return fig
                
                df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
                
                t_sektor, t_ozet, t_veri, t_rapor = st.tabs(
                    ["📂 KATEGORİ DETAY", "📊 PİYASA ÖZETİ", "📋 TAM LİSTE", "📝 RAPORLAMA"])

                with t_sektor:
                    st.markdown("### 🏆 Sektörel Liderler")
                    
                    df_analiz['Agirlikli_Fark'] = df_analiz['Fark'] * df_analiz[agirlik_col]
                    sektor_ozet = df_analiz.groupby('Grup').agg({
                        'Agirlikli_Fark': 'sum',
                        'Agirlik_2025': 'sum'
                    }).reset_index()
                    sektor_ozet['Ortalama_Degisim'] = (sektor_ozet['Agirlikli_Fark'] / sektor_ozet['Agirlik_2025']) * 100
                    
                    top_sektorler = sektor_ozet.sort_values('Agirlik_2025', ascending=False).head(4)
                    
                    sc_cols = st.columns(4)
                    for idx, (i, row) in enumerate(top_sektorler.iterrows()):
                        degisim = row['Ortalama_Degisim']
                        renk = "#ef4444" if degisim > 0 else "#10b981"
                        icon = "▲" if degisim > 0 else "▼"
                        
                        smart_card_html = f"""
                        <div class="smart-card delay-1">
                            <div class="sc-title">{row['Grup']}</div>
                            <div class="sc-val">
                                <span style="color:{renk}">{icon}</span>
                                %{degisim:.2f}
                            </div>
                        </div>
                        """
                        with sc_cols[idx]:
                            st.markdown(smart_card_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("### 🔍 Detaylı Fiyat Analizi")

                    f_col1, f_col2 = st.columns([1, 2])
                    with f_col1:
                        # KATEGORİ SEÇİMİ (BOŞ VARSAYILAN)
                        kategoriler = ["Kategori Seçiniz..."] + sorted(df_analiz['Grup'].unique().tolist())
                        secilen_kategori = st.selectbox("Kategori Filtrele:", kategoriler)
                    with f_col2:
                        arama_terimi = st.text_input("Ürün Ara...", placeholder="Örn: Zeytinyağı, Beyaz Peynir...")

                    # BOŞ KATEGORİ KONTROLÜ
                    if secilen_kategori != "Kategori Seçiniz...":
                        df_goster = df_analiz.copy()
                        df_goster = df_goster[df_goster['Grup'] == secilen_kategori]

                        if arama_terimi:
                            df_goster = df_goster[
                                df_goster[ad_col].astype(str).str.contains(arama_terimi, case=False, na=False)]

                        if not df_goster.empty:
                            cols = st.columns(4)
                            for idx, row in df_goster.iterrows():
                                fiyat = row[son]
                                fark = row.get('Gunluk_Degisim', 0) * 100

                                if fark > 0:
                                    badge_cls = "pg-red"; symbol = "▲"
                                elif fark < 0:
                                    badge_cls = "pg-green"; symbol = "▼"
                                else:
                                    badge_cls = "pg-yellow"; symbol = "-"

                                card_html = f"""<div class="pg-card delay-2"><div class="pg-name">{html.escape(str(row[ad_col]))}</div><div class="pg-price">{fiyat:.2f} ₺</div><div class="pg-badge {badge_cls}">{symbol} %{fark:.2f}</div></div>"""
                                with cols[idx % 4]:
                                    st.markdown(card_html, unsafe_allow_html=True)
                                    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
                        else:
                            st.info("🔍 Aradığınız kriterlere uygun ürün bulunamadı.")
                    else:
                        st.info("👆 Lütfen ürünleri görüntülemek için bir kategori seçiniz.")

                with t_ozet:
                    st.subheader("📊 Piyasa Derinliği ve Dağılım")
                    
                    ozet_col1, ozet_col2 = st.columns([2, 1])
                    
                    with ozet_col1:
                        df_analiz['Fark_Yuzde'] = pd.to_numeric(df_analiz['Fark_Yuzde'], errors='coerce')
                        
                        fig_hist = px.histogram(df_analiz, x="Fark_Yuzde", nbins=20, 
                                                title="Fiyat Değişim Dağılımı",
                                                labels={"Fark_Yuzde": "Değişim Oranı (%)"},
                                                color_discrete_sequence=["#3b82f6"])
                        
                        fig_hist.update_layout(
                            bargap=0.1,
                            margin=dict(l=10, r=10, t=40, b=10) 
                        )
                        
                        fig_hist.update_xaxes(
                            type="linear",        
                            tickmode="auto",        
                            nticks=5,                
                            tickformat=".4f",        
                            title_font=dict(size=11),
                            tickfont=dict(size=10, color="#a1a1aa")
                        )
                        
                        fig_hist.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
                        
                        st.plotly_chart(make_neon_chart(style_chart(fig_hist)), use_container_width=True)
                        
                    with ozet_col2:
                          rising = len(df_analiz[df_analiz['Fark'] > 0])
                          falling = len(df_analiz[df_analiz['Fark'] < 0])
                          total = len(df_analiz)
                          if total > 0:
                            r_pct = (rising / total) * 100
                            f_pct = (falling / total) * 100
                            n_pct = 100 - r_pct - f_pct
                            
                            st.markdown(f"""
                            <div class="delay-1 animate-enter" style="background:rgba(255,255,255,0.03); border-radius:12px; padding:20px; border:1px solid rgba(255,255,255,0.05);">
                                <div style="font-size:12px; color:#a1a1aa; margin-bottom:10px;">PİYASA YÖNÜ</div>
                                <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-weight:600;">
                                    <span style="color:#ef4444">Yükselen</span>
                                    <span>{rising}</span>
                                </div>
                                <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-weight:600;">
                                    <span style="color:#10b981">Düşen</span>
                                    <span>{falling}</span>
                                </div>
                                <div style="width:100%; height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden; display:flex;">
                                    <div style="width:{r_pct}%; background:#ef4444;"></div>
                                    <div style="width:{n_pct}%; background:transparent;"></div>
                                    <div style="width:{f_pct}%; background:#10b981;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    c_ozet1, c_ozet2 = st.columns(2)
                    with c_ozet1:
                        st.subheader("☀️ Pazar Dağılımı")
                        
                        grafik_tipi = st.radio("Görünüm Modu:", ["Halka (Sunburst)", "Kutu (Treemap)"], 
                                               horizontal=True, label_visibility="collapsed")
                        
                        if grafik_tipi == "Halka (Sunburst)":
                            fig_sun = px.sunburst(
                                df_analiz, path=['Grup', ad_col], values=agirlik_col, color='Fark',
                                color_continuous_scale='RdYlGn_r', title=None
                            )
                            st.plotly_chart(style_chart(fig_sun, is_sunburst=True), use_container_width=True)
                        else:
                            fig_tree = px.treemap(
                                df_analiz, path=[px.Constant("Piyasa"), 'Grup', ad_col], 
                                values=agirlik_col, color='Fark',
                                color_continuous_scale='RdYlGn_r',
                                hover_data={ad_col:True, 'Fark':':.2%'}
                            )
                            fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0))
                            st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)

                    with c_ozet2:
                        st.subheader("💧 Sektörel Etki")
                        toplam_agirlik = df_analiz[agirlik_col].sum()
                        df_analiz['Katki_Puan'] = (df_analiz['Fark'] * df_analiz[agirlik_col] / toplam_agirlik) * 100
                        df_sektor_katki = df_analiz.groupby('Grup')['Katki_Puan'].sum().reset_index().sort_values(
                            'Katki_Puan', ascending=False)
                        fig_water = go.Figure(go.Waterfall(
                            name="", orientation="v", measure=["relative"] * len(df_sektor_katki),
                            x=df_sektor_katki['Grup'], textposition="outside",
                            text=df_sektor_katki['Katki_Puan'].apply(lambda x: f"{x:.4f}"),
                            y=df_sektor_katki['Katki_Puan'], connector={"line": {"color": "#52525b"}},
                            decreasing={"marker": {"color": "#34d399", "line": {"width": 0}}},
                            increasing={"marker": {"color": "#f87171", "line": {"width": 0}}},
                            totals={"marker": {"color": "#f8fafc"}}
                        ))
                        st.plotly_chart(make_neon_chart(style_chart(fig_water)), use_container_width=True)

                with t_veri:
                    st.markdown("### 📋 Veri Seti")
                    
                    def fix_sparkline(row):
                        vals = row.tolist()
                        # Eğer tüm değerler aynıysa (örneğin hepsi 80), grafik hata vermesin diye
                        # son değeri mikroskobik düzeyde değiştiriyoruz.
                        if vals and min(vals) == max(vals):
                            vals[-1] += 0.00001
                        return vals
    
                    df_analiz['Fiyat_Trendi'] = df_analiz[gunler].apply(fix_sparkline, axis=1)
    
                    st.data_editor(
                        df_analiz[['Grup', ad_col, 'Fiyat_Trendi', baz_col, son, 'Gunluk_Degisim']], 
                        column_config={
                            "Fiyat_Trendi": st.column_config.LineChartColumn(
                                "Fiyat Grafiği", 
                                width="medium", 
                                help="Seçilen dönem içindeki fiyat hareketi",
                                y_min=0  # <--- BURAYA BU SATIRI EKLEDİK (Grafiği 0'dan başlatır)
                            ),
                            ad_col: "Ürün", 
                            "Grup": "Kategori",
                            baz_col: st.column_config.NumberColumn(f"Fiyat ({baz_tanimi})", format="%.2f ₺"),
                            son: st.column_config.NumberColumn(f"Fiyat ({son})", format="%.2f ₺"),
                            "Gunluk_Degisim": st.column_config.ProgressColumn(
                                "Günlük Değişim",
                                help="Bir önceki güne göre değişim",
                                format="%.2f%%",
                                min_value=-0.5,
                                max_value=0.5,
                            ),
                        },
                        hide_index=True, use_container_width=True, height=600
                    )
                    
                    # --- EXCEL HAZIRLIĞI ---
                    export_cols = ['Kod', 'Grup', ad_col]
                    if agirlik_col in df_analiz.columns:
                        export_cols.append(agirlik_col)
                    export_cols.extend(gunler)
                    if 'Fark' in df_analiz.columns:
                        export_cols.append('Fark')
                    
                    final_cols = [c for c in export_cols if c in df_analiz.columns]
                    df_export = df_analiz[final_cols].copy()

                    output = BytesIO()
                    try:
                        import xlsxwriter
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: 
                            df_export.to_excel(writer, index=False, sheet_name='Analiz')
                            workbook = writer.book
                            worksheet = writer.sheets['Analiz']
                            format_red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                            format_green = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
                            worksheet.set_column('A:Z', 12) 
                            if 'Fark' in df_export.columns:
                                fark_col_idx = df_export.columns.get_loc('Fark')
                                row_count = len(df_export)
                                worksheet.conditional_format(1, fark_col_idx, row_count, fark_col_idx,
                                                             {'type': 'cell', 'criteria': '>', 'value': 0, 'format': format_red})
                                worksheet.conditional_format(1, fark_col_idx, row_count, fark_col_idx,
                                                             {'type': 'cell', 'criteria': '<', 'value': 0, 'format': format_green})
                    except ImportError:
                         with pd.ExcelWriter(output) as writer:
                             df_export.to_excel(writer, index=False)

                    st.download_button(
                        label="📥 Excel İndir", 
                        data=output.getvalue(), 
                        file_name=f"Fiyat_Analizi_{son}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )

                with t_rapor:
                    st.markdown("### 📝 Stratejik Görünüm Raporu")
                    
                    rap_text = generate_detailed_static_report(df_analiz=df_analiz, tarih=son,
                                                               enf_genel=enf_genel, enf_gida=enf_gida,
                                                               gun_farki=gun_farki, tahmin=month_end_forecast,
                                                               ad_col=ad_col, agirlik_col=agirlik_col)
                    
                    st.markdown(f"""
                    <div class="delay-3 animate-enter" style="
                        background: rgba(255,255,255,0.03); 
                        padding: 30px; 
                        border-radius: 12px; 
                        border: 1px solid rgba(255,255,255,0.08); 
                        color: #e4e4e7; 
                        line-height: 1.8; 
                        font-family: 'Inter', sans-serif;
                        font-size: 15px;
                        box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);">
                        {rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    c_dl1, c_dl2 = st.columns([1, 4])
                    with c_dl1:
                        word_buffer = create_word_report(rap_text, son, df_analiz)
                        st.download_button(
                            label="📥 Rapor İndir ",
                            data=word_buffer,
                            file_name=f"Strateji_Raporu_{son}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary"
                        )

        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
    st.markdown(
        '<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - CONFIDENTIAL</div>',
        unsafe_allow_html=True)
        
if __name__ == "__main__":
    dashboard_modu()
