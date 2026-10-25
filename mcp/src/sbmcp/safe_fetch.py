"""Fetch a web page without ever reaching the server's own network.

Every hostname is resolved first, every address must be public, and the connection goes to that exact address
(so a name can't change its answer between the check and the connection). Redirects are checked the same way.
"""
import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx

from . import config

MAX_REDIRECTS = 5
USER_AGENT = "Mozilla/5.0 (compatible; SharedBrowserMCP/0.1)"


class BlockedURL(Exception):
    pass


def host_blocked(host: str) -> bool:
    host = host.lower().rstrip(".")
    return any(host == b or host.endswith("." + b) for b in config.BLOCKED_SITES)


def address_ok(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    return addr.is_global and not addr.is_multicast


async def resolve_public(host: str, port: int) -> str:
    """Returns one public address for host, or raises BlockedURL if any of its addresses is not public."""
    try:
        literal = ipaddress.ip_address(host.strip("[]"))
        infos = [(None, None, None, None, (str(literal), port))]
    except ValueError:
        loop = asyncio.get_running_loop()
        for attempt in range(3):   # the first lookups after a restart can fail once
            try:
                infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
                break
            except socket.gaierror as exc:
                if attempt == 2:
                    raise BlockedURL(f"Can't find the address of {host}.") from exc
                await asyncio.sleep(0.7)
    addresses = [i[4][0] for i in infos]
    if not addresses or not all(address_ok(a) for a in addresses):
        raise BlockedURL(f"{host} points inside a private network. Blocked on purpose.")
    return addresses[0]


def check_url(url: str) -> tuple[str, str, int]:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise BlockedURL("Only http and https addresses can be read.")
    if not p.hostname:
        raise BlockedURL("That address has no website name.")
    if host_blocked(p.hostname):
        raise BlockedURL(f"{p.hostname} is on the blocked sites list.")
    return p.scheme, p.hostname, p.port or (443 if p.scheme == "https" else 80)


@dataclass
class Fetched:
    url: str
    status: int
    content_type: str
    body: bytes
    truncated: bool


async def fetch(url: str) -> Fetched:
    return await asyncio.wait_for(_fetch(url), 30)   # one overall limit, however slowly a site answers


async def _fetch(url: str) -> Fetched:
    async with httpx.AsyncClient(timeout=config.FETCH_TIMEOUT_S, follow_redirects=False, trust_env=False) as client:
        for _ in range(MAX_REDIRECTS + 1):
            scheme, host, port = check_url(url)
            ip = await resolve_public(host, port)
            p = urlparse(url)
            netloc = f"[{ip}]" if ":" in ip else ip
            if p.port:
                netloc += f":{p.port}"
            target = p._replace(netloc=netloc).geturl()
            headers = {"Host": p.netloc, "User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*;q=0.5", "Accept-Encoding": "identity",   # no compressed bombs
                       
                       "Accept-Language": config.DEFAULT_LANGUAGE}
            async with client.stream("GET", target, headers=headers, extensions={"sni_hostname": host}) as r:
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                    url = urljoin(url, r.headers["location"])
                    continue
                chunks, size, truncated = [], 0, False
                async for chunk in r.aiter_bytes():
                    size += len(chunk)
                    chunks.append(chunk)
                    if size >= config.FETCH_MAX_BYTES:
                        truncated = True
                        break
                return Fetched(url, r.status_code, r.headers.get("content-type", ""), b"".join(chunks), truncated)
    raise BlockedURL("Too many redirects.")
