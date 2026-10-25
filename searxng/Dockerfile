# searxng: your own search engine, with this project's settings baked in. Based on the official SearXNG image.
# No HEALTHCHECK here: the mcp container checks search itself (Self-test). Works on amd64 and arm64.
FROM searxng/searxng:2026.10.19-81371861f@sha256:5ed0323b5f5f8701264ef65e239a2bd83cb57098f2b971fa30bf79c06eeae271
COPY settings.yml /etc/searxng/settings.yml
