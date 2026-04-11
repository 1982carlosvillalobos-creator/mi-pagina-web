# ============================================================
# GOLDEN CHARGE ERP PRO - Sistema de Gestión Empresarial
# Desarrollado para Golden Charge, LLC - Fremont, CA
# ============================================================

import streamlit as st
import os
import json
import datetime
from pathlib import Path
from fpdf import FPDF
import anthropic

# ─────────────────────────────────────────────
# CONFIGURACIÓN INICIAL DE LA APLICACIÓN
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Golden Charge ERP Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para modo oscuro y apariencia profesional
st.markdown("""
<style>
    /* Fondo principal oscuro */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Sidebar oscuro */
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d3748;
    }
    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 15px;
    }
    /* Botones principales */
    .stButton > button {
        background-color: #f6c90e;
        color: #0e1117;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #e0b800;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(246, 201, 14, 0.3);
    }
    /* Encabezados con acento dorado */
    h1, h2, h3 {
        color: #f6c90e !important;
    }
    /* Formularios */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #1e2130;
        color: #ffffff;
        border: 1px solid #2d3748;
        border-radius: 6px;
    }
    /* Separador dorado */
    hr {
        border-color: #f6c90e;
        opacity: 0.3;
    }
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-user {
        background-color: #1e3a5f;
        border-left: 3px solid #4a9eff;
    }
    .chat-assistant {
        background-color: #1e2d1e;
        border-left: 3px solid #f6c90e;
    }
    /* Logo header */
    .company-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1a1d27, #2d3748);
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #f6c90e33;
    }
    /* Galería de imágenes */
    .gallery-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #2d3748;
        margin: 5px;
    }
    /* Tabla de datos */
    .dataframe {
        background-color: #1e2130 !important;
    }
    /* Alertas de éxito */
    .stSuccess {
        background-color: #1e3a1e;
        border: 1px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATOS FIJOS DE LA EMPRESA
# ─────────────────────────────────────────────

COMPANY_INFO = {
    "name": "Golden Charge, LLC",
    "dba": "DBA Golden Charge Electrician Company",
    "address": "38725 Lexington ST, Fremont, CA. 94536",
    "email1": "info@goldencharge.net",
    "email2": "carlos.villalobos@goldencharge.net",
    "phone1": "+1 (510) 221-1258",
    "phone2": "+1 (424) 465-3362",
    "license": "CA License C-10 # 1143055",
    "ein": "EIN: 39-4119592",
    "payment_terms": "50% upfront payment, 50% upon completion"
}

# ─────────────────────────────────────────────
# RUTAS DE CARPETAS
# ─────────────────────────────────────────────

DATA_DIR = Path("data")
UPLOADS_DIR = Path("uploads")
ESTIMATES_FILE = DATA_DIR / "estimates.json"
PROJECTS_FILE = DATA_DIR / "projects.json"

# Crear carpetas si no existen
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# FUNCIONES DE PERSISTENCIA DE DATOS
# ─────────────────────────────────────────────

def cargar_estimados():
    """Carga los estimados guardados desde el archivo JSON."""
    if ESTIMATES_FILE.exists():
        with open(ESTIMATES_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_estimado(estimado):
    """Guarda un nuevo estimado en el archivo JSON."""
    estimados = cargar_estimados()
    estimados.append(estimado)
    with open(ESTIMATES_FILE, "w") as f:
        json.dump(estimados, f, indent=2, default=str)

def cargar_proyectos():
    """Carga los proyectos guardados desde el archivo JSON."""
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_proyecto(proyecto):
    """Guarda un nuevo proyecto en el archivo JSON."""
    proyectos = cargar_proyectos()
    # Evitar duplicados por nombre de proyecto
    nombres = [p["project_name"] for p in proyectos]
    if proyecto["project_name"] not in nombres:
        proyectos.append(proyecto)
        with open(PROJECTS_FILE, "w") as f:
            json.dump(proyectos, f, indent=2, default=str)

# ─────────────────────────────────────────────
# GENERADOR DE PDF PROFESIONAL
# ─────────────────────────────────────────────

class GoldenChargePDF(FPDF):
    """Clase personalizada para generar PDFs con el estilo de Golden Charge."""

    def header(self):
        """Encabezado del PDF con información de la empresa."""
        # Fondo dorado en el encabezado
        self.set_fill_color(246, 201, 14)  # Color dorado
        self.rect(0, 0, 210, 40, 'F')

        # Nombre de la empresa
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(14, 17, 23)  # Texto oscuro sobre fondo dorado
        self.set_xy(10, 8)
        self.cell(0, 8, COMPANY_INFO["name"], ln=True, align='C')

        # DBA
        self.set_font('Helvetica', 'I', 10)
        self.set_xy(10, 17)
        self.cell(0, 5, COMPANY_INFO["dba"], ln=True, align='C')

        # Dirección
        self.set_font('Helvetica', '', 9)
        self.set_xy(10, 23)
        self.cell(0, 4, COMPANY_INFO["address"], ln=True, align='C')

        # Contacto
        self.set_xy(10, 28)
        contact = f"{COMPANY_INFO['phone1']} | {COMPANY_INFO['phone2']} | {COMPANY_INFO['email1']}"
        self.cell(0, 4, contact, ln=True, align='C')

        # Licencia y EIN
        self.set_xy(10, 33)
        license_info = f"{COMPANY_INFO['license']} | {COMPANY_INFO['ein']}"
        self.cell(0, 4, license_info, ln=True, align='C')

        # Línea separadora
        self.set_draw_color(246, 201, 14)
        self.set_line_width(0.5)
        self.line(10, 42, 200, 42)
        self.ln(15)

    def footer(self):
        """Pie de página con número de página y términos de pago."""
        self.set_y(-20)
        self.set_draw_color(246, 201, 14)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"Page {self.page_no()} | {COMPANY_INFO['name']} | {COMPANY_INFO['email1']}", align='C')

    def seccion_titulo(self, titulo):
        """Agrega un título de sección con estilo dorado."""
        self.set_fill_color(246, 201, 14)
        self.set_text_color(14, 17, 23)
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 8, f"  {titulo}", ln=True, fill=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def campo_info(self, label, valor):
        """Agrega un campo de información con label en negrita."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(60, 60, 60)
        self.cell(50, 7, f"{label}:", ln=False)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, str(valor), ln=True)


