# Updates

For when you want the newest fixes. Chromium gets security fixes often, so update at least every week.

## Know when there's an update

On GitHub, press **Watch**, **Custom**, **Releases**. You get a message for each release. The images tagged `latest` change with every change to `main`.

## Update by hand

In the project folder on your server, get the newest files:

```bash
git pull
```

Pull the newest images and restart:

```bash
docker compose -f docker-compose.server.yml pull && docker compose -f docker-compose.server.yml up -d
```

Then press **Self-test** on **Settings**. Everything should pass.

## Update every week by itself (optional)

Add a weekly job on the server, for example with `crontab -e`:

```bash
0 4 * * 1 cd /path/to/Shared-Browser-MCP && docker compose -f docker-compose.server.yml pull -q && docker compose -f docker-compose.server.yml up -d
```

This runs on Mondays at 04:00. Change `/path/to/` to your folder.

## Staying on one version

Each release has its own image tag, like `0.1.0`. Replace `:latest` with that tag in `docker-compose.server.yml`.

## Going back

Use the version tag of the release you want, as above, then `docker compose -f docker-compose.server.yml up -d`.

## What an update never touches

Your volumes: settings, connected apps, the action log, your files and your sign-ins in the shared browser. Your `.env` stays as it is.
