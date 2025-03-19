import os
import streamlit as st
from together import Together

def get_query_embedding(query, api_key):
    # Establecer la clave API como una variable de entorno
    os.environ['TOGETHER_API_KEY'] = api_key
    # Crear el cliente de Together
    client = Together()
    # Generar el embedding
    response = client.embeddings.create(
        model="BAAI/bge-large-en-v1.5",  # O "togethercomputer/m2-bert-80M-8k-retrieval"
        input=[query]  # Usar 'input' como lista para compatibilidad
    )
    return response.data[0].embedding


api_key = api_key = st.secrets["together"]["TOGETHER_API_KEY"]
query = "Experienced AI engineer with Python and PyTorch for a job portal"
embedding = get_query_embedding(query, api_key)
print(f"Vector de la consulta (primeros 10 valores): {embedding}... (total {len(embedding)})")
