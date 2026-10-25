"""The user's side door. Listens on its own port, reachable only from inside the server's network and through the front
page (which sits behind Zero Trust). It is never published on Claude's public address."""
import asyncio
import json
import socket
import threading
import time
from urllib.parse import urlparse

import httpx
import uvicorn
import websockets
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from . import access, config, files, security, selftest, settings
from .state import STATE, clear_log, log_action, read_log

NO_STORE = {"Cache-Control": "no-store"}


async def status(request: Request):
    return JSONResponse(STATE.snapshot(), headers=NO_STORE)


async def handoff_done(request: Request):
    if STATE.handoff and not STATE.handoff["done"]:
        STATE.handoff["done"] = True
        log_action("handoff finished by the user")
    return JSONResponse(STATE.snapshot(), headers=NO_STORE)


async def pause(request: Request):
    body = await request.json() if request.headers.get("content-length") not in (None, "0") else {}
    STATE.paused = bool(body.get("paused", not STATE.paused))
    flag = config.DATA_DIR / "paused"
    flag.touch() if STATE.paused else flag.unlink(missing_ok=True)
    log_action("The user paused Claude" if STATE.paused else "The user resumed Claude")
    return JSONResponse(STATE.snapshot(), headers=NO_STORE)


async def log(request: Request):
    return JSONResponse({"lines": read_log(200)}, headers=NO_STORE)


async def get_settings(request: Request):
    return JSONResponse(settings.load(), headers=NO_STORE)


async def set_settings(request: Request):
    try:
        body = await request.json()
        saved = settings.save(body if isinstance(body, dict) else {})
    except (ValueError, TypeError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400, headers=NO_STORE)
    log_action(f"settings changed: {', '.join(sorted(body))}")
    return JSONResponse(saved, headers=NO_STORE)


async def log_clear(request: Request):
    clear_log()
    log_action("action log cleared by the user")
    return JSONResponse({"ok": True}, headers=NO_STORE)


async def clear_history(request: Request):
    """Closes Chromium. Docker starts it again, and on start it deletes its history (saved logins stay)."""
    try:
        ip = socket.gethostbyname(config.BROWSER_HOST)
        async with httpx.AsyncClient(timeout=5, trust_env=False) as c:
            ws_url = (await c.get(f"http://{ip}:{config.BROWSER_CDP_PORT}/json/version")).json()["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, open_timeout=5, max_size=None) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Browser.close"}))
            try:
                await asyncio.wait_for(ws.recv(), 3)
            except Exception:
                pass
    except Exception as exc:
        return JSONResponse({"ok": False, "error": f"Could not restart the browser ({type(exc).__name__})."}, status_code=502, headers=NO_STORE)
    log_action("browser history cleared (browser restarted)")
    return JSONResponse({"ok": True}, headers=NO_STORE)


async def files_list(request: Request):
    return JSONResponse({"downloads": files.listing("downloads"), "uploads": files.listing("uploads"),
                         "max_mb": config.FILES_MAX_MB, "keep_days": settings.load()["files_keep_days"],
                         "blocked": sorted(config.BLOCKED_EXT)}, headers=NO_STORE)


async def file_get(request: Request):
    """The user saves a file. Always sent as a plain download, never shown in the page, so a downloaded web page can't run."""
    try:
        p = files.path_for(request.path_params["kind"], request.path_params["name"])
    except files.FileError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400, headers=NO_STORE)
    if not p.is_file():
        return JSONResponse({"error": "No such file."}, status_code=404, headers=NO_STORE)
    return FileResponse(p, media_type="application/octet-stream", filename=p.name,
                        headers={**NO_STORE, "X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox"})


async def file_delete(request: Request):
    try:
        files.delete(request.path_params["kind"], request.path_params["name"])
    except files.FileError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400, headers=NO_STORE)
    return JSONResponse({"ok": True}, headers=NO_STORE)


