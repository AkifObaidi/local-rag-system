from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Configuration
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "knowledge_base"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 3


def main():
    # Load the same embedding model used when creating the database
    model = SentenceTransformer(MODEL_NAME)

    # Connect to our persistent ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Get the existing collection
    collection = client.get_collection(name=COLLECTION_NAME)

    # Ask the user for a question
    query = input("Ask a question: ")

    # Convert the question into an embedding
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB for the most similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    # Display results
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    print("\n" + "=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    for i, (document, distance, metadata) in enumerate(
        zip(documents, distances, metadatas),
        start=1,
    ):
        print(f"\n--- Result {i} ---")
        print(f"Distance: {distance}")
        print(f"Section: {metadata['section']}")
        print()
        print(document)


if __name__ == "__main__":
    main()
