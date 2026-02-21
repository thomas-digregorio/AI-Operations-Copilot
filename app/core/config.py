from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(default="sqlite:///./data/artifacts/app.db", alias="DATABASE_URL")

    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")
    vector_store: str = Field(default="faiss", alias="VECTOR_STORE")

    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    llm_model: str = Field(default="llama3.1:8b", alias="LLM_MODEL")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    use_llm_fallback: bool = Field(default=True, alias="USE_LLM_FALLBACK")

    data_dir: str = Field(default="./data", alias="DATA_DIR")
    model_dir: str = Field(default="./data/artifacts/models", alias="MODEL_DIR")
    vector_dir: str = Field(default="./data/artifacts/vector_index", alias="VECTOR_DIR")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    def ensure_runtime_dirs(self) -> None:
        for path in [
            Path(self.data_dir),
            Path(self.model_dir),
            Path(self.vector_dir),
            Path("./data/artifacts/metrics"),
            Path("./data/artifacts/evals"),
            Path("./data/processed"),
            Path("./data/raw/ulbrich_public"),
            Path("./data/raw/internal_mock_docs"),
            Path("./data/raw/steel_plates_faults"),
        ]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
