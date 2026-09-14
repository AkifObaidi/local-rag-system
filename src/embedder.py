import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("processed/chunks.json")
CHROMA_PATH = "chroma_db"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "knowledge_base"


def main():
    # Load chunks
    chunks = json.loads(
        CHUNKS_FILE.read_text(encoding="utf-8")
    )

    print(f"Loaded {len(chunks)} chunks")

    # Load embedding model
    print(f"Loading model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    # Create persistent ChromaDB client
    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    # Create or get our collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Prepare data
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]

    metadatas = [
        {
            "section": chunk["section"],
            "chunk_index": chunk["chunk_index"],
            "token_count": chunk["token_count"],
        }
        for chunk in chunks
    ]

    # Generate embeddings
    print("Generating embeddings...")

    embeddings = model.encode(
        documents,
        show_progress_bar=True,
    ).tolist()

    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimensions: {len(embeddings[0])}")

    # Store everything in ChromaDB
    print("Saving to ChromaDB...")

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print()
    print("Done!")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents stored: {collection.count()}")
    print(f"Database path: {CHROMA_PATH}")


if __name__ == "__main__":
    main()
