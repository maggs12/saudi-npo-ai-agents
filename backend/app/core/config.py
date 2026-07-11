from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/npo_ai"
    database_url_sync: str | None = None

    # Security
    secret_key: str = "change-me"
    encryption_key: str | None = None
    api_key: str | None = None

    # LLM
    llm_provider: Literal["openai", "ollama", "mock"] = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Embeddings
    embedding_provider: Literal["openai", "fastembed", "mock"] = "mock"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12V2"
    embedding_dimension: int = 384

    # Arabic PDF font
    arabic_font_path: str = "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"

    # Web search
    web_search_max_results: int = 5

    # Application
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    reports_dir: Path = project_root / "reports"

    @property
    def sync_database_url(self) -> str:
        return self.database_url_sync or self.database_url


settings = Settings()

# Ensure reports directory exists
settings.reports_dir.mkdir(parents=True, exist_ok=True)
