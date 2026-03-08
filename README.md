# PDF Query App

A web app that lets you query PDF documents in natural language. After uploading a PDF, the system builds vector and keyword search indexes and uses RAG (Retrieval-Augmented Generation) with OpenAI to answer your questions, with references to page numbers and source snippets.

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.10+, FastAPI, LangChain, Chroma, BM25, OpenAI API |
| **Frontend** | Vue 3, Vite, Pinia, Vue Router, Axios, vue-pdf-embed, marked |

## Features

- **PDF upload and parsing**: Upload PDFs with validation (extension, Content-Type, magic-byte check); max file size is configurable.
- **Hybrid retrieval (RAG)**: Vector search (Chroma + OpenAI Embeddings) plus BM25 keyword search; results are merged and sent to the LLM.
- **Vector storage**: Chroma for persistent vector indexes.
- **OpenAI integration**: Embeddings and chat use the OpenAI API; model and temperature are configurable.
- **Interactive UI**: Vue frontend with PDF preview, question input, answers with source references, and click-to-jump to page numbers.

## Project Structure

```
pdf-query-app/
├── backend/                 # FastAPI backend
│   ├── api/
│   │   └── routes.py        # API routes: /upload-pdf, /query, /reset, /config
│   ├── core/
│   │   ├── config.py        # Env and config (upload size, models, RAG prompts, etc.)
│   │   ├── exceptions.py   # Custom exceptions
│   │   └── logging_config.py
│   ├── prompts/             # RAG prompts (optional YAML override)
│   ├── schemas/             # Pydantic request/response models
│   ├── services/
│   │   ├── pdf_service.py   # PDF parsing, Chroma + BM25 index building
│   │   ├── retrieval_service.py  # RAG chain (EnsembleRetriever + LLM)
│   │   └── state.py         # Document state (document_id → index & chain)
│   ├── main.py              # FastAPI app, CORS, middleware, .env loading
│   └── uploaded_pdfs/       # Uploaded PDFs directory (default)
├── frontend/                # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/      # AnswerContent, etc.
│   │   ├── composables/     # usePdfUpload, etc.
│   │   ├── services/
│   │   │   └── apiService.js  # Backend API client
│   │   ├── views/
│   │   │   └── HomeView.vue   # Home: upload, query, preview, answer
│   │   └── main.js
│   └── package.json
├── .env.example             # Backend env example
├── frontend/.env.example    # Frontend env example (API base URL)
├── pyproject.toml           # Poetry dependencies
└── README.md
```

### Data Flow

1. **Upload**: Frontend selects PDF → `POST /upload-pdf` → backend validates and saves file → PyPDF parses pages → OpenAI Embeddings + Chroma build vector index, BM25 builds keyword index → store `document_id`, vectorstore, BM25, and RAG chain in memory → return `document_id`.
2. **Query**: Frontend sends `document_id` and question → `POST /query` → backend runs the corresponding RAG chain (hybrid retrieval + LLM) → return answer and source references (page, snippet).
3. **Reset**: `POST /reset` clears state for that `document_id` and deletes the uploaded PDF file.

## Requirements

- **Python** 3.10 or later (Poetry recommended for dependencies)
- **Node.js** 16 or later (for frontend npm / Vite)
- **OpenAI API Key** (required for embeddings and chat)

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/your-org/pdf-query-app.git
cd pdf-query-app
```

### 2. Backend setup and run

From the project root:

```bash
# Install dependencies (Poetry)
poetry install --no-root

# Copy env example and fill in values
cp .env.example .env
# Edit .env and set at least: OPENAI_API_KEY=your_api_key_here

# Start backend (must run from project root so .env is loaded)
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or run as a module:

```bash
poetry run python -m backend.main
```

Backend runs at `http://localhost:8000` by default; `GET /` returns a welcome message.

### 3. Frontend setup and run

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Optional: override API base URL (default is http://localhost:8000)
# cp .env.example .env
# Edit .env and set VITE_API_BASE_URL (use your backend URL when deploying)

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:5173` by default; open it in your browser.

### 4. Usage

1. On the home page, select a PDF and click **Analyze PDF** to upload and build the index.
2. Enter your question in the text area and click **Query**.
3. View the answer and source references; click a source to jump to that PDF page.
4. To switch documents or free resources, use reset to clear the current document state.

## Environment Variables

### Backend (project root `.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` |
| `VECTOR_RETRIEVER_K` / `BM25_RETRIEVER_K` | Number of results from vector / BM25 | `6` |
| `MAX_UPLOAD_SIZE_MB` | Max upload size (MB) | `50` |
| `RAG_PROMPTS_FILE` | Path to RAG prompts YAML (optional) | - |
| `RAG_SYSTEM_PROMPT` / `RAG_USER_TEMPLATE` / `RAG_NO_MATCH_INSTRUCTION` | Override RAG prompts (optional) | See `.env.example` |

See `.env.example` in the project root for more options.

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

When deploying, set `VITE_API_BASE_URL` to your backend URL and set `CORS_ORIGINS` on the backend to your frontend URL.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Welcome message |
| GET | `/config` | Client config (e.g. `max_upload_size_mb`) |
| POST | `/upload-pdf` | Upload PDF (multipart `file`); returns `document_id` |
| POST | `/query` | Query: body `{ "document_id": "...", "question": "..." }`; returns answer and sources |
| POST | `/reset` | Reset: body `{ "document_id": "..." }`; clears state and deletes uploaded PDF |

## FAQ

**Q: How do I set environment variables?**  
A: Copy `.env.example` to `.env` in the project root and fill in `OPENAI_API_KEY` and any other required variables.

**Q: No results or irrelevant answers?**  
A: Ensure your OpenAI API key is valid and the network is reachable. If the content is unrelated to the question, the system will respond that no relevant content was found.

**Q: Upload or parse errors?**  
A: Confirm the file is a valid PDF, under `MAX_UPLOAD_SIZE_MB`, and check backend logs for errors.

**Q: How do I customize RAG answer style?**  
A: Use `RAG_SYSTEM_PROMPT`, `RAG_USER_TEMPLATE`, `RAG_NO_MATCH_INSTRUCTION`, or `RAG_PROMPTS_FILE` to point to a YAML file (see `backend/prompts/`).

## License

This project is licensed under the MIT License.
