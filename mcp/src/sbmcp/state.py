"""What Claude is doing right now, shared between the MCP door and the user's page, plus the one small action log.
The log keeps what was done and where (site name only), never searches, page text or typed text."""
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import config, settings

LOCAL = ZoneInfo(config.env("TZ", "UTC") or "UTC")   # the log clock, from TZ
_lock = threading.Lock()


class State:
    def __init__(self):
        self.paused = (config.DATA_DIR / "paused").exists()   # the user pressed Pause: refused until they resume, even after a restart
        self.handoff: dict | None = None   # {"message": str, "since": float, "done": bool}
        self.inflight = 0              # tool calls running right now
        self.last_end = 0.0            # when the last one finished

    def working(self) -> bool:
        """True while any tool call is running, and for 2 seconds after, so quick steps don't flicker."""
        return self.inflight > 0 or time.time() < self.last_end + 2

    def begin(self) -> None:
        with _lock:
            self.inflight += 1

    def end(self) -> None:
        with _lock:
            self.inflight = max(0, self.inflight - 1)
            self.last_end = time.time()

    def mark_busy(self, seconds: float = 4.0) -> None:   # kept for callers that only touch the browser
        pass

    def snapshot(self) -> dict:
        h = self.handoff
        waiting = bool(h and not h["done"])
        return {"paused": self.paused, "working": self.working() and not waiting,
                "handoff": {"message": h["message"], "since": h["since"]} if h and not h["done"] else None}


STATE = State()


def purge_old() -> None:
    """Lines older than the keep-days setting are deleted."""
    if not config.LOG_FILE.exists():
        return
    days = settings.load()["log_keep_days"]
    cutoff = (datetime.now(LOCAL) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    lines = config.LOG_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [l for l in lines if l[:19] >= cutoff]
    if len(kept) != len(lines):
        config.LOG_FILE.write_text("".join(kept), encoding="utf-8")


def clear_log() -> None:
    with _lock:
        if config.LOG_FILE.exists():
            config.LOG_FILE.write_text("", encoding="utf-8")


def log_action(text: str) -> None:
    """One line per action. Lines expire after the keep-days setting; the file is also capped at ACTION_LOG_MAX_MB."""
    line = f"{datetime.now(LOCAL):%Y-%m-%d %H:%M:%S} {text}\n"
    with _lock:
        config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with config.LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
        purge_old()
        limit = config.ACTION_LOG_MAX_MB * 1024 * 1024
        if config.LOG_FILE.stat().st_size > limit:
            lines = config.LOG_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
            config.LOG_FILE.write_text("".join(lines[len(lines) // 2:]), encoding="utf-8")


def read_log(limit: int = 200) -> list[str]:
    with _lock:
        purge_old()
    if not config.LOG_FILE.exists():
        return []
    return config.LOG_FILE.read_text(encoding="utf-8").splitlines()[-limit:][::-1]
