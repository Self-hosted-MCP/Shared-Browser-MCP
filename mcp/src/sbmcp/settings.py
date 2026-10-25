"""Settings the user changes on their Settings tab. One small file; secrets never live here."""
import json
import os
import tempfile

from . import config

DEFAULTS = {"log_keep_days": 7, "files_keep_days": 3, "browser_theme": "dark"}
THEMES = ("dark", "light")


def load() -> dict:
    try:
        data = json.loads(config.SETTINGS_FILE.read_text())
    except (OSError, ValueError):
        data = {}
    out = {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
    out["log_keep_days"] = max(1, min(365, int(out["log_keep_days"])))
    out["files_keep_days"] = max(1, min(30, int(out["files_keep_days"])))
    if out["browser_theme"] not in THEMES:
        out["browser_theme"] = "dark"
    return out


def _write(path, text: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def save(changes: dict) -> dict:
    current = load()
    for key in DEFAULTS:
        if key in changes:
            current[key] = changes[key]
    if current["browser_theme"] not in THEMES:
        raise ValueError("theme must be dark or light")
    current["log_keep_days"] = max(1, min(365, int(current["log_keep_days"])))
    current["files_keep_days"] = max(1, min(30, int(current["files_keep_days"])))
    _write(config.SETTINGS_FILE, json.dumps(current, indent=1), 0o600)
    apply(current)
    return current


def apply(current: dict | None = None) -> None:
    """The browser container reads the theme file."""
    current = current or load()
    _write(config.THEME_FILE, current["browser_theme"] + "\n", 0o644)
