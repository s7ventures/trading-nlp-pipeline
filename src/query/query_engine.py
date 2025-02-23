import os
import chromadb
from langchain_community.embeddings import OpenAIEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma  # Updated import
import openai

# Load Config
from src.config import OPENAI_API_KEY, CHROMA_DB_PATH

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")  # Ensure correct model

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="trading_transcripts")

def query_transcripts(user_query, top_k=5):
    """
    Queries ChromaDB for relevant transcript chunks based on user input.
    """
    query_embedding = embeddings.embed_query(user_query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_texts = [doc for doc in results["documents"][0]]

    prompt = f"""
    You are an expert options trader. Based on the retrieved transcripts below, answer the user's query.

    --- Retrieved Data ---
    {retrieved_texts}

    --- User Query ---
    {user_query}
    """

    # Call GPT-4 Turbo for response
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response["choices"][0]["message"]["content"].strip()

# Example Usage
if __name__ == "__main__":
    user_query = "What is the best way to trade 0DTE options?"
    response = query_transcripts(user_query)
    print(f"Query Response: {response}")