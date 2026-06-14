import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import upload, query

logger = logging.getLogger("legalmind")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()


def _warmup_models() -> None:
    """Load embedder + reranker into memory so the first user request is fast.
    Runs in a background thread so it doesn't block the Railway healthcheck."""
    try:
        logger.info("Warming up embedder…")
        from app.services.embedder import embed_texts
        embed_texts(["warmup"])
        logger.info("Warming up reranker…")
        from app.services.reranker import rerank
        from app.services.vectorstore import SearchResult
        rerank("warmup", [SearchResult("0", "0", None, "warmup text", None, 0.0)], 1)
        logger.info("Models warm.")
    except Exception:  # noqa: BLE001 — warmup must not crash the server
        logger.exception("Model warmup failed; will retry on first request.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=_warmup_models, daemon=True).start()
    yield


app = FastAPI(
    title="LegalMind API",
    description="Upload a legal contract, ask plain-english questions, get answers with exact clause citations.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow * via env for initial Railway smoke-test; tighten to your frontend URL afterwards.
cors_origins = settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "llm": settings.groq_model, "embedder": settings.embedding_model}
