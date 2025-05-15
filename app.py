# app.py
import streamlit as st
import os
import textwrap
from datetime import datetime
from src.study_agent import StudyAgent
from src.user_model import UserProfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ── CONFIGURACIÓN DE PÁGINA Y ESTILOS ─────────────────────────────────────────
LOGO_PATH = "imgs/Brainee_ByteTutor.png"

st.set_page_config(
    page_title="Brainee ByteTutor",
    page_icon=LOGO_PATH,
    layout="wide",
)

# CSS personalizado
st.markdown(
    """
    <style>
      /* Ajuste de márgenes y padding */
      .main .block-container { padding-top: 1rem; padding-left: 2rem; padding-right: 2rem; }
      /* Botones con color de marca */
      .stButton>button { background-color: #1E88E5; color: white; font-weight: bold; }
      /* Sidebar header */
      .css-1d391kg h2 { color: #1E88E5; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header con logo + título
col_logo, col_title = st.columns([1, 8], gap="small")
with col_logo:
    st.image(LOGO_PATH, width=64)
with col_title:
    st.markdown("<h1 style='color:#1E88E5; margin-bottom: 0;'>Brainee ByteTutor</h1>", unsafe_allow_html=True)

st.write("---")

# ── CARPETA DE EXPORTACIÓN ─────────────────────────────────────────────────────
if not os.path.exists("exports"):
    os.makedirs("exports")

# ── INICIALIZAR AGENTE ──────────────────────────────────────────────────────────
agent = StudyAgent()

# ── SIDEBAR: PERSONALIZACIÓN DEL ESTUDIANTE ────────────────────────────────────
st.sidebar.header("🎓 Personalización del Estudiante")
learning_style  = st.sidebar.selectbox("🧠 Estilo de Aprendizaje", ["Visual", "Auditivo", "Kinestésico", "Lectura/Escritura"])
knowledge_level = st.sidebar.selectbox("📈 Nivel de Conocimiento", ["Principiante", "Intermedio", "Avanzado"])

# ── SUBIR ARCHIVO ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Sube un archivo PDF o TXT", type=["pdf", "txt"])
if uploaded_file:
    ext = uploaded_file.name.split(".")[-1]
    temp_path = f"temp_upload.{ext}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Ingestión y vista previa
    texto = agent.ingest(temp_path)
    st.subheader("👀 Vista previa del documento")
    st.text(texto[:1000])
    st.write("---")

    col1, col2, col3 = st.columns(3)
    export_data = {}

    # ── Generar preguntas ─────────────────────────────────────────────────────
    with col1:
        if st.button("🧠 Generar preguntas"):
            preguntas = agent.ask_questions(
                texto,
                n=5,
                style=learning_style,
                level=knowledge_level
            )
            export_data["preguntas"] = preguntas
            st.markdown("### ❓ Preguntas de comprensión")
            for i, q in enumerate(preguntas, start=1):
                st.markdown(f"{i}. {q}")

    # ── Generar resumen ────────────────────────────────────────────────────────
    with col2:
        if st.button("📝 Resumen"):
            resumen = agent.get_summary(texto)
            export_data["resumen"] = resumen
            st.markdown("### 📝 Resumen")
            st.write(resumen)

    # ── Adaptar a estilo ───────────────────────────────────────────────────────
    with col3:
        if st.button("🎨 Adaptar a mi estilo"):
            adaptacion = agent.adapt_to_user(
                texto,
                style=learning_style,
                level=knowledge_level
            )
            export_data["adaptacion"] = adaptacion
            st.markdown("### 🌟 Estrategia de estudio adaptada")
            st.markdown(adaptacion, unsafe_allow_html=True)

    st.write("---")

    # ── Consulta específica (RAG) ─────────────────────────────────────────────
    consulta = st.text_input("🔍 Haz una consulta específica sobre el documento:")
    if consulta:
        agent.index_text_sections(texto)
        resultados = agent.retrieve_relevant_sections(consulta)
        export_data["consulta"] = consulta
        export_data["resultados"] = resultados
        st.markdown("### 🤖 Respuesta generada")
        st.write(resultados[0])

    # ── Ver progreso ────────────────────────────────────────────────────────────
    if st.button("📊 Ver progreso"):
        progreso = agent.get_progress()
        st.markdown("### 📈 Progreso")
        st.json(progreso)

    st.write("---")

    # ── Exportar a PDF ──────────────────────────────────────────────────────────
    if st.button("📥 Exportar resultados (.pdf)"):
        # Asegurar datos
        if "resumen" not in export_data:
            export_data["resumen"] = agent.get_summary(texto)
        if "preguntas" not in export_data:
            export_data["preguntas"] = agent.ask_questions(texto, n=5, style=learning_style, level=knowledge_level)
        if "consulta" not in export_data:
            export_data["consulta"] = ""
            export_data["resultados"] = ["(Sin respuesta generada)"]
        if "adaptacion" not in export_data:
            export_data["adaptacion"] = agent.adapt_to_user(texto, style=learning_style, level=knowledge_level)

        filename = f"exports/informe_estudio_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        class PDFWriter:
            def __init__(self, canvas_obj, page_height):
                self.c = canvas_obj
                self.y = page_height - 40
                self.height = page_height

            def write_line(self, text, size=11, max_chars=90):
                self.c.setFont("Helvetica", size)
                lines = textwrap.wrap(text, width=max_chars)
                for line in lines:
                    if self.y < 50:
                        self.c.showPage()
                        self.y = self.height - 40
                        self.c.setFont("Helvetica", size)
                    self.c.drawString(50, self.y, line)
                    self.y -= 20

        writer = PDFWriter(c, height)
        writer.write_line("📚 Informe del Asistente de Estudio", size=14)
        writer.write_line(f"Fecha: {datetime.now():%Y-%m-%d %H:%M}")
        writer.write_line("")

        # Resumen
        writer.write_line("📝 Resumen:", size=12)
        for line in export_data["resumen"].split("\n"):
            writer.write_line(line)
        writer.write_line("")

        # Preguntas
        writer.write_line("❓ Preguntas de comprensión:", size=12)
        for i, q in enumerate(export_data["preguntas"], 1):
            writer.write_line(f"{i}. {q}")
        writer.write_line("")

        # Adaptación
        writer.write_line("🎨 Estrategia de estudio adaptada:", size=12)
        for line in export_data["adaptacion"].split("\n"):
            writer.write_line(line)
        writer.write_line("")

        # Consulta y respuesta
        writer.write_line("🔍 Consulta realizada:", size=12)
        writer.write_line(export_data["consulta"])
        writer.write_line("🤖 Respuesta generada:")
        for line in export_data["resultados"][0].split("\n"):
            writer.write_line(line)

        c.save()

        with open(filename, "rb") as f:
            st.download_button(
                "📄 Descargar PDF",
                f,
                file_name=os.path.basename(filename),
                mime="application/pdf"
            )