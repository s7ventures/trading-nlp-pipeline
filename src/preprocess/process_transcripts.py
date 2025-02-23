"""
process_transcripts.py

Reads .txt transcripts from data/transcripts/,
applies cleaning, chunking, and optional GPT compression,
then writes results to data/processed/ (both cleaned text and chunk data).
"""

import os
import glob
import json

# Use relative imports to avoid ModuleNotFoundError
from .cleaner import clean_text
from .chunker import chunk_text
from .gpt_compress import gpt_compress_chunk  # Ensure this file exists if USE_GPT is True

TRANSCRIPTS_DIR = os.path.join("data", "transcripts")
PROCESSED_DIR = os.path.join("data", "processed")

def ensure_dirs():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

def process_one_file(file_path: str, use_gpt=False):
    """
    Clean, chunk, (optionally GPT-compress) a single transcript file,
    then save outputs to data/processed/.
    """
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # 1. Read raw transcript
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 2. Basic regex cleaning
    cleaned = clean_text(raw_text)

    # 3. Chunk the cleaned text
    chunks = chunk_text(cleaned, chunk_size=500, chunk_overlap=50)

    # 3.5 GPT compress if enabled
    if use_gpt:
        print("[INFO] Using GPT compression for each chunk.")
        compressed_chunks = []
        for c in chunks:
            compressed = gpt_compress_chunk(c)
            compressed_chunks.append(compressed)
        chunks = compressed_chunks

    # 4. Write out the cleaned transcript
    cleaned_path = os.path.join(PROCESSED_DIR, f"{base_name}_cleaned.txt")
    with open(cleaned_path, "w", encoding="utf-8") as cf:
        cf.write(cleaned)

    # 5. Write out the chunk data (as JSON for easy loading later)
    chunk_path = os.path.join(PROCESSED_DIR, f"{base_name}_chunks.json")
    with open(chunk_path, "w", encoding="utf-8") as jf:
        json.dump(chunks, jf, indent=2)

    print(f"[INFO] Processed '{file_path}' -> '{cleaned_path}', '{chunk_path}'")

def main():
    ensure_dirs()

    # Find all transcript files
    transcript_files = glob.glob(os.path.join(TRANSCRIPTS_DIR, "*.txt"))
    if not transcript_files:
        print("[WARN] No transcript files found in data/transcripts/")
        return

    # Set this to True if you want GPT compression
    # Make sure gpt_compress.py is implemented if set to True
    USE_GPT = False

    for file_path in transcript_files:
        process_one_file(file_path, use_gpt=USE_GPT)

if __name__ == "__main__":
    main()