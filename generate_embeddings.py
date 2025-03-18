import json
import pickle
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# Cargar modelo InstructorXL
print("Cargando el modelo InstructorXL...")
try:
    model = SentenceTransformer("hkunlp/instructor-xl")
    print("Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()

# Cargar datos de ofertas de empleo
print("Cargando el archivo JSON...")
try:
    with open("joined_data_standar.json", "r", encoding="utf-8") as f:
        job_offers = json.load(f)
    print(f"Se cargaron {len(job_offers)} ofertas de empleo.")
except Exception as e:
    print(f"Error al cargar el JSON: {e}")
    exit()

# Procesar las ofertas de empleo y generar embeddings
job_vectors = {}
for i, job in enumerate(job_offers):
    print(f"Procesando oferta {i + 1}/{len(job_offers)}: {job['title']}")
    try:
        job_text = f"Title: {job['title']}. Description: {job['description']}. Skills: {', '.join(job['skills'])}"
        instruction = "Represent this job offer for a job matching system"
        embedding = model.encode([[instruction, job_text]])[0]
        job_vectors[job["id"]] = {"embedding": embedding, "data": job}
        print(f"Embedding generado para ID: {job['id']}")
    except Exception as e:
        print(f"Error al procesar la oferta {job['title']}: {e}")
        continue

# Guardar embeddings en un archivo
print("Guardando los vectores en job_vectors.pkl...")
try:
    with open("job_vectors.pkl", "wb") as f:
        pickle.dump(job_vectors, f)
    print("Espacio vectorial creado y guardado en job_vectors.pkl")
except Exception as e:
    print(f"Error al guardar el archivo: {e}")