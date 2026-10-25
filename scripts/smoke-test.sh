#!/bin/bash
# Run after a deploy (on the server) or after a local start (on the Mac). Usage: scripts/smoke-test.sh [project-name]
# Checks the parts that matter for safety and for working at all. Prints PASS / FAIL lines.
P="${1:-shared-browser}"
cd "$(dirname "$0")/.." || exit 1
if docker compose version >/dev/null 2>&1; then dc() { docker compose -p "$P" "$@"; }; else dc() { docker-compose -p "$P" "$@"; }; fi
pass() { printf "  PASS  %s\n" "$1"; }
fail() { printf "  FAIL  %s\n" "$1"; FAIL=1; }
echo "Smoke test, project: $P"

for s in dns searxng egress browser front mcp; do
  st=$(docker inspect -f '{{.State.Status}}' "${P}-${s}-1" 2>/dev/null)
  [ "$st" = running ] && pass "$s is running" || fail "$s is $st"
done

py() { dc exec -T mcp python -c "$1" 2>&1; }
[ "$(py "import urllib.request as u; print(u.urlopen('http://127.0.0.1:8765/health').status)")" = 200 ] && pass "mcp health" || fail "mcp health"
[ "$(py "
import urllib.request as u, urllib.error as e
try: u.urlopen(u.Request('http://127.0.0.1:8765/mcp', b'{}', {'content-type':'application/json'}))
except e.HTTPError as x: print(x.code)")" = 401 ] && pass "Claude's door refuses callers without a login (401)" || fail "Claude's door is not asking for a login"
[ "$(py "
import urllib.request as u
try: print(u.urlopen('http://127.0.0.1:8766/api/status').status)
except Exception as x: print('x')")" = 200 ] && pass "admin API answers inside the container" || fail "admin API"

n=$(py "
import asyncio; from sbmcp import search
d = asyncio.run(search.raw_search('open source')); print(len(d.get('results', [])))")
[ "${n:-0}" -gt 0 ] 2>/dev/null && pass "search works ($n results)" || fail "search returned nothing: $n"

# the wall: a throwaway container on the browser's own network, going out through the filter
out=$(docker run --rm --network "${P}_wall" --entrypoint sh curlimages/curl -c '
P=http://egress:3128
c(){ curl -s -m 10 -o /dev/null -w "%{http_code}" -x $P "$@"; }
echo "pub=$(c https://example.com) mcp=$(c http://mcp:8765/health) meta=$(c http://169.254.169.254/) lo=$(c http://127.0.0.1/) lan=$(c http://192.168.1.1/) direct=$(curl -s -m 6 -o /dev/null -w "%{http_code}" https://example.com --noproxy "*")"' 2>&1 | tail -1)
echo "  info  $out"
case "$out" in *"pub=200"*) pass "wall: public sites open";; *) fail "wall: public site did not open";; esac
case "$out" in *"mcp=403"*"meta=403"*"lo=403"*"lan=403"*) pass "wall: private addresses are refused";; *) fail "wall: a private address was not refused";; esac
case "$out" in *"direct=000"*) pass "wall: no direct internet for the browser network";; *) fail "wall: direct internet works from the browser network";; esac

sb=$(py "
import asyncio
from sbmcp.browser import SHARED
async def m():
    ctx = await SHARED.context(); p = await ctx.new_page(); await p.goto('chrome://sandbox')
    t = await p.inner_text('body'); await p.close(); print('adequately sandboxed' if 'adequately sandboxed' in t else 'NOT SANDBOXED')
asyncio.run(m())")
case "$sb" in *adequately*) pass "Chromium's own sandbox is on";; *) fail "Chromium sandbox: $sb";; esac

dns=$(py "
import socket; print(len(socket.getaddrinfo('example.com', 443)) > 0)")
[ "$dns" = True ] && pass "private DNS answers" || fail "DNS check: $dns"

w=$(py "
import os; ok = all(os.access(p, os.W_OK) for p in ('/files/downloads','/files/uploads','/data')); print(ok)")
[ "$w" = True ] && pass "file folders are writable" || fail "file folders: $w"

[ -n "$FAIL" ] && { echo "Result: SOMETHING FAILED"; exit 1; }
echo "Result: all passed"
