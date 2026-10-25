# egress: the wall. Squid is the browser's only way out and refuses private networks and SERVER_PUBLIC_IP.
# Keeps no log. Starts as root to write the block list, then Squid drops to its own user. Works on amd64 and arm64.
FROM ubuntu/squid:6.6-24.04_edge@sha256:8a3baed477e2c282ab8aa5edad442f69873246964f225c5c2ae8364b6610963c
COPY squid.conf /etc/squid/squid.conf
COPY blocked_sites.txt /etc/squid/blocked_sites.txt
COPY blocked_ips.txt /etc/squid/blocked_ips.txt
COPY --chmod=755 start.sh /usr/local/bin/start.sh
HEALTHCHECK --interval=60s --timeout=5s --start-period=30s CMD bash -c "exec 3<>/dev/tcp/127.0.0.1/3128" || exit 1
ENTRYPOINT ["start.sh"]
CMD ["-f", "/etc/squid/squid.conf", "-NYC"]
