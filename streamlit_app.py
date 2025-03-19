import streamlit as st
import json
import pickle
from datetime import datetime
import os
from together import Together
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from prompts import get_ai_explanation_prompt

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

# Cargar CSS externo
with open("styles.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Función para generar respuesta del modelo de texto
def generate_ai_explanation(jobs, user_query, client):
    prompt = get_ai_explanation_prompt(jobs, user_query)
    
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7
        )
        explanation = response.choices[0].message.content
    except Exception as e:
        try:
            response = client.chat.completions.create(
                model=LLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.7
            )
            explanation = response.choices[0].message.content
        except Exception as e2:
            st.error(f"Error generating explanations: {str(e2)}")
            return {"overall_explanation": "Unable to generate explanations at this time.", "job_explanations": {}}
    
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
                    return {"overall_explanation": explanation, "job_explanations": {}}
    except Exception as e:
        st.warning(f"Could not parse AI explanation: {str(e)}")
        return {"overall_explanation": explanation, "job_explanations": {}}

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

# Función para obtener el embedding de la consulta
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
        if similarity > 0.5:
            similarities.append((job_id, similarity, job_data["data"]))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

# Título y pestañas
st.title("Portal de Empleos Tech")
tabs = st.tabs(["Explorar Ofertas", "Buscador Semántico"])

# Pestaña 1: Explorar Ofertas
with tabs[0]:
    st.write("Explora ofertas de trabajo disponibles en el sector tecnológico.")
    jobs_data = load_data()

    if jobs_data:
        st.sidebar.header("Filtros")
        companies = ["Todas"] + sorted(set(job.get("company", "") for job in jobs_data))
        locations = ["Todas"] + sorted(set(job.get("location", "") for job in jobs_data))
        sources = ["Todas"] + sorted(set(job.get("source", "") for job in jobs_data))
        
        selected_company = st.sidebar.selectbox("Empresa", companies)
        selected_location = st.sidebar.selectbox("Ubicación", locations)
        selected_source = st.sidebar.selectbox("Fuente", sources)
        search_term = st.sidebar.text_input("Buscar por título o empresa", "")
        
        filtered_jobs = jobs_data.copy()
        if selected_company != "Todas":
            filtered_jobs = [job for job in filtered_jobs if job.get("company") == selected_company]
        if selected_location != "Todas":
            filtered_jobs = [job for job in filtered_jobs if job.get("location") == selected_location]
        if selected_source != "Todas":
            filtered_jobs = [job for job in filtered_jobs if job.get("source") == selected_source]
        if search_term:
            filtered_jobs = [job for job in filtered_jobs 
                           if search_term.lower() in job.get("title", "").lower() 
                           or search_term.lower() in job.get("company", "").lower()]
        
        st.write(f"Mostrando {len(filtered_jobs)} de {len(jobs_data)} ofertas de trabajo")
        
        for job in filtered_jobs:
            with st.container():
                date_str = job.get("date", "")
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%d %b, %Y")
                except:
                    formatted_date = date_str
                
                skills = job.get("skills", [])
                skills_html = '<div class="job-skills">' + ''.join(f'<span class="skill-tag">{skill}</span>' for skill in skills) + '</div>' if skills else ''
                
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
        st.error("No se pudieron cargar los datos.")

# Pestaña 2: Buscador Semántico
with tabs[1]:
    st.write("Busca ofertas de trabajo usando una consulta semántica.")
    user_query = st.text_input("Ingresa tu consulta (ejemplo: 'AI engineer with Python')", "")
    show_ai_explanations = st.checkbox("Mostrar explicaciones de IA", value=True)
    
    if st.button("Buscar Ofertas"):
        if user_query:
            with st.spinner("Buscando ofertas relevantes..."):
                os.environ['TOGETHER_API_KEY'] = TOGETHER_API_KEY
                client = Together()
                query_embedding = get_query_embedding(user_query, TOGETHER_API_KEY)
                job_vectors = load_job_vectors()
                
                if job_vectors:
                    top_jobs = get_top_similar_jobs(query_embedding, job_vectors)
                    if top_jobs:
                        ai_explanations = {}
                        if show_ai_explanations:
                            with st.spinner("Generando explicaciones con IA..."):
                                ai_explanations = generate_ai_explanation(top_jobs, user_query, client)
                        
                        if show_ai_explanations and "overall_explanation" in ai_explanations:
                            st.markdown(f'<div class="overall-explanation"><h3>💡 Análisis de resultados</h3><p>{ai_explanations["overall_explanation"]}</p></div>', unsafe_allow_html=True)
                        
                        st.write(f"Mostrando las {len(top_jobs)} ofertas más relevantes (similitud > 0.5):")
                        
                        for job_id, similarity, job in top_jobs:
                            with st.container():
                                date_str = job.get("date", "")
                                try:
                                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                                    formatted_date = date_obj.strftime("%d %b, %Y")
                                except:
                                    formatted_date = date_str
                                
                                skills = job.get("skills", [])
                                skills_html = '<div class="job-skills">' + ''.join(f'<span class="skill-tag">{skill}</span>' for skill in skills) + '</div>' if skills else ''
                                
                                explanation_html = f'<div class="job-explanation"><p>💡 {ai_explanations["job_explanations"][job_id]}</p></div>' if (show_ai_explanations and "job_explanations" in ai_explanations and job_id in ai_explanations["job_explanations"]) else ""
                                
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
                        st.info("Sugerencias: Usa términos más generales o prueba con habilidades relacionadas.")
                else:
                    st.error("No se pudieron cargar los vectores precalculados.")
        else:
            st.warning("Por favor, ingresa una consulta.")

st.caption("Portal de Empleos - Construido con Streamlit")