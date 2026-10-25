# Every setting

For when you set it up or want to change how it behaves. Every setting, its default, and what it does.

## Where settings come from

Settings come from environment variables, set before the stack starts. Put them in a `.env` file next to the compose file, or in your server panel's environment settings. [`.env.example`](../.env.example) lists all of them, with no real values.

A few choices live on your own page instead, under **Settings**: how long to keep the action log and files, and the browser's light or dark look. Those are saved in the `mcp-data` volume and survive restarts.

> [!IMPORTANT]
> Never commit a real `.env`. It holds your login hash and other secrets. `.gitignore` already keeps it out of git.

## Addresses

| Setting | Default | What it does |
|---|---|---|
| `PUBLIC_URL` | none, required | The AI app's door, like `https://mcp.example.com`. Your AI app connects to `PUBLIC_URL/mcp`. Public, with the passphrase login. |
| `FRONT_URL` | none, required | Your own page, like `https://browser.example.com`. Must sit behind Cloudflare Zero Trust. |
| `ALLOWED_REDIRECT_HOSTS` | `claude.ai,claude.com` | The AI apps allowed to finish a login, as host names, comma separated. Add your app's host if it is not Claude. |

## Secrets

| Setting | Default | What it does |
|---|---|---|
| `LOGIN_HASH` | none, required | Your passphrase, as a hash. Make it with `python3 scripts/hash_passphrase.py` on your own computer. The passphrase itself is never stored. |
| `SEARXNG_SECRET` | none, required | Any long random text for the search engine. Make one with `openssl rand -hex 32`. |

## The lock on your page

| Setting | Default | What it does |
|---|---|---|
| `CF_ACCESS_TEAM_DOMAIN` | none | Your Cloudflare Zero Trust team domain, like `yourteam.cloudflareaccess.com`. |
| `CF_ACCESS_AUD` | none | The **Application Audience (AUD) Tag** of the Zero Trust app that protects `FRONT_URL`. |
| `ACCESS_ENFORCE` | `1` | `1` means your page and its admin API refuse every request without Cloudflare's signed token. If the two settings above are empty, everything is refused. Only `docker-compose.local.yml` sets it to `0`, for trying it on your computer. |

> [!WARNING]
> Your page has no login of its own. On a server, keep `ACCESS_ENFORCE=1` and fill in both Zero Trust settings. See [setup-own-server.md](setup-own-server.md).

## Optional

| Setting | Default | What it does |
|---|---|---|
| `SERVER_PUBLIC_IP` | empty | Your server's public address, or several, comma separated. The browser's filter then refuses them, so a web page can't reach your server through its own address. Recommended. |
| `PAGESPEED_API_KEY` | empty | A free Google Cloud key for the `pagespeed_check` tool. Without it, Google's shared limit applies and checks may fail. |
| `CHROME_NO_SANDBOX` | `0` | `1` turns off Chromium's own sandbox. Only for servers that refuse it. See [troubleshooting.md](troubleshooting.md#the-browser-wont-start). |
| `TZ` | `UTC` | The clock for the browser and the action log, like `Europe/Berlin`. Websites see this time zone. |

## Advanced

The MCP server also reads these. The compose files don't pass them, so add them under `mcp:` and `environment:` in your compose file if you need them.

| Setting | Default | What it does |
|---|---|---|
| `DEFAULT_LANGUAGE` | `en` | Search language when the AI doesn't pick one. |
| `MAX_RESULTS` | `8` | Results per search. |
| `READ_MAX_CHARS` | `12000` | Characters per piece when reading a page. |
| `FETCH_MAX_BYTES` | `8000000` | Biggest page or PDF the reader downloads. |
| `MAX_TABS` | `8` | Most tabs open in the shared browser. |
| `FILES_MAX_MB` | `50` | Biggest file for downloads and uploads. |
| `BLOCKED_SITES` | empty | Site names the page reader refuses, comma separated. |

## Files in the volumes

| Volume | What's in it |
|---|---|
| `mcp-data` | `settings.json`, the action log, connected apps and their token hashes |
| `browser-profile` | Chromium's profile: your sign-ins and cookies in the shared browser |
| `work` | The browser's working folder (your uploads are mounted inside it) |
| `downloads`, `uploads` | Files the browser downloaded, and files you dropped for the AI |
| `ctl` | A tiny file the browser container reads: the theme |

What next: [check it works](setup-own-server.md#8-check-it-works).
