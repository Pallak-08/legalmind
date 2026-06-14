# LegalMind

AI-powered Q&A over legal contracts. Upload a PDF or DOCX, ask plain-english
questions, get answers with **exact clause citations**.

**Live demo:** <https://legalmind-production-76f7.up.railway.app>
**API:** <https://legalmind-production-b9a9.up.railway.app/docs>

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PDF / DOCX  ──▶  Parser     ──▶  Clause-aware chunker                  │
│                   (pdfplumber,    (preserves section #, title,          │
│                    python-docx)    page metadata)                       │
│                                       │                                 │
│                                       ▼                                 │
│                                  bge-large-en-v1.5  ──▶  ChromaDB       │
│                                  (1024-dim vectors)      (persistent)   │
│                                                                         │
│  Question  ──▶  Hybrid retrieval (dense + BM25, RRF fused)              │
│                   │                                                     │
│                   ▼                                                     │
│                bge-reranker-base  ──▶  top-5 clauses                    │
│                                            │                            │
│                                            ▼                            │
│                          Groq llama-3.3-70b-versatile                   │
│                          (system prompt enforces citations)             │
│                                            │                            │
│                                            ▼                            │
│                              Answer + cited clauses                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## What makes the citations real

Most "RAG over a PDF" demos chunk by character count, which mangles the
document's structure. When the LLM cites "Section 5", the citation might be
fabricated because no chunk knows what section it came from.

LegalMind does it differently:

1. **Parser detects clause boundaries** — regex patterns for Article numerals,
   Section X.Y.Z decimals, lettered subclauses `(a) (b)`, and ALL-CAPS
   headings. See [backend/app/services/parser.py](backend/app/services/parser.py).
2. **Chunker preserves clause metadata** — each chunk knows its section
   number, title, page, and character range. We never merge across clauses.
   See [backend/app/services/chunker.py](backend/app/services/chunker.py).
3. **Hybrid retrieval** — dense (`bge-large-en-v1.5`) catches paraphrases;
   BM25 catches exact legal terms ("indemnification", "force majeure").
   Merged via Reciprocal Rank Fusion. See [backend/app/services/rag.py](backend/app/services/rag.py).
4. **Cross-encoder reranker** — top-30 fused candidates reranked by
   `bge-reranker-base`, top-5 fed to the LLM.
5. **System prompt enforces citation format** — the LLM must cite using the
   exact `[Section X.Y]` header it sees on each clause. If the answer's
   citation doesn't match a clause we passed in, we know it's hallucinated.

## Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Backend | FastAPI | Pythonic, async, auto OpenAPI docs |
| Vector DB | ChromaDB (local, persistent) | No signup, no quota. Interface abstracted via `VectorStore` protocol — swap to Pinecone in ~20 LOC. |
| Embeddings | `BAAI/bge-large-en-v1.5` | Free, MIT-licensed, top of MTEB Retrieval. Runs on CPU. |
| Sparse retrieval | BM25 (`rank-bm25`) | Catches legal terms-of-art that paraphrase-trained embeddings miss. |
| Reranker | `BAAI/bge-reranker-base` | Cross-encoder. Big quality bump over bi-encoder retrieval alone. |
| LLM | Groq `llama-3.3-70b-versatile` | Fast, free tier, capable enough for grounded summarization. |
| Frontend | Next.js 14 (App Router) + Tailwind | Standard React stack. |

## Run it

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# paste your GROQ_API_KEY into .env

# Optional but recommended: warm up models so first request is fast.
python -c "from app.services.embedder import embed_texts; embed_texts(['warmup'])"
python -c "from app.services.reranker import rerank; from app.services.vectorstore import SearchResult; rerank('warmup', [SearchResult('1','1','t','x',1,0.0)], 1)"

