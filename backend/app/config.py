from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Optional so retrieval-only flows (e.g., tests/eval.py) work without a key.
    # The Groq client itself will raise if it's actually called without a key.
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "BAAI/bge-large-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"

    chroma_persist_dir: str = "./chroma_data"

    top_k_dense: int = 15
    top_k_bm25: int = 15
    top_k_rerank: int = 5

    cors_origins: str = "http://localhost:3000"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
