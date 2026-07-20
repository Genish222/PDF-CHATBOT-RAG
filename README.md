<<<<<<< HEAD
# PDF Chatbot RAG

Production-ready PDF chatbot using Retrieval-Augmented Generation (RAG).

## Tech Stack

- **Python** — Application runtime
- **Streamlit** — Web UI
- **LangChain** — RAG orchestration
- **FAISS** — Vector similarity search
- **Google Gemini API** — Embeddings & LLM
- **PyPDF** — PDF text extraction

## Project Structure

```
pdf-chatbot-rag/
├── app/                    # Application entry point
├── src/
│   ├── config/             # Settings & environment configuration
│   ├── domain/             # Core models & interfaces (ports)
│   ├── infrastructure/     # External adapters (Gemini, FAISS, PyPDF)
│   ├── application/        # Business logic & use cases
│   └── presentation/       # Streamlit UI layer
├── data/
│   ├── uploads/            # Uploaded PDF files
│   └── vectorstores/       # Persisted FAISS indexes
└── tests/                  # Unit & integration tests
```

## Architecture

This project follows **clean architecture** principles:

| Layer | Responsibility |
|-------|----------------|
| **Domain** | Entities, value objects, and abstract interfaces |
| **Application** | Use cases and orchestration logic |
| **Infrastructure** | Concrete implementations (Gemini, FAISS, PyPDF) |
| **Presentation** | Streamlit UI components |
| **Config** | Centralized settings via environment variables |

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your Google API key
4. Run the app:

   ```bash
   streamlit run app/main.py
   ```

## Status

Backend and UI complete: PDF loading, chunking, Gemini embeddings, FAISS vector
store, Gemini chat completion (`GeminiLLM`), and the Streamlit chat interface
are all wired together in `app/main.py`.
=======
# PDF-CHATBOT-RAG
>>>>>>> e7b10427539e78f246152eee01cd7c5c7c86c623
