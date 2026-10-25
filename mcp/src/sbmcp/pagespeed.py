"""Speed and quality check of a PUBLIC web page, using Google's free PageSpeed Insights.
The address is sent to Google, so private addresses are refused before anything leaves the server."""
import asyncio

import httpx

from . import config
from .safe_fetch import BlockedURL, check_url, resolve_public

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
METRICS = [("first-contentful-paint", "First paint"), ("largest-contentful-paint", "Largest paint"),
           ("total-blocking-time", "Blocking time"), ("cumulative-layout-shift", "Layout shift"),
           ("speed-index", "Speed index"), ("interactive", "Interactive")]


class PageSpeedError(Exception):
    pass


async def run(url: str, strategy: str) -> dict:
    scheme, host, port = check_url(url)
    await resolve_public(host, port)   # refuses anything that points inside a private network
    params = [("url", url), ("strategy", strategy)] + [("category", c) for c in CATEGORIES]
    if config.env("PAGESPEED_API_KEY"):
        params.append(("key", config.env("PAGESPEED_API_KEY")))
    try:
        async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
            r = await client.get(API, params=params)
    except httpx.HTTPError as exc:
        raise PageSpeedError(f"Could not reach Google PageSpeed ({type(exc).__name__}).") from exc
    if r.status_code == 429:
        raise PageSpeedError("Google's free PageSpeed limit is used up for now. Try again in a few minutes.")
    if r.status_code != 200:
        msg = ""
        try:
            msg = r.json().get("error", {}).get("message", "")
        except ValueError:
            pass
        raise PageSpeedError(f"PageSpeed refused the check ({r.status_code}). {msg[:200]}".strip())
    return r.json()


def summarize(data: dict, strategy: str) -> str:
    lh = data.get("lighthouseResult", {})
    cats = lh.get("categories", {})
    audits = lh.get("audits", {})
    lines = [f"{strategy.capitalize()} · {lh.get('finalDisplayedUrl') or data.get('id', '')}"]
    scores = [f"{c['title']} {round((c.get('score') or 0) * 100)}" for c in cats.values()]
    lines.append("Scores (0-100): " + ", ".join(scores))
    lines.append("Metrics: " + ", ".join(f"{label} {audits[k]['displayValue']}" for k, label in METRICS if k in audits and audits[k].get("displayValue")))
    wins = []
    for key, a in audits.items():
        d = a.get("details") or {}
        if d.get("type") == "opportunity" and (a.get("score") is not None and a["score"] < 0.9):
            wins.append((d.get("overallSavingsMs") or 0, a.get("title", key), a.get("displayValue", "")))
    wins.sort(reverse=True)
    if wins:
        lines.append("Biggest fixes: " + "; ".join(f"{t}{' (' + v + ')' if v else ''}" for _, t, v in wins[:5]))
    failed = [a.get("title", k) for k, a in audits.items()
              if a.get("score") == 0 and (a.get("details") or {}).get("type") != "opportunity" and a.get("scoreDisplayMode") == "binary"]
    if failed:
        lines.append("Failed checks: " + "; ".join(failed[:6]))
    field = data.get("loadingExperience", {}).get("metrics", {})
    if field:
        bits = [f"{k.replace('_', ' ').lower()} {v.get('category', '').lower()}" for k, v in list(field.items())[:4] if v.get("category")]
        if bits:
            lines.append("Real visitors (Chrome data): " + ", ".join(bits))
    return "\n".join(lines)


async def check(url: str, strategy: str) -> str:
    strategies = ["mobile", "desktop"] if strategy == "both" else [strategy]
    results = await asyncio.gather(*(run(url, s) for s in strategies), return_exceptions=True)
    out = []
    for s, r in zip(strategies, results):
        if isinstance(r, BlockedURL):
            raise r
        out.append(f"{s.capitalize()}: {r}" if isinstance(r, Exception) else summarize(r, s))
    return "\n\n".join(out)
