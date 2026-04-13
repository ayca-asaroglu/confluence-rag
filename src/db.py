import logging
from typing import List

import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

from .config import Config

logger = logging.getLogger(__name__)

CREATE_EXTENSION = "CREATE EXTENSION IF NOT EXISTS vector;"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS confluence_chunks (
    id            SERIAL PRIMARY KEY,
    page_id       TEXT        NOT NULL,
    space_key     TEXT        NOT NULL,
    title         TEXT        NOT NULL,
    url           TEXT        NOT NULL,
    chunk_index   INTEGER     NOT NULL,
    content       TEXT        NOT NULL,
    embedding     vector({dim}),
    UNIQUE (page_id, chunk_index)
);
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS confluence_chunks_embedding_idx
ON confluence_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""

UPSERT = """
INSERT INTO confluence_chunks (page_id, space_key, title, url, chunk_index, content, embedding)
VALUES %s
ON CONFLICT (page_id, chunk_index)
DO UPDATE SET
    title      = EXCLUDED.title,
    url        = EXCLUDED.url,
    content    = EXCLUDED.content,
    embedding  = EXCLUDED.embedding;
"""


class VectorDB:
    def __init__(self, config: Config):
        self.conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            dbname=config.db_name,
            user=config.db_user,
            password=config.db_password,
        )
        register_vector(self.conn)
        self._init_schema(config.embedding_dim)

    def _init_schema(self, dim: int):
        with self.conn.cursor() as cur:
            cur.execute(CREATE_EXTENSION)
            cur.execute(CREATE_TABLE.format(dim=dim))
            cur.execute(CREATE_INDEX)
        self.conn.commit()
        logger.info("DB şeması hazır.")

    def upsert_chunks(
        self,
        page_id: str,
        space_key: str,
        title: str,
        url: str,
        chunks: List[str],
        embeddings: List[List[float]],
    ):
        """Chunk ve embedding'leri toplu olarak kaydeder."""
        rows = [
            (page_id, space_key, title, url, i, chunk, embedding)
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        with self.conn.cursor() as cur:
            execute_values(cur, UPSERT, rows)
        self.conn.commit()

    def close(self):
        self.conn.close()
