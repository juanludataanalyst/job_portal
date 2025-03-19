import streamlit as st
import pandas as pd
import json
import pickle
from datetime import datetime
import os
from together import Together
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Configuración de la página
st.set_page_config(
    page_title="Portal de Empleos",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key for Together AI
TOGETHER_API_KEY = st.secrets["together"]["TOGETHER_API_KEY"]

# Free serverless models
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
LLAMA_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

# Función para generar respuesta del modelo de texto
def generate_ai_explanation(jobs, user_query, client):
    """
    Generate personalized explanations for job recommendations based on user query
    
    Args:
        jobs: List of jobs with their similarity scores
        user_query: User's search query
        client: Together API client
        
    Returns:
        Dictionary with overall explanation and per-job explanations
    """
    # Prepare job data for the model (limited to essential fields)
    job_data = []
    for job_id, similarity, job in jobs:
        job_data.append({
            "id": job_id,
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "skills": job.get("skills", []),
            "location": job.get("location", ""),
            "type": job.get("type", ""),
            "similarity_score": f"{similarity:.4f}"
        })
    
    # Create the prompt for the model
    prompt = f"""
You are an AI career assistant helping to explain job recommendations.

USER QUERY: "{user_query}"

JOB LISTINGS (ordered by relevance):
{json.dumps(job_data, indent=2)}

Your task:
1. Provide a brief overview explaining how these jobs match the user's search query.
2. For each job, provide a short personalized explanation of why it might be a good fit based on the query.
3. If any jobs don't fully match some criteria in the query (like location preferences, experience level, job type), mention it.
4. Format your response as a JSON with these keys:
   - "overall_explanation": A paragraph explaining the overall match
   - "job_explanations": A dictionary with job IDs as keys and explanations as values

Keep explanations concise and focused on the match between query and job requirements.
"""
    
    try:
        # Try with DeepSeek first
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7
        )
        explanation = response.choices[0].message.content
    except Exception as e:
        try:
            # Fall back to Llama if DeepSeek fails
            response = client.chat.completions.create(
                model=LLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.7
            )
            explanation = response.choices[0].message.content
        except Exception as e2:
            st.error(f"Error generating explanations: {str(e2)}")
            return {
                "overall_explanation": "Unable to generate explanations at this time.",
                "job_explanations": {}
            }
    
    # Parse the response
    try:
        try:
            return json.loads(explanation)
        except:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', explanation)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                json_match = re.search(r'({[\s\S]*})', explanation)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    return {
                        "overall_explanation": explanation,
                        "job_explanations": {}
                    }
    except Exception as e:
        st.warning(f"Could not parse AI explanation: {str(e)}")
        return {
            "overall_explanation": explanation,
            "job_explanations": {}
        }

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

# Función para cargar los vectores precalculados
@st.cache_data
def load_job_vectors():
    try:
        with open("job_vectors.pkl", "rb") as f:
            job_vectors = pickle.load(f)
        return job_vectors
    except Exception as e:
        st.error(f"Error al cargar job_vectors.pkl: {e}")
        return {}

# Función para obtener el embedding de la consulta usando Together AI
def get_query_embedding(query, api_key):
    os.environ['TOGETHER_API_KEY'] = api_key
    client = Together()
    response = client.embeddings.create(
        model="BAAI/bge-large-en-v1.5",
        input=[query]
    )
    return response.data[0].embedding

# Función para calcular las ofertas más relevantes
def get_top_similar_jobs(query_embedding, job_vectors, top_n=10):
    similarities = []
    for job_id, job_data in job_vectors.items():
        job_embedding = np.array(job_data["embedding"])
        if job_embedding.shape != (1024,):
            st.warning(f"Embedding incorrecto para job_id {job_id}: {job_embedding.shape}")
            continue
        job_embedding = job_embedding.reshape(1, -1)
        query_embedding_array = np.array(query_embedding).reshape(1, -1)
        similarity = cosine_similarity(query_embedding_array, job_embedding)[0][0]
        if similarity > 0.5:  # Filtrar similitudes mayores a 0.5
            similarities.append((job_id, similarity, job_data["data"]))

    # Ordenar por similitud descendente
    similarities.sort(key=lambda x: x[1], reverse=True)
    # Devolver las top_n ofertas
    return similarities[:top_n]

# Título y pestañas
st.title("Portal de Empleos Tech")
tabs = st.tabs(["Explorar Ofertas", "Buscador Semántico"])

