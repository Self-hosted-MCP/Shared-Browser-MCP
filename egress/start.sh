#!/bin/sh
# Writes the server's own public address(es) from SERVER_PUBLIC_IP into the block list, then starts Squid as usual.
# The browser can then never reach the server through its public address. 192.0.2.1 is a documentation address
# that keeps the list from being empty.
set -eu
{
  echo "192.0.2.1"
  for ip in $(echo "${SERVER_PUBLIC_IP:-}" | tr ',' ' '); do echo "$ip"; done
} > /etc/squid/blocked_ips.txt
exec entrypoint.sh "$@"