uvicorn app.main:app --reload --port 8000
```

First run downloads ~1.3 GB of model weights (one-time).

API docs at <http://localhost:8000/docs>.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open <http://localhost:3000>.

### Try it without a UI

```bash
cd backend
# Generate a sample NDA, parse it, run 10 retrieval evals — no API key required.
python -m tests.eval
```

Expected output: `Reranker recall@5: 10/10 (100%)`.

## Deploy to Railway

Both services deploy from this one repo as separate Railway services. Steps assume the [Railway CLI](https://docs.railway.app/develop/cli) is installed and you're logged in.

### 1. Push to GitHub

```bash
cd ~/Desktop/projects/legalmind
git init && git add . && git commit -m "Initial commit"
gh repo create legalmind --public --source=. --push
```

### 2. Create a Railway project

```bash
railway init    # name it "legalmind"
```

### 3. Add the backend service

In the Railway dashboard:

1. **+ New Service** → **GitHub Repo** → pick `legalmind`.
2. Service **Settings** → **Root Directory** = `backend`.
3. **Variables** → add:
   - `GROQ_API_KEY=gsk_…`
   - `CORS_ORIGINS=*` (tighten in step 5)
   - `CHROMA_PERSIST_DIR=/data/chroma`
   - `HF_HOME=/data/hf-cache`
4. **Volumes** → **+ Add Volume** → mount path `/data`, size 2 GB. This persists indexed contracts and cached model weights across redeploys.
5. **Deploy**. First build takes ~5–8 min (downloads ~1.3 GB of models into the volume during the nixpacks `build` phase).
6. **Settings → Networking** → **Generate Domain**. Save the URL — that's your `NEXT_PUBLIC_API_URL`.

Smoke-test:
```bash
curl https://<backend>.up.railway.app/health
```

### 4. Add the frontend service

1. Same project → **+ New Service** → **GitHub Repo** → same `legalmind` repo.
2. Service **Settings** → **Root Directory** = `frontend`.
3. **Variables**:
   - `NEXT_PUBLIC_API_URL=https://<backend>.up.railway.app`
4. **Deploy**. ~2 min build.
5. **Settings → Networking** → **Generate Domain**.

### 5. Tighten CORS

Back to the backend service → **Variables** → set `CORS_ORIGINS=https://<frontend>.up.railway.app` → **Deploy**.

### Cost notes

The embedding + reranker models hold ~2 GB resident. Railway Hobby plan ($5/mo + usage) typically lands the backend at **$8–15/mo** running 24/7. The frontend is roughly **$3–5/mo**. To save:

- Sleep the backend when idle (Settings → **Serverless** → idle timeout). First request after sleep is ~30s while models reload.
- Or downsize: swap `bge-large` → `bge-small-en-v1.5` and drop the reranker. Backend drops to ~600 MB RAM, ~$3/mo.

## Evaluation

`backend/tests/eval.py` ships with 10 held-out questions against a sample
mutual NDA and measures top-5 retrieval recall — both hybrid-only and after
reranking. This is the metric to track when tuning chunk size, retrieval `k`,
or swapping embedding models.

```bash
cd backend
python -m tests.eval
pytest tests/  # unit tests for parser + chunker
```

## Project layout

```
backend/
  app/
    main.py                 FastAPI entry point + CORS
    config.py               env-driven settings
    schemas.py              Pydantic request/response models
    routers/
      upload.py             POST /upload
      query.py              POST /query
    services/
      parser.py             PDF/DOCX → structured clauses
      chunker.py             clauses → embeddable chunks (metadata preserved)
      embedder.py            sentence-transformers wrapper
      vectorstore.py         ChromaDB-backed, swappable
      bm25.py                in-memory BM25 keyword index
      reranker.py            BGE cross-encoder
      rag.py                 hybrid retrieval + RRF + rerank + Groq call
  sample_contracts/
    mutual_nda.py            generates a realistic NDA for evals
  tests/
    test_parser.py
    test_chunker.py
    eval.py                  end-to-end retrieval eval
frontend/
  app/
    layout.tsx
    page.tsx
  components/
    Upload.tsx
    Chat.tsx
    CitationCard.tsx
  lib/
    api.ts                   typed API client
```

## Disclaimers

Not legal advice. Outputs must be verified against the source document.
Designed for review assistance, not replacing counsel.
