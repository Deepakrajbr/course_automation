import numpy as np
from utils.embedding import get_embedding
from models.course_model import get_all_courses

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_courses(query, top_k=3):
    query_embedding = get_embedding(query)
    courses = get_all_courses()

    scored = []
    for c in courses:
        if "embedding" not in c:
            continue
        score = cosine_similarity(query_embedding, c["embedding"])
        scored.append((score, c))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:top_k]]



def build_context(courses):
    text = ""
    for c in courses:
        text += f"""
Course: {c['name']}
Duration: {c['duration']}
Price: {c['price']}
Description: {c['description']}
"""
    return text