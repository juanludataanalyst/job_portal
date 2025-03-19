import json
import pickle
from sentence_transformers import SentenceTransformer

print("Cargando el modelo BAAI/bge-large-en-v1.5...")
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
print("Modelo cargado.")

print("Cargando el archivo JSON...")
with open("joined_data_standar.json", "r", encoding="utf-8") as f:
    job_offers = json.load(f)
print(f"Se cargaron {len(job_offers)} ofertas.")

job_vectors = {}
for i, job in enumerate(job_offers):
    print(f"Procesando oferta {i + 1}/{len(job_offers)}: {job['title']}")
    job_text = f"Title: {job['title']}. Description: {job['description']}. Skills: {', '.join(job['skills'])}"
    embedding = model.encode(job_text)  # Embedding completo: shape=(1024,)
    # Verificar las dimensiones del embedding
    print(f"Dimensión del embedding para oferta {i + 1}: {embedding.shape}")
    job_vectors[job["id"]] = {"embedding": embedding.tolist(), "data": job}  # Guardar el vector completo

print("Guardando los vectores en job_vectors.pkl...")
with open("job_vectors.pkl", "wb") as f:
    pickle.dump(job_vectors, f)
print("Espacio vectorial creado y guardado en job_vectors.pkl")