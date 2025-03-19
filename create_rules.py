import json
import re

# Listas de valores para generar reglas
negation_patterns = ["not", "no", "without", "exclude"]
job_types = ["Freelance", "Full Time", "Part Time", "Contract", "Internship", "Temporary"]
skills = ["Python", "TensorFlow", "PyTorch", "Java", "JavaScript", "SQL", "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "C++", "C#", "Ruby", "PHP", "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Spark", "Hadoop", "Kafka", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch", "GraphQL", "REST", "SOAP", "Linux", "Windows", "MacOS", "Android", "iOS", "Swift", "Kotlin", "Flutter", "Dart", "TypeScript", "Perl", "Scala", "Go", "Rust", "MATLAB", "R", "Julia", "Pandas", "NumPy", "SciPy", "Scikit-learn", "Keras", "OpenCV", "NLTK", "Spacy", "Hugging Face", "FastAPI", "Express", "Golang", "Terraform", "Ansible", "Jenkins", "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Slack", "Trello", "Asana", "Notion", "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator", "InDesign"]
locations = ["Remote", "Fully Remote", "On-site", "Hybrid", "USA", "Europe", "Asia", "Africa", "Australia", "Canada", "UK", "Germany", "France", "Spain", "Italy", "Netherlands", "Sweden", "Denmark", "Norway", "Finland", "Japan", "China", "India", "Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru", "New York", "California", "London", "Berlin", "Paris", "Tokyo", "Singapore", "Sydney", "Toronto", "Amsterdam", "Stockholm", "Barcelona", "Madrid", "Rome", "Zurich", "Dublin"]
seniorities = ["Senior", "Junior", "Mid-level", "Lead", "Principal", "Manager", "Director", "VP", "C-level", "Intern"]
experience_levels = [f"{i} years of experience" for i in range(1, 21)]  # 1 a 20 años
experience_conditions = ["less than", "more than", "at least", "under", "over"]

# Generar reglas
rules = []

# Reglas para tipos de empleo
for negation in negation_patterns:
    for job_type in job_types:
        rules.append({
            "pattern": f"{negation} {job_type.lower()}",
            "field": "type",
            "condition": "not_contains",
            "value": job_type
        })

# Reglas para habilidades
for negation in negation_patterns:
    for skill in skills:
        rules.append({
            "pattern": f"{negation} {skill.lower()}",
            "field": "skills",
            "condition": "not_contains",
            "value": skill
        })

# Reglas para ubicaciones
for negation in negation_patterns:
    for location in locations:
        rules.append({
            "pattern": f"{negation} in {location.lower()}",
            "field": "location",
            "condition": "not_contains",
            "value": location
        })

# Reglas para seniorities
for negation in negation_patterns:
    for seniority in seniorities:
        rules.append({
            "pattern": f"{negation} {seniority.lower()}",
            "field": "title",
            "condition": "not_contains",
            "value": seniority
        })

# Reglas para experiencia
for condition in experience_conditions:
    for years in range(1, 21):
        rules.append({
            "pattern": f"{condition} {years} years of experience",
            "field": "description",
            "condition": condition.replace(" ", "_"),
            "value": str(years)
        })

# Combinaciones adicionales (por ejemplo, "not remote python developer")
for negation in negation_patterns:
    for skill in skills[:20]:  # Limitar para no exceder demasiado
        for location in locations[:20]:
            rules.append({
                "pattern": f"{negation} {location.lower()} {skill.lower()}",
                "field": "skills",
                "condition": "not_contains",
                "value": skill
            })
            rules.append({
                "pattern": f"{negation} {location.lower()} {skill.lower()}",
                "field": "location",
                "condition": "not_contains",
                "value": location
            })

# Guardar las reglas en un archivo
rules_dict = {"rules": rules}
with open("filter_rules.json", "w", encoding="utf-8") as f:
    json.dump(rules_dict, f, indent=2)

print(f"Se generaron {len(rules)} reglas y se guardaron en filter_rules.json")