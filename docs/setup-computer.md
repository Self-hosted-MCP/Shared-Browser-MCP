# Try it on your computer

For when you want to see it working before you set up a server. You end with the whole stack on your own computer, with your page at `http://localhost:8081`. About 20 minutes, most of it waiting for the images to build.

> [!NOTE]
> This is for trying it. Your page has no lock here (`ACCESS_ENFORCE` is `0`), and AI apps on the internet, like Claude on the website, can't reach `localhost`. For real use, see [setup-own-server.md](setup-own-server.md).

## Before you start

- [Docker Desktop](https://docs.docker.com/get-docker/) or another Docker with Compose, with about 6 GB of memory for Docker.
- About 10 GB of free disk.
- Python 3, to make your passphrase hash.

## 1. Get the code

```bash
git clone https://github.com/Self-hosted-MCP/Shared-Browser-MCP.git && cd Shared-Browser-MCP
```

## 2. Make your settings

Make the passphrase hash. It asks for a passphrase twice and prints `LOGIN_HASH=...`:

```bash
python3 scripts/hash_passphrase.py
```

Copy the example settings into `.env.local`:

```bash
cp .env.example .env.local
```

Open `.env.local` and set:

| Setting | Value on your computer |
|---|---|
| `PUBLIC_URL` | `http://localhost:8765` |
| `FRONT_URL` | `http://localhost:8081` |
| `LOGIN_HASH` | The hash from above |
| `SEARXNG_SECRET` | Any long random text |

Leave the Cloudflare settings empty.

## 3. Build and start it

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml --env-file .env.local up -d --build
```

The first build takes 10 to 20 minutes. Chromium is the big one. You should see six containers with `Started`.

## 4. Open your page

Open `http://localhost:8081` in your browser. You should see four tabs: **Browser**, **Log**, **Files** and **Settings**. The **Browser** tab shows the shared Chromium live.

## 5. Check it works

```bash
scripts/smoke-test.sh shared-browser
```

You should see only `PASS` lines. Or press **Self-test** on the **Settings** tab. The Zero Trust check shows as off, which is expected here.

## 6. Connect an AI app on the same computer

Claude Code on the same computer can reach `localhost`. Press **Allow a new app** on the **Settings** tab, then:

```bash
claude mcp add --transport http shared-browser http://localhost:8765/mcp
```

Log in with your passphrase when your browser opens the login page.

## Stop or remove it

Stop it:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml stop
```

Remove it, with all its data:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml down -v
```

## What we tested

- The stack this release comes from was built and tested on a Mac with Docker, including a real Claude Code login, in October 2026.
- This public release (0.1.0) has not been run on a computer yet. Its compose files are checked by GitHub Actions on every change.
