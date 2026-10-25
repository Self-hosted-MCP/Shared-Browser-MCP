# front: your page (static files) and the routes to the live view and the admin API, served by nginx.
# Runs as nginx's default user setup (see AGENTS.md). Works on amd64 and arm64.
FROM nginx:1.28-alpine@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY html /usr/share/nginx/html
HEALTHCHECK --interval=60s --timeout=5s CMD wget -q -O /dev/null http://127.0.0.1/index.html || exit 1
