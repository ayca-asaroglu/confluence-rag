import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Confluence
    confluence_url: str = field(default_factory=lambda: os.getenv("CONFLUENCE_URL", "").rstrip("/"))
    confluence_username: str = field(default_factory=lambda: os.getenv("CONFLUENCE_USERNAME", ""))
    confluence_token: str = field(default_factory=lambda: os.getenv("CONFLUENCE_TOKEN", ""))

    # Database
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "rag_db"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # Embeddings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    embedding_dim: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "1536")))

    # Chunking
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))

    def validate(self):
        errors = []
        if not self.confluence_url:
            errors.append("CONFLUENCE_URL is required")
        if not self.confluence_token:
            errors.append("CONFLUENCE_TOKEN is required")
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        if not self.db_password and self.db_user != "postgres":
            errors.append("DB_PASSWORD is required")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
