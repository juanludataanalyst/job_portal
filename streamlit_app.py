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

# Page configuration
st.set_page_config(
    page_title="Job Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key for Together AI
TOGETHER_API_KEY = st.secrets["together"]["TOGETHER_API_KEY"]

# Free serverless models
DEEPSEEK_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
LLAMA_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

# Function to generate text model response
def generate_ai_explanation(jobs, user_query, client):
    prompt = get_ai_explanation_prompt(jobs, user_query) + "\n\n**Important Instructions:**\n1. Return **only** a valid JSON object with the following structure:\n```json\n{\n  \"overall_explanation\": \"A paragraph explaining the overall match\",\n  \"job_explanations\": {\n    \"job_id_1\": \"Explanation for job 1\",\n    \"job_id_2\": \"Explanation for job 2\"\n  }\n}\n```\n2. Do **not** include any additional text, comments, or <think> blocks outside the JSON.\n3. Ensure the JSON is complete and properly formatted.\n4. Be concise to avoid truncation (limit each explanation to 1-2 sentences)."
    
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.7
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        try:
            response = client.chat.completions.create(
                model=LLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.7
            )
            explanation = response.choices[0].message.content
        except Exception as e2:
            st.error(f"Error generating explanations: {str(e2)}")
            return {"overall_explanation": "Unable to generate explanations at this time.", "job_explanations": {}}
    
    # Remove the <think> block
    explanation = re.sub(r'<think>[\s\S]*?</think>', '', explanation).strip()
    
    # Extract the JSON content within ```json ... ```
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', explanation)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # If no triple backticks are found, assume the entire response is the JSON
        json_str = explanation
    
    # Try to parse the JSON
    try:
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        st.warning(f"Could not parse AI explanation as JSON: {str(e)}. Using raw text as overall explanation.")
        return {"overall_explanation": "Error parsing AI explanation.", "job_explanations": {}}

# Function to load data from JSON file
@st.cache_data
def load_data():
    try:
        with open("joined_data_standar.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return []

# Function to load pre-calculated vectors
@st.cache_data
def load_job_vectors():
    try:
        with open("job_vectors.pkl", "rb") as f:
            job_vectors = pickle.load(f)
        return job_vectors
    except Exception as e:
        st.error(f"Error loading job_vectors.pkl: {e}")
        return {}

# Function to get query embedding
def get_query_embedding(query, api_key):
    os.environ['TOGETHER_API_KEY'] = api_key
    client = Together()
    response = client.embeddings.create(
        model="BAAI/bge-large-en-v1.5",
        input=[query]
    )
    return response.data[0].embedding

# Function to calculate most relevant job offers
def get_top_similar_jobs(query_embedding, job_vectors, top_n=10):
    similarities = []
    for job_id, job_data in job_vectors.items():
        job_embedding = np.array(job_data["embedding"])
        if job_embedding.shape != (1024,):
            st.warning(f"Incorrect embedding for job_id {job_id}: {job_embedding.shape}")
            continue
        job_embedding = job_embedding.reshape(1, -1)
        query_embedding_array = np.array(query_embedding).reshape(1, -1)
        similarity = cosine_similarity(query_embedding_array, job_embedding)[0][0]
        if similarity > 0.5:
            similarities.append((job_id, similarity, job_data["data"]))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

# Title and welcome message
st.title("Tech Job Portal")
st.write("Welcome to the Tech Job Portal. Use the sidebar to navigate between pages.")
st.caption("Job Portal - Built with Streamlit")