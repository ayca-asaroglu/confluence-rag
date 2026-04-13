import logging
import time
from typing import List

from openai import OpenAI

from .config import Config

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """LiteLLM proxy üzerinden embedding oluşturur."""

    def __init__(self, config: Config):
        self.model = config.embedding_model
        self.client = OpenAI(
            base_url=f"{config.litellm_base_url.rstrip('/')}/v1",
            api_key=config.litellm_api_key,
        )

    def embed(self, texts: List[str], retries: int = 3) -> List[List[float]]:
        """Metin listesi için embedding vektörleri döner."""
        if not texts:
            return []

        for attempt in range(retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"Embedding hatası (deneme {attempt + 1}/{retries}): {e}. {wait}s bekleniyor...")
                    time.sleep(wait)
                else:
                    raise

    def embed_one(self, text: str) -> List[float]:
        """Tek bir metin için embedding vektörü döner."""
        return self.embed([text])[0]
