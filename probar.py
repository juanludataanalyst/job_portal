import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Paso 1: Cargar las ofertas con embeddings desde un archivo JSON
with open('ofertas_con_embeddings.json', 'r', encoding='utf-8') as file:
    ofertas = json.load(file)

# Paso 2: Definir la consulta del usuario
consulta = "Python Job freelance as senior data analyst"

# Paso 3: Cargar el modelo y generar el embedding de la consulta
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
consulta_embedding = model.encode(consulta)

# Paso 4: Extraer los embeddings de las ofertas
embeddings = np.array([oferta['embedding'] for oferta in ofertas])

# Paso 5: Calcular la similitud coseno entre la consulta y todas las ofertas
similitudes = cosine_similarity([consulta_embedding], embeddings)[0]

# Paso 6: Filtrar ofertas con similitud mayor a 0.5
ofertas_relevantes = [(oferta, similitud) for oferta, similitud in zip(ofertas, similitudes) if similitud > 0.4]

# Paso 7: Mostrar todas las ofertas relevantes
print(f"\nOfertas con similitud mayor a 0.4 para la consulta: '{consulta}'")
for oferta, similitud in ofertas_relevantes:
    print(f"\nTítulo: {oferta['title']}")
    print(f"Empresa: {oferta['company']}")
    print(f"Descripción: {oferta['description'][:200]}...")
    print(f"Similitud: {similitud:.2f}")
    print("---")