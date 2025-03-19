import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os  # Añadimos esta importación para usar os.environ
from together import Together

# Configuración de la página
st.set_page_config(
    page_title="Portal de Empleos",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar datos desde el archivo JSON
@st.cache_data
def load_data():
    try:
        with open("joined_data_standar.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo JSON: {e}")
        return []

# Función para obtener el embedding de la consulta usando Together AI
def get_query_embedding(query, api_key):
    os.environ['TOGETHER_API_KEY'] = api_key
    client = Together()
    response = client.embeddings.create(
        model="BAAI/bge-large-en-v1.5",
        input=[query]
    )
    return response.data[0].embedding

# Título y pestañas
st.title("Portal de Empleos Tech")
tabs = st.tabs(["Explorar Ofertas", "Buscador Semántico"])

# Pestaña 1: Explorar Ofertas
with tabs[0]:
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
        
        # Estilo CSS para las tarjetas
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
            margin-top: 15px;
        }
        .job-link a {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        .job-link a:hover {
            background-color: #45a049;
        }
        .job-skills {
            margin-top: 15px;
        }
        .skill-tag {
            display: inline-block;
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 5px 10px;
            margin-right: 8px;
            margin-bottom: 8px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar trabajos como tarjetas
        for job in filtered_jobs:
            with st.container():
                # Formatear la fecha
                date_str = job.get("date", "")
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d %b, %Y")
                except:
                    formatted_date = date_str
                
                # Obtener las habilidades
                skills = job.get("skills", [])
                skills_html = ""
                if skills:
                    skills_html = '<div class="job-skills">'
                    for skill in skills:
                        skills_html += f'<span class="skill-tag">{skill}</span>'
                    skills_html += '</div>'
                
                # Crear la tarjeta HTML con enlace directo
                job_html = f"""
                <div class="job-card">
                    <div class="job-title">{job.get("title", "")}</div>
                    <div class="job-company">{job.get("company", "")}</div>
                    <div class="job-details">
                        <span>📍 {job.get("location", "")}</span>
                        <span>📅 {formatted_date}</span>
                        <span>🔍 {job.get("source", "")}</span>
                    </div>
                    {skills_html}
                    <div class="job-link">
                        <a href="{job.get("link", "")}" target="_blank">Ver oferta</a>
                    </div>
                </div>
                """
                st.markdown(job_html, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.error("No se pudieron cargar los datos. Verifica que el archivo 'joined_data_standar.json' exista y tenga el formato correcto.")

    # Añadir pie de página
    st.caption("Portal de Empleos - Construido con Streamlit")

# Pestaña 2: Buscador Semántico
with tabs[1]:
    st.write("Busca ofertas de trabajo usando una consulta semántica.")
    
    # Campo de entrada para la consulta
    user_query = st.text_input("Ingresa tu consulta (ejemplo: 'AI engineer with Python')", "")
    
    # Botón para generar el embedding
    if st.button("Generar Embedding"):
        if user_query:
            try:
                api_key = st.secrets["together"]["TOGETHER_API_KEY"]
                embedding = get_query_embedding(user_query, api_key)
                st.write(f"Vector de embedding (primeros 10 valores): {embedding[:10]}... (total {len(embedding)} dimensiones)")
                st.json({"embedding": embedding.tolist()})
            except Exception as e:
                st.error(f"Error al generar el embedding: {e}")
        else:
            st.warning("Por favor, ingresa una consulta.")

# Añadir pie de página
st.caption("Portal de Empleos - Construido con Streamlit")