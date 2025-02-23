# vectorstore_inserter.py
from typing import List
from langchain.schema import Document
from langchain.vectorstores import Chroma
from .embedder import get_embedding_model

def insert_chunks_into_vectorstore(chunks: List[str], metadata: dict = None):
    """
    Creates or loads a Chroma store and inserts the given chunks
    as separate documents, each with metadata (e.g. video_id, title).
    """
    embedding_model = get_embedding_model()
    vectordb = Chroma(
        collection_name="tastyliveshow",
        embedding_function=embedding_model
    )

    # Create Document objects
    docs = []
    for chunk in chunks:
        docs.append(Document(page_content=chunk, metadata=metadata))

    vectordb.add_documents(docs)