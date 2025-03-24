import os
import together
import math

api_key = os.getenv("TOGETHER_API_KEY")
together_client = together.Together(api_key=api_key)

def get_embeddings(text_list):
    """Fetch embeddings for a list of texts using Together AI."""
    if not text_list or not all(isinstance(text, str) for text in text_list):
        return []
    try:
        response = together.Embeddings.create(
            model="togethercomputer/m2-bert-80M-8k-retrieval",
            input=text_list
        )
        return [item["embedding"] for item in response.get("data", [])]
    except Exception:
        return []

def cosine_similarity_manual(vec1, vec2):
    """Compute cosine similarity manually."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
