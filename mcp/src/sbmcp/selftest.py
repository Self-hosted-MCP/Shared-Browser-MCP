"""Checks the parts that matter for safety and for working at all, from inside the running app.
Used by the Self-test button on the user's Settings tab and by the self_test tool, so a server can be checked without a shell.
The browser checks use their own short-lived connection and tab, so they never disturb what the user is looking at."""
import asyncio
import socket
import time
from datetime import datetime

import httpx
from playwright.async_api import Error as PWError
from playwright.async_api import async_playwright

from . import __version__, access, config, settings
from .safe_fetch import BlockedURL, resolve_public
from .state import LOCAL

PRIVATE_TARGETS = [("the connector's own admin port", "http://mcp:8766/api/status"),
                   ("the cloud metadata address", "http://169.254.169.254/"),
                   ("localhost (the live view is listening there)", "http://127.0.0.1:6080/vnc.html"),
                   ("a home network address", "http://192.168.1.1/")]


LAST: dict | None = None   # the newest result, shown on the user's search page


def row(name: str, ok: bool, detail: str = "") -> dict:
    return {"name": name, "ok": ok, "detail": detail}


async def door() -> list[dict]:
    out = []
    try:
        async with httpx.AsyncClient(timeout=8, trust_env=False) as c:
            r = await c.get(f"http://127.0.0.1:{config.PORT}/health")
            out.append(row("Claude's door answers", r.status_code == 200))
            r = await c.post(f"http://127.0.0.1:{config.PORT}/mcp", content=b"{}", headers={"content-type": "application/json"})
            out.append(row("Claude's door refuses callers without a login", r.status_code == 401, f"got {r.status_code}"))
    except Exception as exc:
        out.append(row("Claude's door answers", False, type(exc).__name__))
    # the second lock on the user's page: without Cloudflare's token the admin API must answer 401
    try:
        async with httpx.AsyncClient(timeout=8, trust_env=False) as c:
            r = await c.get(f"http://127.0.0.1:{config.ADMIN_PORT}/api/status")
        local = any(h in config.PUBLIC_URL for h in ("localhost", "127.0.0.1"))
        if access.ENFORCE:
            ok = r.status_code == 401 and access.configured()
            detail = "on" if ok else ("on but the team domain or audience tag is missing" if not access.configured() else f"on but answered {r.status_code} without a token")
        else:
            ok, detail = local, "off (fine on a Mac)" if local else "OFF on a public address: set ACCESS_ENFORCE=1"
        out.append(row("Zero Trust second lock on the user's page", ok, detail))
    except Exception as exc:
        out.append(row("Zero Trust second lock on the user's page", False, type(exc).__name__))
    return out


async def search_check() -> dict:
    from . import search
    try:
        data = await search.raw_search("open source")
        n = len(data.get("results", []))
        note = search.engine_notes(data)
        return row("Search works", n > 0, f"{n} results" + (f". {note}" if note else ""))
    except Exception as exc:
        return row("Search works", False, str(exc)[:120])


async def dns_check() -> dict:
    """Our own DNS container answers for public names (it never logs them)."""
    try:
        infos = await asyncio.get_running_loop().getaddrinfo("example.com", 443)
        return row("Private DNS answers", bool(infos), f"{len(infos)} answers for example.com")
    except Exception as exc:
        return row("Private DNS answers", False, type(exc).__name__)


async def reader_refuses_private() -> dict:
    try:
        await resolve_public("searxng", 8080)
        return row("The page reader refuses private addresses", False, "it accepted searxng")
    except BlockedURL:
        return row("The page reader refuses private addresses", True)


def folders() -> dict:
    import os
    bad = [str(p) for p in (config.DOWNLOADS_DIR, config.UPLOADS_DIR, config.DATA_DIR, config.CTL_DIR) if not os.access(p, os.W_OK)]
    return row("File folders are writable", not bad, ", ".join(bad))


