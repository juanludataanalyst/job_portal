import streamlit as st
import os
from datetime import datetime
import sys
import json

# Add the parent directory to sys.path to import functions from streamlit_app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app import (
    load_job_vectors, 
    get_query_embedding, 
    get_top_similar_jobs, 
    generate_ai_explanation,
    TOGETHER_API_KEY,
    DEEPSEEK_MODEL,
    LLAMA_MODEL
)
from together import Together

# Load CSS from the styles.css file in the root directory
def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Load the CSS file
try:
    load_css('styles.css')
except FileNotFoundError:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_css(os.path.join(parent_dir, 'styles.css'))

st.title("AI Search")
st.write("Search for job offers using a IA query.")

user_query = st.text_input("Enter your query (example: 'AI engineer with Python')", "")
show_ai_explanations = st.checkbox("Show AI explanations", value=True)

if st.button("Search Jobs"):
    if user_query:
        with st.spinner("Searching for relevant job offers..."):
            os.environ['TOGETHER_API_KEY'] = TOGETHER_API_KEY
            client = Together()
            query_embedding = get_query_embedding(user_query, TOGETHER_API_KEY)
            job_vectors = load_job_vectors()
            
            if job_vectors:
                top_jobs = get_top_similar_jobs(query_embedding, job_vectors)
                if top_jobs:
                    ai_explanations = {}
                    if show_ai_explanations:
                        with st.spinner("Generating AI explanations..."):
                            ai_explanations = generate_ai_explanation(top_jobs, user_query, client)
                            st.write("Debug: Contenido de ai_explanations:", ai_explanations)
                
                    # Display overall explanation if available
                    if show_ai_explanations and ai_explanations and "overall_explanation" in ai_explanations:
                        st.markdown(f'<div class="overall-explanation"><h3>💡 Results Analysis</h3><p>{ai_explanations["overall_explanation"]}</p></div>', unsafe_allow_html=True)
                    elif show_ai_explanations:
                        st.markdown('<div class="overall-explanation"><h3>💡 Results Analysis</h3><p>No overall explanation available.</p></div>', unsafe_allow_html=True)
                    
                    st.write(f"Showing the {len(top_jobs)} most relevant job offers (similarity > 0.5):")

                    for job_id, similarity, job in top_jobs:
                        with st.container():
                            date_str = job.get("date", "")
                            try:
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                                formatted_date = date_obj.strftime("%d %b, %Y")
                            except:
                                formatted_date = date_str
                            
                            # Generar HTML para las skills
                            skills = job.get("skills", [])
                            if skills:
                                skills_html = '<div class="job-skills">'
                                for skill in skills:
                                    skills_html += f'<span class="skill-tag">{skill}</span>'
                                skills_html += '</div>'
                            else:
                                skills_html = ''
                            
                            # Construir el HTML de la tarjeta
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
                                    <a href="{job.get("link", "")}" target="_blank">View job</a>
                                </div>
                            </div>
                            """
                            # Renderizar la tarjeta
                            st.markdown(job_html, unsafe_allow_html=True)

                            # Mostrar la explicación individual debajo de la tarjeta
                            if show_ai_explanations and ai_explanations and "job_explanations" in ai_explanations and job_id in ai_explanations["job_explanations"]:
                                explanation_text = ai_explanations["job_explanations"][job_id]
                                st.markdown(f'<div class="job-explanation"><h4>Why this job?</h4><p>{explanation_text}</p></div>', unsafe_allow_html=True)

                            st.markdown("---")
                else:
                    st.error("No relevant jobs found for your query.")
            else:
                st.error("Could not load job vectors.")
    else:
        st.warning("Please enter a query to search for jobs.")