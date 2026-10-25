FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8
RUN apt-get update && apt-get install -y --no-install-recommends unbound ca-certificates dnsutils curl \
    && rm -rf /var/lib/apt/lists/*
# HaGeZi Multi ULTIMATE (domain list, about 250,000 names). Baked in now, refreshed every day by run.sh.
RUN curl -fsSL --retry 5 --max-time 180 -o /etc/unbound/hagezi-domains.txt https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/ultimate-onlydomains.txt \
    && test "$(grep -vc '^#' /etc/unbound/hagezi-domains.txt)" -gt 100000
COPY allow.txt /etc/unbound/allow.txt
RUN mkdir -p /state && chown 1000:1000 /state
COPY run.sh /run.sh
RUN chmod +x /run.sh
EXPOSE 53/udp 53/tcp
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s CMD nslookup example.com 127.0.0.1 >/dev/null 2>&1 || exit 1
CMD ["/run.sh"]