def generar_pdf_estimado(datos, tipo="Estimate"):
    """
    Genera un PDF profesional para un estimado o factura.
    Retorna los bytes del PDF generado.
    """
    pdf = GoldenChargePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # ── Número de documento y fecha ──
    numero_doc = f"GC-{tipo[:3].upper()}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Título del documento
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(246, 201, 14)
    pdf.cell(0, 12, tipo.upper(), ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Document #: {numero_doc}", ln=True, align='C')
    pdf.ln(5)

    # ── Información del cliente ──
    pdf.seccion_titulo("CLIENT INFORMATION")
    pdf.campo_info("Customer Name", datos.get("customer_name", ""))
    pdf.campo_info("Project Name", datos.get("project_name", ""))
    pdf.campo_info("Address", datos.get("address", ""))
    pdf.campo_info("Date", str(datos.get("date", datetime.date.today())))
    pdf.ln(5)

    # ── Alcance del trabajo ──
    pdf.seccion_titulo("SCOPE OF WORK")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)

    # Texto multilínea para el alcance del trabajo
    scope_text = datos.get("scope_of_work", "")
    pdf.multi_cell(0, 6, scope_text)
    pdf.ln(5)

    # ── Precio total ──
    pdf.seccion_titulo("PRICING")
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(14, 17, 23)
    pdf.set_fill_color(246, 201, 14)

    # Caja de precio total
    precio = datos.get("total_price", 0)
    pdf.cell(0, 12, f"  TOTAL PRICE: ${float(precio):,.2f}", ln=True, fill=True)
    pdf.ln(5)

    # ── Términos de pago ──
    pdf.seccion_titulo("PAYMENT TERMS")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, COMPANY_INFO["payment_terms"], ln=True)
    pdf.ln(3)

    # Desglose de pagos
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(95, 8, "  Upfront Payment (50%):", fill=True, ln=False)
    pdf.cell(95, 8, f"  ${float(precio) * 0.5:,.2f}", fill=True, ln=True)
    pdf.cell(95, 8, "  Upon Completion (50%):", fill=True, ln=False)
    pdf.cell(95, 8, f"  ${float(precio) * 0.5:,.2f}", fill=True, ln=True)
    pdf.ln(8)

    # ── Firma ──
    pdf.seccion_titulo("AUTHORIZATION")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "By signing below, the client agrees to the scope of work and payment terms described above.", ln=True)
    pdf.ln(15)

    # Líneas de firma
    pdf.set_draw_color(0, 0, 0)
    pdf.line(15, pdf.get_y(), 95, pdf.get_y())
    pdf.line(115, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(95, 5, "Client Signature & Date", align='C', ln=False)
    pdf.cell(95, 5, "Golden Charge Representative & Date", align='C', ln=True)

    # Retornar bytes del PDF
    return bytes(pdf.output())


# ─────────────────────────────────────────────
# SIDEBAR - NAVEGACIÓN PRINCIPAL
# ─────────────────────────────────────────────

with st.sidebar:
    # Logo y nombre de la empresa en el sidebar
    st.markdown("""
    <div class="company-header">
        <h2 style="color: #f6c90e; margin: 0; font-size: 1.3rem;">⚡ Golden Charge</h2>
        <p style="color: #aaa; margin: 0; font-size: 0.75rem;">ERP Pro System</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Menú de navegación
    pagina = st.radio(
        "Navigation",
        options=[
            "🏠 Dashboard",
            "📄 Estimates & Invoices",
            "✍️ Contracts",
            "📅 Calendar",
            "📂 Project Gallery",
            "🤖 AI Assistant"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Información de la empresa en el sidebar
    st.markdown("""
    <div style="font-size: 0.7rem; color: #666; padding: 0.5rem;">
        <p>📍 38725 Lexington ST<br>Fremont, CA 94536</p>
        <p>📞 (510) 221-1258</p>
        <p>🔑 C-10 # 1143055</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PÁGINA: DASHBOARD
# ─────────────────────────────────────────────

if pagina == "🏠 Dashboard":
    st.title("⚡ Golden Charge ERP Pro")
    st.markdown("### Welcome back! Here's your business overview.")
    st.markdown("---")

    # Cargar datos para las métricas
    estimados = cargar_estimados()
    proyectos = cargar_proyectos()

    # Calcular métricas
    total_ventas = sum(float(e.get("total_price", 0)) for e in estimados)
    proyectos_activos = len(proyectos)
    total_estimados = len(estimados)

    # Calcular ventas del mes actual
    mes_actual = datetime.datetime.now().month
    anio_actual = datetime.datetime.now().year
    ventas_mes = sum(
        float(e.get("total_price", 0))
        for e in estimados
        if datetime.datetime.strptime(str(e.get("date", "2000-01-01")), "%Y-%m-%d").month == mes_actual
        and datetime.datetime.strptime(str(e.get("date", "2000-01-01")), "%Y-%m-%d").year == anio_actual
    ) if estimados else 0

    # ── Fila de métricas principales ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Sales",
            value=f"${total_ventas:,.2f}",
            delta="All time"
        )

    with col2:
        st.metric(
            label="📅 Sales This Month",
            value=f"${ventas_mes:,.2f}",
            delta=f"{mes_actual}/{anio_actual}"
        )

    with col3:
        st.metric(
            label="📂 Active Projects",
            value=proyectos_activos,
            delta="Total registered"
        )

    with col4:
        st.metric(
            label="📄 Total Estimates",
            value=total_estimados,
            delta="Documents created"
        )

    st.markdown("---")

    # ── Sección de actividad reciente ──
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📋 Recent Estimates")
        if estimados:
            # Mostrar los últimos 5 estimados
            ultimos = estimados[-5:][::-1]
            for est in ultimos:
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.write(f"**{est.get('customer_name', 'N/A')}**")
                        st.caption(est.get('project_name', 'N/A'))
                    with col_b:
                        st.write(est.get('address', 'N/A'))
                        st.caption(str(est.get('date', 'N/A')))
                    with col_c:
                        st.write(f"**${float(est.get('total_price', 0)):,.2f}**")
                    st.markdown("---")
        else:
            st.info("No estimates created yet. Go to **Estimates & Invoices** to create your first one!")

    with col_right:
        st.subheader("📂 Recent Projects")
        if proyectos:
            for proj in proyectos[-5:][::-1]:
                st.markdown(f"""
                <div style="background:#1e2130; padding:10px; border-radius:8px; 
                            margin:5px 0; border-left:3px solid #f6c90e;">
                    <strong style="color:#f6c90e;">{proj.get('project_name', 'N/A')}</strong><br>
                    <small style="color:#aaa;">{proj.get('customer_name', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No projects yet.")

    # ── Gráfico de ventas si hay datos ──
    if len(estimados) > 1:
        st.markdown("---")
        st.subheader("📈 Sales Overview")

        import pandas as pd

        # Preparar datos para el gráfico
        df_ventas = pd.DataFrame(estimados)
        df_ventas['date'] = pd.to_datetime(df_ventas['date'])
        df_ventas['total_price'] = df_ventas['total_price'].astype(float)
        df_ventas = df_ventas.sort_values('date')

        # Gráfico de línea de ventas
        st.line_chart(
            df_ventas.set_index('date')['total_price'],
            use_container_width=True
        )


# ─────────────────────────────────────────────
# PÁGINA: ESTIMATES & INVOICES
# ─────────────────────────────────────────────

elif pagina == "📄 Estimates & Invoices":
    st.title("📄 Estimates & Invoices")
    st.markdown("Create professional estimates and invoices for your clients.")
    st.markdown("---")

    # Pestañas: Crear nuevo vs Ver existentes
    tab_nuevo, tab_lista = st.tabs(["➕ New Document", "📋 All Documents"])

    # ── TAB: Crear nuevo estimado ──
    with tab_nuevo:
        st.subheader("Create New Estimate / Invoice")

        # Tipo de documento
        tipo_doc = st.selectbox(
            "Document Type",
            ["Estimate", "Invoice"],
            help="Select whether this is an estimate or a final invoice"
        )

        st.markdown("#### 👤 Client Information")
        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input("Customer Name *", placeholder="John Smith")
            project_name = st.text_input("Project Name *", placeholder="Panel Upgrade - Main House")
            address = st.text_input("Project Address *", placeholder="123 Main St, Fremont, CA 94536")

        with col2:
            fecha = st.date_input("Date", value=datetime.date.today())
            total_price = st.number_input(
                "Total Price ($) *",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                help="Enter the total project price"
            )

            # Mostrar desglose de pagos en tiempo real
            if total_price > 0:
                st.markdown(f"""
                <div style="background:#1e2130; padding:10px; border-radius:8px; border:1px solid #f6c90e33;">
                    <p style="color:#f6c90e; margin:0; font-size:0.85rem;"><strong>Payment Breakdown:</strong></p>
                    <p style="margin:3px 0; font-size:0.85rem;">• Upfront (50%): <strong>${total_price * 0.5:,.2f}</strong></p>
                    <p style="margin:3px 0; font-size:0.85rem;">• On Completion (50%): <strong>${total_price * 0.5:,.2f}</strong></p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### 🔧 Scope of Work")
        scope_of_work = st.text_area(
            "Describe the work to be performed *",
            height=150,
            placeholder="Example:\n- Install 200A main panel upgrade\n- Replace all outlets in kitchen and bathrooms\n- Install EV charger in garage\n- All work per NEC 2020 and CA Title 24"
        )

        # ── Subida de archivos del proyecto ──
        st.markdown("#### 📎 Project Files")
        st.caption("Upload photos or documents related to this project (optional)")

        archivos_subidos = st.file_uploader(
            "Upload project photos or PDFs",
            type=["jpg", "jpeg", "png", "pdf", "heic", "webp"],
            accept_multiple_files=True,
            help="You can upload multiple files at once"
        )

        st.markdown("---")

        # Botón para generar el PDF
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

        with col_btn1:
            generar = st.button("⚡ Generate PDF", use_container_width=True)

        with col_btn2:
            guardar_solo = st.button("💾 Save Only", use_container_width=True)

        # ── Lógica de generación y guardado ──
        if generar or guardar_solo:
            # Validar campos requeridos
            if not customer_name or not project_name or not address or not scope_of_work:
                st.error("⚠️ Please fill in all required fields marked with *")
            elif total_price <= 0:
                st.error("⚠️ Please enter a valid total price greater than $0")
            else:
                # Preparar datos del estimado
                datos_estimado = {
                    "tipo": tipo_doc,
                    "customer_name": customer_name,
                    "project_name": project_name,
                    "address": address,
                    "date": str(fecha),
                    "scope_of_work": scope_of_work,
                    "total_price": total_price,
                    "created_at": str(datetime.datetime.now())
                }

                # Guardar el estimado en JSON
                guardar_estimado(datos_estimado)

                # Guardar el proyecto para la galería
                guardar_proyecto({
                    "project_name": project_name,
                    "customer_name": customer_name,
                    "address": address,
                    "date": str(fecha)
                })

                # Guardar archivos subidos en la carpeta del proyecto
                if archivos_subidos:
                    # Crear subcarpeta con el nombre del proyecto (sanitizado)
                    nombre_carpeta = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    nombre_carpeta = nombre_carpeta.replace(' ', '_')
                    carpeta_proyecto = UPLOADS_DIR / nombre_carpeta
                    carpeta_proyecto.mkdir(exist_ok=True)

                    archivos_guardados = []
                    for archivo in archivos_subidos:
                        ruta_archivo = carpeta_proyecto / archivo.name
                        with open(ruta_archivo, "wb") as f:
                            f.write(archivo.getbuffer())
                        archivos_guardados.append(archivo.name)

                    st.success(f"✅ {len(archivos_guardados)} file(s) saved to project folder: `{nombre_carpeta}`")

                if generar:
                    # Generar el PDF
                    try:
                        pdf_bytes = generar_pdf_estimado(datos_estimado, tipo=tipo_doc)

                        st.success(f"✅ {tipo_doc} created successfully!")

                        # Botón de descarga del PDF
                        nombre_archivo = f"GoldenCharge_{tipo_doc}_{project_name.replace(' ', '_')}_{fecha}.pdf"
                        st.download_button(
                            label=f"📥 Download {tipo_doc} PDF",
                            data=pdf_bytes,
                            file_name=nombre_archivo,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                else:
                    st.success("✅ Document saved successfully!")

    # ── TAB: Lista de todos los documentos ──
    with tab_lista:
        st.subheader("All Estimates & Invoices")
        estimados = cargar_estimados()

        if estimados:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_tipo = st.selectbox("Filter by Type", ["All", "Estimate", "Invoice"])
            with col_f2:
                filtro_buscar = st.text_input("Search by customer or project", placeholder="Type to search...")

            # Aplicar filtros
            estimados_filtrados = estimados
            if filtro_tipo != "All":
                estimados_filtrados = [e for e in estimados_filtrados if e.get("tipo") == filtro_tipo]
            if filtro_buscar:
                buscar = filtro_buscar.lower()
                estimados_filtrados = [
                    e for e in estimados_filtrados
                    if buscar in e.get("customer_name", "").lower()
                    or buscar in e.get("project_name", "").lower()
                ]

            # Mostrar tabla de estimados
            import pandas as pd
            if estimados_filtrados:
                df = pd.DataFrame(estimados_filtrados)
                df['total_price'] = df['total_price'].apply(lambda x: f"${float(x):,.2f}")
                df_display = df[['tipo', 'customer_name', 'project_name', 'address', 'date', 'total_price']].copy()
                df_display.columns = ['Type', 'Customer', 'Project', 'Address', 'Date', 'Total Price']
                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # Estadísticas del filtro
                total_filtrado = sum(float(e.get("total_price", 0)) for e in estimados_filtrados)
                st.info(f"📊 Showing {len(estimados_filtrados)} documents | Total: ${total_filtrado:,.2f}")
            else:
                st.warning("No documents match your search criteria.")
        else:
            st.info("No estimates or invoices created yet. Use the **New Document** tab to create your first one!")


# ─────────────────────────────────────────────
# PÁGINA: CONTRACTS
# ─────────────────────────────────────────────

elif pagina == "✍️ Contracts":
    st.title("✍️ Contracts")
    st.markdown("Generate and manage professional electrical service contracts.")
    st.markdown("---")

    st.subheader("📝 New Contract")

    col1, col2 = st.columns(2)

    with col1:
        contrato_cliente = st.text_input("Client Name *", placeholder="John Smith")
        contrato_proyecto = st.text_input("Project Name *", placeholder="Electrical Panel Upgrade")
        contrato_direccion = st.text_input("Project Address *", placeholder="123 Main St, Fremont, CA")

    with col2:
        contrato_fecha_inicio = st.date_input("Start Date", value=datetime.date.today())
        contrato_fecha_fin = st.date_input(
            "Estimated Completion Date",
            value=datetime.date.today() + datetime.timedelta(days=14)
        )
        contrato_valor = st.number_input("Contract Value ($)", min_value=0.0, step=100.0, format="%.2f")

    contrato_alcance = st.text_area(
        "Scope of Work *",
        height=120,
        placeholder="Describe all electrical work to be performed..."
    )

    contrato_condiciones = st.text_area(
        "Special Conditions / Notes",
        height=80,
        placeholder="Any special conditions, exclusions, or notes..."
    )

    # Cláusulas estándar del contrato
    st.markdown("#### 📋 Standard Contract Clauses")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        incluir_garantia = st.checkbox("Include 1-Year Workmanship Warranty", value=True)
        incluir_permisos = st.checkbox("Include Permits & Inspections Clause", value=True)
    with col_c2:
        incluir_cambios = st.checkbox("Include Change Order Clause", value=True)
        incluir_limpieza = st.checkbox("Include Site Cleanup Clause", value=True)

    if st.button("📄 Generate Contract PDF", use_container_width=False):
        if not contrato_cliente or not contrato_proyecto or not contrato_alcance:
            st.error("⚠️ Please fill in all required fields.")
        else:
            # Generar PDF del contrato
            try:
                pdf = GoldenChargePDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=25)

                # Título del contrato
                pdf.set_font('Helvetica', 'B', 18)
                pdf.set_text_color(246, 201, 14)
                pdf.cell(0, 12, "ELECTRICAL SERVICE CONTRACT", ln=True, align='C')
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 6, f"Contract Date: {datetime.date.today().strftime('%B %d, %Y')}", ln=True, align='C')
                pdf.ln(5)

                # Partes del contrato
                pdf.seccion_titulo("PARTIES")
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6,
                    f"This Electrical Service Contract ('Agreement') is entered into between:\n\n"
                    f"CONTRACTOR: {COMPANY_INFO['name']} ({COMPANY_INFO['dba']})\n"
                    f"Address: {COMPANY_INFO['address']}\n"
                    f"License: {COMPANY_INFO['license']} | {COMPANY_INFO['ein']}\n\n"
                    f"CLIENT: {contrato_cliente}\n"
                    f"Project Address: {contrato_direccion}"
                )
                pdf.ln(3)

                # Alcance del trabajo
                pdf.seccion_titulo("SCOPE OF WORK")
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, contrato_alcance)
                pdf.ln(3)

                # Fechas y valor
                pdf.seccion_titulo("PROJECT TIMELINE & COMPENSATION")
                pdf.campo_info("Start Date", contrato_fecha_inicio.strftime('%B %d, %Y'))
                pdf.campo_info("Est. Completion", contrato_fecha_fin.strftime('%B %d, %Y'))
                pdf.campo_info("Contract Value", f"${contrato_valor:,.2f}")
                pdf.campo_info("Payment Terms", COMPANY_INFO["payment_terms"])
                pdf.ln(3)

                # Cláusulas seleccionadas
                pdf.seccion_titulo("TERMS AND CONDITIONS")
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(0, 0, 0)

                clausulas = []
                if incluir_garantia:
                    clausulas.append(
                        "WARRANTY: Contractor warrants all workmanship for a period of one (1) year "
                        "from the date of completion. This warranty covers defects in workmanship only "
                        "and does not cover damage caused by misuse, accidents, or acts of nature."
                    )
                if incluir_permisos:
                    clausulas.append(
                        "PERMITS & INSPECTIONS: Contractor shall obtain all necessary permits required "
                        "by local authorities. All work shall be performed in accordance with the National "
                        "Electrical Code (NEC) and California Title 24 requirements."
                    )
                if incluir_cambios:
                    clausulas.append(
                        "CHANGE ORDERS: Any changes to the scope of work must be agreed upon in writing "
                        "by both parties before work begins. Additional costs resulting from change orders "
                        "will be billed separately."
                    )
                if incluir_limpieza:
                    clausulas.append(
                        "SITE CLEANUP: Contractor shall maintain a clean and safe work environment "
                        "throughout the project and shall remove all debris and materials upon completion."
                    )

                # Agregar cláusula de condiciones especiales
                if contrato_condiciones:
                    clausulas.append(f"SPECIAL CONDITIONS: {contrato_condiciones}")

                for i, clausula in enumerate(clausulas, 1):
                    pdf.multi_cell(0, 5, f"{i}. {clausula}")
                    pdf.ln(2)

                # Firmas
                pdf.ln(5)
                pdf.seccion_titulo("SIGNATURES")
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(0, 6,
                    "By signing below, both parties agree to the terms and conditions of this contract."
                )
                pdf.ln(10)

                # Líneas de firma
                pdf.line(15, pdf.get_y(), 90, pdf.get_y())
                pdf.line(115, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)
                pdf.set_font('Helvetica', '', 8)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(95, 5, f"Client: {contrato_cliente}", align='C', ln=False)
                pdf.cell(95, 5, "Golden Charge Representative", align='C', ln=True)
                pdf.ln(2)
                pdf.cell(95, 5, "Date: _______________", align='C', ln=False)
                pdf.cell(95, 5, "Date: _______________", align='C', ln=True)

                contrato_bytes = bytes(pdf.output())
                nombre_contrato = f"GoldenCharge_Contract_{contrato_proyecto.replace(' ', '_')}_{datetime.date.today()}.pdf"

                st.success("✅ Contract generated successfully!")
                st.download_button(
                    label="📥 Download Contract PDF",
                    data=contrato_bytes,
                    file_name=nombre_contrato,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating contract: {str(e)}")


# ─────────────────────────────────────────────
# PÁGINA: CALENDAR
# ─────────────────────────────────────────────

elif pagina == "📅 Calendar":
    st.title("📅 Project Calendar")
    st.markdown("Schedule and track your electrical projects.")
    st.markdown("---")

    # Formulario para agregar evento
    st.subheader("➕ Schedule New Job")

    col1, col2, col3 = st.columns(3)
    with col1:
        cal_cliente = st.text_input("Client Name", placeholder="John Smith")
        cal_proyecto = st.text_input("Job Description", placeholder="Panel upgrade")
    with col2:
        cal_fecha = st.date_input("Job Date", value=datetime.date.today())
        cal_hora = st.time_input("Start Time", value=datetime.time(8, 0))
    with col3:
        cal_duracion = st.selectbox("Duration", ["2 hours", "4 hours", "Full day", "Multiple days"])
        cal_tecnico = st.text_input("Assigned Technician", placeholder="Carlos")

    cal_notas = st.text_area("Notes", height=80, placeholder="Special instructions, materials needed, etc.")

    # Archivo de calendario
    CALENDAR_FILE = DATA_DIR / "calendar.json"

    def cargar_eventos():
        """Carga los eventos del calendario."""
        if CALENDAR_FILE.exists():
            with open(CALENDAR_FILE, "r") as f:
                return json.load(f)
        return []

    def guardar_evento(evento):
        """Guarda un nuevo evento en el calendario."""
        eventos = cargar_eventos()
        eventos.append(evento)
        with open(CALENDAR_FILE, "w") as f:
            json.dump(eventos, f, indent=2, default=str)

    if st.button("📅 Add to Schedule"):
        if cal_cliente and cal_proyecto:
            nuevo_evento = {
                "cliente": cal_cliente,
                "proyecto": cal_proyecto,
                "fecha": str(cal_fecha),
                "hora": str(cal_hora),
                "duracion": cal_duracion,
                "tecnico": cal_tecnico,
                "notas": cal_notas,
                "creado": str(datetime.datetime.now())
            }
            guardar_evento(nuevo_evento)
            st.success(f"✅ Job scheduled for {cal_fecha.strftime('%B %d, %Y')} at {cal_hora.strftime('%I:%M %p')}")
        else:
            st.error("Please enter client name and job description.")

    st.markdown("---")

    # Mostrar calendario de eventos
    st.subheader("📋 Upcoming Jobs")
    eventos = cargar_eventos()

    if eventos:
        # Ordenar por fecha
        eventos_ordenados = sorted(eventos, key=lambda x: x.get("fecha", ""))
        hoy = str(datetime.date.today())

        # Separar en próximos y pasados
        proximos = [e for e in eventos_ordenados if e.get("fecha", "") >= hoy]
        pasados = [e for e in eventos_ordenados if e.get("fecha", "") < hoy]

        if proximos:
            for evento in proximos:
                fecha_evento = datetime.datetime.strptime(evento["fecha"], "%Y-%m-%d")
                dias_restantes = (fecha_evento.date() - datetime.date.today()).days

                if dias_restantes == 0:
                    badge = "🔴 TODAY"
                    color = "#ff4444"
                elif dias_restantes <= 3:
                    badge = f"🟡 In {dias_restantes} days"
                    color = "#f6c90e"
                else:
                    badge = f"🟢 In {dias_restantes} days"
                    color = "#4caf50"

                st.markdown(f"""
                <div style="background:#1e2130; padding:15px; border-radius:10px; 
                            margin:8px 0; border-left:4px solid {color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="color:#f6c90e; font-size:1rem;">{evento['proyecto']}</strong>
                            <span style="color:{color}; margin-left:10px; font-size:0.8rem;">{badge}</span><br>
                            <span style="color:#ccc;">👤 {evento['cliente']}</span> &nbsp;|&nbsp;
                            <span style="color:#ccc;">🔧 {evento.get('tecnico', 'Unassigned')}</span><br>
                            <span style="color:#aaa; font-size:0.85rem;">
                                📅 {fecha_evento.strftime('%A, %B %d, %Y')} at {evento.get('hora', 'TBD')} 
                                ({evento.get('duracion', 'TBD')})
                            </span>
                        </div>
                    </div>
                    {f'<p style="color:#888; font-size:0.8rem; margin-top:5px;">📝 {evento["notas"]}</p>' if evento.get("notas") else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming jobs scheduled.")

        # Mostrar trabajos pasados en un expander
        if pasados:
            with st.expander(f"📁 Past Jobs ({len(pasados)})"):
                for evento in pasados[::-1]:
                    st.markdown(f"**{evento['fecha']}** — {evento['proyecto']} ({evento['cliente']})")
    else:
        st.info("No jobs scheduled yet. Add your first job above!")


# ─────────────────────────────────────────────
# PÁGINA: PROJECT GALLERY
# ─────────────────────────────────────────────

elif pagina == "📂 Project Gallery":
    st.title("📂 Project Gallery")
    st.markdown("View photos and files from all your electrical projects.")
    st.markdown("---")

    # Verificar si hay carpetas de proyectos en uploads/
    carpetas_proyectos = [f for f in UPLOADS_DIR.iterdir() if f.is_dir()]

    if not carpetas_proyectos:
        st.info("""
        📸 No project photos yet!
        
        To add photos to the gallery:
        1. Go to **Estimates & Invoices**
        2. Create or edit an estimate
        3. Upload photos using the file uploader
        
        Photos will be automatically organized by project name.
        """)
    else:
        # Selector de proyecto
        nombres_proyectos = [f.name.replace('_', ' ') for f in carpetas_proyectos]
        proyecto_seleccionado = st.selectbox(
            "Select Project",
            ["All Projects"] + nombres_proyectos
        )

        # Filtrar carpetas según selección
        if proyecto_seleccionado == "All Projects":
            carpetas_mostrar = carpetas_proyectos
        else:
            nombre_carpeta = proyecto_seleccionado.replace(' ', '_')
            carpetas_mostrar = [f for f in carpetas_proyectos if f.name == nombre_carpeta]

        # Mostrar archivos de cada proyecto
        for carpeta in carpetas_mostrar:
            nombre_proyecto = carpeta.name.replace('_', ' ')
            archivos = list(carpeta.iterdir())

            if archivos:
                st.subheader(f"📁 {nombre_proyecto}")

                # Separar imágenes de otros archivos
                extensiones_imagen = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
                imagenes = [f for f in archivos if f.suffix.lower() in extensiones_imagen]
                otros = [f for f in archivos if f.suffix.lower() not in extensiones_imagen]

                # Mostrar imágenes en grid
                if imagenes:
                    st.markdown("**📸 Photos:**")
                    # Grid de 3 columnas para las imágenes
                    cols = st.columns(3)
                    for idx, imagen in enumerate(imagenes):
                        with cols[idx % 3]:
                            try:
                                st.image(
                                    str(imagen),
                                    caption=imagen.name,
                                    use_container_width=True
                                )
                                # Botón de descarga para cada imagen
                                with open(imagen, "rb") as img_file:
                                    st.download_button(
                                        label="⬇️ Download",
                                        data=img_file.read(),
                                        file_name=imagen.name,
                                        mime=f"image/{imagen.suffix[1:].lower()}",
                                        key=f"dl_{carpeta.name}_{imagen.name}"
                                    )
                            except Exception:
                                st.warning(f"Could not display: {imagen.name}")

                # Mostrar otros archivos (PDFs, etc.)
                if otros:
                    st.markdown("**📄 Documents:**")
                    for archivo in otros:
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"📄 `{archivo.name}` ({archivo.stat().st_size / 1024:.1f} KB)")
                        with col_b:
                            with open(archivo, "rb") as doc_file:
                                st.download_button(
                                    label="⬇️ Download",
                                    data=doc_file.read(),
                                    file_name=archivo.name,
                                    mime="application/pdf",
                                    key=f"dl_{carpeta.name}_{archivo.name}"
                                )

                st.markdown("---")


# ─────────────────────────────────────────────
# PÁGINA: AI ASSISTANT
# ─────────────────────────────────────────────

elif pagina == "🤖 AI Assistant":
    st.title("🤖 AI Assistant")
    st.markdown("Your intelligent assistant for drafting contracts, emails, and professional documents.")
    st.markdown("---")

    # Inicializar el historial del chat en la sesión
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []

    # Plantillas de prompts rápidos para el asistente
    st.subheader("⚡ Quick Templates")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)

    prompt_rapido = None

    with col_t1:
        if st.button("📧 Follow-up Email", use_container_width=True):
            prompt_rapido = (
                "Write a professional follow-up email to a client who received an estimate "
                "3 days ago and hasn't responded yet. The email should be friendly but professional, "
                "from Golden Charge Electrician Company."
            )

    with col_t2:
        if st.button("📝 Contract Draft", use_container_width=True):
            prompt_rapido = (
                "Draft a professional electrical service contract introduction paragraph "
                "for Golden Charge, LLC. Include standard terms about licensing, insurance, "
                "and compliance with California electrical codes."
            )

    with col_t3:
        if st.button("⭐ Review Request", use_container_width=True):
            prompt_rapido = (
                "Write a short, friendly email asking a satisfied client to leave a Google review "
                "for Golden Charge Electrician Company. Keep it brief and include a thank you."
            )

    with col_t4:
        if st.button("⚠️ Delay Notice", use_container_width=True):
            prompt_rapido = (
                "Write a professional email to notify a client about a slight project delay "
                "due to permit processing. Apologize professionally and provide a new estimated timeline."
            )

    st.markdown("---")

    # Mostrar historial del chat
    st.subheader("💬 Chat")

    # Contenedor para los mensajes del chat
    chat_container = st.container()

    with chat_container:
        for mensaje in st.session_state.mensajes_chat:
            if mensaje["role"] == "user":
                st.markdown(f"""
                <div class="chat-message chat-user">
                    <strong style="color:#4a9eff;">👤 You:</strong><br>
                    {mensaje["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message chat-assistant">
                    <strong style="color:#f6c90e;">⚡ Golden Charge AI:</strong><br>
                    {mensaje["content"].replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

    # Input del usuario
    col_input, col_send = st.columns([5, 1])

    with col_input:
        user_input = st.text_area(
            "Type your message...",
            value=prompt_rapido if prompt_rapido else "",
            height=100,
            placeholder="Ask me to draft a contract, write an email, explain electrical codes, etc.",
            label_visibility="collapsed",
            key="chat_input"
        )

    with col_send:
        st.markdown("<br>", unsafe_allow_html=True)
        enviar = st.button("Send ➤", use_container_width=True)

    # Botón para limpiar el chat
    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Clear Chat"):
            st.session_state.mensajes_chat = []
            st.rerun()

    # Procesar el mensaje del usuario
    if (enviar or prompt_rapido) and (user_input or prompt_rapido):
        mensaje_a_enviar = user_input if user_input else prompt_rapido

        if mensaje_a_enviar:
            # Agregar mensaje del usuario al historial
            st.session_state.mensajes_chat.append({
                "role": "user",
                "content": mensaje_a_enviar
            })

            # Llamar a la API de Anthropic
            try:
                api_key = os.getenv("ANTHROPIC_API_KEY")

                if not api_key:
                    st.error("""
                    ⚠️ **API Key not found!**
                    
                    Please set your Anthropic API key:
                    ```
                    export ANTHROPIC_API_KEY='your-key-here'
                    ```
                    Or add it to your `.env` file or Streamlit secrets.
                    """)
                else:
                    # Crear cliente de Anthropic
                    cliente_ai = anthropic.Anthropic(api_key=api_key)

                    # Contexto del sistema para el asistente
                    system_prompt = f"""You are a professional business assistant for {COMPANY_INFO['name']} 
                    ({COMPANY_INFO['dba']}), an electrical contracting company based in Fremont, California.
                    
                    Company Details:
                    - Address: {COMPANY_INFO['address']}
                    - Phone: {COMPANY_INFO['phone1']}, {COMPANY_INFO['phone2']}
                    - Email: {COMPANY_INFO['email1']}, {COMPANY_INFO['email2']}
                    - License: {COMPANY_INFO['license']}
                    - {COMPANY_INFO['ein']}
                    
                    Your role is to help draft professional business documents, emails, contracts, 
                    and communications in English. Always maintain a professional yet approachable tone.
                    When drafting documents, include the company information where appropriate.
                    You are knowledgeable about California electrical codes, NEC standards, and 
                    electrical contracting business practices."""

                    # Preparar mensajes para la API
                    mensajes_api = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.mensajes_chat
                    ]

                    # Mostrar spinner mientras se procesa
                    with st.spinner("⚡ Generating response..."):
                        respuesta = cliente_ai.messages.create(
                            model="claude-opus-4-5",
                            max_tokens=2048,
                            system=system_prompt,
                            messages=mensajes_api
                        )

                    # Extraer el texto de la respuesta
                    texto_respuesta = respuesta.content[0].text

                    # Agregar respuesta al historial
                    st.session_state.mensajes_chat.append({
                        "role": "assistant",
                        "content": texto_respuesta
                    })

                    # Recargar para mostrar la nueva respuesta
                    st.rerun()

            except anthropic.APIConnectionError:
                st.error("❌ Connection error. Please check your internet connection.")
            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key. Please check your ANTHROPIC_API_KEY.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
