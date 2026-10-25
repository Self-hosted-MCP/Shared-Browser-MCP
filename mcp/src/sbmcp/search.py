"""Talks to our own SearXNG. No cache and no history: a search lives only for the length of the call."""
import asyncio
from urllib.parse import urlparse

import httpx

from . import config


class SearchError(Exception):
    pass


async def raw_search(query: str, *, engines: str = "", category: str = "", language: str = "",
                     time_range: str = "", safe_search: int | None = None, page: int = 1) -> dict:
    data = {"q": query, "format": "json", "pageno": max(1, page),
            "language": language or config.DEFAULT_LANGUAGE,
            "safesearch": config.SAFE_SEARCH if safe_search is None else safe_search}
    if engines:
        data["engines"] = engines
    if category:
        data["categories"] = category
    if time_range:
        data["time_range"] = time_range
    try:
        async with httpx.AsyncClient(timeout=20, trust_env=False) as client:
            r = await client.post(f"{config.SEARXNG_URL}/search", data=data)
    except httpx.HTTPError as exc:
        raise SearchError(f"The search engine did not answer ({type(exc).__name__}). Try again in a moment.") from exc
    if r.status_code == 403:
        raise SearchError("The search engine refused the request. Its settings.yml must allow the json format.")
    if r.status_code != 200:
        raise SearchError(f"The search engine returned {r.status_code}.")
    return r.json()


def clip(text: str, n: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def clean_url(url: str) -> str:
    return url.split("#")[0]


def merge(results: list[dict]) -> list[dict]:
    """Same page from several engines or several searches shows once. Higher score first."""
    seen: dict[str, dict] = {}
    for r in results:
        key = clean_url(r.get("url", "")).rstrip("/").lower()
        if not key:
            continue
        if key in seen:
            seen[key]["score"] = seen[key].get("score", 0) + r.get("score", 0)
            seen[key]["engines"] = sorted(set(seen[key].get("engines", [])) | set(r.get("engines", [])))
        else:
            seen[key] = dict(r)
    return sorted(seen.values(), key=lambda r: r.get("score", 0), reverse=True)


def format_results(results: list[dict], limit: int, full: bool) -> list[str]:
    lines = []
    for i, r in enumerate(results[:limit], 1):
        host = urlparse(r["url"]).hostname or ""
        head = f"{i}. {clip(r.get('title', ''), 120)}  ({host})"
        lines.append(head)
        lines.append(f"   {r['url']}")
        snippet = clip(r.get("content", ""), config.MAX_SNIPPET_CHARS * (3 if full else 1))
        if snippet:
            lines.append(f"   {snippet}")
        if r.get("publishedDate"):
            lines.append(f"   Published: {str(r['publishedDate'])[:10]}")
    return lines


def engine_notes(data: dict) -> str:
    bad = data.get("unresponsive_engines") or []
    if not bad:
        return ""
    return "Engines that did not answer: " + ", ".join(f"{e[0]} ({e[1]})" for e in bad)


async def many(queries: list[str], **kw) -> list[dict | Exception]:
    return await asyncio.gather(*(raw_search(q, **kw) for q in queries), return_exceptions=True)
