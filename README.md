# Local RAG System

A simple local Retrieval-Augmented Generation (RAG) system built with Python, ChromaDB, Sentence Transformers, and Ollama.

## Project Structure

rag-system/
├── data/
│   └── demo_data.md
├── requirements.txt
└── src/
    ├── chunker.py
    ├── embedder.py
    ├── generator.py
    └── retriever.py

## How It Works

Knowledge Base
      ↓
   Chunking
      ↓
   Embeddings
      ↓
   ChromaDB
      ↓
Semantic Retrieval
      ↓
 Top 3 Chunks
      ↓
    LLM
      ↓
   Answer

### 1. Chunking

`chunker.py` reads `data/demo_data.md` and splits it into semantic Markdown sections.

- Uses `##` sections as the primary chunk boundaries.
- Large sections are split further when necessary.
- `tiktoken` is used for token counting.
- Chunks are saved to `processed/chunks.json`.

### 2. Embeddings

`embedder.py` converts each chunk into a vector using:

sentence-transformers/all-MiniLM-L6-v2

The model produces 384-dimensional embeddings.

The embeddings, documents, and metadata are stored in ChromaDB.

### 3. Retrieval

`retriever.py` embeds the user's question using the same embedding model and searches ChromaDB for the most semantically similar chunks.

The system currently retrieves the top 3 chunks.

### 4. Generation

`generator.py` takes the retrieved chunks and sends them as context to a local LLM running through Ollama.

Current model:

mannix/llama3.1-8b-abliterated:q4_k_m

The LLM generates the final answer using the retrieved knowledge-base context.

The prompt instructs the model to answer only from the provided context and avoid making up information.

## Setup

Create and activate a virtual environment:

python3 -m venv env
source env/bin/activate

Install Python dependencies:

pip install -r requirements.txt

Install Ollama separately and pull the LLM:

ollama pull mannix/llama3.1-8b-abliterated:q4_k_m

## Run

Create chunks:

python src/chunker.py

Create embeddings and populate ChromaDB:

python src/embedder.py

Run the RAG system:

python src/generator.py

Then enter a question when prompted.

## Technologies

- Python
- Sentence Transformers
- all-MiniLM-L6-v2
- ChromaDB
- Ollama
- Llama 3.1 8B
- tiktoken

## Architecture

The project intentionally avoids a RAG framework such as LangChain so that the core RAG pipeline remains explicit and easy to understand.

The main pipeline is:

Chunking → Embedding → Vector Storage → Retrieval → Generation

## Local

The entire RAG pipeline runs locally.

- Embeddings run locally using Sentence Transformers.
- Vector storage runs locally using ChromaDB.
- LLM inference runs locally using Ollama.
- No external LLM API is required.

## Git

The virtual environment, generated ChromaDB files, processed chunks, Python cache, and environment files are excluded using `.gitignore`.
