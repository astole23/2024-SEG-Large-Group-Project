from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast BERT model

def match_job_to_cv_bert(job_title, cv_job_titles):
    embeddings = model.encode([job_title] + cv_job_titles)
    cosine_sim = cosine_similarity([embeddings[0]], embeddings[1:])[0]

    sorted_matches = sorted(zip(cv_job_titles, cosine_sim), key=lambda x: x[1], reverse=True)
    return sorted_matches
