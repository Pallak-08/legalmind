# LegalMind

Ask plain-english questions about a legal contract. Get answers that cite exact clause numbers.

Demo: https://legalmind-production-76f7.up.railway.app
API docs: https://legalmind-production-b9a9.up.railway.app/docs

## Why this is different from a standard PDF RAG demo

Most RAG-over-a-PDF projects chunk by character count. That destroys the document's structure, so when the LLM cites "Section 5" you can't tell which clause it actually used (or if it made the citation up).

LegalMind parses contracts by their real clause boundaries. Each chunk knows its Article / Section / decimal number, its title, and its page. The system prompt forces the LLM to cite using those exact section numbers, so a citation either matches a real clause or doesn't appear.

## How it works

1. Parse PDF/DOCX into clauses. Regex patterns cover Article numerals, Section X.Y.Z decimals, lettered subclauses (a)(i), and ALL-CAPS headings.
2. Embed each clause with `bge-large-en-v1.5` (1024-dim, runs locally).
3. Index in ChromaDB (persistent, swappable to Pinecone via a Protocol).
4. On a question: dense retrieval + BM25, fused with Reciprocal Rank Fusion. Top 30 go to a `bge-reranker-base` cross-encoder, which picks the top 5.
5. Top 5 go to Groq `llama-3.3-70b-versatile` with a system prompt that forces citations and refuses to answer if the contract doesn't cover the question.

## Stack

FastAPI, ChromaDB, sentence-transformers (BGE), rank-bm25, Groq. Frontend: Next.js 14 + Tailwind. Deployed on Railway.

## Eval

`backend/tests/eval.py` runs 10 questions over a generated mutual NDA and measures top-5 retrieval recall. Current scores: 10/10 hybrid alone, 10/10 after reranking. No API key needed to run it.

```bash
cd backend && python -m tests.eval
```

## Run locally

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # paste GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

First run downloads ~1.3 GB of model weights into the HuggingFace cache.

Frontend:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Deploy

Both services run on Railway from this same repo, monorepo style. Each service sets its Root Directory (`backend` or `frontend`) and reads its own `railway.json`. Backend needs a persistent volume mounted at `/data` so ChromaDB survives redeploys.

Required env vars on the backend service:

- `GROQ_API_KEY`
- `CORS_ORIGINS` (your frontend URL)
- `CHROMA_PERSIST_DIR=/data/chroma`

Required env var on the frontend service:

- `NEXT_PUBLIC_API_URL` (your backend URL)

## Project layout

```
backend/app/services/
  parser.py       PDF/DOCX -> clauses with metadata
  chunker.py      clauses -> embeddable chunks
  embedder.py     sentence-transformers wrapper
  vectorstore.py  ChromaDB behind a thin interface
  bm25.py         keyword index, in-memory
  reranker.py     BGE cross-encoder
  rag.py          retrieval + RRF + rerank + Groq

backend/tests/
  test_parser.py
  test_chunker.py
  eval.py         retrieval recall over the sample NDA
```

## Notes

Not legal advice. The model produces fluent prose even when grounded, so verify the cited clauses against the source.