async def browser_checks() -> list[dict]:
    out = []
    pw = await async_playwright().start()
    try:
        ip = socket.gethostbyname(config.BROWSER_HOST)
        browser = await pw.chromium.connect_over_cdp(f"http://{ip}:{config.BROWSER_CDP_PORT}", timeout=10000)
        ctx = browser.contexts[0]
        page = await ctx.new_page()
        try:
            try:
                await page.goto("chrome://sandbox", timeout=10000)
                text = await page.inner_text("body")
                out.append(row("Chromium's own sandbox is on", "adequately sandboxed" in text))
            except PWError as exc:
                out.append(row("Chromium's own sandbox is on", False, str(exc).splitlines()[0][:100]))
            # a web page must not reach the live view or DevTools through loopback (a page can open a WebSocket there)
            try:
                await page.goto("https://example.com/", wait_until="domcontentloaded", timeout=10000)
                reach = await page.evaluate("""() => new Promise(res => { try { const ws = new WebSocket('ws://127.0.0.1:6080/websockify');
                    ws.onopen = () => { ws.close(); res('opened'); }; ws.onerror = () => res('refused'); setTimeout(() => res('refused'), 4000); } catch (e) { res('refused'); } })""")
                out.append(row("A web page cannot reach the live view through loopback", reach == "refused", "" if reach == "refused" else "a page opened a WebSocket to the live view"))
            except PWError as exc:
                out.append(row("A web page cannot reach the live view through loopback", False, str(exc).splitlines()[0][:100]))
            try:
                resp = await page.goto(f"https://example.com/?selftest={int(time.time())}", wait_until="domcontentloaded", timeout=10000)   # a new address each time, so Chrome's cache cannot answer for a broken wall
                out.append(row("The browser opens public sites through the wall", bool(resp) and resp.status == 200))
            except PWError as exc:
                out.append(row("The browser opens public sites through the wall", False, str(exc).splitlines()[0][:100]))
            for label, url in PRIVATE_TARGETS:
                blocked, detail = False, ""
                try:
                    resp = await page.goto(url, wait_until="domcontentloaded", timeout=6000)
                    blocked = bool(resp and resp.headers.get("x-squid-error"))
                    detail = "" if blocked else f"opened with status {resp.status if resp else '?'}"
                except PWError as exc:
                    blocked = any(e in str(exc) for e in ("ERR_ADDRESS_UNREACHABLE", "ERR_TUNNEL", "ERR_PROXY"))   # a plain "connection refused" is NOT proof: it means the browser went around the wall
                    detail = "" if blocked else str(exc).splitlines()[0][:100]
                out.append(row(f"The wall refuses {label}", blocked, detail))
        finally:
            await page.close()
    except Exception as exc:
        out.append(row("The browser is reachable", False, f"{type(exc).__name__}: {str(exc)[:100]}"))
    finally:
        await pw.stop()
    return out


async def run() -> dict:
    t0 = time.time()
    results = list(await door())
    results.append(await search_check())
    results.append(await dns_check())
    results.append(await reader_refuses_private())
    results.append(folders())
    results += await browser_checks()
    failed = [r for r in results if not r["ok"]]
    st = settings.load()
    res = {"ok": not failed, "passed": len(results) - len(failed), "total": len(results), "seconds": round(time.time() - t0, 1),
           "results": results, "when": datetime.now(LOCAL).strftime("%Y-%m-%d %H:%M %Z"),
           "context": f"version {__version__}, browser theme {st['browser_theme']}, public address {config.PUBLIC_URL}"}
    res["text"] = as_text(res, header=True)
    global LAST
    LAST = {"ok": res["ok"], "passed": res["passed"], "total": res["total"], "ts": time.time(),
            "sandbox": next((r["ok"] for r in results if "sandbox" in r["name"].lower()), None)}
    return res


def as_text(res: dict, header: bool = False) -> str:
    """Plain text of a run. With header=True it is ready to paste to Claude: failures first, plus what Claude needs to start."""
    lines = []
    if header:
        lines += ["Self-test of my Shared Browser" + (f" ({res.get('when', '')})" if res.get("when") else "") + ". Please find and fix what failed.",
                  "The code is in ~/Projects/Shared-Browser-MCP (mcp/, browser/, egress/, dns/, front/, docker-compose.yml). Context: " + res.get("context", "") + "."]
    lines.append(f"Self-test: {res['passed']} of {res['total']} passed in {res['seconds']} s" + ("" if res["ok"] else ". SOMETHING FAILED"))
    rows = sorted(res["results"], key=lambda r: r["ok"])   # failures first
    for r in rows:
        lines.append(f"{'PASS' if r['ok'] else 'FAIL'}  {r['name']}" + (f" ({r['detail']})" if r["detail"] else ""))
    return "\n".join(lines)
