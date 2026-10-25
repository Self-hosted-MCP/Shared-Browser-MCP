"""Settings come from environment variables only. Secrets (LOGIN_HASH, SECRET_KEY) live in the server's environment settings, never in files."""
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data")).expanduser()


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name) or default)
    except ValueError:
        return default


def env_list(name: str, default: str = "") -> list[str]:
    return [x.strip().lower() for x in (env(name) or default).split(",") if x.strip()]


PUBLIC_URL = env("PUBLIC_URL", "http://localhost:8765").rstrip("/")
HOST = env("HOST", "0.0.0.0")
PORT = env_int("PORT", 8765)
SEARXNG_URL = env("SEARXNG_URL", "http://searxng:8080").rstrip("/")
REDIRECT_HOSTS = env_list("ALLOWED_REDIRECT_HOSTS", "claude.ai,claude.com")

# search defaults
DEFAULT_LANGUAGE = env("DEFAULT_LANGUAGE", "en")
SAFE_SEARCH = env_int("SAFE_SEARCH", 0)
MAX_RESULTS = env_int("MAX_RESULTS", 8)
MAX_SNIPPET_CHARS = env_int("MAX_RESULT_CHARS", 300)

# page reader limits
READ_MAX_CHARS = env_int("READ_MAX_CHARS", 12000)
FETCH_TIMEOUT_S = env_int("FETCH_TIMEOUT_MS", 15000) / 1000
FETCH_MAX_BYTES = env_int("FETCH_MAX_BYTES", 8_000_000)

BLOCKED_SITES = env_list("BLOCKED_SITES")

# shared browser
BROWSER_HOST = env("BROWSER_HOST", "browser")
BROWSER_CDP_PORT = env_int("BROWSER_CDP_PORT", 9223)
NAV_TIMEOUT_MS = env_int("NAVIGATION_TIMEOUT_MS", 30000)
ACTION_TIMEOUT_MS = env_int("ACTION_TIMEOUT_MS", 8000)
MAX_TABS = env_int("MAX_TABS", 8)
ADMIN_PORT = env_int("ADMIN_PORT", 8766)
ACTION_LOG_MAX_MB = env_int("ACTION_LOG_MAX_MB", 2)
LOG_FILE = DATA_DIR / "actions.log"

AUTO_MIN_WORDS = env_int("AUTO_MIN_WORDS", 40)   # fewer words than this from a plain fetch: try the real browser

SETTINGS_FILE = DATA_DIR / "settings.json"
CTL_DIR = Path(env("CTL_DIR", "/ctl"))   # the only folder the browser and dns containers can read

# files: downloads (the browser saves here) and uploads (The user drops files here for Claude to attach on websites)
DOWNLOADS_DIR = Path(env("DOWNLOADS_DIR", "/files/downloads"))
UPLOADS_DIR = Path(env("UPLOADS_DIR", "/files/uploads"))
FILES_MAX_MB = env_int("FILES_MAX_MB", 50)
FRONT_URL = env("FRONT_URL", "http://localhost:8081").rstrip("/")
BLOCKED_EXT = set(env_list("BLOCKED_EXT", "exe,msi,dll,bat,cmd,com,scr,sh,bash,zsh,ps1,vbs,vbe,js,mjs,jse,wsf,hta,jar,apk,ipa,dmg,pkg,app,deb,rpm,appimage,lnk,iso,reg,command,cpl,pif,gadget,py,pl,rb,php,scpt,scptd,terminal,workflow,docm,xlsm,pptm,url,webloc,chm,jnlp,vb,wsh"))
THEME_FILE = CTL_DIR / "browser-theme"   # read by the browser container
