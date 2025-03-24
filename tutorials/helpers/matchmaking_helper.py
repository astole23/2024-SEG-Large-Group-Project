from .embedding_helper import get_embeddings, cosine_similarity_manual

def match_job_to_cv_together(cv_items, job_titles):
    """Match job titles using AI embeddings."""
    if not cv_items or not job_titles:
        return []
    cv_query = " ".join(item.strip() for item in cv_items if item)
    embeddings = get_embeddings([cv_query] + job_titles)
    if not embeddings or len(embeddings) < 2:
        return []
    job_embedding = embeddings[0]
    job_title_embeddings = embeddings[1:]
    return sorted(
        zip(job_titles, [cosine_similarity_manual(job_embedding, emb) for emb in job_title_embeddings]),
        key=lambda x: x[1], reverse=True
    )

def compute_final_scores(sorted_matches, job_lookup, user_locations):
    """Calculate final job match scores, including location bonus."""
    from .location_helper import is_location_match

    unique_jobs = {}
    for job_title, base_score in sorted_matches:
        job = job_lookup.get(job_title)
        if not job or job_title in unique_jobs:
            continue
        unique_jobs[job_title] = (job, base_score + is_location_match(user_locations, job.location))
    return sorted(unique_jobs.values(), key=lambda x: x[1], reverse=True)
