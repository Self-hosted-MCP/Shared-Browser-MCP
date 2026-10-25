# Security policy

Shared-Browser-MCP gives an AI app a real browser on your server, with your own sign-ins in it, plus web search and a page reader. That makes security reports very welcome.

Works with Cloudflare Zero Trust, SearXNG, Chromium and AI apps such as Claude. Not made by or affiliated with any of them. Problems in those products go to their own projects.

## Supported versions

Only the newest release gets security fixes. Updating is the fix. See [docs/updates.md](docs/updates.md).

| Version | Security fixes |
|---|---|
| 0.1.x (the latest release, [see Releases](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/releases/latest)) | Yes |
| Anything older | No, please update |

## Reporting a problem

Please **don't** open a public issue, discussion or pull request for a security problem.

1. Go to the **Security** tab of this repository and click **[Report a vulnerability](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/security/advisories/new)**. Only the maintainer sees it.
2. Tell us what's in the next section.
3. Never send real passwords, keys, tokens or private data. Use test data.

There's no email contact. Use private reporting.

## What to include

- The version (the `health` tool shows it) and how you run it (which server, which compose file, which tunnel).
- Your AI app, if it matters.
- What you found, and which part of the code it's in, if you know.
- The steps to reproduce it.
- What an attacker could do with it, and what they need first.

## What happens next

| When | What |
|---|---|
| Within 3 days | You get a first answer saying the report arrived |
| Within 10 days | We confirm the problem (or explain why it isn't one) and agree on a plan |
| Usually within 30 days | A fixed release is published |
| After the release | The advisory is published, with a CVE when it's useful |

This is a project run in spare time, so a date can slip. If it does, you'll hear why. Please keep the problem private until the fixed release is out, or until 90 days have passed, whichever comes first.

## Credit

If you'd like, you're named in the published advisory and in [CHANGELOG.md](CHANGELOG.md). Tell us the name or GitHub account to use, or say you'd rather stay anonymous. There's no paid bug bounty.

## Testing in good faith

If you follow this policy, we won't take any action against you for your research. Please:

- test only on your own server, or one you have permission to test
- never open, read or change other people's data
- stop and report as soon as you see someone else's data
- don't run denial-of-service tests against someone else's server

## In scope

- Any way for a web page in the shared browser to reach your server's inside: the live view, DevTools, the admin API, another container, a private network or the server's public address.
- Any way to use the owner's page or its admin API without Cloudflare Zero Trust's token while `ACCESS_ENFORCE=1`.
- Any way for an AI app to connect without the passphrase, or while pairing is closed.
- Any way for the AI to type into a password field, or to read one.
- Anything that leaks a token, a passphrase hash, a sign-in from the browser profile, or page text into logs or tool answers where it shouldn't be.
- Any way for a downloaded or uploaded file to run.

## Out of scope

- An AI model following instructions hidden in a web page (prompt injection). That's a known limit of today's AI models. The defences are in [docs/safety.md](docs/safety.md), and improvements are welcome as normal issues.
- An owner who sets `ACCESS_ENFORCE=0` or `CHROME_NO_SANDBOX=1` on a server.
- An owner who approves a harmful action in their AI app.
- Weak passphrases chosen by the owner.
- What's listed under "What it can't protect" in [docs/threat-model.md](docs/threat-model.md).
- Problems in Cloudflare, SearXNG, Chromium, your hosting company or your AI app. Please report those to them.
- Missing security headers or reports from automated scanners without a real attack that works.

## Keeping your own setup safe

- Update when a new release comes out. Chromium is the biggest part to attack, so pull new images at least every week.
- Use a passphrase nobody can guess: 12 characters is the minimum, more is better.
- Keep `ACCESS_ENFORCE=1` and both Zero Trust settings filled in on a server.
- Set `SERVER_PUBLIC_IP`.
- Disconnect AI apps you no longer use: **Settings**, the **Claude** section, **Disconnect** next to the app.
- More in [docs/safety.md](docs/safety.md) and [docs/privacy.md](docs/privacy.md).
