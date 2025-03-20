import streamlit as st
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import functions from data_loader.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import load_data  # Importamos load_data desde data_loader

# Load CSS from the styles.css file in the root directory
def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Load the CSS file
try:
    # Try to load from the current directory
    load_css('styles.css')
except FileNotFoundError:
    # If not found, try to load from the parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_css(os.path.join(parent_dir, 'styles.css'))

# Cargar los datos al inicio de la página
jobs_data = load_data()

st.title("Explore Jobs")
st.write("Explore available job offers in the tech sector.")

if jobs_data:
    st.sidebar.header("Filters")
    companies = ["All"] + sorted(set(job.get("company", "") for job in jobs_data))
    sources = ["All"] + sorted(set(job.get("source", "") for job in jobs_data))
    
    selected_company = st.sidebar.selectbox("Company", companies)
    selected_source = st.sidebar.selectbox("Source", sources)
    search_term = st.sidebar.text_input("Search by title or company", "")
    
    filtered_jobs = jobs_data.copy()
    if selected_company != "All":
        filtered_jobs = [job for job in filtered_jobs if job.get("company") == selected_company]
    if selected_source != "All":
        filtered_jobs = [job for job in filtered_jobs if job.get("source") == selected_source]
    if search_term:
        filtered_jobs = [job for job in filtered_jobs 
                       if search_term.lower() in job.get("title", "").lower() 
                       or search_term.lower() in job.get("company", "").lower()]
    
    st.write(f"Showing {len(filtered_jobs)} of {len(jobs_data)} job offers")
    
    for job in filtered_jobs:
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
                skills_html = '<div class="job-skills"><span class="skill-tag">No skills specified</span></div>'
            
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
                    <a href="{job.get("link", "")}" target="_blank" class="view-job-button">View job</a>
                </div>
            </div>
            """
            st.markdown(job_html, unsafe_allow_html=True)
            st.markdown("---")
else:
    st.error("Could not load data.")