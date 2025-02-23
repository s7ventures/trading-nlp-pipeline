# embedder.py

import os
from langchain.embeddings import OpenAIEmbeddings
# If you prefer local, from sentence_transformers import SentenceTransformer

def get_embedding_model():
    # Example with OpenAI
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing.")
    return OpenAIEmbeddings(openai_api_key=api_key)

def embed_texts(texts):
    """
    Returns list of embeddings for each string in 'texts'.
    """
    embedding_model = get_embedding_model()
    embeddings = []
    for text in texts:
        emb = embedding_model.embed_query(text)
        embeddings.append(emb)
    return embeddings