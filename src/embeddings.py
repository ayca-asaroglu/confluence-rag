import logging
import time
from typing import List

import requests
import urllib3

from .config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Yerel embedding servisi üzerinden embedding oluşturur."""

    def __init__(self, config: Config):
        self.url = config.litellm_base_url
        self.api_key = config.litellm_api_key
        self.model = config.embedding_model
        self.timeout = config.embedding_timeout

    def _call(self, input: str | List[str], retries: int = 3) -> List[List[float]]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "input": input,
        }

        for attempt in range(retries):
            try:
                response = requests.post(
                    self.url,
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                result = response.json()

                if "data" not in result or not result["data"]:
                    raise ValueError(f"Embedding servisinden beklenen formatta cevap dönmedi: {result}")

                return [item["embedding"] for item in result["data"]]

            except Exception as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"Embedding hatası (deneme {attempt + 1}/{retries}): {e}. {wait}s bekleniyor...")
                    time.sleep(wait)
                else:
                    raise

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Metin listesi için embedding vektörleri döner."""
        if not texts:
            return []
        return self._call(texts)

    def embed_one(self, text: str) -> List[float]:
        """Tek bir metin için embedding vektörü döner."""
        return self._call(text)[0]
