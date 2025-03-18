import json
from sentence_transformers import SentenceTransformer

# Paso 1: Cargar el archivo JSON
with open("joined_data_standar.json", "r", encoding="utf-8") as file:
    ofertas = json.load(file)

# Paso 2: Cargar el modelo de embeddings
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Paso 3: Generar embeddings para cada descripción
print("Generando embeddings para", len(ofertas), "ofertas...")
for oferta in ofertas:
    descripcion = oferta["description"]  # Asumimos que "description" es la clave en tu JSON
    embedding = model.encode(descripcion, show_progress_bar=True)
    oferta["embedding"] = embedding.tolist()  # Convertimos el embedding a lista para guardarlo en JSON

# Paso 4: Guardar las ofertas con los embeddings en un nuevo archivo JSON
with open("ofertas_con_embeddings.json", "w", encoding="utf-8") as file:
    json.dump(ofertas, file, ensure_ascii=False, indent=4)

print("Ofertas con embeddings guardadas en 'ofertas_con_embeddings.json'.")
