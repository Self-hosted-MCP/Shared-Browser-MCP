# Questions people ask

For quick answers before you set it up, or while you use it.

## The basics

<details><summary><b>What is it?</b></summary>

One connector that gives your AI app private web search, a page and PDF reader, and a real Chrome on your server. You can watch that Chrome live and take over at any time.

</details>

<details><summary><b>Who is it for?</b></summary>

One person who wants their AI app to browse the web for them, on a server they own, without a third-party browser service.

</details>

<details><summary><b>Do I need to know how to code?</b></summary>

No. You copy commands from the guides and paste them into a terminal on your server. You also click through the Cloudflare dashboard. The setup guide shows every step and what you should see.

</details>

<details><summary><b>Does it cost anything?</b></summary>

The software is free. You pay for your server. Cloudflare Zero Trust has a free plan, which is enough.

</details>

<details><summary><b>Is it made by Cloudflare, SearXNG, Google or Anthropic?</b></summary>

No. It works with Cloudflare Zero Trust, SearXNG, Chromium and Claude, but it is not made by or affiliated with any of them.

</details>

<details><summary><b>Which languages does it speak?</b></summary>

The pages, the messages and the guides are in English only. Your AI app can still search and read pages in any language: the search tools take a language code like `de` or `pt-PT`.

</details>

## Your data

<details><summary><b>Does it collect anything about me?</b></summary>

No. This project collects nothing. No account, no tracking. What your server sends to search engines and websites is listed in [privacy.md](privacy.md).

</details>

<details><summary><b>Is my search history kept?</b></summary>

No. Searches and page text are never stored. Browser history is wiped on every start. Saved logins (cookies) stay, so you don't have to sign in again.

</details>

<details><summary><b>What does the action log keep?</b></summary>

What the AI did and on which site, by site name only. It never keeps searches, page text or what was typed. It is deleted after 7 days by default, and you can clear it on the **Settings** tab.

</details>

<details><summary><b>How long are downloaded and uploaded files kept?</b></summary>

3 days by default, then they delete themselves. You can change that on the **Settings** tab.

</details>

<details><summary><b>Can I undo what the AI did?</b></summary>

No. What happens on a website (a form sent, a message posted, a booking made) can't be undone by this project. That is why every action that changes something asks you first in your AI app. Read what it asks before you approve.

</details>

## Compatibility

<details><summary><b>Which AI apps work?</b></summary>

Claude is tested: the website, the phone app, the desktop app and Claude Code. Other apps that support remote MCP over HTTP with OAuth may work, but nobody has tested them yet. See [connect-your-ai.md](connect-your-ai.md).

</details>

<details><summary><b>Does it work on my phone?</b></summary>

Yes. Your AI app's phone app uses the same connector. Your page works in a phone browser, with a **Phone** screen size for tapping and typing.

</details>

<details><summary><b>Intel or ARM server?</b></summary>

Both. The images are built for both.

</details>

<details><summary><b>Can I run it without Docker?</b></summary>

No. It is six containers that rely on each other's private networks. See [setup-own-server.md](setup-own-server.md#without-docker).

</details>

## Passwords and logins

<details><summary><b>Can the AI see my passwords?</b></summary>

No. It can't type into password fields, and scripts that mention password fields are refused. When a site needs a login, the AI asks you to take over, and you sign in yourself on your page.

</details>

<details><summary><b>Why do I need Cloudflare Zero Trust?</b></summary>

Your page has no login of its own. Zero Trust is its lock, and the app checks Cloudflare's signed token itself too. A way without Cloudflare is on the [roadmap](roadmap.md).

</details>

<details><summary><b>Can someone else connect their AI app?</b></summary>

Only with your passphrase, and only in the 5 minutes after you press **Allow a new app** on the **Settings** tab.

</details>

<details><summary><b>What if I forget my passphrase?</b></summary>

Make a new hash with `scripts/hash_passphrase.py`, put it in `LOGIN_HASH`, and restart. Your AI apps then log in again.

</details>

<details><summary><b>Can a web page attack my server through the browser?</b></summary>

The browser can't reach private networks, the other containers or your server's own address (when you set `SERVER_PUBLIC_IP`). The limits are in [threat-model.md](threat-model.md).

</details>

## Running it

<details><summary><b>What if the AI does something wrong?</b></summary>

Press **Pause** on your page to stop the browser tools at once. The **Log** tab shows what it did. Then check the site yourself.

</details>

<details><summary><b>How much server does it need?</b></summary>

About 10 GB of disk and 2 to 5 GB of memory while the browser is busy.

</details>

<details><summary><b>How do I check that everything works?</b></summary>

Open your page, go to **Settings** and press **Self-test**. Your AI app can run the same checks with the `self_test` tool.

</details>

<details><summary><b>How do I update?</b></summary>

See [updates.md](updates.md).

</details>

<details><summary><b>How do I remove it?</b></summary>

See [setup-own-server.md](setup-own-server.md#update-stop-or-remove-it).

</details>

<details><summary><b>Where do I report a bug?</b></summary>

In a [bug report](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/issues/new?template=bug_report.yml). Paste the **Self-test** result, and never paste your passphrase or keys.

</details>

<details><summary><b>Where do I report a security problem?</b></summary>

Privately, in a [private report](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/security/advisories/new). Never in a public issue. See [SECURITY.md](../SECURITY.md).

</details>

## Still have a question?

Ask in a [question issue](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/issues/new?template=question.yml).

What next: [set it up on your server](setup-own-server.md).
