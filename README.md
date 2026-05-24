# MyKepatuhan

A RAG-based compliance assistant for Malaysian entrepreneurs. Users ask questions in English or Bahasa Melayu about business registration, licensing, tax, and related regulations. The system retrieves relevant passages from ingested government documents and returns a cited, plain-language answer.

---

## Architecture

```
Frontend (Next.js)
    └── REST API (FastAPI)
            ├── /auth          JWT-based auth + Google OAuth bridge
            ├── /query         Hybrid retrieval → rerank → Gemini generation
            └── /ingest        Admin-only PDF ingestion pipeline (background job)

Ingestion Pipeline
    Parse (Docling) → Enrich (gemma3:1b via Ollama) → Sanitize → Upload (Pinecone)

Retrieval Pipeline
    Hybrid search (BM25 + dense, Pinecone) → SBERT rerank → Gemini answer
```

---

## Tech Stack

**Backend**
- Python 3.13, FastAPI, SQLAlchemy
- LlamaIndex — orchestration, hybrid retrieval, query engine
- Pinecone — vector store with sparse+dense hybrid search
- Docling — PDF parsing and structure-aware chunking
- nomic-embed-text-v2-moe (Ollama) — embeddings
- gemma3:1b (Ollama) — metadata enrichment during ingestion
- gemini-2.0-flash — answer generation
- cross-encoder/ms-marco-MiniLM-L-6-v2 — reranking
- PostgreSQL (Neon) — user accounts

**Frontend**
- Next.js 15, TypeScript, Tailwind CSS
- Stack Auth — Google OAuth
- Lucide React — icons

---

## Project Structure

```
MyKepatuhan/
├── backend/
│   ├── main.py                  FastAPI app entry point
│   ├── auth/
│   │   └── utils.py             JWT creation, password hashing, auth dependencies
│   ├── database/
│   │   ├── db.py                SQLAlchemy engine + session
│   │   └── models.py            User model
│   ├── pipeline/
│   │   ├── retriever.py         Hybrid retriever + query engine builder
│   │   └── ingestion/
│   │       ├── main.py          Pipeline entry point
│   │       ├── parse.py         Docling PDF parsing + chunking
│   │       ├── metadata.py      LLM-based metadata enrichment
│   │       ├── sanitize.py      Metadata cleanup for Pinecone compatibility
│   │       ├── upload.py        Embedding + Pinecone upsert
│   │       └── checkpointing.py Resume logic, deduplication, hash registry
│   └── routers/
│       ├── query.py             /query endpoint
│       ├── ingest.py            /ingest endpoints (admin)
│       ├── login.py             /auth/login, /auth/me, /auth/oauth-login
│       └── register.py          /auth/register
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx         Landing page
│       │   ├── (auth)/          Login + register pages
│       │   └── (app)/           Chat UI + admin panel
│       ├── components/          Navbar, Footer, LanguageToggle, etc.
│       └── lib/
│           ├── api.ts           Typed API client
│           └── i18n.tsx         EN/BM translation strings
└── evaluation/
    ├── eval.ipynb               DeepEval evaluation notebook
    └── questions.py             20-question bilingual test dataset
```

---

## Getting Started

### Prerequisites

- Python 3.13
- Node.js 20+
- [Ollama](https://ollama.com) with the following models pulled:
  ```
  ollama pull nomic-embed-text-v2-moe
  ollama pull gemma3:1b
  ```
- A Pinecone account with an index named `mykepatuhan` (dimensionality: 768, metric: dotproduct)
- A Neon (or any PostgreSQL) database
- A Gemini API key ([get one free](https://aistudio.google.com/apikey))

### Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@host/dbname
PINECON_KEY=your_pinecone_api_key
GEMINI_KEY=your_gemini_api_key
JWT_SECRET_KEY=a_long_random_secret_string
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STACK_PROJECT_ID=your_stack_auth_project_id
NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY=your_stack_auth_key
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Ollama (with parallel inference enabled)

```bash
pkill ollama
OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_LOADED_MODELS=1 ollama serve
```

---

## Ingestion

Only admins can ingest documents. Once you have an admin account, use the admin panel at `/admin` or call the API directly:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@your_document.pdf"
```

The pipeline runs as a background job through four stages:

1. **Parse** — Docling converts the PDF into semantically chunked nodes using the embedding model's tokenizer.
2. **Enrich** — gemma3:1b extracts four metadata fields per chunk: jurisdiction, authority, topic, document\_type.
3. **Sanitize** — Docling layout data is stripped; metadata is size-capped for Pinecone's 40KB limit.
4. **Upload** — Nodes are embedded with nomic-embed-text-v2-moe and upserted to Pinecone with sparse vectors for hybrid search.

Each stage checkpoints its output. If the process is interrupted, it resumes from the last completed stage rather than starting over. Documents are deduplicated by SHA-256 hash so re-uploading the same file is a no-op.

Check ingestion status:

```bash
curl http://localhost:8000/ingest/status/JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Retrieval

Each query goes through three steps:

1. **Hybrid search** — Pinecone runs BM25 keyword search and dense vector search in parallel, combined at alpha=0.6 (60% semantic, 40% keyword). Top 15 candidates are returned.
2. **Reranking** — A cross-encoder (ms-marco-MiniLM-L-6-v2) re-scores the 15 candidates and keeps the top 3.
3. **Generation** — The top 3 passages are passed to Gemini with a strict prompt that instructs it to answer only from the provided context.

Users can optionally filter by `authority` (e.g. SSM, LHDN) or `topic` (e.g. tax, licensing) before retrieval.

---

## Evaluation

The evaluation notebook is in `evaluation/eval.ipynb`. It uses DeepEval with a Gemini judge to measure four metrics across 20 bilingual test questions:

- **Faithfulness** — is the answer grounded in the retrieved passages?
- **Answer Relevancy** — does the answer address the question?
- **Contextual Precision** — are the retrieved chunks relevant?
- **Contextual Recall** — did retrieval find all relevant chunks?

To run:

```bash
cd evaluation
pip install deepeval google-generativeai
# Add GEMINI_API_KEY to your .env
jupyter notebook eval.ipynb
```

Use a different model as judge from the one generating answers. If both use the same model, scores will be inflated.

---

## Known Limitations

- Ingestion speed is bound by the local LLM enrichment step. For large documents (250+ pages), expect 30–60 minutes with gemma3:1b at 5 concurrent requests. This is a deliberate tradeoff to avoid cloud API costs during development.
- The jobs dictionary in `ingest.py` is in-memory. Restarting the server clears job history.
- Conversation history is not persisted. Each query is stateless.
- Metadata enrichment accuracy depends on the enrichment model. Some chunks, particularly tables and forms, may receive `unknown` classifications.

---

## License

MIT
