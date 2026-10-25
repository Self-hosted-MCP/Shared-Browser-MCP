FROM ubuntu/squid:6.6-24.04_edge@sha256:8a3baed477e2c282ab8aa5edad442f69873246964f225c5c2ae8364b6610963c
COPY squid.conf /etc/squid/squid.conf
COPY blocked_sites.txt /etc/squid/blocked_sites.txt
COPY blocked_ips.txt /etc/squid/blocked_ips.txt
COPY --chmod=755 start.sh /usr/local/bin/start.sh
ENTRYPOINT ["start.sh"]
CMD ["-f", "/etc/squid/squid.conf", "-NYC"]