# Estilos CSS para la aplicación
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
.job-explanation {
    background-color: #F5F5F5;
    border-left: 3px solid #3498DB;
    padding: 10px 15px;
    margin-top: 10px;
    border-radius: 0 5px 5px 0;
    font-style: italic;
    color: #444;
}
.overall-explanation {
    background-color: #EBF5FB;
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    border-left: 4px solid #3498DB;
}
</style>
""", unsafe_allow_html=True)

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

# Pestaña 2: Buscador Semántico
with tabs[1]:
    st.write("Busca ofertas de trabajo usando una consulta semántica.")
    
    # Campo de entrada para la consulta
    user_query = st.text_input("Ingresa tu consulta (ejemplo: 'AI engineer with Python')", "")
    
    # Opción para mostrar explicaciones de IA
    show_ai_explanations = st.checkbox("Mostrar explicaciones de IA", value=True)
    
    # Botón para generar el embedding y buscar
    if st.button("Buscar Ofertas"):
        if user_query:
            try:
                # Mostrar un spinner mientras se procesa
                with st.spinner("Buscando ofertas relevantes..."):
                    # Establecer la API key para Together
                    os.environ['TOGETHER_API_KEY'] = TOGETHER_API_KEY
                    client = Together()
                    
                    # Obtener el embedding de la consulta
                    query_embedding = get_query_embedding(user_query, TOGETHER_API_KEY)
                    
                    # Cargar los vectores precalculados
                    job_vectors = load_job_vectors()
                    
                    if job_vectors:
                        # Obtener las ofertas más relevantes (similitud > 0.5)
                        top_jobs = get_top_similar_jobs(query_embedding, job_vectors, top_n=10)
                        
                        if top_jobs:
                            # Si se solicitan explicaciones de IA
                            ai_explanations = {}
                            if show_ai_explanations:
                                with st.spinner("Generando explicaciones con IA..."):
                                    ai_explanations = generate_ai_explanation(top_jobs, user_query, client)
                            
                            # Mostrar explicación general si existe
                            if show_ai_explanations and "overall_explanation" in ai_explanations:
                                st.markdown(f"""
                                <div class="overall-explanation">
                                    <h3>💡 Análisis de resultados</h3>
                                    <p>{ai_explanations["overall_explanation"]}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.write(f"Mostrando las {len(top_jobs)} ofertas más relevantes (similitud > 0.5):")
                            
                            # Mostrar las ofertas como tarjetas
                            for job_id, similarity, job in top_jobs:
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
                                    
                                    # Obtener explicación personalizada si existe
                                    explanation_html = ""
                                    if show_ai_explanations and "job_explanations" in ai_explanations and job_id in ai_explanations["job_explanations"]:
                                        explanation_html = f"""
                                        <div class="job-explanation">
                                            <p>💡 {ai_explanations["job_explanations"][job_id]}</p>
                                        </div>
                                        """
                                    
                                    # Crear la tarjeta HTML completa
                                    job_html = f"""
                                    <div class="job-card">
                                        <div class="job-title">{job.get("title", "")}</div>
                                        <div class="job-company">{job.get("company", "")}</div>
                                        <div class="job-details">
                                            <span>📍 {job.get("location", "")}</span>
                                            <span>📅 {formatted_date}</span>
                                            <span>🔍 {job.get("source", "")}</span>
                                            <span>💯 Similitud: {similarity:.4f}</span>
                                        </div>
                                        {skills_html}
                                        {explanation_html}
                                        <div class="job-link">
                                            <a href="{job.get("link", "")}" target="_blank">Ver oferta</a>
                                        </div>
                                    </div>
                                    """
                                    st.markdown(job_html, unsafe_allow_html=True)
                                    st.markdown("---")
                        else:
                            st.warning("No se encontraron ofertas con similitud mayor a 0.5.")
                            
                            # Ofrecer sugerencias si no hay resultados
                            st.info("""
                            Sugerencias para mejorar tu búsqueda:
                            - Utiliza términos más generales
                            - Prueba con tecnologías o habilidades relacionadas
                            """)
                    else:
                        st.error("No se pudieron cargar los vectores precalculados.")
            except Exception as e:
                st.error(f"Error al procesar la consulta: {e}")
        else:
            st.warning("Por favor, ingresa una consulta.")

# Añadir pie de página
st.caption("Portal de Empleos - Construido con Streamlit")