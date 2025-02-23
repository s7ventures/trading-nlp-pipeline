import os
import json
import chromadb
from langchain_community.embeddings import OpenAIEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma  # Updated import

# Load Configuration
from src.config import OPENAI_API_KEY, CHROMA_DB_PATH

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")  # Ensure consistency

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="trading_transcripts")

# Paths
PROCESSED_DIR = os.path.join("data", "processed")
EMBEDDED_VIDEOS_PATH = "data/embedded_videos.json"

# ──────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────

def load_embedded_videos():
    """Load already embedded video transcripts from JSON file."""
    if not os.path.exists(EMBEDDED_VIDEOS_PATH):
        return {}
    with open(EMBEDDED_VIDEOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_embedded_video(video_id):
    """Save video ID to JSON file to prevent re-embedding."""
    embedded_videos = load_embedded_videos()
    embedded_videos[video_id] = True  # Mark as processed
    with open(EMBEDDED_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_videos, f, indent=2)

def embed_transcripts():
    """
    Reads processed transcripts, generates embeddings, and stores them in ChromaDB.
    Only embeds new transcripts that haven't been embedded before.
    """
    embedded_videos = load_embedded_videos()
    files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith("_chunks.json")]

    if not files:
        print("[WARN] No chunked transcript files found!")
        return
    
    for file in files:
        video_id = file.split("_")[0]  # Extract video ID

        # Skip if already embedded
        if video_id in embedded_videos:
            print(f"[INFO] Skipping already embedded video: {file}")
            continue

        file_path = os.path.join(PROCESSED_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        for idx, chunk in enumerate(chunks):
            doc_id = f"{video_id}_{idx}"  # Unique ID per chunk
            embedding_vector = embeddings.embed_documents([chunk])  # Generate embedding

            collection.add(
                ids=[doc_id],
                documents=[chunk],
                embeddings=embedding_vector,  # Store correct dimension
                metadatas=[{"source": file}]
            )

        # Mark video as embedded
        save_embedded_video(video_id)
        print(f"[INFO] Embedded {len(chunks)} chunks from {file}")

    print("[INFO] Finished embedding new transcripts.")

if __name__ == "__main__":
    embed_transcripts()