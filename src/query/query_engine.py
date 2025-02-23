import os
import openai
import chromadb
from langchain_openai import OpenAIEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma  # Updated import

# Load Configuration
from src.config import OPENAI_API_KEY, CHROMA_DB_PATH

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="trading_transcripts")

# OpenAI API Setup
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def query_transcripts(query, top_k=5):
    """
    Queries the vector database and retrieves relevant transcript segments.
    Then, sends those to GPT for a refined answer.
    """
    query_embedding = embeddings.embed_query(query)

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]  # Extract docs
    metadatas = results.get("metadatas", [[]])[0]  # Extract metadata if available

    if not documents:
        return "[INFO] No relevant transcripts found."

    # Format transcripts for better clarity
    formatted_transcripts = "\n\n".join(
        [f"Excerpt {i+1}: {doc}" for i, doc in enumerate(documents)]
    )

    # 🔥 System Role Instructions to make GPT sound sharper
    system_message = {
        "role": "system",
        "content": (
            "You are a highly experienced quantitative options trader. You specialize in "
            "trading 0DTE SPX options and risk management strategies. Your responses should be "
            "clear, data-driven, and concise. If the user asks a vague question, request clarification "
            "before answering. If relevant, include real trading strategies, probability concepts, "
            "or statistical edges used by professional traders."
        )
    }

    # 🔥 Smarter Query Prompt
    user_prompt = {
        "role": "user",
        "content": (
            f"Below are key excerpts from trading discussions related to your question:\n\n"
            f"{formatted_transcripts}\n\n"
            f"🔥 Now, based on these, provide a professional response to:\n'{query}'"
        )
    }

    # OpenAI API v1.0+ Query
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[system_message, user_prompt],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    while True:
        user_query = input("\n🔍 Enter your query (or type 'exit' to quit): ")
        if user_query.lower() == "exit":
            break
        
        response = query_transcripts(user_query)
        print("\n📜 GPT Response:\n", response)