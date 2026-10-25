"""The safety rules in docs/safety.md, checked without a browser or the network. Each test names its rule."""
import asyncio
import time

import pytest

from sbmcp import auth, files
from sbmcp.browser import BrowserError, run_js
from sbmcp.safe_fetch import BlockedURL, address_ok, check_url, resolve_public


# Rule: the reader never opens private addresses (home, server and cloud networks, odd ways to write them).
@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.5", "172.16.3.4", "192.168.1.1", "169.254.169.254", "100.64.0.1",
                                "0.0.0.0", "::1", "fc00::1", "fe80::1", "::ffff:127.0.0.1", "::ffff:10.0.0.1", "224.0.0.1"])
def test_private_addresses_are_refused(ip):
    assert not address_ok(ip)


@pytest.mark.parametrize("ip", ["93.184.215.14", "1.1.1.1", "2606:4700:4700::1111"])
def test_public_addresses_are_allowed(ip):
    assert address_ok(ip)


@pytest.mark.parametrize("host", ["127.0.0.1", "[::1]", "169.254.169.254", "10.1.2.3"])
def test_reader_refuses_a_private_literal_address(host):
    with pytest.raises(BlockedURL):
        asyncio.run(resolve_public(host, 80))


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/x", "javascript:alert(1)", "http:///nohost"])
def test_reader_refuses_other_kinds_of_address(url):
    with pytest.raises(BlockedURL):
        check_url(url)


# Rule: AI apps log in with a passphrase that is only ever stored as a slow hash.
def test_passphrase_hash_checks_the_right_passphrase_only():
    stored = auth.hash_passphrase("correct horse battery", rounds=1000)
    assert stored.startswith("pbkdf2:1000:")
    assert "correct horse battery" not in stored
    assert auth.check_passphrase("correct horse battery", stored)
    assert not auth.check_passphrase("correct horse batterY", stored)
    assert not auth.check_passphrase("anything", "not a hash")


# Rule: a new AI app can only connect while you have pressed Allow a new app (the pairing window).
def test_pairing_window_opens_for_a_limited_time():
    provider = auth.PassphraseOAuth("https://mcp.example.com", ["claude.ai"])
    assert not provider.pairing_open()
    until = provider.open_pairing(5)
    assert provider.pairing_open()
    assert 4 * 60 < until - time.time() <= 5 * 60
    assert provider.open_pairing(999) - time.time() <= 15 * 60   # never more than 15 minutes
    provider.pairing_until = time.time() - 1
    assert not provider.pairing_open()


def test_a_new_app_is_refused_while_pairing_is_closed():
    provider = auth.PassphraseOAuth("https://mcp.example.com", ["claude.ai"])
    provider.pending["req"] = (time.time() + 600, "new-app", None)
    with pytest.raises(PermissionError):
        provider.complete_login("req", "any passphrase")


# Rule: programs and scripts are never stored or run, and file names can't escape their folder.
@pytest.mark.parametrize("name", ["setup.exe", "run.SH", "x.exe.", "macro.docm", "script.js", "app.dmg", "a.py"])
def test_programs_and_scripts_are_blocked(name):
    assert files.is_blocked(files.safe_name(name))


@pytest.mark.parametrize("name", ["report.pdf", "notes.txt", "photo.jpg"])
def test_documents_are_allowed(name):
    assert not files.is_blocked(name)


def test_file_names_cannot_leave_their_folder():
    path = files.path_for("uploads", "../../etc/passwd")
    assert path.parent == files.directory("uploads").resolve()
    assert path.name == "passwd"


# Rule: the AI never reads or types passwords. Scripts that mention password fields are refused before they run.
@pytest.mark.parametrize("js", ["document.querySelector('input[type=password]').value", "x.PASSWD"])
def test_scripts_about_passwords_are_refused(js):
    with pytest.raises(BrowserError):
        asyncio.run(run_js(js))
