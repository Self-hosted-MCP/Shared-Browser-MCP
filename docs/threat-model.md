# Threat model

For when you want the exact limits: what Shared-Browser-MCP protects, and what it can't.

## What it protects

- **Your server's inside, from web pages.** The browser has no direct internet and no route to the other containers. The wall refuses private networks, the cloud metadata address and your server's public address (`SERVER_PUBLIC_IP`). The live view and DevTools ports are not reachable from inside the browser.
- **Your page, from strangers.** With `ACCESS_ENFORCE=1`, every page and admin request needs Cloudflare Zero Trust's signed token for your application. If the settings are missing, everything is refused.
- **The door, from strangers.** OAuth with your passphrase (stored only as a PBKDF2 hash), new apps only while pairing is open, a lockout after many wrong tries, and login returns only to allowed hosts.
- **Your passwords, from the AI.** No typing into password fields, no scripts that read them, password values never shown to the AI.
- **Your server, from downloaded files.** Files are stored and read, never run, and programs are refused.

## What it can't protect

- **An action you approved.** If you approve a click or a form, it happens.
- **Sites you are signed in to.** The AI acts with your account there. Sign in only where you need to.
- **Prompt injection.** The AI can still be misled by a page. The defences reduce the harm (data marking, approvals, Pause), they don't remove the risk.
- **Your AI app's company.** It sees everything the AI reads for you.
- **Cloudflare.** It runs the tunnel and the lock, and sees that traffic.
- **A server you don't control.** Whoever runs the server can read the volumes, including your sign-ins.
- **Settings you turn off.** `ACCESS_ENFORCE=0` or `CHROME_NO_SANDBOX=1` on a server removes a lock.
- **Old images.** Chromium bugs are found often. An image you never update stays open to them.

## Not audited yet

No outside security audit has been done. The checks are the project's own: the Self-test, `scripts/smoke-test.sh`, and GitHub's code scanning (CodeQL) once published. Reports are welcome, see [SECURITY.md](../SECURITY.md).

What next: [if something goes wrong](troubleshooting.md).
