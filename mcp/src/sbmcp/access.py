"""A second lock behind Cloudflare Zero Trust.

Zero Trust adds a signed token (the Cf-Access-Jwt-Assertion header) to every request it lets through. This module checks that
token itself, so the user's page and its admin API refuse anything that did not come through Zero Trust, even if a Zero Trust rule
is wrong or someone reaches the server by another road.

ACCESS_ENFORCE=1 turns it on (the server default). Off only for trying it on a Mac. When it is on but not configured
(CF_ACCESS_TEAM_DOMAIN and CF_ACCESS_AUD missing), everything is refused: it fails closed."""
import asyncio
import logging

import jwt

from . import config

ENFORCE = config.env("ACCESS_ENFORCE", "0").lower() in ("1", "true", "on", "yes")
TEAM = config.env("CF_ACCESS_TEAM_DOMAIN").replace("https://", "").strip("/")   # like yourteam.cloudflareaccess.com
AUD = config.env("CF_ACCESS_AUD")                                               # the Application Audience (AUD) Tag
HEADER = "cf-access-jwt-assertion"
log = logging.getLogger("sbmcp.access")
_client = None


def configured() -> bool:
    return bool(TEAM and AUD)


def _keys():
    global _client
    if _client is None:
        _client = jwt.PyJWKClient(f"https://{TEAM}/cdn-cgi/access/certs", cache_keys=True, lifespan=3600)
    return _client


def verify(token: str, signing_key=None) -> bool:
    """True only for a token signed by this team's Zero Trust, made for this application, not expired. Never raises."""
    try:
        key = signing_key if signing_key is not None else _keys().get_signing_key_from_jwt(token).key
        jwt.decode(token, key, algorithms=["RS256"], audience=AUD, issuer=f"https://{TEAM}",
                   options={"require": ["exp", "iat", "aud", "iss"]}, leeway=30)
        return True
    except Exception as exc:   # bad signature, wrong audience, expired, keys unreachable: all the same answer
        log.warning("access token refused [build 2]: %s (%s)", type(exc).__name__, (repr(exc.__cause__ or exc))[:200])
        if type(exc).__name__ == "PyJWKClientConnectionError":   # say why the keys cannot be fetched
            import socket
            try:
                log.warning("keys host lookup ok: %s", sorted({a[4][0] for a in socket.getaddrinfo(TEAM, 443)})[:3])
            except Exception as dns_exc:
                log.warning("keys host lookup failed: %r", dns_exc)
        return False


async def allowed(headers) -> bool:
    if not ENFORCE:
        return True
    if not configured():
        return False
    token = headers.get(HEADER, "")
    if not token:
        return False
    return await asyncio.to_thread(verify, token)