async def file_upload(request: Request):
    limit = (config.FILES_MAX_MB + 5) * 1024 * 1024
    if int(request.headers.get("content-length") or 0) > limit * 10:
        return JSONResponse({"error": "Too much at once."}, status_code=413, headers=NO_STORE)
    form = await request.form(max_files=10, max_fields=10)
    saved, errors = [], []
    for item in form.getlist("file"):
        if not hasattr(item, "filename"):
            continue
        try:
            saved.append(files.save_upload(item.filename, item.file))
        except files.FileError as exc:
            errors.append(f"{item.filename}: {exc}")
    return JSONResponse({"saved": saved, "errors": errors}, status_code=200 if saved or not errors else 400, headers=NO_STORE)


async def restart_browser(request: Request):
    """Closes Chromium. Docker starts it again (with the current theme); on start it also deletes its history."""
    try:
        ip = socket.gethostbyname(config.BROWSER_HOST)
        async with httpx.AsyncClient(timeout=5, trust_env=False) as c:
            ws_url = (await c.get(f"http://{ip}:{config.BROWSER_CDP_PORT}/json/version")).json()["webSocketDebuggerUrl"]
        async with websockets.connect(ws_url, open_timeout=5, max_size=None) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Browser.close"}))
            try:
                await asyncio.wait_for(ws.recv(), 3)
            except Exception:
                pass
    except Exception as exc:
        return JSONResponse({"ok": False, "error": f"Could not restart the browser ({type(exc).__name__})."}, status_code=502, headers=NO_STORE)
    log_action("browser restarted")
    return JSONResponse({"ok": True}, headers=NO_STORE)


async def files_list(request: Request):
    return JSONResponse({"downloads": files.listing("downloads"), "uploads": files.listing("uploads"),
                         "max_mb": config.FILES_MAX_MB, "keep_days": settings.load()["files_keep_days"],
                         "blocked": sorted(config.BLOCKED_EXT)}, headers=NO_STORE)


async def file_get(request: Request):
    """The user saves a file. Always sent as a plain download, never shown in the page, so a downloaded web page can't run."""
    try:
        p = files.path_for(request.path_params["kind"], request.path_params["name"])
    except files.FileError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400, headers=NO_STORE)
    if not p.is_file():
        return JSONResponse({"error": "No such file."}, status_code=404, headers=NO_STORE)
    return FileResponse(p, media_type="application/octet-stream", filename=p.name,
                        headers={**NO_STORE, "X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox"})


async def file_delete(request: Request):
    try:
        files.delete(request.path_params["kind"], request.path_params["name"])
    except files.FileError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400, headers=NO_STORE)
    return JSONResponse({"ok": True}, headers=NO_STORE)


async def file_upload(request: Request):
    limit = (config.FILES_MAX_MB + 5) * 1024 * 1024
    if int(request.headers.get("content-length") or 0) > limit * 10:
        return JSONResponse({"error": "Too much at once."}, status_code=413, headers=NO_STORE)
    form = await request.form(max_files=10, max_fields=10)
    saved, errors = [], []
    for item in form.getlist("file"):
        if not hasattr(item, "filename"):
            continue
        try:
            saved.append(files.save_upload(item.filename, item.file))
        except files.FileError as exc:
            errors.append(f"{item.filename}: {exc}")
    return JSONResponse({"saved": saved, "errors": errors}, status_code=200 if saved or not errors else 400, headers=NO_STORE)


PROVIDER = None   # set by start(): the login provider that knows the connected apps


async def selftest_run(request: Request):
    return JSONResponse(await selftest.run(), headers=NO_STORE)


async def pairing_status(request: Request):
    left = max(0, int((PROVIDER.pairing_until if PROVIDER else 0) - time.time()))
    return JSONResponse({"open": left > 0, "seconds_left": left}, headers=NO_STORE)


async def pairing_open(request: Request):
    if not PROVIDER:
        return JSONResponse({"error": "Not ready."}, status_code=503, headers=NO_STORE)
    PROVIDER.open_pairing(5)
    log_action("pairing opened for 5 minutes")
    return await pairing_status(request)


