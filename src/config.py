import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Confluence
    confluence_url: str = field(default_factory=lambda: os.getenv("CONFLUENCE_URL", "").rstrip("/"))
    confluence_username: str = field(default_factory=lambda: os.getenv("CONFLUENCE_USERNAME", ""))
    confluence_token: str = field(default_factory=lambda: os.getenv("CONFLUENCE_TOKEN", ""))
    confluence_space_keys: List[str] = field(
        default_factory=lambda: [k.strip() for k in os.getenv("CONFLUENCE_SPACE_KEY", "").split(",") if k.strip()]
    )

    # Database
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "rag_db"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # LiteLLM Embeddings
    litellm_base_url: str = field(default_factory=lambda: os.getenv("LITELLM_BASE_URL", "http://localhost:4000"))
    litellm_api_key: str = field(default_factory=lambda: os.getenv("LITELLM_API_KEY", "dummy"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "llama-embed-nemotron-8b"))
    embedding_dim: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "1536")))
    embedding_timeout: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_TIMEOUT", "120")))

    # Chunking
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))

    def validate(self):
        errors = []
        if not self.confluence_url:
            errors.append("CONFLUENCE_URL is required")
        if not self.confluence_token:
            errors.append("CONFLUENCE_TOKEN is required")
        if not self.confluence_space_keys:
            errors.append("CONFLUENCE_SPACE_KEY is required")
        if not self.litellm_base_url:
            errors.append("LITELLM_BASE_URL is required")
        if not self.db_password and self.db_user != "postgres":
            errors.append("DB_PASSWORD is required")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
