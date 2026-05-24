<img width="1763" height="980" alt="Screenshot 2026-05-24 at 6 34 42 PM" src="https://github.com/user-attachments/assets/5439ffeb-fc57-4df1-8517-a0f688d2cb9c" />
<img width="1920" height="994" alt="Screenshot 2026-05-24 at 6 30 10 PM" src="https://github.com/user-attachments/assets/ecfca571-ca66-422f-a5bd-dc4cd3f419ea" />



# MyKepatuhan

A RAG-based compliance assistant for Malaysian entrepreneurs. Users ask questions in English or Bahasa Melayu about business registration, licensing, tax, and related regulations. The system retrieves relevant passages from ingested government documents and returns a cited, plain-language answer.

---

## RAG Pipeline Architecture

```

Ingestion Pipeline
    Parse (Docling) → Enrich (gemma3:1b via Ollama) → Sanitize → Upload (Pinecone)

Retrieval Pipeline
    Hybrid search (BM25 + dense, Pinecone) → SBERT rerank → Gemini answer
```

---

## Tech Stack

**Backend**
- Python 3.13, FastAPI, SQLAlchemy
- LlamaIndex 
- Pinecone 
- Docling 
- nomic-embed-text-v2-moe (Ollama) for embeddings
- gemma3:1b (Ollama) for metadata enrichment during ingestion
- gemini-2.0-flash for answer generation
- cross-encoder/ms-marco-MiniLM-L-6-v2 for reranking
- PostgreSQL (Neon) for user accounts database

**Frontend**
- Next.js 15, TypeScript, Tailwind CSS
- Stack Auth 
- Lucide React 

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
    ├── eval.ipynb               Evaluation notebook
    └── questions.py             questions test dataset
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
- A Pinecone account (dimensionality: 768, metric: dotproduct) or other preferred vectorstore
- A Neon (or any PostgreSQL) database
- A Gemini API key ([get one free](https://aistudio.google.com/apikey)) or other preferred llm

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

1. **Parse** : Docling converts the PDF into semantically chunked nodes using the embedding model's tokenizer.

2. **Enrich** : gemma3:1b extracts four metadata fields per chunk: jurisdiction, authority, topic, document\_type.

3. **Sanitize** : Docling layout data is stripped; metadata is size-capped for Pinecone's 40KB limit.

4. **Upload** : Nodes are embedded with nomic-embed-text-v2-moe and upserted to Pinecone with sparse vectors for hybrid search.

Each stage checkpoints its output. If the process is interrupted, it resumes from the last completed stage rather than starting over. Documents are deduplicated by SHA-256 hash so re-uploading the same file is a no-op.

Check ingestion status:

```bash
curl http://localhost:8000/ingest/status/JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Retrieval

Each query goes through three steps:

1. **Hybrid search** : Pinecone runs BM25 keyword search and dense vector search in parallel, combined at alpha=0.6 (60% semantic, 40% keyword). Top 15 candidates are returned.

2. **Reranking** : A cross-encoder (ms-marco-MiniLM-L-6-v2) re-scores the 15 candidates and keeps the top 3.

3. **Generation** : The top 3 passages are passed to Gemini with a strict prompt that instructs it to answer only from the provided context.

Users can optionally filter by `authority` (e.g. SSM, LHDN) or `topic` (e.g. tax, licensing) before retrieval.

---

## Evaluation

The evaluation notebook is in `evaluation/eval.ipynb`. It uses LlamaIndex built-in evaluatorsto measure four metrics:

- **Faithfulness** : Is the answer grounded in the retrieved passages?
- **Answer Relevancy** : Does the answer address the question?
- **Contextual Precision** : Are the retrieved chunks relevant?
- **Contextual Recall** : Did retrieval find all relevant chunks?

Use a different model as judge from the one generating answers. If both use the same model, scores will be inflated.

---

## Known Limitations

- Ingestion speed is bottlenecked by the local LLM enrichment step. For large documents
  (250+ pages), expect 8-20 minutes using gemma3:1b at 5 concurrent requests. Heavier
  models like gemma4:e4b can push this to several hours depending on hardware. This is a
  deliberate tradeoff to keep ingestion costs at zero during development. To improve speed,
  use a smaller enrichment model or increase OLLAMA_NUM_PARALLEL if your machine has
  enough RAM.

- The jobs dictionary in `ingest.py` is in-memory. Restarting the server clears all job
  history, including jobs that are still processing.

- Conversation history is not persisted. Each query is independent. The model has no
  memory of previous messages in the same session.

- Metadata enrichment accuracy depends on the enrichment model. Chunks that are purely
  tabular, form-based, or contain very short text may receive `unknown` classifications,
  which reduces the effectiveness of authority and topic filtering.

- The current evaluation coverage is limited. Only 5 questions were used, which is not enough to draw statistically reliable conclusions about system
  performance. A more rigorous evaluation would include the following:

  - A larger question set (100+ questions) covering every ingested authority and document
    type, not just the ones currently tested.
  - Manual evaluation by someone with working knowledge of Malaysian business compliance,
    particularly for Bahasa Melayu responses where automated judges tend to be weaker.
  - Adversarial questions. Questions about topics not in the knowledge base, to verify
    the system correctly says it does not know rather than hallucinating an answer.
  - Regression testing after each new document is ingested, to catch cases where adding
    new content degrades retrieval quality for previously working questions.
  - A separate faithfulness check on citations. Verifying that the excerpt shown to the
    user actually supports the answer given, not just that it was retrieved.

---

## License

MIT
