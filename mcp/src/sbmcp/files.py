"""Downloads and uploads. Files are only ever stored and read: nothing here opens or runs them.
Programs and scripts are refused, big files are refused, and every file expires."""
import io
import re
import threading
import time
import zipfile
from pathlib import Path

from . import config, settings
from .state import log_action

KINDS = {"downloads": lambda: config.DOWNLOADS_DIR, "uploads": lambda: config.UPLOADS_DIR}
TEMP_SUFFIXES = (".crdownload", ".tmp", ".part")
TEXT_EXT = {"txt", "md", "csv", "tsv", "json", "xml", "html", "htm", "log", "yaml", "yml", "ini", "srt", "vtt", "rtf"}
IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}


class FileError(Exception):
    pass


def directory(kind: str) -> Path:
    if kind not in KINDS:
        raise FileError("Use downloads or uploads.")
    d = KINDS[kind]()
    d.mkdir(parents=True, exist_ok=True)
    return d


def safe_name(name: str) -> str:
    base = Path((name or "").replace("\\", "/")).name
    base = re.sub(r"[\x00-\x1f\x7f]", "", base).strip().lstrip(".").rstrip(". ")   # no trailing dots or spaces: "x.exe." is x.exe
    base = re.sub(r"\s+", " ", base)[:120]
    if not base:
        raise FileError("That file name is not usable.")
    return base


def ext_of(name: str) -> str:
    return Path(name).suffix.lower().lstrip(".")


def is_blocked(name: str) -> bool:
    return ext_of(name) in config.BLOCKED_EXT


def path_for(kind: str, name: str) -> Path:
    d = directory(kind).resolve()
    p = (d / safe_name(name)).resolve()
    if p.parent != d:
        raise FileError("That file name is not usable.")
    return p


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def listing(kind: str) -> list[dict]:
    out = []
    for p in directory(kind).iterdir():
        if p.is_file() and not p.name.endswith(TEMP_SUFFIXES):
            st = p.stat()
            out.append({"name": p.name, "size": st.st_size, "modified": int(st.st_mtime)})
    return sorted(out, key=lambda r: r["modified"], reverse=True)


def delete(kind: str, name: str) -> None:
    p = path_for(kind, name)
    if not p.is_file():
        raise FileError("No such file.")
    p.unlink()
    log_action(f"{kind[:-1]} deleted")


def free_path(kind: str, name: str) -> Path:
    """A path in the folder that does not exist yet (report.pdf, report-1.pdf, ...)."""
    d = directory(kind)
    name = safe_name(name)
    target, n = d / name, 1
    while target.exists():
        target = d / f"{Path(name).stem}-{n}{Path(name).suffix}"
        n += 1
    return target


def save_upload(filename: str, source) -> dict:
    name = safe_name(filename)
    if is_blocked(name):
        raise FileError(f"Files of type .{ext_of(name)} are not accepted.")
    d = directory("uploads")
    target = d / name
    n = 1
    while target.exists():
        target = d / f"{Path(name).stem}-{n}{Path(name).suffix}"
        n += 1
    limit = config.FILES_MAX_MB * 1024 * 1024
    size = 0
    try:
        with target.open("wb") as f:
            while chunk := source.read(1024 * 256):
                size += len(chunk)
                if size > limit:
                    raise FileError(f"Too big: the limit is {config.FILES_MAX_MB} MB.")
                f.write(chunk)
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    log_action("upload received")
    return {"name": target.name, "size": size}


def sweep() -> int:
    """Delete refused types, oversize files and expired files. Returns how many were removed."""
    removed, now = 0, time.time()
    max_age = settings.load()["files_keep_days"] * 86400
    limit = config.FILES_MAX_MB * 1024 * 1024
    for kind in KINDS:
        for p in directory(kind).iterdir():
            if not p.is_file():
                continue
            try:
                st = p.stat()
                temp = p.name.endswith(TEMP_SUFFIXES)
                expired = now - st.st_mtime > (max_age if not temp else 86400)
                if (is_blocked(p.name) and not temp) or st.st_size > limit or expired:
                    p.unlink()
                    removed += 1
            except OSError:
                pass
    return removed


def start_sweeper() -> None:
    def loop():
        while True:
            try:
                n = sweep()
                if n:
                    log_action(f"{n} file(s) removed (expired, too big or refused type)")
            except Exception:
                pass
            time.sleep(20)
    threading.Thread(target=loop, name="file-sweeper", daemon=True).start()


def docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        info = z.getinfo("word/document.xml")
        if info.file_size > 20 * 1024 * 1024 or sum(i.file_size for i in z.infolist()) > 200 * 1024 * 1024:
            raise FileError("That Word file expands to far more than its size (a possible zip bomb). Not read.")
        xml = z.read(info).decode("utf-8", errors="replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)


def read(kind: str, name: str) -> tuple[str, str | bytes]:
    """('text', str) or ('image', bytes). Raises FileError for anything it cannot read."""
    p = path_for(kind, name)
    if not p.is_file():
        raise FileError("No such file.")
    ext = ext_of(p.name)
    data = p.read_bytes()
    if ext in IMAGE_EXT:
        if len(data) > 5 * 1024 * 1024:
            raise FileError("That image is over 5 MB.")
        return "image", data
    if ext == "pdf":
        from pypdf import PdfReader
        r = PdfReader(io.BytesIO(data))
        return "text", "\n\n".join(f"[page {i}]\n{(pg.extract_text() or '').strip()}" for i, pg in enumerate(r.pages, 1))
    if ext == "docx":
        return "text", docx_text(data)
    if ext in TEXT_EXT:
        text = data.decode("utf-8", errors="replace")
        if ext in ("html", "htm"):
            import trafilatura
            text = trafilatura.extract(text, favor_recall=True) or text
        return "text", text
    raise FileError(f"Cannot read .{ext} files. The user can still save it from the Files page.")
