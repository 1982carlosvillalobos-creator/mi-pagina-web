# ============================================================
# GOLDEN CHARGE ERP PRO - Sistema de Gestión Empresarial
# Desarrollado para Golden Charge, LLC - Fremont, CA
# CRM Jerárquico, Mobile-First PWA, NEC 220.82 + Blocks Merged
# ============================================================

import streamlit as st
import os
import json
import datetime
import base64
import subprocess
import io
import tempfile
from pathlib import Path
from fpdf import FPDF

# ── Gemini AI ────────────────────────────────────────────────
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyC_1svBIXVNCR06OOcrd-YuKq0DkRQeDrk"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# ── Google Drive ─────────────────────────────────────────────
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2 import service_account
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False

DRIVE_SECRET_PATH = "drive_secret.json"
DRIVE_FOLDER_ID   = "10YQQAGkhPk3xQwwU9mHTYUrpEYQ0qQeF"
LOGO_URL          = "https://pub-a9f35b2b86db4656b16e6e97d0d62544.r2.dev/logo.png"

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Golden Charge ERP Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        .login-box {
            max-width: 400px; margin: 8vh auto; padding: 2.5rem;
            background: #1a1d27; border-radius: 16px;
            border: 1px solid #f6c90e44; text-align: center;
        }
        h1, h2, h3 { color: #f6c90e !important; }
        .stButton > button {
            background-color: #f6c90e; color: #0e1117;
            font-weight: bold; border-radius: 8px; border: none;
            width: 100%; padding: 0.6rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("## ⚡ Golden Charge ERP Pro")
        st.markdown("##### Please enter your password to continue")
        st.markdown("---")
        pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password…")
        if st.button("🔐 Login", use_container_width=True):
            if pwd == "Golden2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# GLOBAL CSS (PWA & Mobile-First)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1a1d27; border-right: 1px solid #2d3748; }
    div[data-testid="metric-container"] { background-color: #1e2130; border: 1px solid #2d3748; border-radius: 10px; padding: 15px; width: 100%; }
    .stButton > button {
        background-color: #f6c90e; color: #0e1117; font-weight: bold; border-radius: 8px; 
        border: none; padding: 0.75rem 1.5rem; transition: all 0.3s ease; width: 100%;
    }
    .stButton > button:hover { background-color: #e0b800; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(246,201,14,0.3); }
    h1, h2, h3, h4, h5 { color: #f6c90e !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background-color: #1e2130; color: #ffffff; border: 1px solid #2d3748; border-radius: 6px;
    }
    hr { border-color: #f6c90e; opacity: 0.3; }
    .chat-message { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; width: 100%; }
    .chat-user    { background-color: #1e3a5f; border-left: 3px solid #4a9eff; }
    .chat-assistant { background-color: #1e2d1e; border-left: 3px solid #f6c90e; }
    .calc-box, .costing-box { background: #1e2130; border: 1px solid #f6c90e44; border-radius: 10px; padding: 1rem; margin-top: 0.5rem; width: 100%; }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
        h1 { font-size: 1.8rem !important; }
        .stColumns { display: flex; flex-direction: column; }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COMPANY DATA
# ─────────────────────────────────────────────
COMPANY_INFO = {
    "name":         "Golden Charge, LLC",
    "dba":          "DBA Golden Charge Electrician Company",
    "address":      "38725 Lexington ST, Fremont, CA. 94536",
    "email1":       "info@goldencharge.net",
    "email2":       "carlos.villalobos@goldencharge.net",
    "phone1":       "+1 (510) 221-1258",
    "phone2":       "+1 (424) 465-3362",
    "license":      "CA License C-10 # 1143055",
    "ein":          "EIN: 39-4119592"
}

# ─────────────────────────────────────────────
# FILE PATHS & INIT
# ─────────────────────────────────────────────
DATA_DIR       = Path("data")
UPLOADS_DIR    = Path("uploads")
ESTIMATES_FILE = DATA_DIR / "estimates.json"
PROJECTS_FILE  = DATA_DIR / "projects.json"
CALENDAR_FILE  = DATA_DIR / "calendar.json"
COUNTERS_FILE  = DATA_DIR / "counters.json"

DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

CLIENT_SUBFOLDERS = ["01_Photos", "02_Estimates", "03_Contracts", "04_Invoices", "05_Blueprints"]

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
def load_json(filepath, default_val):
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return default_val

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ── COUNTERS (FOLIOS) ──
def get_next_folio(doc_type):
    counters = load_json(COUNTERS_FILE, {"E": 1000, "C": 1000, "I": 1000})
    yr = datetime.datetime.now().year
    prefix = doc_type[0].upper()
    
    if prefix not in counters:
        counters[prefix] = 1000
    
    counters[prefix] += 1
    save_json(COUNTERS_FILE, counters)
    return f"{prefix}-{yr}-{counters[prefix]:03d}"

# ── DRIVE HIERARCHICAL FOLDERS ──
def get_drive_service():
    if not DRIVE_AVAILABLE or not os.path.exists(DRIVE_SECRET_PATH):
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(DRIVE_SECRET_PATH, scopes=["https://www.googleapis.com/auth/drive.file"])
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None

def get_or_create_drive_folder(service, folder_name, parent_id):
    query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
        folder = service.files().create(body=meta, fields='id').execute()
        return folder.get('id')

def ensure_client_folders(client_name):
    # Local
    safe_name = "".join(c for c in client_name if c.isalnum() or c in " -_").strip().replace(" ", "_")
    client_dir = UPLOADS_DIR / safe_name
    client_dir.mkdir(exist_ok=True)
    for sub in CLIENT_SUBFOLDERS:
        (client_dir / sub).mkdir(exist_ok=True)
    
    # Drive
    drive_map = {}
    service = get_drive_service()
    if service:
        try:
            c_id = get_or_create_drive_folder(service, safe_name, DRIVE_FOLDER_ID)
            drive_map["ROOT"] = c_id
            for sub in CLIENT_SUBFOLDERS:
                sub_id = get_or_create_drive_folder(service, sub, c_id)
                drive_map[sub] = sub_id
        except Exception as e:
            st.warning(f"Drive sync warning: {e}")
            
    return safe_name, drive_map

def upload_file_to_drive(service, file_bytes, filename, parent_folder_id):
    if not service: return None
    try:
        meta = {"name": filename, "parents": [parent_folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype="application/pdf")
        file_obj = service.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()
        return file_obj.get("webViewLink", "")
    except Exception:
        return None

# ── LOGO HELPER ──
@st.cache_data(show_spinner=False)
def _get_logo_bytes() -> bytes | None:
    try:
        import requests
        r = requests.get(LOGO_URL, timeout=5)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None

def _logo_temp_path() -> str | None:
    data = _get_logo_bytes()
    if data is None: return None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(data)
    tmp.close()
    return tmp.name

# ─────────────────────────────────────────────
# PDF GENERATOR (MATCHING KAMRAN STANDARDS)
# ─────────────────────────────────────────────
class GoldenChargePDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self._logo_path = logo_path

    def header(self):
        # Top right logo
        if self._logo_path and os.path.exists(self._logo_path):
            try:
                self.image(self._logo_path, x=160, y=10, w=35)
            except Exception:
                pass

        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.set_xy(10, 15)
        self.cell(0, 5, f"{COMPANY_INFO['name']}", ln=True)
        self.cell(0, 5, f"{COMPANY_INFO['address']}", ln=True)
        self.cell(0, 5, f"{COMPANY_INFO['dba']}", ln=True)
        self.cell(0, 5, f"{COMPANY_INFO['email1']} | {COMPANY_INFO['email2']}", ln=True)
        self.cell(0, 5, f"{COMPANY_INFO['phone1']} | {COMPANY_INFO['phone2']}", ln=True)
        self.cell(0, 5, f"License: {COMPANY_INFO['license']} | {COMPANY_INFO['ein']}", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def doc_title(self, title, folio, date_str, project_name, client_name):
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(22, 54, 131) # Dark blue/brand color
        self.cell(0, 10, title, ln=True)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(200, 20, 100)
        self.cell(0, 6, f"Submitted on {date_str}", ln=True)
        self.ln(5)

        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        
        # Grid format
        x_start = self.get_x()
        self.cell(60, 6, "Estimate for" if "Estimate" in title else "Client", ln=0)
        self.cell(70, 6, "Project", ln=0)
        self.cell(0, 6, "Folio #", ln=1)
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        y_vals = self.get_y()
        self.multi_cell(60, 5, client_name)
        self.set_xy(x_start + 60, y_vals)
        self.multi_cell(70, 5, project_name)
        self.set_xy(x_start + 130, y_vals)
        self.cell(0, 5, folio, ln=1)
        self.ln(10)

    def print_totals_table(self, total_price):
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(240, 240, 250)
        self.cell(100, 8, "Description", 0, 0, 'L', fill=True)
        self.cell(30, 8, "Qty", 0, 0, 'C', fill=True)
        self.cell(30, 8, "Unit price", 0, 0, 'R', fill=True)
        self.cell(30, 8, "Total price", 0, 1, 'R', fill=True)

        self.set_font('Helvetica', '', 10)
        self.cell(100, 8, "Materials and Labor", 'B', 0, 'L')
        self.cell(30, 8, "1", 'B', 0, 'C')
        self.cell(30, 8, f"${total_price:,.2f}", 'B', 0, 'R')
        self.cell(30, 8, f"${total_price:,.2f}", 'B', 1, 'R')
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(160, 8, "Subtotal", 0, 0, 'R')
        self.cell(30, 8, f"${total_price:,.2f}", 0, 1, 'R')
        self.ln(5)

    def print_payment_schedule(self, payments):
        if not payments: return
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, f"Payment Schedule ({len(payments)} Installments)", ln=True)
        
        self.set_fill_color(240, 240, 240)
        self.set_font('Helvetica', 'B', 9)
        
        # 1. Ajustamos los anchos para dar más espacio a la descripción
        w_pay, w_amt, w_pct, w_cond = 45, 25, 20, 100
        
        # Encabezados
        self.cell(w_pay, 8, "Payment", border=1, fill=True)
        self.cell(w_amt, 8, "Amount Due", border=1, fill=True)
        self.cell(w_pct, 8, "% of Total", border=1, fill=True)
        self.cell(w_cond, 8, "Condition / Milestone", border=1, ln=True, fill=True)

        self.set_font('Helvetica', '', 9)
        for p in payments:
            # Guardamos las coordenadas iniciales de la fila
            x_start = self.get_x()
            y_start = self.get_y()
            
            # 2. Dibujamos PRIMERO la celda multilínea (Condición) para saber cuánto crece hacia abajo
            self.set_xy(x_start + w_pay + w_amt + w_pct, y_start)
            self.multi_cell(w_cond, 6, p["condition"], border=1)
            
            # Calculamos la altura total que tomó esa fila
            y_end = self.get_y()
            row_height = y_end - y_start
            
            # 3. Dibujamos las primeras tres columnas usando esa misma altura exacta
            self.set_xy(x_start, y_start)
            self.cell(w_pay, row_height, p["name"], border=1)
            self.cell(w_amt, row_height, f"${p['amount']:,.2f}", border=1)
            self.cell(w_pct, row_height, f"{p['percent']:.2f}%", border=1)
            
            # Regresamos el cursor al final de la fila para que la siguiente empiece bien
            self.set_xy(x_start, y_end)
            
        self.ln(5)

def generar_pdf_documento(datos, doc_type="Estimate"):
    pdf = GoldenChargePDF(logo_path=_logo_temp_path())
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    folio = datos.get("folio", f"{doc_type[0]}-000")
    pdf.doc_title(
        title=doc_type,
        folio=folio,
        date_str=datos.get("date", str(datetime.date.today())),
        project_name=datos.get("project_name", ""),
        client_name=datos.get("customer_name", "")
    )

    pdf.print_totals_table(datos.get("total_price", 0))

    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(200, 20, 100)
    pdf.cell(0, 8, f"Total: ${datos.get('total_price', 0):,.2f}", ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Scope of Work (Inclusions)", ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, datos.get("scope_of_work", "N/A"))
    self_y = pdf.get_y()
    pdf.ln(5)

    excl = datos.get("exclusions", "").strip()
    if excl:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, "Exclusions and Conditions", ln=True)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, excl)
        pdf.ln(5)

    pagos = datos.get("payments", [])
    if pagos:
        pdf.print_payment_schedule(pagos)

    if doc_type == "Contract":
        pdf.ln(15)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, "IN WITNESS WHEREOF, the parties execute this Contract:", ln=True)
        pdf.ln(15)
        pdf.line(10, pdf.get_y(), 90, pdf.get_y())
        pdf.line(110, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(100, 5, "CONTRACTOR (Golden Charge, LLC)", ln=0)
        pdf.cell(90, 5, f"CLIENT ({datos.get('customer_name', '')})", ln=1)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(100, 5, "Carlos Villalobos - Licensed Electrician", ln=0)
        pdf.cell(90, 5, "Signature & Date", ln=1)

    return pdf.output(dest='S').encode('latin-1')

def mostrar_pdf_viewer(pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" style="border:1px solid #f6c90e44; border-radius:8px;"></iframe>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    logo_bytes = _get_logo_bytes()
    if logo_bytes:
        st.image(logo_bytes, use_container_width=True)
    else:
        st.markdown("<h2 style='color:#f6c90e;text-align:center;'>⚡ Golden Charge</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    pagina = st.radio("Navigation", [
        "🏠 Dashboard", 
        "📄 Estimates & Invoices", 
        "✍️ Contracts", 
        "📅 Calendar", 
        "📂 CRM & Project Gallery", 
        "🤖 AI Assistant", 
        "🗺️ Blueprint Copilot",
        "⚡ Electrical Calc & NEC",
        "🏙️ Bay Area Estimator"
    ], label_visibility="collapsed")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ═══════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════

# ── 🏠 DASHBOARD ──
if pagina == "🏠 Dashboard":
    st.title("⚡ Golden Charge ERP Pro")
    estimados = load_json(ESTIMATES_FILE, [])
    
    # Manejo seguro del total de ventas para datos viejos
    total_sales = 0.0
    for e in estimados:
        try: total_sales += float(e.get("total_price", 0) or 0)
        except ValueError: pass

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Est. Sales", f"${total_sales:,.2f}")
    col2.metric("📄 Total Documents", len(estimados))
    col3.metric("📂 Active Clients", len(set(e.get("customer_name", "Unknown") for e in estimados)))

    st.markdown("---")
    st.subheader("📋 Recent Activity")

    recent = estimados[-5:][::-1]
    if not recent:
        st.info("No documents yet. Create your first Estimate!")
    else:
        # Enumerate añade un índice (idx) para que ningún botón se duplique
        for idx, est in enumerate(recent):
            folio      = est.get("folio", f"Old-{idx}")
            if folio == "N/A": folio = f"Old-{idx}"
            
            tipo       = est.get("tipo", "Estimate")
            cliente    = est.get("customer_name", "Unknown")
            proyecto   = est.get("project_name", "Unnamed")
            fecha_doc  = est.get("date", "No date")
            
            try: precio = float(est.get("total_price", 0) or 0)
            except ValueError: precio = 0.0

            safe_client = "".join(c for c in cliente if c.isalnum() or c in " -_").strip().replace(" ", "_")
            target_sub = "04_Invoices" if tipo == "Invoice" else "02_Estimates"
            pdf_path   = None
            search_dir = UPLOADS_DIR / safe_client / target_sub
            
            if search_dir.exists():
                matches = sorted(search_dir.glob(f"{folio}_*.pdf"))
                if matches:
                    pdf_path = matches[0]

            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                <div style="background:#1e2130;padding:14px 16px;border-radius:8px;
                            border-left:4px solid #f6c90e;line-height:1.6;margin-bottom:8px;">
                    <span style="background:#f6c90e;color:#0e1117;font-weight:bold;
                                 padding:2px 8px;border-radius:4px;font-size:0.8rem;">
                        {folio}
                    </span>
                    &nbsp;
                    <strong style="font-size:1rem;">{cliente}</strong>
                    <span style="color:#aaa;"> — {proyecto}</span><br>
                    <span style="color:#4caf50;font-weight:bold;">${precio:,.2f}</span>
                    &nbsp;&nbsp;
                    <small style="color:#666;">{tipo} · {fecha_doc}</small>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if pdf_path and pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Open", data=f.read(), file_name=pdf_path.name,
                            mime="application/pdf", key=f"dash_dl_{folio}_{idx}",
                            use_container_width=True,
                        )
                else:
                    if st.button("⚡ Gen PDF", key=f"dash_gen_{folio}_{idx}", use_container_width=True):
                        try:
                            pb = generar_pdf_documento(est, doc_type=tipo)
                            st.download_button(
                                label="📥 Download", data=pb, file_name=f"{folio}.pdf",
                                mime="application/pdf", key=f"dash_dl2_{folio}_{idx}",
                            )
                        except Exception as ex:
                            st.error(f"Error: {ex}")

# ── 📄 ESTIMATES & INVOICES (PHASE 2 CRM/COSTING) ──
elif pagina == "📄 Estimates & Invoices":
    st.title("📄 Estimates & Invoices")
    tab_nuevo, tab_lista = st.tabs(["➕ New Document", "📋 All Documents"])

    with tab_nuevo:
        tipo_doc = st.selectbox("Document Type", ["Estimate", "Invoice"])
        
        st.markdown("#### 👤 Client & Project")
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Client Name *", placeholder="Nucon Builders")
            project_name  = st.text_input("Project Name *", placeholder="New Two-Story House ADU")
        with col2:
            address = st.text_input("Project Address", placeholder="101 W. Duane Ave, Los Gatos")
            fecha   = st.date_input("Date", value=datetime.date.today())

        # INTERNAL COSTING ENGINE
        with st.expander("💼 Internal Costing Engine (Private)"):
            st.markdown("<div class='costing-box'>", unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            workers = cc1.number_input("Number of Workers", 1, value=1)
            rate_day = cc2.number_input("Daily Pay Rate per Worker ($)", 0.0, value=250.0)
            days = cc3.number_input("Estimated Days", 1.0, value=3.0)
            labor_cost = workers * rate_day * days
            
            mc1, mc2 = st.columns(2)
            mat_base = mc1.number_input("Materials Base Cost ($)", 0.0, value=1000.0)
            mat_markup = mc2.slider("Materials Markup (%)", 0, 100, 20)
            mat_total = mat_base * (1 + mat_markup/100)
            
            suggested_price = labor_cost + mat_total
            st.markdown(f"**Labor Cost:** ${labor_cost:,.2f} | **Materials (w/ markup):** ${mat_total:,.2f}")
            st.success(f"💡 Suggested Total Price: **${suggested_price:,.2f}**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("#### 💰 Final Pricing & Scope")
        total_price = st.number_input("Actual Total Price ($) *", min_value=0.0, value=float(suggested_price), step=100.0)
        
        if total_price > 0:
            net_profit = total_price - labor_cost - mat_base
            margin = (net_profit / total_price) * 100 if total_price > 0 else 0
            st.info(f"📊 **Net Profit Estimate:** ${net_profit:,.2f} ({margin:.1f}% Margin)")

        scope_of_work = st.text_area("Scope of Work (Inclusions) *", height=120)
        exclusions = st.text_area("Exclusions / Conditions", height=80, value="Permit Fees: The total price excludes the cost of permits and inspection fees. Trenching/Excavation is excluded.")

        st.markdown("#### ⚖️ Dynamic Payment Schedule")
        num_payments = st.number_input("Number of Payments", 1, 10, 5)
        payments_data = []
        
        for i in range(int(num_payments)):
            pc1, pc2, pc3 = st.columns([2, 1, 3])
            p_name = pc1.text_input(f"Payment {i+1} Name", key=f"p_name_{i}", placeholder="e.g. Deposit")
            p_amt  = pc2.number_input(f"Amount ($)", 0.0, float(total_price), key=f"p_amt_{i}")
            p_cond = pc3.text_input(f"Condition/Milestone", key=f"p_cond_{i}", placeholder="e.g. Due upon contract signing")
            p_pct  = (p_amt / total_price * 100) if total_price > 0 else 0
            if p_name and p_amt > 0:
                payments_data.append({"name": p_name, "amount": p_amt, "percent": p_pct, "condition": p_cond})

        if st.button("⚡ Generate & Save Document"):
            if not customer_name or not project_name or not scope_of_work or total_price <= 0:
                st.error("⚠️ Fill all required fields (*).")
            else:
                # 1. Setup Folders (Local + Drive)
                safe_client, drive_map = ensure_client_folders(customer_name)
                
                # 2. Get Folio
                folio = get_next_folio(tipo_doc)
                
                datos_est = {
                    "folio": folio, "tipo": tipo_doc, "customer_name": customer_name,
                    "project_name": project_name, "address": address, "date": str(fecha),
                    "scope_of_work": scope_of_work, "exclusions": exclusions,
                    "total_price": total_price, "payments": payments_data,
                    "created_at": str(datetime.datetime.now())
                }
                
                # 3. Save Data
                estimados = load_json(ESTIMATES_FILE, [])
                estimados.append(datos_est)
                save_json(ESTIMATES_FILE, estimados)
                
                # 4. Generate PDF
                pdf_bytes = generar_pdf_documento(datos_est, doc_type=tipo_doc)
                pdf_filename = f"{folio}_{project_name.replace(' ','_')}.pdf"
                
                # Save locally to client folder
                target_sub = "04_Invoices" if tipo_doc == "Invoice" else "02_Estimates"
                (UPLOADS_DIR / safe_client / target_sub / pdf_filename).write_bytes(pdf_bytes)
                
                # Drive upload
                if drive_map and target_sub in drive_map:
                    srv = get_drive_service()
                    link = upload_file_to_drive(srv, pdf_bytes, pdf_filename, drive_map[target_sub])
                    if link: st.success(f"☁️ Uploaded to Drive: [Open PDF]({link})")
                
                st.success(f"✅ {tipo_doc} {folio} Generated!")
                st.download_button("📥 Download PDF", pdf_bytes, pdf_filename, "application/pdf")
                st.session_state["pdf_preview"] = pdf_bytes

        if st.session_state.get("pdf_preview"):
            mostrar_pdf_viewer(st.session_state["pdf_preview"])

    with tab_lista:
        estimados = load_json(ESTIMATES_FILE, [])
        if estimados:
            for e in estimados[::-1]:
                with st.expander(f"{e.get('folio','')} - {e.get('customer_name','')} ({e.get('tipo','')})"):
                    st.write(f"**Project:** {e.get('project_name','')}")
                    st.write(f"**Total:** ${float(e.get('total_price',0)):,.2f}")
                    st.write(f"**Date:** {e.get('date','')}")

# ── ✍️ CONTRACTS ──
elif pagina == "✍️ Contracts":
    st.title("✍️ Contracts")
    st.markdown("Convert an Estimate into a formal Contract, or create a new one from scratch.")
    st.markdown("---")

    estimados      = load_json(ESTIMATES_FILE, [])
    estimates_only = [e for e in estimados if e.get("tipo") == "Estimate"]

    # Se usa .get() para evitar KeyErrors con archivos viejos
    opts    = ["-- Create Blank Contract --"] + [
        f"{e.get('folio', 'N/A')} : {e.get('customer_name', 'Unknown')} – {e.get('project_name', 'Unnamed')}"
        for e in estimates_only
    ]
    sel_est = st.selectbox("Base Contract on Estimate:", opts)

    pre_data = {}
    if sel_est != opts[0]:
        sel_folio = sel_est.split(" : ")[0]
        pre_data  = next((x for x in estimates_only if x.get("folio") == sel_folio), {})

    # ── Contract Fields ──────────────────────────────────────
    st.markdown("#### 👤 Client & Project")
    cf1, cf2 = st.columns(2)
    with cf1:
        c_cliente = st.text_input("Client Name *",   value=pre_data.get("customer_name", ""))
        c_proj    = st.text_input("Project Name *",  value=pre_data.get("project_name", ""))
        c_addr    = st.text_input("Project Address", value=pre_data.get("address", ""))
    with cf2:
        # Extraemos el precio con cuidado por si el estimado viejo estaba vacío
        try: val_total = float(pre_data.get("total_price", 0.0) or 0.0)
        except ValueError: val_total = 0.0
        
        c_total      = st.number_input("Contract Total ($) *",
                                       min_value=0.0, step=100.0,
                                       value=val_total)
        c_start_date = st.date_input("Start Date",      value=datetime.date.today())
        c_end_date   = st.date_input("Estimated Completion",
                                     value=datetime.date.today() + datetime.timedelta(days=30))

    # ── Scope ───────────────────────────────────────────────
    st.markdown("#### 🔧 Scope of Work")
    c_scope = st.text_area(
        "What's Included — Scope of Work *", height=140,
        value=pre_data.get("scope_of_work", ""),
        placeholder=(
            "• Install new 200A main electrical panel (Square D QO)\n"
            "• Replace meter base and weatherhead\n"
            "• Install (2) 20A kitchen small appliance circuits\n"
            "• Install (1) 20A dedicated laundry circuit\n"
            "• Install GFCI outlets in all wet locations\n"
            "• All work per NEC 2023 and CA Title 24\n"
            "• All materials, labor, and cleanup included"
        )
    )

    # ── Inclusions / Exclusions ──────────────────────────────
    st.markdown("#### ✅ Inclusions & ❌ Exclusions")
    inc_col, exc_col = st.columns(2)
    with inc_col:
        c_inclusions = st.text_area(
            "✅ Inclusions",
            height=130,
            value=pre_data.get("inclusions", ""),
            placeholder=(
                "• All labor and materials\n"
                "• Building permit application\n"
                "• City inspection coordination\n"
                "• 1-year workmanship warranty\n"
                "• Site cleanup upon completion"
            )
        )
    with exc_col:
        c_exclusions = st.text_area(
            "❌ Exclusions",
            height=130,
            value=pre_data.get("exclusions",
                "Permit Fees: The total price excludes the cost of permits and "
                "inspection fees.\nTrenching/Excavation is excluded.\n"
                "Drywall patching/painting after installation is excluded."),
            placeholder=(
                "• Permit & inspection fees (billed separately)\n"
                "• Trenching or excavation\n"
                "• Drywall patching or painting\n"
                "• Any work not listed in scope above"
            )
        )

    # ── Standard Clauses ────────────────────────────────────
    st.markdown("#### 📋 Standard Clauses")
    cl1, cl2 = st.columns(2)
    with cl1:
        inc_warranty = st.checkbox("1-Year Workmanship Warranty",     value=True)
        inc_permits  = st.checkbox("Permits & Inspections Clause",    value=True)
    with cl2:
        inc_changes  = st.checkbox("Change Order Clause",             value=True)
        inc_cleanup  = st.checkbox("Site Cleanup Clause",             value=True)

    extra_clauses = []
    if inc_warranty:
        extra_clauses.append(
            "WARRANTY: Contractor warrants all workmanship for a period of one (1) year "
            "from the date of final inspection. This warranty covers defects in workmanship "
            "only and does not cover damage caused by misuse, accidents, or acts of nature."
        )
    if inc_permits:
        extra_clauses.append(
            "PERMITS & INSPECTIONS: Contractor shall apply for and coordinate all required "
            "permits. All work shall be performed in compliance with NEC 2023, California "
            "Title 24, and all applicable local codes. Permit fees are not included in the "
            "contract price unless explicitly stated."
        )
    if inc_changes:
        extra_clauses.append(
            "CHANGE ORDERS: Any changes to the scope of work must be agreed upon in writing "
            "by both parties via a signed Change Order before additional work begins. "
            "Unauthorized verbal changes are not binding and will not be compensated."
        )
    if inc_cleanup:
        extra_clauses.append(
            "SITE CLEANUP: Contractor shall maintain a clean and safe work environment "
            "throughout the project and shall remove all debris, packaging, and waste "
            "materials upon completion of work."
        )

    # ── Dynamic 5-Payment Schedule ───────────────────────────
    st.markdown("#### 💳 Payment Schedule")
    st.caption("Default is the industry-standard 5-payment structure. Adjust amounts and milestones as needed.")

    # Compute CSLB default splits for the 5 payments
    def _default_5_payments(total):
        """
        Golden Charge standard 5-milestone schedule:
          1. Deposit      — 10% (max $1,000)           — Due upon contract signing
          2. Mobilization — 20%                         — Due on first day of work
          3. Rough-in     — 30%                         — Due upon rough-in inspection approval
          4. Materials    — 25%                         — Due upon final material delivery
          5. Final        — remaining balance            — Due upon project completion & walk-through
        """
        deposit     = min(round(total * 0.10, 2), 1000.00)
        after_dep   = total - deposit
        mob         = round(after_dep * 0.20, 2)
        rough       = round(after_dep * 0.30, 2)
        materials   = round(after_dep * 0.25, 2)
        final_pay   = round(total - deposit - mob - rough - materials, 2)
        return [
            {"name": "Deposit",          "amount": deposit,   "condition": "Due upon contract signing"},
            {"name": "Mobilization",     "amount": mob,       "condition": "Due on first day of work on site"},
            {"name": "Rough-in",         "amount": rough,     "condition": "Due upon rough-in inspection approval"},
            {"name": "Material Delivery","amount": materials,  "condition": "Due upon final material delivery"},
            {"name": "Final Payment",    "amount": final_pay,  "condition": "Due upon project completion & client walk-through"},
        ]

    num_payments = st.number_input("Number of Payments", min_value=1, max_value=10,
                                   value=5, step=1, key="cont_num_pay")

    # Seed defaults when total > 0
    defaults = _default_5_payments(c_total) if c_total > 0 else []

    payments_data  = []
    running_total  = 0.0
    pay_cols_heads = st.columns([2, 2, 1, 1])
    pay_cols_heads[0].markdown("**Milestone / Payment Name**")
    pay_cols_heads[1].markdown("**Condition**")
    pay_cols_heads[2].markdown("**Amount ($)**")
    pay_cols_heads[3].markdown("**% of Total**")

    for i in range(int(num_payments)):
        # Pull default values if available
        if i < len(defaults):
            def_name  = defaults[i]["name"]
            def_amt   = defaults[i]["amount"]
            def_cond  = defaults[i]["condition"]
        else:
            def_name  = f"Payment {i+1}"
            def_amt   = 0.0
            def_cond  = ""

        pc1, pc2, pc3, pc4 = st.columns([2, 2, 1, 1])
        p_name = pc1.text_input(f"Name #{i+1}",   value=def_name,
                                key=f"cont_pname_{i}", label_visibility="collapsed")
        p_cond = pc2.text_input(f"Cond #{i+1}",   value=def_cond,
                                key=f"cont_pcond_{i}", label_visibility="collapsed")
        p_amt  = pc3.number_input(f"Amt #{i+1}",  min_value=0.0,
                                  value=def_amt, step=100.0, format="%.2f",
                                  key=f"cont_pamt_{i}", label_visibility="collapsed")
        p_pct  = (p_amt / c_total * 100) if c_total > 0 else 0.0
        pc4.markdown(f"<div style='padding-top:8px;color:#f6c90e;font-weight:bold;'>"
                     f"{p_pct:.1f}%</div>", unsafe_allow_html=True)

        running_total += p_amt
        if p_name and p_amt > 0:
            payments_data.append({
                "name":      p_name,
                "amount":    p_amt,
                "percent":   p_pct,
                "condition": p_cond,
            })

    # Running balance indicator
    balance   = c_total - running_total
    bal_color = "#4caf50" if abs(balance) < 0.50 else "#ff4444"
    bal_label = "✅ Balanced" if abs(balance) < 0.50 else f"⚠️ ${balance:+,.2f} remaining"
    st.markdown(
        f'<div style="background:#1e2130;padding:8px 12px;border-radius:6px;'
        f'border-left:3px solid {bal_color};margin-top:4px;">'
        f'<span style="color:{bal_color};font-weight:bold;">{bal_label}</span>'
        f'&nbsp;&nbsp;<small style="color:#aaa;">Total scheduled: '
        f'${running_total:,.2f} / ${c_total:,.2f}</small></div>',
        unsafe_allow_html=True
    )

    # ── Generate Button ──────────────────────────────────────
    st.markdown("---")
    if st.button("📄 Generate Contract PDF", use_container_width=False):
        if not c_cliente or not c_proj or not c_scope or c_total <= 0:
            st.error("⚠️ Please fill in all required fields (Client, Project, Scope, Total).")
        else:
            safe_client, drive_map = ensure_client_folders(c_cliente)
            folio = get_next_folio("Contract")

            # Build full scope text that includes clauses for PDF body
            full_scope = c_scope.strip()
            if extra_clauses:
                full_scope += "\n\n--- TERMS & CONDITIONS ---\n\n"
                full_scope += "\n\n".join(extra_clauses)

            datos_cont = {
                "folio":        folio,
                "tipo":         "Contract",
                "customer_name":c_cliente,
                "project_name": c_proj,
                "address":      c_addr,
                "date":         str(datetime.date.today()),
                "start_date":   str(c_start_date),
                "end_date":     str(c_end_date),
                "total_price":  c_total,
                "scope_of_work":full_scope,
                "inclusions":   c_inclusions,
                "exclusions":   c_exclusions,
                "payments":     payments_data,
            }

            pdf_bytes = generar_pdf_documento(datos_cont, doc_type="Contract")
            filename  = f"{folio}_{c_proj.replace(' ', '_')}.pdf"

            # Save locally
            local_path = UPLOADS_DIR / safe_client / "03_Contracts" / filename
            local_path.write_bytes(pdf_bytes)

            # Upload to Drive
            if drive_map and "03_Contracts" in drive_map:
                srv  = get_drive_service()
                link = upload_file_to_drive(srv, pdf_bytes, filename,
                                            drive_map["03_Contracts"])
                if link:
                    st.success(f"☁️ Uploaded to Google Drive — [Open PDF]({link})")

            st.success(f"✅ Contract **{folio}** created for **{c_cliente}**!")

            dc1, dc2 = st.columns(2)
            with dc1:
                st.download_button("📥 Download Contract PDF",
                                   pdf_bytes, filename, "application/pdf",
                                   use_container_width=True)
            with dc2:
                if st.button("👁️ Preview Contract", use_container_width=True,
                             key="prev_contract"):
                    st.session_state["contract_preview"] = pdf_bytes

    if st.session_state.get("contract_preview"):
        st.markdown("#### 🔍 PDF Preview")
        mostrar_pdf_viewer(st.session_state["contract_preview"])

# ── 📅 CALENDAR ──
elif pagina == "📅 Calendar":
    st.title("📅 Project Calendar")
    st.markdown("Schedule jobs and link them to your clients.")
    st.markdown("---")

    # ── helpers scoped to this page ──────────────────────────
    def _load_events():
        return load_json(CALENDAR_FILE, [])

    def _save_event(ev):
        evts = _load_events()
        evts.append(ev)
        save_json(CALENDAR_FILE, evts)

    def _delete_event(idx):
        evts = _load_events()
        if 0 <= idx < len(evts):
            evts.pop(idx)
            save_json(CALENDAR_FILE, evts)

    # ── Add New Job ──────────────────────────────────────────
    with st.expander("➕ Schedule New Job", expanded=True):
        # Client dropdown (pulled from saved estimates)
        estimados_cal = load_json(ESTIMATES_FILE, [])
        client_names  = sorted(set(e.get("customer_name", "") for e in estimados_cal if e.get("customer_name")))
        
        ev_c1, ev_c2 = st.columns(2)
        with ev_c1:
            # Allow typing a new name OR selecting existing client
            ev_client = st.selectbox(
                "Client *",
                options=["-- New client (type below) --"] + client_names,
                key="cal_client_sel"
            )
            if ev_client == "-- New client (type below) --":
                ev_client = st.text_input("New Client Name *", key="cal_client_new",
                                          placeholder="e.g. John Smith")
            
            ev_project = st.text_input("Job / Project Description *",
                                       placeholder="Panel Upgrade – 200A Service")
            ev_tech    = st.text_input("Assigned Technician",
                                       placeholder="Carlos Villalobos")

        with ev_c2:
            ev_date    = st.date_input("Job Date *", value=datetime.date.today(),
                                       key="cal_date")
            ev_time    = st.time_input("Start Time", value=datetime.time(8, 0),
                                       key="cal_time")
            ev_dur     = st.selectbox("Duration",
                                      ["2 hours", "4 hours", "Full day", "Multiple days"])
            ev_status  = st.selectbox("Status",
                                      ["Scheduled", "Confirmed", "In Progress",
                                       "Completed", "Cancelled"])

        ev_notes = st.text_area("Notes / Special Instructions", height=70,
                                placeholder="Key code: 1234 | Materials already on site | Permit #AP-2024-001")

        if st.button("📅 Add to Schedule", use_container_width=False):
            if not ev_client or not ev_project:
                st.error("⚠️ Client name and job description are required.")
            else:
                new_event = {
                    "cliente":   ev_client,
                    "proyecto":  ev_project,
                    "tecnico":   ev_tech,
                    "fecha":     str(ev_date),
                    "hora":      str(ev_time),
                    "duracion":  ev_dur,
                    "estado":    ev_status,
                    "notas":     ev_notes,
                    "creado":    str(datetime.datetime.now()),
                }
                _save_event(new_event)
                st.success(f"✅ Job scheduled: **{ev_project}** for **{ev_client}** on {ev_date.strftime('%B %d, %Y')}")
                st.rerun()

    # ── View & Filter ────────────────────────────────────────
    st.markdown("---")
    all_events = _load_events()

    if not all_events:
        st.info("No jobs scheduled yet. Add your first job above!")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            all_clients_cal = sorted(set(e.get("cliente", "") for e in all_events))
            filter_client   = st.selectbox("Filter by Client",
                                           ["All Clients"] + all_clients_cal,
                                           key="cal_filter_client")
        with fc2:
            filter_status = st.selectbox("Filter by Status",
                                         ["All", "Scheduled", "Confirmed",
                                          "In Progress", "Completed", "Cancelled"],
                                         key="cal_filter_status")
        with fc3:
            view_mode = st.radio("View", ["Upcoming", "All", "Past"],
                                 horizontal=True, key="cal_view_mode")

        # Apply filters
        today_str = str(datetime.date.today())
        filtered  = all_events[:]

        if filter_client != "All Clients":
            filtered = [e for e in filtered if e.get("cliente") == filter_client]
        if filter_status != "All":
            filtered = [e for e in filtered if e.get("estado") == filter_status]
        if view_mode == "Upcoming":
            filtered = [e for e in filtered if e.get("fecha", "") >= today_str]
        elif view_mode == "Past":
            filtered = [e for e in filtered if e.get("fecha", "") < today_str]

        filtered_sorted = sorted(filtered, key=lambda x: x.get("fecha", ""))

        st.markdown(f"**{len(filtered_sorted)} job(s) found**")
        st.markdown("")

        # Status color map
        STATUS_COLORS = {
            "Scheduled":   "#4a9eff",
            "Confirmed":   "#f6c90e",
            "In Progress": "#ff9800",
            "Completed":   "#4caf50",
            "Cancelled":   "#ff4444",
        }

        for idx, event in enumerate(filtered_sorted):
            # Find original index for deletion
            orig_idx = all_events.index(event) if event in all_events else -1

            ev_fecha_str = event.get("fecha", "")
            try:
                ev_fecha_obj = datetime.datetime.strptime(ev_fecha_str, "%Y-%m-%d").date()
                days_away    = (ev_fecha_obj - datetime.date.today()).days
                if days_away == 0:   countdown = "🔴 TODAY"
                elif days_away < 0:  countdown = f"✅ {abs(days_away)}d ago"
                elif days_away <= 3: countdown = f"🟡 In {days_away}d"
                else:                countdown = f"🟢 In {days_away}d"
                date_display = ev_fecha_obj.strftime("%A, %B %d, %Y")
            except Exception:
                countdown    = ""
                date_display = ev_fecha_str

            status = event.get("estado", "Scheduled")
            sc     = STATUS_COLORS.get(status, "#888888")

            card_col, del_col = st.columns([10, 1])
            with card_col:
                st.markdown(f"""
                <div style="background:#1e2130;padding:14px 16px;border-radius:10px;
                            margin:4px 0;border-left:5px solid {sc};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <strong style="color:#f6c90e;font-size:1rem;">
                                {event.get('proyecto', '')}
                            </strong>
                            &nbsp;&nbsp;
                            <span style="background:{sc};color:#0e1117;padding:1px 7px;
                                         border-radius:4px;font-size:0.75rem;font-weight:bold;">
                                {status}
                            </span>
                            <span style="color:#aaa;margin-left:8px;font-size:0.8rem;">
                                {countdown}
                            </span>
                        </div>
                    </div>
                    <div style="margin-top:4px;line-height:1.7;">
                        <span style="color:#ccc;">👤 {event.get('cliente', '')}</span>
                        &nbsp;|&nbsp;
                        <span style="color:#ccc;">🔧 {event.get('tecnico', 'Unassigned')}</span><br>
                        <span style="color:#aaa;font-size:0.88rem;">
                            📅 {date_display} &nbsp;·&nbsp;
                            🕐 {event.get('hora', 'TBD')} &nbsp;·&nbsp;
                            ⏱ {event.get('duracion', '')}
                        </span>
                        {"<br><span style='color:#888;font-size:0.82rem;'>📝 " + event.get('notas','') + "</span>" if event.get('notas') else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with del_col:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_ev_{idx}_{orig_idx}",
                             help="Delete this event"):
                    _delete_event(orig_idx)
                    st.rerun()

        # ── Summary stats ───────────────────────────────────
        if filtered_sorted:
            st.markdown("---")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Total jobs",    len(filtered_sorted))
            sc2.metric("Scheduled",     sum(1 for e in filtered_sorted if e.get("estado") == "Scheduled"))
            sc3.metric("Confirmed",     sum(1 for e in filtered_sorted if e.get("estado") == "Confirmed"))
            sc4.metric("Completed",     sum(1 for e in filtered_sorted if e.get("estado") == "Completed"))

# ── 📂 CRM & PROJECT GALLERY ──
elif pagina == "📂 CRM & Project Gallery":
    st.title("📂 CRM & Client Folders")
    st.markdown("Navigate hierarchical client files and quick actions.")

    carpetas = [f for f in UPLOADS_DIR.iterdir() if f.is_dir()]
    if not carpetas:
        st.info("No clients found yet. Create an estimate to auto-generate folders.")
    else:
        clientes = [f.name for f in carpetas]
        sel_cliente = st.selectbox("Select Client Workspace", clientes)
        c_dir = UPLOADS_DIR / sel_cliente

        # 🚀 SMART LINKS (Accesos Directos Híbridos)
        st.markdown(f"#### ⚡ Quick Actions for {sel_cliente}")
        btn1, btn2, btn3 = st.columns(3)

        with btn1:
            # Abre Gmail ya buscando el nombre del cliente
            gmail_url = f"https://mail.google.com/mail/u/0/#search/{sel_cliente.replace(' ', '+')}"
            st.link_button("📧 Search in Gmail", gmail_url, use_container_width=True)

        with btn2:
            # Abre Google Calendar directo en la pantalla de "Nuevo Evento"
            gcal_url = "https://calendar.google.com/calendar/u/0/r/eventedit"
            st.link_button("📅 Open Google Calendar", gcal_url, use_container_width=True)

        with btn3:
            # Abre la carpeta local directamente en Kubuntu
            if st.button("📂 Open Local Folder", use_container_width=True):
                try: 
                    subprocess.Popen(["dolphin", str(c_dir.resolve())])
                except: 
                    st.warning("Dolphin file manager not found.")

        st.markdown("---")
        st.markdown("#### 📁 Project Files")
        
        for sub in CLIENT_SUBFOLDERS:
            sub_path = c_dir / sub
            if sub_path.exists():
                archivos = list(sub_path.iterdir())
                with st.expander(f"📁 {sub} ({len(archivos)} files)"):
                    for arch in archivos:
                        st.write(f"- `{arch.name}`")

# ── 🤖 AI ASSISTANT ──
elif pagina == "🤖 AI Assistant":
    st.title("🤖 AI Assistant (Gemini)")
    st.markdown("AI responding in **Spanish**, formatting legal text in **English**.")
    if "chat" not in st.session_state: st.session_state.chat = []
    
    for msg in st.session_state.chat:
        role_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
        st.markdown(f"<div class='chat-message {role_class}'><b>{msg['role'].upper()}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

    user_in = st.chat_input("Ask me anything...")
    if user_in:
        st.session_state.chat.append({"role": "user", "content": user_in})
        sys_prompt = "Eres el asistente experto C-10 de Golden Charge. SIEMPRE RESPONDE EN ESPAÑOL PROFESIONAL, PERO SI DEBES REDACTAR UN DOCUMENTO O EMAIL, HAZLO EN INGLÉS."
        try:
            with st.spinner("Pensando..."):
                resp = gemini_model.generate_content([sys_prompt, user_in])
                st.session_state.chat.append({"role": "assistant", "content": resp.text})
            st.rerun()
        except Exception as e:
            st.error(f"Error AI: {e}")

# ── 🗺️ BLUEPRINT COPILOT ──
elif pagina == "🗺️ Blueprint Copilot":
    st.title("🗺️ Blueprint Copilot")
    st.info("Upload blueprints to let Gemini Vision analyze them.")
    f = st.file_uploader("Upload Image", type=["jpg", "png"])
    if f and st.button("Analyze"):
        with st.spinner("Analyzing..."):
            resp = gemini_model.generate_content(["Describe this blueprint from an electrical C-10 perspective. Output in Spanish.", {"mime_type": f.type, "data": f.read()}])
            st.markdown(f"<div class='calc-box'>{resp.text}</div>", unsafe_allow_html=True)

# ── ⚡ ELECTRICAL CALC & NEC 220.82 ──
elif pagina == "⚡ Electrical Calc & NEC":
    st.title("⚡ Electrical Calculators")
    t1, t2, t3 = st.tabs(["🔴 NEC 220.82 Load Calc", "🔵 Ohm's Law", "🟡 Watt's Law"])

    with t1:
        st.subheader("NEC 220.82 Residential Load Calculation (Optional Method)")
        c1, c2 = st.columns(2)
        sqft = c1.number_input("Total Dwelling Square Footage", 0, value=2500)
        small_app = c2.number_input("Small Appliance Circuits (min 2)", 2, value=2)
        laundry = c1.number_input("Laundry Circuits (min 1)", 1, value=1)
        fixed_app = c2.number_input("Total Nameplate VA of Fixed Appliances", 0, value=6000)
        
        st.markdown("---")
        c3, c4 = st.columns(2)
        hvac = c3.number_input("Largest HVAC Load (VA) (e.g. A/C or Heat)", 0, value=8000)
        ev_amps = c4.number_input("EV Charger Rating (Amps)", 0, value=40)

        if st.button("🧮 Calculate Panel Size", use_container_width=True):
            va_sqft = sqft * 3
            va_small = small_app * 1500
            va_laund = laundry * 1500
            total_general = va_sqft + va_small + va_laund + fixed_app
            
            first_10 = min(10000, total_general)
            rem = max(0, total_general - 10000)
            discounted_gen = first_10 + (rem * 0.40)
            
            ev_va = ev_amps * 240 * 1.25 # Continuous load
            total_va = discounted_gen + hvac + ev_va
            total_amps = total_va / 240

            panel = 100
            if total_amps > 100: panel = 200
            if total_amps > 200: panel = 400

            st.markdown(f"""
            <div class='calc-box'>
                <h3 style='margin:0'>Total Calculated Load: {total_amps:,.1f} Amps</h3>
                <p>General Load (Discounted): {discounted_gen:,.0f} VA</p>
                <p>HVAC Load (100%): {hvac:,.0f} VA</p>
                <p>EV Load (125%): {ev_va:,.0f} VA</p>
                <hr>
                <h4 style='color:#4caf50'>🟢 Recommended Main Service: {panel}A Panel</h4>
            </div>
            """, unsafe_allow_html=True)

    with t2: st.info("Ohm's Law: V = I × R")
    with t3: st.info("Watt's Law: P = V × I")

# ── 🏙️ BAY AREA ESTIMATOR ──
elif pagina == "🏙️ Bay Area Estimator":
    st.title("🏙️ Quick Square Foot Estimator")
    st.info("Pricing ranges from $10/sqft (Basic) to $25/sqft (Premium).")
    
    TIERS = {
        "🔵 Basic — $10/SqFt": {
            "rate": 10,
            "desc": "Minor repairs, outlet replacement, basic fixture installs, small panel work.",
            "color": "#4a9eff"
        },
        "🟡 Standard — $18/SqFt": {
            "rate": 18,
            "desc": "Panel upgrades, full rewires, EV chargers, bathroom/kitchen circuits.",
            "color": "#f6c90e"
        },
        "🔴 Premium — $25/SqFt": {
            "rate": 25,
            "desc": "Full commercial buildouts, smart-home systems, solar tie-ins, service upgrades.",
            "color": "#ff6b6b"
        }
    }

    col_ba1, col_ba2 = st.columns([2, 1])

    with col_ba1:
        sqft = st.number_input("Project Area (Square Feet)", min_value=0.0, step=50.0, format="%.0f", key="ba_sqft")
        selected_tier = st.selectbox("Pricing Tier", list(TIERS.keys()))

        st.markdown(f"""
        <div style="background:#1e2130;padding:0.8rem;border-radius:8px;
                    border-left:3px solid {TIERS[selected_tier]['color']};margin-top:0.5rem;">
            <small style="color:#aaa;">{TIERS[selected_tier]['desc']}</small>
        </div>""", unsafe_allow_html=True)

        include_permit = st.checkbox("Add permit allowance (~$800 flat)", value=True)
        include_markup = st.slider("Additional markup (%)", 0, 30, 10)

    with col_ba2:
        if sqft > 0:
            rate         = TIERS[selected_tier]["rate"]
            base         = sqft * rate
            permit_fee   = 800.0 if include_permit else 0.0
            markup_amt   = base * (include_markup / 100)
            total        = base + permit_fee + markup_amt
            
            # CSLB simple breakdown for visual reference
            deposit = min(total * 0.10, 1000.0)
            remainder = total - deposit
            rough = remainder * 0.50
            final = remainder - rough

            st.markdown(f"""
            <div class="calc-box">
                <p style="color:#f6c90e;font-size:1rem;margin:0 0 8px;">
                    <strong>📋 Quick Estimate</strong>
                </p>
                <hr style="border-color:#f6c90e33;margin:6px 0;">
                <p style="margin:4px 0;">Area: <strong>{sqft:,.0f} sqft</strong></p>
                <p style="margin:4px 0;">Rate: <strong>${rate}/sqft</strong></p>
                <p style="margin:4px 0;">Base Price: <strong>${base:,.2f}</strong></p>
                {"<p style='margin:4px 0;'>Permits: <strong>$800.00</strong></p>" if include_permit else ""}
                {"<p style='margin:4px 0;'>Markup (" + str(include_markup) + "%): <strong>$" + f"{markup_amt:,.2f}" + "</strong></p>" if include_markup > 0 else ""}
                <hr style="border-color:#f6c90e33;margin:6px 0;">
                <p style="font-size:1.3rem;color:#f6c90e;margin:4px 0;">
                    Total: <strong>${total:,.2f}</strong>
                </p>
            </div>""", unsafe_allow_html=True)

            st.markdown("##### ⚖️ Recommended Schedule (CSLB)")
            st.markdown(f"""
            <div class="calc-box">
                <p style="margin:4px 0;">1. Deposit: <strong>${deposit:,.2f}</strong></p>
                <p style="margin:4px 0;">2. Rough Inspection: <strong>${rough:,.2f}</strong></p>
                <p style="margin:4px 0;">3. Final: <strong>${final:,.2f}</strong></p>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Enter the square footage to see a price estimate.")

    st.markdown("---")
    st.markdown("""
    <div style="background:#1e2130;padding:1rem;border-radius:8px;border:1px solid #2d3748;">
        <small style="color:#888;">
            ⚠️ <strong>Disclaimer:</strong> These are rough ballpark figures for initial client conversations only.
            Final pricing must be based on a full site assessment, material takeoff, and permit requirements.
            Prices reflect Bay Area market rates as of 2024–2025.
        </small>
    </div>""", unsafe_allow_html=True)
