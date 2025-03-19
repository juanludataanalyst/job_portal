def get_ai_explanation_prompt(jobs, user_query):
    # Prepare job data for the model (limited to essential fields)
    job_data = []
    for job_id, similarity, job in jobs:
        job_data.append({
            "id": job_id,
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "skills": job.get("skills", []),
            "location": job.get("location", ""),
            "type": job.get("type", ""),
            "similarity_score": f"{similarity:.4f}"
        })
    
    return f"""
You are an AI career assistant helping to explain job recommendations.

USER QUERY: "{user_query}"

JOB LISTINGS (ordered by relevance):
{json.dumps(job_data, indent=2)}

Your task:
1. Provide a brief overview explaining how these jobs match the user's search query.
2. For each job, provide a short personalized explanation of why it might be a good fit based on the query.
3. If any jobs don't fully match some criteria in the query (like location preferences, experience level, job type), mention it.
4. Format your response as a JSON with these keys:
   - "overall_explanation": A paragraph explaining the overall match
   - "job_explanations": A dictionary with job IDs as keys and explanations as values

Keep explanations concise and focused on the match between query and job requirements.
"""