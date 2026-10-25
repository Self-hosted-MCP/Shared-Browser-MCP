# Connect your AI app

For when Shared-Browser-MCP runs on your server and you want your AI app to use it. You end with the 25 tools in your AI app, on your computer and your phone.

Your server's door is `PUBLIC_URL` plus `/mcp`, like `https://mcp.example.com/mcp`. It speaks MCP over HTTP (streamable HTTP) with an OAuth login, where you type your passphrase.

## Before you start

A new AI app can only connect while you allow it, even with the right passphrase. This stops a stranger's AI app from asking you to type your passphrase for their connection.

1. Open your page and go to **Settings**.
2. In the **Claude** section, press **Allow a new app**. It stays open for 5 minutes.
3. Connect your app as below, and log in with your passphrase on the page that opens.

Apps that are already connected are not affected when the window closes.

> [!TIP]
> In your AI app's tool settings, keep the browser actions (`browser_act`, `browser_batch`, `browser_js`, `download_delete`, `browser_upload`) on "needs approval".

## Claude website and phone app

1. On claude.ai, open **Settings**, **Connectors**, and add a custom connector.
2. Paste `https://mcp.example.com/mcp` as the address.
3. Press **Connect** and log in with your passphrase.

The Claude phone app then shows the connector too. Your AI app's servers must be able to reach the door: see [setup-own-server.md](setup-own-server.md#7-cloudflare-let-your-ai-app-through).

Tested with Claude in October 2026.

## Claude Desktop

Claude Desktop uses the same connectors as the website. Add it on claude.ai or in **Settings**, **Connectors** in the app.

## Claude Code

```bash
claude mcp add --transport http shared-browser https://mcp.example.com/mcp
```

Then type `/mcp` in Claude Code and pick `shared-browser` to log in. Claude Code runs on your computer, not on Anthropic's servers, so your Zero Trust policy for the door must let your own address in.

Tested in October 2026.

## Other MCP apps

Any app that supports remote MCP servers over HTTP with OAuth can work. Add the app's login return host to `ALLOWED_REDIRECT_HOSTS` (see [settings.md](settings.md#addresses)), and let its servers through your Zero Trust policy for the door.

Not tested yet: ChatGPT, Codex, Cursor, VS Code, Gemini CLI. Reports are welcome in an issue.

## Check it works

Ask your AI app: *Search the web for today's weather in Paris.* It should call `web_search` and answer with sources. Then: *Open example.com in the shared browser.* Your page's **Browser** tab should show the page.

## Disconnect an app

On **Settings**, in the **Claude** section, press **Disconnect** next to the app. Its tokens stop working at once.
