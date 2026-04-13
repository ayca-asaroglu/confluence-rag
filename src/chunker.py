from typing import List
from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """HTML içeriğini düz metne dönüştürür."""
    soup = BeautifulSoup(html, "lxml")

    # Gereksiz etiketleri kaldır
    for tag in soup(["script", "style", "head"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Fazla boşlukları temizle
    lines = [line.strip() for line in text.splitlines()]
    return " ".join(word for line in lines for word in [line] if word)


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Metni örtüşen chunk'lara böler."""
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += chunk_size - chunk_overlap

    return chunks
