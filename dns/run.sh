#!/bin/sh
# Our own DNS for the whole stack: it blocks the HaGeZi list and forwards everything else to the machine's own DNS.
# Nothing is logged: no query, no answer.
LIST=/etc/unbound/hagezi-domains.txt
ALLOW=/etc/unbound/allow.txt
BLOCK_CONF=/etc/unbound/hagezi.conf
LIST_URL=https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/ultimate-onlydomains.txt
CONF=/etc/unbound/unbound.conf

# Turns the domain list into unbound rules. A blocked name (and everything under it) answers "does not exist".
# Domains in allow.txt are let through again.
build_block() {
  awk -v allow="$ALLOW" 'BEGIN { while ((getline l < allow) > 0) { sub(/#.*/, "", l); gsub(/[ \t\r]/, "", l); if (l != "") a[l] = 1 } }
    /^#/ || NF == 0 { next }
    { d = tolower($1); if (!(d in a)) print "local-zone: \"" d ".\" always_nxdomain" }
    END { for (d in a) print "local-zone: \"" d ".\" transparent" }' "$LIST" > "$BLOCK_CONF.new" && mv "$BLOCK_CONF.new" "$BLOCK_CONF"
}

render() {
  cat > "$CONF" <<EOT
server:
  interface: 0.0.0.0
  access-control: 172.16.0.0/12 allow
  access-control: 10.88.0.0/16 allow
  access-control: 127.0.0.0/8 allow
  do-ip6: no
  verbosity: 0
  log-queries: no
  log-replies: no
  use-syslog: no
  hide-identity: yes
  hide-version: yes
  do-not-query-localhost: no   # it asks Docker's own resolver at 127.0.0.11
  tls-cert-bundle: /etc/ssl/certs/ca-certificates.crt
  cache-min-ttl: 30
  include: $BLOCK_CONF
forward-zone:
  name: "."
EOT
  printf '  forward-tls-upstream: no\n  forward-addr: 127.0.0.11\n' >> "$CONF"
}

build_block
render
echo "dns ready, blocklist: $(grep -c always_nxdomain "$BLOCK_CONF") names"
unbound -d -c "$CONF" &
pid=$!
next_refresh=$(( $(date +%s) + 86400 ))
while kill -0 "$pid" 2>/dev/null; do
  sleep 2
  # once a day: fetch the newest list; keep the old one if the download looks wrong
  if [ "$(date +%s)" -ge "$next_refresh" ]; then
    next_refresh=$(( $(date +%s) + 86400 ))
    if curl -fsS --max-time 180 -o /tmp/hagezi.new "$LIST_URL" && [ "$(grep -vc '^#' /tmp/hagezi.new)" -gt 100000 ]; then
      mv /tmp/hagezi.new "$LIST" && build_block && kill -HUP "$pid" && echo "blocklist refreshed: $(grep -c always_nxdomain "$BLOCK_CONF") names"
    else
      echo "blocklist refresh failed, keeping the old list"
    fi
  fi
done
