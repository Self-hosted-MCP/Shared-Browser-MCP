#!/bin/bash
# Run on the SERVER before the first deploy. Changes nothing. Prints OK / WARN / FAIL lines.
ok()   { printf "  OK    %s\n" "$1"; }
warn() { printf "  WARN  %s\n" "$1"; WARN=1; }
fail() { printf "  FAIL  %s\n" "$1"; FAIL=1; }
echo "Shared Browser preflight"

command -v docker >/dev/null && ok "docker found" || fail "docker not found"
docker compose version >/dev/null 2>&1 && ok "docker compose found" || fail "docker compose plugin not found"
echo "  info  architecture: $(uname -m)"

free_gb=$(df -BG --output=avail "$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo /)" 2>/dev/null | tail -1 | tr -dc '0-9')
[ "${free_gb:-0}" -ge 10 ] && ok "free disk: ${free_gb} GB" || fail "free disk ${free_gb:-?} GB, want 10 GB or more (grow the disk first)"
mem_gb=$(free -g | awk '/Mem:/ {print $7}')
[ "${mem_gb:-0}" -ge 4 ] && ok "free memory: ${mem_gb} GB" || warn "free memory ${mem_gb:-?} GB, the stack uses 2 to 5 GB"

used=$(docker network ls -q | xargs -r docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}' 2>/dev/null)
for net in 10.88.250.0/24 10.88.251.0/24; do
  if echo "$used" | grep -qw "$net" || ip route 2>/dev/null | grep -q "${net%/*}"; then
    fail "network $net is already in use: change the subnets in docker-compose.yml, egress/squid.conf (wall_net) and dns (10.88.251.53)"
  else ok "network $net is free"; fi
done

[ -f browser/seccomp.json ] && ok "browser/seccomp.json present" || fail "browser/seccomp.json missing: run this from the project folder"

# Chromium's own sandbox needs user namespaces
ns=$(sysctl -n user.max_user_namespaces 2>/dev/null)
[ "${ns:-0}" -gt 0 ] && ok "user namespaces allowed (max $ns)" || warn "user namespaces look disabled: Chromium's sandbox will fail"
v=$(sysctl -n kernel.unprivileged_userns_clone 2>/dev/null); [ "$v" = "0" ] && warn "kernel.unprivileged_userns_clone=0: sandbox will fail"
v=$(sysctl -n kernel.apparmor_restrict_unprivileged_userns 2>/dev/null)
[ "$v" = "1" ] && warn "AppArmor restricts user namespaces (Ubuntu 24.04 default). If Chromium fails to start, set CHROME_NO_SANDBOX=1 or allow it for the container"

[ -n "$FAIL" ] && { echo "Result: FIX THE FAIL LINES FIRST"; exit 1; }
[ -n "$WARN" ] && { echo "Result: OK with warnings"; exit 0; }
echo "Result: all clear"
