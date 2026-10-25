"""The few security facts the user can see at the bottom of their search page: where the server reaches the internet from, how its
DNS goes, whether the last self-test passed, the lock in front of the page, and the browser version.
Lookups are cached for 10 minutes so the page costs nothing."""
import asyncio
import socket
import time

import httpx

from . import __version__, access, config, selftest
from .state import STATE

CACHE_SECONDS = 600
_cache: dict[str, tuple[float, object]] = {}


def country_name(code: str) -> str:
    try:
        with open("/usr/share/zoneinfo/iso3166.tab", encoding="utf-8") as f:
            for line in f:
                if line.startswith(code + "\t"):
                    return line.rstrip("\n").split("\t", 1)[1]
    except OSError:
        pass
    return code


async def cached(key: str, fn):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]
    try:
        value = await fn()
    except Exception:
        value = None
    _cache[key] = (time.time(), value)
    return value


VPN_NAMES = ("mullvad", "nordvpn", "nordlynx", "proton", "ivpn", "expressvpn", "surfshark", "privateinternetaccess", "pia.", "windscribe",
             "cyberghost", "tunnelbear", "hide.me", "vpn")


async def ivpn_lookup() -> dict | None:
    """IVPN's own public check: provider, city, and whether this address is one of its servers. None if unreachable."""
    try:
        async with httpx.AsyncClient(timeout=4, trust_env=False) as c:
            r = await c.get("https://api.ivpn.net/v4/geo-lookup")
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


async def network_of(ip: str) -> dict:
    """Who owns the address, from its reverse DNS name (no third-party service). Honest about what it can tell:
    a VPN is only 'detected' when the name says so, otherwise 'not detected'."""
    try:
        host = (await asyncio.to_thread(socket.gethostbyaddr, ip))[0].lower()
    except OSError:
        return {"name": None, "vpn": False, "vpn_name": None}
    vpn = next((n for n in VPN_NAMES if n in host), None)
    parts = host.split(".")
    return {"name": ".".join(parts[-3:]) if len(parts) > 3 else host, "vpn": bool(vpn), "vpn_name": vpn}


async def exit_address() -> dict | None:
    async with httpx.AsyncClient(timeout=4, trust_env=False) as c:
        text = (await c.get("https://www.cloudflare.com/cdn-cgi/trace")).text
    f = dict(l.split("=", 1) for l in text.splitlines() if "=" in l)
    ip = f.get("ip", "?")
    network, geo = await asyncio.gather(network_of(ip), ivpn_lookup())
    if geo and geo.get("ip_address") == ip:   # IVPN's own check also names the provider and the city
        network = {"name": geo.get("isp") or network["name"], "vpn": bool(geo.get("isIvpnServer")) or network["vpn"],
                   "vpn_name": "IVPN" if geo.get("isIvpnServer") else network["vpn_name"]}
    return {"ip": ip, "country": f.get("loc", "?"), "country_name": country_name(f.get("loc", "?")), "colo": f.get("colo", ""),
            "city": (geo or {}).get("city", ""), "warp": f.get("warp") == "on", "network": network}


async def chromium() -> str | None:
    ip = socket.gethostbyname(config.BROWSER_HOST)
    async with httpx.AsyncClient(timeout=3, trust_env=False) as c:
        v = (await c.get(f"http://{ip}:{config.BROWSER_CDP_PORT}/json/version")).json().get("Browser", "")
    return v.replace("Chrome/", "Chromium ").split(".")[0] if v else None


async def facts(provider=None) -> dict:
    ex, chrome = await asyncio.gather(cached("exit", exit_address), cached("chromium", chromium))
    st = selftest.LAST
    zt = "on" if access.ENFORCE and access.configured() else ("keys missing" if access.ENFORCE else "off")
    return {
        "exit": ex,
        "selftest": ({"ok": st["ok"], "passed": st["passed"], "total": st["total"], "age_seconds": int(time.time() - st["ts"]),
                      "sandbox": st["sandbox"]} if st else None),
        "zero_trust": zt,
        "chromium": chrome,
        "paused": STATE.paused,
        "apps": len(provider.apps()) if provider else 0,
        "version": __version__,
    }
