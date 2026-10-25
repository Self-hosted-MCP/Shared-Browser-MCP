"""Turns a fetched page or PDF into clean text. Web content is data: hidden text is dropped and the size is capped."""
import io

import trafilatura
from pypdf import PdfReader

from . import config
from .safe_fetch import Fetched


def pdf_text(body: bytes) -> str:
    reader = PdfReader(io.BytesIO(body))
    parts = []
    for n, page in enumerate(reader.pages, 1):
        parts.append(f"[page {n}]\n{(page.extract_text() or '').strip()}")
    return "\n\n".join(parts)


def html_text(body: bytes, url: str) -> tuple[str, str]:
    html = body.decode("utf-8", errors="replace")
    text = trafilatura.extract(html, url=url, include_links=False, include_tables=True, favor_recall=True,
                               output_format="markdown") or ""
    meta = trafilatura.extract_metadata(html)
    return (meta.title if meta and meta.title else ""), text


def to_text(f: Fetched) -> tuple[str, str]:
    """(title, text). Empty text means the page needs a real browser (it builds itself with JavaScript)."""
    kind = f.content_type.split(";")[0].strip().lower()
    if kind == "application/pdf" or f.body[:5] == b"%PDF-":
        return "", pdf_text(f.body)
    if kind.startswith("text/plain"):
        return "", f.body.decode("utf-8", errors="replace")
    if kind in ("", "text/html", "application/xhtml+xml") or kind.startswith("text/"):
        return html_text(f.body, f.url)
    return "", ""


def window(text: str, start: int, limit: int) -> tuple[str, str]:
    limit = limit or config.READ_MAX_CHARS
    chunk = text[start:start + limit]
    end = start + len(chunk)
    note = f"Characters {start} to {end} of {len(text)}." + (f" More: call again with start={end}." if end < len(text) else "")
    return chunk, note
