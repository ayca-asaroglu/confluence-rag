import requests
import time
import logging
from typing import Iterator, Dict, Any, Optional
from .config import Config

logger = logging.getLogger(__name__)


class ConfluenceClient:
    """Confluence Data Center REST API client."""

    def __init__(self, config: Config):
        self.base_url = config.confluence_url
        self.session = requests.Session()

        # Confluence Data Center: Personal Access Token (Bearer) veya Basic Auth
        if config.confluence_token and not config.confluence_username:
            self.session.headers["Authorization"] = f"Bearer {config.confluence_token}"
        else:
            self.session.auth = (config.confluence_username, config.confluence_token)

        self.session.headers["Accept"] = "application/json"
        self.session.headers["Content-Type"] = "application/json"

    def _get(self, path: str, params: Optional[Dict] = None, retries: int = 3) -> Dict:
        url = f"{self.base_url}/rest/api{path}"
        for attempt in range(retries):
            try:
                resp = self.session.get(url, params=params, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait = int(e.response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                elif attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def get_space_pages(self, space_key: str, page_size: int = 50) -> Iterator[Dict[str, Any]]:
        """Space'deki tüm sayfaları paginate ederek getirir."""
        start = 0
        total_fetched = 0

        while True:
            data = self._get(
                "/content",
                params={
                    "spaceKey": space_key,
                    "type": "page",
                    "status": "current",
                    "start": start,
                    "limit": page_size,
                    "expand": "ancestors,version,metadata.labels",
                },
            )

            results = data.get("results", [])
            if not results:
                break

            for page in results:
                yield page
                total_fetched += 1

            size = data.get("size", 0)
            if size < page_size:
                break

            start += page_size

        logger.info(f"Space '{space_key}': toplam {total_fetched} sayfa listelendi.")

    def get_page_body(self, page_id: str) -> str:
        """Sayfanın HTML storage format içeriğini getirir."""
        data = self._get(
            f"/content/{page_id}",
            params={"expand": "body.storage"},
        )
        return data.get("body", {}).get("storage", {}).get("value", "")

    def get_page_url(self, page_id: str, space_key: str, title: str) -> str:
        """Sayfanın UI URL'ini döner."""
        slug = title.replace(" ", "+")
        return f"{self.base_url}/display/{space_key}/{slug}"
