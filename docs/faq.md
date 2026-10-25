# Questions people ask

For quick answers before you set it up, or while you use it.

## The basics

**What is it?**
One connector that gives your AI app private web search, a page and PDF reader, and a real Chrome on your server that you can watch and take over.

**Who is it for?**
One person who wants their AI app to browse the web for them, on a server they own, without a third-party browser service.

**Does it cost anything?**
The software is free. You pay for your server. Cloudflare Zero Trust has a free plan.

**Does it collect anything about me?**
No. Nothing is collected by this project. No account, no tracking. What your server sends to search engines and websites is in [privacy.md](privacy.md).

**Which AI apps work?**
Claude (website, phone, desktop and Claude Code) is tested. Other apps that support remote MCP over HTTP with OAuth should work. See [connect-your-ai.md](connect-your-ai.md).

## Your data and safety

**Can the AI see my passwords?**
No. It can't type into password fields or read them. Logins come to you.

**What if the AI does something wrong?**
Actions that change something ask you first in your AI app. Press **Pause** on your page to stop the browser tools at once. The **Log** tab shows what it did.

**Can a web page attack my server through the browser?**
The browser can't reach private networks, the other containers or your server's own address. See [threat-model.md](threat-model.md).

**Is my search history kept?**
No. Searches and page text are never stored. Browser history is wiped on every start.

**Who can open my page?**
Only who your Cloudflare Zero Trust policy allows. The app checks Cloudflare's signed token itself too.

**Can someone else connect their AI app?**
Only with your passphrase, and only while you have pressed **Allow a new app**.

## Running it

**Why do I need Cloudflare Zero Trust?**
Your page has no login of its own. Zero Trust is its lock. A way without Cloudflare is on the [roadmap](roadmap.md).

**Does it work on my phone?**
Yes. Your AI app's phone app uses the same connector, and your page works in a phone browser, with a **Phone** screen size for tapping and typing.

**Intel or ARM server?**
Both. The images are built for both.

**How much server does it need?**
About 10 GB of disk and 2 to 5 GB of memory while the browser is busy.

**How do I update?**
See [updates.md](updates.md).

**How do I remove it?**
See [setup-own-server.md](setup-own-server.md#update-stop-or-remove-it).

## Still have a question?

Ask in a [question issue](https://github.com/Self-hosted-MCP/Shared-Browser-MCP/issues/new?template=question.yml).
