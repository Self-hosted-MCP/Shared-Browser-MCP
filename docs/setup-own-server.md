# Setup on your own server

For when you want Shared-Browser-MCP running for real, reachable by your AI app from your computer and your phone. You end with two addresses: your own page, locked to you, and a door for your AI app with a passphrase login. About 45 minutes, half of it in the Cloudflare dashboard.

<details>
<summary><b>Table of contents</b></summary>

- [What you need](#what-you-need)
- [1. Check the server](#1-check-the-server)
- [2. Make your passphrase hash](#2-make-your-passphrase-hash)
- [3. Fill in the settings](#3-fill-in-the-settings)
- [4. Start it](#4-start-it)
- [5. Cloudflare: the tunnel and two addresses](#5-cloudflare-the-tunnel-and-two-addresses)
- [6. Cloudflare: lock your page](#6-cloudflare-lock-your-page)
- [7. Cloudflare: let your AI app through](#7-cloudflare-let-your-ai-app-through)
- [8. Check it works](#8-check-it-works)
- [9. Connect your AI app](#9-connect-your-ai-app)
- [Using a server panel such as Coolify](#using-a-server-panel-such-as-coolify)
- [Backups](#backups)
- [Update, stop or remove it](#update-stop-or-remove-it)
- [What we tested](#what-we-tested)

</details>

## What you need

| You need | Why |
|---|---|
| A Linux server with Docker and Docker Compose, 10 GB free disk, 4 GB free memory | The six containers. Intel/AMD and ARM both work. |
| A domain on Cloudflare | For the two addresses. |
| A free Cloudflare Zero Trust account | It is the only lock on your own page. **Required.** |
| A shell on the server (SSH) | To run the commands below. Server panels work too, see [Using a server panel such as Coolify](#using-a-server-panel-such-as-coolify). |

> [!WARNING]
> Your own page (the live browser, the log, your files and the settings) has **no login of its own**. Cloudflare Zero Trust is the lock, and the app checks Cloudflare's signed token on every request as a second lock. Never publish the page without it.

Why a tunnel: with a Cloudflare tunnel, your server needs no open web ports. Both addresses only reach it through Cloudflare.

## 1. Check the server

Get the code onto the server:

```bash
git clone https://github.com/Self-hosted-MCP/Shared-Browser-MCP.git && cd Shared-Browser-MCP
```

Run the check. It changes nothing:

```bash
scripts/preflight.sh
```

You should see `OK` lines for Docker, free disk, the two networks and user namespaces. A `FAIL` tells you what to fix:

- **A network is in use:** the stack uses `10.88.250.0/24` and `10.88.251.0/24`. Change them in both compose files, in `egress/squid.conf` (`wall_net`) and the DNS address `10.88.251.53`.
- **User namespaces look disabled:** Chromium's own sandbox needs them. See [troubleshooting.md](troubleshooting.md#the-browser-wont-start).

## 2. Make your passphrase hash

Do this **on your own computer**, not on the server. It asks for your passphrase twice, then prints one line:

```bash
python3 scripts/hash_passphrase.py
```

You should see `LOGIN_HASH=pbkdf2:600000:...`. Copy that line. Keep the passphrase itself in your password manager. It is never stored anywhere, only its hash.

## 3. Fill in the settings

On the server, copy the example and open it:

```bash
cp .env.example .env && nano .env
```

Fill in at least these. Every setting is explained in [settings.md](settings.md).

| Setting | What to put |
|---|---|
| `PUBLIC_URL` | The AI app's door, like `https://mcp.example.com` |
| `FRONT_URL` | Your page, like `https://browser.example.com` |
| `LOGIN_HASH` | The line from step 2, without `LOGIN_HASH=` |
| `SEARXNG_SECRET` | The result of `openssl rand -hex 32` |
| `SERVER_PUBLIC_IP` | Your server's public address (recommended) |

Leave `CF_ACCESS_TEAM_DOMAIN` and `CF_ACCESS_AUD` empty for now. You fill them in step 6.

## 4. Start it

```bash
docker compose -f docker-compose.server.yml up -d
```

This pulls the six ready-made images from `ghcr.io/self-hosted-mcp`. The first start takes a few minutes. You should see six containers with `Started`. Check them:

```bash
docker compose -f docker-compose.server.yml ps
```

All six should say `running` (the browser and mcp may say `healthy` after a minute). The page listens on `127.0.0.1:8081` and the door on `127.0.0.1:8765`, on the server only. Nothing is open to the internet yet.

## 5. Cloudflare: the tunnel and two addresses

1. In the Cloudflare dashboard, open **Zero Trust**, then **Networks**, **Tunnels**, and create a tunnel. Install the connector on your server with the command Cloudflare shows.
2. Add two **Public Hostnames** (also called published applications) to the tunnel:

| Address | Service |
|---|---|
| The host from `FRONT_URL`, like `browser.example.com` | `http://localhost:8081` |
| The host from `PUBLIC_URL`, like `mcp.example.com` | `http://localhost:8765` |

> [!CAUTION]
> Never add an address for port `8766`. That is the admin API, and it is only reached through your page.

## 6. Cloudflare: lock your page

1. In **Zero Trust**, **Access**, **Applications**, add a **Self-hosted** application for your page's address (`browser.example.com`).
2. Give it a policy that allows only you, for example your own email address.
3. Open the application's **Overview** and copy the **Application Audience (AUD) Tag**.
4. Put it in `.env` as `CF_ACCESS_AUD`, and your team domain (like `yourteam.cloudflareaccess.com`) as `CF_ACCESS_TEAM_DOMAIN`. Keep `ACCESS_ENFORCE=1`.
5. Restart so the settings apply:

```bash
docker compose -f docker-compose.server.yml up -d
```

Now open your page's address in a browser. Cloudflare asks you to sign in, then your page opens with four tabs: **Browser**, **Log**, **Files** and **Settings**. If you reach the page's address another way, without Cloudflare's token, the app refuses it.

## 7. Cloudflare: let your AI app through

The door (`mcp.example.com`) is reached by your AI app's servers, not by you. It has its own lock: the passphrase login, and new apps can only connect while you allow it.

1. Add a second **Self-hosted** application for the door's address.
2. Give it a policy that lets your AI app's servers in. For Claude, a **Bypass** policy for Anthropic's address range `160.79.104.0/21` works. Check your AI app's documentation for its range.
3. If you use Claude Code on your own computer, that is not Anthropic's servers: add your own address too, or test through the policy that allows you.

## 8. Check it works

On your page, open **Settings** and press **Self-test**. It runs about 12 checks from inside the stack: the door, search, DNS, the wall around the browser, Chromium's sandbox and the file folders. All should pass.

With a shell on the server you can also run the longer check:

```bash
scripts/smoke-test.sh shared-browser
```

You should see only `PASS` lines. If a search engine fails, that is common: Google, DuckDuckGo and Wikipedia sometimes refuse server addresses. Brave usually works.

## 9. Connect your AI app

Follow [connect-your-ai.md](connect-your-ai.md). In short: press **Allow a new app** on the **Settings** tab, add `https://mcp.example.com/mcp` in your AI app, and type your passphrase on the login page.

## Using a server panel such as Coolify

Panels that run a Docker Compose file work. Use `docker-compose.server.yml` as a **raw** compose deployment and turn off the panel's own proxy and domains for it: the stack needs its own sealed network, which a panel's shared proxy network would break. Put the settings in the panel's environment settings (in Coolify, switch **Is Literal** on for secrets). The file `browser/seccomp.json` is read from the repository folder, so the panel must keep the repository on the server.

## Behind your own reverse proxy

If you already run a reverse proxy (Caddy, nginx, Traefik) with HTTPS, you can point the door's address at `http://127.0.0.1:8765` with it instead of using a Cloudflare tunnel for that address. Your page is different: it still has to go through Cloudflare Zero Trust, because the app checks Cloudflare's signed token on every page and admin call and refuses everything else. Never point any address at port `8766`.

## Without Docker

Not supported. The stack is six programs (search, DNS, the wall, the browser, your page and the door) that depend on Docker's private networks to keep the browser away from your server. Running them by hand would remove that wall.

## Backups

The volumes that matter are `mcp-data` (settings, connected apps, action log) and `browser-profile` (your sign-ins in the shared browser). Everything else can be rebuilt. Your secrets are in `.env`: keep a copy in your password manager.

## Update, stop or remove it

- **Update:** see [updates.md](updates.md). Chromium is the biggest part to attack, so pull new images at least every week.
- **Stop:** `docker compose -f docker-compose.server.yml stop`. Pressing **Pause** on your page stops the AI using the browser without stopping anything.
- **Remove:** `docker compose -f docker-compose.server.yml down -v` deletes the containers **and all volumes**, including your sign-ins. Then delete the tunnel addresses and the two Zero Trust applications in Cloudflare.

## What we tested

- The stack this release comes from ran on an ARM server (Ubuntu, Docker Compose through a server panel) behind a Cloudflare tunnel and Zero Trust, with Claude on the website, the phone app and Claude Code, in October 2026. Its Self-test passed every check.
- This public release (0.1.0) was built from scratch and started on a fresh Ubuntu 24.04 machine (Intel/AMD, GitHub Actions) on 25 October 2026, without Cloudflare (`ACCESS_ENFORCE=0`). All 16 checks in `scripts/smoke-test.sh` passed, and the images were built for Intel/AMD and ARM.
- Not tested with this release: a full server setup behind Cloudflare, other AI apps than Claude.

What next: [connect your AI app](connect-your-ai.md).