async def security_facts(request: Request):
    return JSONResponse(await security.facts(PROVIDER), headers=NO_STORE)


WALL_FOOTER = "/wall/footer"


async def wall_footer(request: Request):
    """The five footer lines for the search page inside the shared browser, which has no Zero Trust token. Only the connection
    facts any website already sees (exit address, network, VPN). Never proxied by the main server
    block, so only the browser's own search page (nginx port 8088 on the wall network) reaches it."""
    d = await security.facts(PROVIDER)
    return JSONResponse({"exit": d.get("exit")}, headers=NO_STORE)


async def apps_list(request: Request):
    return JSONResponse({"apps": PROVIDER.apps() if PROVIDER else []}, headers=NO_STORE)


async def app_disconnect(request: Request):
    body = await request.json()
    cid = str(body.get("id", ""))
    if not PROVIDER or cid not in PROVIDER.approved:
        return JSONResponse({"error": "No such app."}, status_code=404, headers=NO_STORE)
    PROVIDER.disconnect(cid, forget=True)
    log_action("app disconnected")
    return JSONResponse({"ok": True}, headers=NO_STORE)


class ZeroTrustOnly(BaseHTTPMiddleware):
    """Every request must carry Cloudflare's signed token (when ACCESS_ENFORCE is on). Nothing here has a login of its own.
    Changes (POST, DELETE) must come from our own page: same site and a JSON or upload body, so another website cannot make
    the user's browser press Pause, delete files or disconnect an app."""
    async def dispatch(self, request, call_next):
        if request.url.path != WALL_FOOTER and not await access.allowed(request.headers):
            return JSONResponse({"error": "Not through Zero Trust."}, status_code=401, headers=NO_STORE)
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            origin = request.headers.get("origin")
            if origin and urlparse(origin).netloc != request.headers.get("host", ""):
                return JSONResponse({"error": "Cross-site request refused."}, status_code=403, headers=NO_STORE)
            ctype = request.headers.get("content-type", "").split(";")[0].strip().lower()
            if request.method != "DELETE" and ctype not in ("application/json", "multipart/form-data"):
                return JSONResponse({"error": "Unsupported content type."}, status_code=415, headers=NO_STORE)
        return await call_next(request)


async def auth_ok(request: Request):
    """nginx asks this before serving any page, the live view or the search page. The middleware has already decided."""
    from starlette.responses import Response
    return Response(status_code=204)


def app() -> Starlette:
    return Starlette(middleware=[Middleware(ZeroTrustOnly)], routes=[
        Route("/auth", auth_ok),
        Route("/api/selftest", selftest_run),
        Route("/api/pairing", pairing_status),
        Route("/api/pairing", pairing_open, methods=["POST"]),
        Route("/api/security", security_facts),
        Route(WALL_FOOTER, wall_footer),
        Route("/api/apps", apps_list),
        Route("/api/apps/disconnect", app_disconnect, methods=["POST"]),
        Route("/api/files", files_list),
        Route("/api/files/upload", file_upload, methods=["POST"]),
        Route("/api/files/{kind}/{name:path}", file_get),
        Route("/api/files/{kind}/{name:path}", file_delete, methods=["DELETE"]),
        Route("/api/settings", get_settings),
        Route("/api/settings", set_settings, methods=["POST"]),
        Route("/api/log/clear", log_clear, methods=["POST"]),
        Route("/api/browser/clear-history", clear_history, methods=["POST"]),
        Route("/api/browser/restart", restart_browser, methods=["POST"]),
        Route("/api/status", status),
        Route("/api/handoff/done", handoff_done, methods=["POST"]),
        Route("/api/pause", pause, methods=["POST"]),
        Route("/api/log", log),
    ])


def start(provider=None) -> None:
    global PROVIDER
    PROVIDER = provider
    server = uvicorn.Server(uvicorn.Config(app(), host="0.0.0.0", port=config.ADMIN_PORT, log_level="warning",
                                           access_log=False))
    server.install_signal_handlers = lambda: None
    threading.Thread(target=server.run, name="admin", daemon=True).start()
