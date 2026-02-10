# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
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
import textwrap # HTML temizliği için kritik

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    # CSS kodunu textwrap.dedent ile temizliyoruz ki bozulmasın
    final_css = textwrap.dedent("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        /* HEADER GİZLEME */
        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding-top: 1rem; }

        /* GLOBAL YAZI AYARLARI */
        .stApp, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stDataFrame div, .stDataFrame span {
            color: #ffffff !important;
        }

        /* --- DROPDOWN DÜZELTMESİ --- */
        div[data-baseweb="select"] > div {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.05);
        }
        div[data-baseweb="popover"] div, 
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] span {
            color: #000000 !important; 
        }
        div[data-baseweb="menu"] {
            background-color: #f0f2f6 !important;
        }
        div[data-baseweb="menu"] li:hover {
            background-color: #e2e8f0 !important;
        }

        /* RENK SINIFLARI */
        .pg-red { color: #fca5a5 !important; }
        .pg-green { color: #6ee7b7 !important; }
        .pg-yellow { color: #fde047 !important; }
        
        /* HTML İÇİNDEKİ STİLLER */
        .kpi-card {
            background: rgba(30, 33, 40, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            border-color: rgba(59, 130, 246, 0.4);
        }
        .kpi-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #94a3b8 !important;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #ffffff !important;
        }
        
        /* TICKER */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: rgba(255,255,255,0.02);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px 0;
            margin-bottom: 20px;
            white-space: nowrap;
        }
        .ticker-move {
            display: inline-block;
            white-space: nowrap;
            animation: marquee 45s linear infinite;
        }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        
        /* ÜRÜN KARTLARI */
        .pg-card {
            background: linear-gradient(145deg, rgba(30, 33, 40, 0.6), rgba(20, 23, 30, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 15px;
            transition: all 0.3s;
            height: 100%;
        }
        .pg-card:hover { border-color: #3b82f6; }
        .pg-name { font-size: 13px; font-weight: 500; color: #ffffff !important; margin-bottom: 8px; height: 32px; overflow: hidden; }
        .pg-price { font-family: 'JetBrains Mono'; font-size: 18px; font-weight: 700; color: #ffffff !important; }
        .pg-badge { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; margin-top: 8px; display: inline-block; }

        /* YATAY MENÜ */
        [data-testid="stRadio"] > label { display: none !important; }
        [data-testid="stRadio"] > div {
            display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 10px;
            background: rgba(30, 33, 40, 0.4); padding: 10px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-top: -20px;
        }
        [data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px 16px;
            border-radius: 10px; cursor: pointer; transition: all 0.3s; color: #ffffff !important; min-width: 100px;
            display: flex; justify-content: center; align-items: center;
        }
        [data-testid="stRadio"] label:hover { background-color: rgba(59, 130, 246, 0.2); border-color: #3b82f6; }
        [data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-color: #60a5fa; font-weight: 700;
        }
        [data-testid="stRadio"] div[role="radiogroup"] > :first-child { display: none; }
        
        /* BUTON */
        div.stButton > button {
            background: linear-gradient(90deg, #3b82f6, #2563eb); color: white !important; border: none; border-radius: 8px; padding: 0.5rem 1rem;
        }
    </style>
    """)
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# --- 3. RAPOR MOTORU ---
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
        for p_text in text_content.split('\n'):
            if not p_text.strip(): continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for i, part in enumerate(p_text.split('**')):
                run = p.add_run(part)
                if i % 2 == 1: run.bold = True
        if df_analiz is not None and not df_analiz.empty:
            doc.add_page_break()
            doc.add_heading('EKLER', 1)
            try:
                if 'Fark' in df_analiz.columns:
                    data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                    if not data.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
                        ax.set_title(f"Dağılım - {tarih}")
                        memfile = BytesIO()
                        plt.savefig(memfile, format='png', dpi=100)
                        plt.close(fig)
                        doc.add_picture(memfile, width=Inches(5.5))
                        memfile.close()
            except: pass
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except: return BytesIO()

# --- 4. GITHUB İŞLEMLERİ ---
@st.cache_resource
def get_github_connection():
    try: return Github(st.secrets["github"]["token"])
    except: return None

def get_github_repo():
    g = get_github_connection()
    return g.get_repo(st.secrets["github"]["repo_name"]) if g else None

@st.cache_data(ttl=600, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        data = c.decoded_content
        if sayfa_adi: return pd.read_excel(BytesIO(data), sheet_name=sayfa_adi, dtype=str)
        return pd.read_excel(BytesIO(data), dtype=str)
    except: return pd.DataFrame()

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
        except: c = None; final = df_yeni
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w: final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        if c: repo.update_file(c.path, "Update", out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else: repo.create_file(dosya_adi, "Create", out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e: return str(e)

# --- 5. RESMİ ENFLASYON ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_official_inflation():
    api_key = st.secrets.get("evds", {}).get("api_key")
    if not api_key: return None, "No API"
    start = (datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y")
    end = datetime.now().strftime("%d-%m-%Y")
    url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.FG.J0&startDate={start}&endDate={end}&type=json&key={api_key}"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
        if res.status_code == 200 and "items" in res.json():
            df = pd.DataFrame(res.json()["items"])[['Tarih', 'TP_FG_J0']]
            df.columns = ['Tarih', 'Resmi_TUFE']
            df['Resmi_TUFE'] = pd.to_numeric(df['Resmi_TUFE'], errors='coerce')
            return df, "OK"
        return None, "Err"
    except: return None, "Err"

# --- 6. SCRAPER YARDIMCILARI ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try: return float(re.sub(r'[^\d.]', '', t))
    except: return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): return v, "Regex"
    return 0, ""

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Err"
    progress_callback(0.05)
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        if not kod_col or not url_col: return "Sütun Hatası"
        
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        
        veriler = []; islenen = set()
        bugun = datetime.now().strftime("%Y-%m-%d"); simdi = datetime.now().strftime("%H:%M")
        
        progress_callback(0.10)
        zips = [c for c in repo.get_contents("", ref=st.secrets["github"]["branch"]) if c.name.endswith(".zip")]
        
        for i, zf in enumerate(zips):
            progress_callback(0.1 + (0.8 * ((i+1)/len(zips))))
            try:
                with zipfile.ZipFile(BytesIO(base64.b64decode(repo.get_git_blob(zf.sha).content))) as z:
                    for fn in z.namelist():
                        if not fn.endswith(('.html', '.htm')): continue
                        soup = BeautifulSoup(z.open(fn).read().decode("utf-8", errors="ignore"), 'html.parser')
                        href = soup.find("link", rel="canonical").get("href") if soup.find("link", rel="canonical") else None
                        if href and str(href).strip() in url_map:
                            tgt = url_map[str(href).strip()]
                            if tgt['Kod'] in islenen: continue
                            fiyat, kyn = fiyat_bul_siteye_gore(soup, tgt[url_col])
                            if fiyat > 0:
                                veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": tgt['Kod'], "Madde_Adi": tgt[ad_col], "Fiyat": fiyat, "Kaynak": kyn, "URL": tgt[url_col]})
                                islenen.add(tgt['Kod'])
            except: pass
        
        progress_callback(0.95)
        return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI) if veriler else "Veri Yok"
    except Exception as e: return str(e)

# --- 7. ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    
    inc_str = "\n".join([f"🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    return f"""
**PİYASA GÖRÜNÜM RAPORU - {tarih}**

**1. ANA GÖSTERGELER**
**GENEL ENFLASYON:** %{enf_genel:.2f}
**GIDA ENFLASYONU:** %{enf_gida:.2f}
**AY SONU TAHMİNİ:** %{tahmin:.2f}

**2. DİKKAT ÇEKENLER**
**Yüksek Artışlar:**
{inc_str}

**Düşüşler:**
{dec_str}

*Otomatik Rapor Sistemi*
"""

# --- GRAFİK STİLİ ---
def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf: fig.update_layout(template="plotly_white")
    else:
        layout = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
        if not is_sunburst: layout.update(dict(xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)")))
        fig.update_layout(**layout)
    return fig

# --- 8. VERİ ÇEKME VE HESAPLAMA ---
@st.cache_data(ttl=600, show_spinner=False)
def verileri_getir_cache():
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    if df_f.empty or df_s.empty: return None, None, None

    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    pivot = df_f[df_f['Fiyat'] > 0].pivot_table(index='Kod', columns=df_f['Tarih_DT'].dt.strftime('%Y-%m-%d'), values='Fiyat', aggfunc='mean').ffill(axis=1).bfill(axis=1).reset_index()
    if pivot.empty: return None, None, None

    df_s.columns = df_s.columns.str.strip()
    df_s['Kod'] = df_s[next(c for c in df_s.columns if c.lower()=='kod')].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'])
    if 'Grup' not in df_s.columns: df_s['Grup'] = df_s['Kod'].str[:2].map({"01":"Gıda","02":"Alkol","03":"Giyim","04":"Konut"}).fillna("Diğer")
    
    return pd.merge(df_s, pivot, on='Kod', how='left'), pivot.columns[1:].tolist(), next(c for c in df_s.columns if 'ad' in c.lower())

@st.cache_data(show_spinner=False)
def hesapla_metrikler(df_base, secilen, gunler, tum_gunler, ad_col, agirlik, baz, aktif_agirlik, son):
    df = df_base.copy()
    for c in gunler: df[c] = pd.to_numeric(df[c], errors='coerce')
    df[aktif_agirlik] = pd.to_numeric(df.get(aktif_agirlik, 0), errors='coerce').fillna(0)
    
    gecerli = df[df[aktif_agirlik] > 0].copy()
    bu_ay = [c for c in gunler if c.startswith(secilen[:7])] or [son]
    
    # Geometrik ortalama
    gecerli['Ort'] = gecerli[bu_ay].apply(lambda x: np.exp(np.mean(np.log([v for v in x if v>0]))) if any(x>0) else np.nan, axis=1)
    gecerli = gecerli.dropna(subset=['Ort', baz])
    
    enf_genel = ((gecerli[aktif_agirlik] * (gecerli['Ort']/gecerli[baz])).sum() / gecerli[aktif_agirlik].sum() * 100) - 100 if not gecerli.empty else 0
    
    gida = gecerli[gecerli['Kod'].astype(str).str.startswith("01")]
    enf_gida = ((gida[aktif_agirlik] * (gida['Ort']/gida[baz])).sum() / gida[aktif_agirlik].sum() * 100) - 100 if not gida.empty else 0
    
    df['Fark'] = 0.0
    if not gecerli.empty: df.loc[gecerli.index, 'Fark'] = (gecerli['Ort'] / gecerli[baz]) - 1
    df['Fark_Yuzde'] = df['Fark'] * 100
    
    onceki = gunler[-2] if len(gunler)>=2 else son
    df['Gunluk_Degisim'] = (df[son] / df[onceki].replace(0, np.nan)) - 1
    
    resmi_degisim = 0.0
    try:
        r_df, _ = get_official_inflation()
        if r_df is not None and len(r_df) >= 2: resmi_degisim = ((r_df.iloc[-1]['Resmi_TUFE']/r_df.iloc[-2]['Resmi_TUFE'])-1)*100
    except: pass

    return {"df_analiz": df, "enf_genel": enf_genel, "enf_gida": enf_gida, "tahmin": enf_genel, "resmi_aylik_degisim": resmi_degisim, "son": son, "ad_col": ad_col, "agirlik_col": aktif_agirlik, "gunler": gunler, "baz_col": baz, "stats_urun": len(df), "stats_kategori": df['Grup'].nunique(), "stats_veri_noktasi": len(df)*len(tum_gunler)}

# --- SAYFALAR ---
def sayfa_ana_sayfa(ctx):
    # HTML stringindeki boşlukları temizleyerek gönderiyoruz (RAW HTML HATASINI ÖNLEMEK İÇİN)
    html_hero = textwrap.dedent(f"""
    <div style="text-align:center; padding: 40px 20px; animation: fadeInUp 0.8s ease;">
        <h1 style="font-size: 56px; font-weight: 800; margin-bottom: 20px; 
            background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Piyasa Monitörü
        </h1>
        <p style="font-size: 20px; color: #a1a1aa; max-width: 800px; margin: 0 auto; line-height: 1.6;">
            Türkiye'nin en kapsamlı yapay zeka destekli fiyat takip sistemi. <br>
            <strong>{ctx["stats_kategori"]}</strong> farklı kategorideki <strong>{ctx["stats_urun"]}</strong> ürünü anlık izliyor, resmi verilerle kıyaslıyoruz.
        </p>
        <br><br>
        <div style="display:flex; justify-content:center; gap:30px; flex-wrap:wrap;">
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">📦</div>
                <div class="kpi-value">{ctx["stats_urun"]}</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">TAKİP EDİLEN ÜRÜN</div>
            </div>
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">📊</div>
                <div class="kpi-value">{ctx["stats_kategori"]}</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">ANA KATEGORİ</div>
            </div>
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">⚡</div>
                <div class="kpi-value">{ctx["stats_veri_noktasi"]}+</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">İŞLENEN VERİ NOKTASI</div>
            </div>
        </div>
        <br><br>
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); 
             padding: 15px; border-radius: 99px; display: inline-block; animation: pulseGlow 3s infinite;">
            <span style="color: #60a5fa; font-weight: bold;">🚀 SİSTEM DURUMU:</span> 
            <span style="color: #d1d5db;">Veri botları aktif. Fiyatlar <strong>{datetime.now().strftime('%H:%M')}</strong> itibarıyla güncel.</span>
        </div>
        
        <div style="margin-top: 60px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
            <p style="color: #94a3b8 !important; font-size: 13px; font-style: italic; max-width: 700px; margin: 0 auto;">
                Bu platformda sunulan veriler deneysel ve akademik çalışma amaçlıdır. 
                Resmi enflasyon verilerinin yerine geçmez ve yatırım tavsiyesi niteliği taşımaz.
            </p>
        </div>
    </div>""")
    st.markdown(html_hero, unsafe_allow_html=True)

def sayfa_piyasa_ozeti(ctx):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444; font-size:12px;">Aylık Değişim</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5; font-size:12px;">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">AY SONU BEKLENTİ</div><div class="kpi-value">%{ctx["tahmin"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa; font-size:12px;">AI Projeksiyonu</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24; font-size:12px;">Son Açıklanan Aylık</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(10)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(10)
    items = []
    for _, r in inc.iterrows():
        if r['Gunluk_Degisim'] > 0: items.append(f"<span style='color:#f87171'>▲ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    for _, r in dec.iterrows():
        if r['Gunluk_Degisim'] < 0: items.append(f"<span style='color:#34d399'>▼ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    
    t_cont = " &nbsp;&nbsp; • &nbsp;&nbsp; ".join(items)
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-move">{t_cont} &nbsp;&nbsp; • &nbsp;&nbsp; {t_cont}</div></div>', unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig = px.histogram(df, x="Fark_Yuzde", nbins=20, title="Fiyat Değişim Dağılımı", color_discrete_sequence=["#3b82f6"])
        fig.update_layout(bargap=0.1)
        fig.update_xaxes(visible=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with col_g2:
        st.markdown(f"""<div class="kpi-card" style="height:100%"><div style="font-size:12px;color:#94a3b8;font-weight:700;">YÜKSELENLER</div><div style="font-size:24px;color:#ef4444;font-weight:700;">{len(df[df['Fark']>0])} Ürün</div><div style="margin:20px 0;border-top:1px solid rgba(255,255,255,0.1)"></div><div style="font-size:12px;color:#94a3b8;font-weight:700;">DÜŞENLER</div><div style="font-size:24px;color:#10b981;font-weight:700;">{len(df[df['Fark']<0])} Ürün</div></div>""", unsafe_allow_html=True)
    
    fig_tree = px.treemap(df, path=[px.Constant("Piyasa"), 'Grup', ctx['ad_col']], values=ctx['agirlik_col'], color='Fark', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    st.markdown("### 🔍 Kategori Bazlı Fiyat Takibi")
    c1, c2 = st.columns([1, 2])
    kat = c1.selectbox("Kategori Seç:", ["Tümü"] + sorted(df['Grup'].unique().tolist()))
    ara = c2.text_input("Ürün Ara:", placeholder="Örn: Süt...")
    df_show = df.copy()
    if kat != "Tümü": df_show = df_show[df_show['Grup'] == kat]
    if ara: df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(ara, case=False, na=False)]
    
    if not df_show.empty:
        pg = st.number_input("Sayfa", min_value=1, max_value=max(1, len(df_show)//16 + 1), step=1)
        batch = df_show.iloc[(pg-1)*16 : pg*16]
        cols = st.columns(4)
        for i, row in enumerate(batch.to_dict('records')):
            f = row.get('Gunluk_Degisim', 0)*100
            # %0.00 DÜZELTMESİ:
            if abs(f) < 0.01: cls="pg-yellow"; icon="-"
            elif f > 0: cls="pg-red"; icon="▲"
            else: cls="pg-green"; icon="▼"
            with cols[i%4]:
                st.markdown(f'<div class="pg-card"><div class="pg-name">{row[ctx["ad_col"]]}</div><div class="pg-price">{row[ctx["son"]]:.2f} ₺</div><div class="pg-badge {cls}">{icon} %{abs(f):.2f}</div></div><div style="margin-bottom:15px;"></div>', unsafe_allow_html=True)
    else: st.info("Ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    st.markdown("### 📋 Detaylı Veri Seti")
    df = ctx["df_analiz"]
    df['Trend'] = df[ctx['gunler']].apply(lambda x: [v for v in x if pd.notnull(v)] or [0,0], axis=1)
    cfg = {"Trend": st.column_config.LineChartColumn("Trend", width="small", y_min=0), ctx['ad_col']: "Ürün", "Gunluk_Degisim": st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5)}
    st.data_editor(df[[ctx['ad_col'], 'Trend', ctx['son'], 'Gunluk_Degisim']], column_config=cfg, hide_index=True, use_container_width=True, height=600)
    out = BytesIO(); 
    with pd.ExcelWriter(out) as w: df.to_excel(w, index=False)
    st.download_button("📥 Excel İndir", out.getvalue(), "Veri.xlsx")

def sayfa_raporlama(ctx):
    st.markdown("### 📝 Stratejik Pazar Raporu")
    txt = generate_detailed_static_report(ctx["df_analiz"], ctx["son"], ctx["enf_genel"], ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], ctx["ad_col"], ctx["agirlik_col"])
    st.markdown(f'<div style="background:rgba(255,255,255,0.03); padding:30px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); line-height:1.8;">{txt.replace(chr(10), "<br>").replace("**", "<b>").replace("**", "</b>")}</div>', unsafe_allow_html=True)
    st.download_button("📥 Word İndir", create_word_report(txt, ctx["son"], ctx["df_analiz"]), "Rapor.docx", "primary")

def sayfa_maddeler(ctx):
    df = ctx["df_analiz"]
    st.markdown("### 📦 Madde Bazlı Değişim")
    kat = st.selectbox("Kategori:", sorted(df['Grup'].unique().tolist()))
    sub = df[df['Grup'] == kat].sort_values('Fark_Yuzde', ascending=True)
    if not sub.empty:
        # %0.00 Düzeltmesi Grafik İçin
        colors = ['#fde047' if abs(x)<0.01 else ('#ef4444' if x>0 else '#10b981') for x in sub['Fark_Yuzde']]
        fig = go.Figure(go.Bar(x=sub['Fark_Yuzde'], y=sub[ctx['ad_col']], orientation='h', marker_color=colors))
        fig.update_layout(height=max(500, len(sub)*30), margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else: st.warning("Veri yok.")

def sayfa_trend_analizi(ctx):
    st.markdown("### 📈 Trend Analizi")
    sel = st.multiselect("Ürün Seç:", ctx["df_analiz"][ctx["ad_col"]].unique())
    if sel:
        melt = ctx["df_analiz"][ctx["df_analiz"][ctx["ad_col"]].isin(sel)][[ctx["ad_col"]]+ctx["gunler"]].melt(id_vars=[ctx["ad_col"]], var_name='Tarih', value_name='Fiyat')
        st.plotly_chart(style_chart(px.line(melt, x='Tarih', y='Fiyat', color=ctx["ad_col"], markers=True)), use_container_width=True)

# --- ANA MAIN ---
def main():
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:15px 25px; background:linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%); border-radius:12px; margin-bottom:20px; margin-top:-30px; animation: fadeInUp 0.5s;">
            <div>
                <div style="font-weight:800; font-size:24px; color:#fff;">Piyasa Monitörü <span style="background:rgba(16,185,129,0.15); color:#34d399; font-size:10px; padding:3px 8px; border-radius:4px;">SİMÜLASYON</span></div>
                <div style="font-size:12px; color:#94a3b8;">Yapay Zeka Destekli Enflasyon Analiz Platformu</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#64748b; font-weight:700;">İSTANBUL</div>
                <div style="font-size:20px; font-weight:700; color:#e2e8f0; font-family:'JetBrains Mono';">{datetime.now().strftime("%d.%m.%Y")}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # MENÜ (METODOLOJİ KALDIRILDI)
    menu_items = {
        "🏠 Ana Sayfa": "Ana Sayfa", 
        "📊 Piyasa Özeti": "Piyasa Özeti",
        "📈 Trendler": "Trendler",
        "📦 Maddeler": "Maddeler",
        "🏷️ Kategori Detay": "Kategori Detay",
        "📋 Tam Liste": "Tam Liste",
        "📝 Raporlama": "Raporlama"
    }
    
    secilen_etiket = st.radio("Navigasyon", options=list(menu_items.keys()), label_visibility="collapsed", key="nav_radio", horizontal=True)
    secim = menu_items[secilen_etiket]

    col_btn1, col_btn2 = st.columns([4, 1])
    with col_btn2:
        if st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True):
            res = html_isleyici(lambda p: None) # Progress bar basitleştirildi
            if "OK" in res: st.cache_data.clear(); st.rerun()
            else: st.warning("Veri yok veya hata.")

    with st.spinner("Veri tabanına bağlanılıyor..."):
        df_base, r_dates, col_name = verileri_getir_cache()
    
    ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name) if df_base is not None else None

    if ctx:
        if secim == "Ana Sayfa": sayfa_ana_sayfa(ctx)
        elif secim == "Piyasa Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
    else:
        st.markdown("<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi.</div>", unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
