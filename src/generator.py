import chromadb
from sentence_transformers import SentenceTransformer
from ollama import chat


# Configuration
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "knowledge_base"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "qwen3:8b"

TOP_K = 3


def retrieve(query, model, collection):
    # Convert the user's question into an embedding
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
    )

    return results["documents"][0]


def build_prompt(query, documents):
    context = "\n\n---\n\n".join(documents)

    prompt = f"""
You are a helpful assistant answering questions using the provided context.

Answer the user's question using ONLY the information in the context.

If the answer cannot be found in the context, say:
"I don't have enough information in the provided knowledge base."

Do not invent information.

Context:
{context}

Question:
{query}
"""

    return prompt


def generate_answer(prompt):
    response = chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content


def main():
    # Load embedding model
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    # Get user's question
    query = input("Ask a question: ")

    # Retrieve relevant chunks
    documents = retrieve(
        query,
        embedding_model,
        collection,
    )

    # Build prompt containing retrieved context
    prompt = build_prompt(
        query,
        documents,
    )

    # Ask the LLM
    answer = generate_answer(prompt)

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
