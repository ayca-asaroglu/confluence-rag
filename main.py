import logging
from tqdm import tqdm

from src.config import Config
from src.confluence import ConfluenceClient
from src.chunker import html_to_text, chunk_text
from src.embeddings import EmbeddingClient
from src.db import VectorDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Kaç chunk'ı bir seferde embed edip kaydedeceğiz
BATCH_SIZE = 32


def process_space(space_key: str, confluence: ConfluenceClient, embedder: EmbeddingClient, db: VectorDB, config: Config):
    logger.info(f"Space işleniyor: {space_key}")
    pages = list(confluence.get_space_pages(space_key))

    for page in tqdm(pages, desc=space_key):
        page_id = page["id"]
        title = page["title"]
        url = confluence.get_page_url(page_id, space_key, title)

        html = confluence.get_page_body(page_id)
        text = html_to_text(html)
        if not text.strip():
            continue

        chunks = chunk_text(text, config.chunk_size, config.chunk_overlap)
        if not chunks:
            continue

        # Batch halinde embed et ve kaydet
        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[batch_start: batch_start + BATCH_SIZE]
            embeddings = embedder.embed(batch)
            db.upsert_chunks(page_id, space_key, title, url, batch, embeddings)


def main():
    config = Config()
    config.validate()

    confluence = ConfluenceClient(config)
    embedder = EmbeddingClient(config)
    db = VectorDB(config)

    try:
        for space_key in config.confluence_space_keys:
            process_space(space_key, confluence, embedder, db, config)
    finally:
        db.close()

    logger.info("Tüm space'ler başarıyla işlendi.")


if __name__ == "__main__":
    main()
