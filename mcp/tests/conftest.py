"""Test setup: every folder the app writes to points at a fresh temporary folder, before the app is imported.
Uses test values only. No network, no browser, no real passphrase."""
import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="sbmcp-tests-"))
for name, sub in {"DATA_DIR": "data", "DOWNLOADS_DIR": "files/downloads", "UPLOADS_DIR": "files/uploads", "CTL_DIR": "ctl"}.items():
    os.environ[name] = str(_tmp / sub)
os.environ["LOGIN_HASH"] = ""
os.environ["LOGIN_PASSPHRASE"] = ""
