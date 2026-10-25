# Privacy

For when you want to know exactly what leaves your server, and what is kept.

Nothing is collected by this project. No account with us, no telemetry, no tracking.

## What leaves your server

| Where it goes | When | What it sends |
|---|---|---|
| Public search engines (through your SearXNG) | Each search | Your search words, from your server's address. No account, no cookies. |
| The websites you or the AI open | Each page | What any browser sends. Signed-in sites see your account. |
| `raw.githubusercontent.com` | At start and once a day | A download of the HaGeZi blocklist. Nothing about you. |
| `www.cloudflare.com` and `api.ivpn.net` | When your page shows its security facts | A lookup of your server's own public address and its country. |
| Google PageSpeed | Only when the AI calls `pagespeed_check` | The address being checked. |
| Cloudflare | Every visit to your two addresses | Cloudflare runs the tunnel and Zero Trust, so it sees that traffic. |

## What the AI app sees

Whatever the AI reads for you, it sends to the company that runs your AI app: search results, page text, what it sees on the browser screen, files it reads. Passwords and typed text in the browser are never shown to it.

## What's kept

| What | Kept for |
|---|---|
| Searches and page text | Never kept |
| Browser history | Wiped on every start |
| Action log: what was done and the site name, no text | 7 days by default |
| Downloads and uploads | 3 days by default |
| Sign-ins and cookies in the shared browser | Until you sign out |
| Connected apps, and hashes of their tokens | Until you disconnect them |

## Logs of the program itself

The containers write short logs (Docker keeps up to 30 MB per container). They hold start-up messages and errors. DNS and the wall keep no log of names or addresses. Secrets are never logged.

## Deleting everything

`docker compose -f docker-compose.server.yml down -v` on the server deletes every container and volume: settings, the log, files, sign-ins. Then remove the two addresses and Zero Trust applications in Cloudflare.
