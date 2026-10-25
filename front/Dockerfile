# front: your page (static files) and the routes to the live view and the admin API, served by nginx.
# Runs as nginx's default user setup (see AGENTS.md). Works on amd64 and arm64.
FROM nginx:1.29-alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY html /usr/share/nginx/html
HEALTHCHECK --interval=60s --timeout=5s CMD wget -q -O /dev/null http://127.0.0.1/index.html || exit 1
