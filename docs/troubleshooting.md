# If something goes wrong

For when something doesn't work. Each problem, what you see, and what to do. Start with **Self-test** on the **Settings** tab: it often names the part that fails.

## Starting it

**`set PUBLIC_URL` (or another setting) when starting.**
A required setting is missing. Fill in `PUBLIC_URL`, `FRONT_URL`, `LOGIN_HASH` and `SEARXNG_SECRET` in `.env`. See [settings.md](settings.md).

**`Pool overlaps with other one on this address space`.**
Another Docker network uses `10.88.250.0/24` or `10.88.251.0/24`. Change them in both compose files, in `egress/squid.conf` (`wall_net`) and the DNS address `10.88.251.53`.

## The browser won't start

The browser container keeps restarting, and its log mentions the sandbox or namespaces. Chromium's own sandbox needs user namespaces, and some servers turn them off.

1. Run `scripts/preflight.sh` and read the user namespace lines.
2. On Ubuntu 24.04 and later, AppArmor can block them: check `kernel.apparmor_restrict_unprivileged_userns`.
3. As a last resort, set `CHROME_NO_SANDBOX=1`. Everything else stays locked down, but you lose one layer. Set it back when you can.

## Your page

**Your page says "Not through Zero Trust."**
The request didn't carry Cloudflare's token. Open the page through its Cloudflare address, check `CF_ACCESS_TEAM_DOMAIN` and `CF_ACCESS_AUD`, and that the AUD tag is from the application for your page.

**Every request is refused, even through Cloudflare.**
`ACCESS_ENFORCE=1` with one of the two Zero Trust settings empty. Fill them in and restart.

## Connecting your AI app

**"A new app can only connect while pairing is open."**
Press **Allow a new app** on **Settings**, then connect within 5 minutes.

**The AI app says it can't reach the server.**
Your Zero Trust policy for the door doesn't let the AI app's servers in. See [setup-own-server.md](setup-own-server.md#7-cloudflare-let-your-ai-app-through).

**The login page says the return address isn't allowed.**
Add your AI app's host to `ALLOWED_REDIRECT_HOSTS`.

**Wrong passphrase, and now logins are refused.**
After many wrong tries, logins pause for 15 minutes. Wait, then try again.

## Search and reading

**Searches return few results, or an engine is missing.**
Some search engines refuse server addresses. The answer says which engines didn't answer. Brave usually works. You can change engines in `searxng/settings.yml` and rebuild that image.

**A page reads as almost empty.**
Some sites only build their page with JavaScript. The AI can open it in the shared browser with `browser_open` instead.

## Still stuck?

Open an issue with the [bug form](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/issues/new?template=bug_report.yml). Paste the Self-test result (the **Copy** button), without secrets.

What next: [questions people ask](faq.md).
