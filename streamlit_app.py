import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Portal de Empleos",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar datos desde el archivo JSON
@st.cache_data
def load_data():
    try:
        with open("joined_data_standar.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo JSON: {e}")
        return []

# Título y descripción
st.title("Portal de Empleos Tech")
st.write("Explora ofertas de trabajo disponibles en el sector tecnológico.")

# Cargar los datos
jobs_data = load_data()

if jobs_data:
    # Añadir filtros en la barra lateral
    st.sidebar.header("Filtros")
    
    # Extraer valores únicos para filtros
    companies = ["Todas"] + sorted(set(job.get("company", "") for job in jobs_data))
    locations = ["Todas"] + sorted(set(job.get("location", "") for job in jobs_data))
    sources = ["Todas"] + sorted(set(job.get("source", "") for job in jobs_data))
    
    # Filtro de empresa
    selected_company = st.sidebar.selectbox("Empresa", companies)
    
    # Filtro de ubicación
    selected_location = st.sidebar.selectbox("Ubicación", locations)
    
    # Filtro de fuente
    selected_source = st.sidebar.selectbox("Fuente", sources)
    
    # Búsqueda por texto
    search_term = st.sidebar.text_input("Buscar por título o empresa", "")
    
    # Aplicar filtros
    filtered_jobs = jobs_data.copy()
    
    if selected_company != "Todas":
        filtered_jobs = [job for job in filtered_jobs if job.get("company") == selected_company]
    
    if selected_location != "Todas":
        filtered_jobs = [job for job in filtered_jobs if job.get("location") == selected_location]
    
    if selected_source != "Todas":
        filtered_jobs = [job for job in filtered_jobs if job.get("source") == selected_source]
    
    # Filtrar por término de búsqueda
    if search_term:
        filtered_jobs = [
            job for job in filtered_jobs 
            if search_term.lower() in job.get("title", "").lower() 
            or search_term.lower() in job.get("company", "").lower()
        ]
    
    # Mostrar número de resultados
    st.write(f"Mostrando {len(filtered_jobs)} de {len(jobs_data)} ofertas de trabajo")
    
    # Definir el estilo CSS para las tarjetas
    st.markdown("""
    <style>
    .job-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .job-title {
        color: #2C3E50;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .job-company {
        color: #3498DB;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .job-details {
        display: flex;
        justify-content: space-between;
        color: #7F8C8D;
        margin-bottom: 10px;
    }
    .job-link {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar trabajos como tarjetas
    for job in filtered_jobs:
        # Crear un contenedor para cada trabajo
        with st.container():
            # Formatear la fecha
            date_str = job.get("date", "")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b, %Y")
            except:
                formatted_date = date_str
            
            # Crear la tarjeta HTML
            job_html = f"""
            <div class="job-card">
                <div class="job-title">{job.get("title", "")}</div>
                <div class="job-company">{job.get("company", "")}</div>
                <div class="job-details">
                    <span>📍 {job.get("location", "")}</span>
                    <span>📅 {formatted_date}</span>
                    <span>🔍 {job.get("source", "")}</span>
                </div>
                <div class="job-link">
                    <a href="{job.get("link", "")}" target="_blank">Ver oferta</a>
                </div>
            </div>
            """
            st.markdown(job_html, unsafe_allow_html=True)
            
            # Añadir botones de acción
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(f"Aplicar 📝", key=f"apply_{job.get('id', '')}"):
                    st.session_state[f"show_form_{job.get('id', '')}"] = True
            
            # Mostrar formulario si se ha pulsado el botón
            if st.session_state.get(f"show_form_{job.get('id', '')}", False):
                with st.expander("Formulario de aplicación", expanded=True):
                    st.write(f"Aplicando a: {job.get('title', '')} en {job.get('company', '')}")
                    st.text_input("Nombre completo")
                    st.text_input("Email")
                    st.text_input("Teléfono")
                    st.file_uploader("Subir CV (PDF)", type=["pdf"])
                    if st.button("Enviar solicitud", key=f"submit_{job.get('id', '')}"):
                        st.success("¡Tu solicitud ha sido enviada correctamente!")
                        st.session_state[f"show_form_{job.get('id', '')}"] = False
            
            st.markdown("---")
else:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'joined_data_standar.json' exista y tenga el formato correcto.")

# Añadir pie de página
st.caption("Portal de Empleos - Construido con Streamlit")