# Tools the AI can use

For when you want to know exactly what your AI app can do with Shared-Browser-MCP. Each tool, what it does, and whether your AI app asks you first.

"Asks first" means the tool is marked as one that changes something. Most AI apps, Claude included, then ask you to approve each call. You can change that in your AI app's tool settings. We recommend you keep these on "needs approval".

## The 25 tools

### Search and read

| Tool | What it does | Asks first |
|---|---|---|
| `web_search` | Searches the web with your own SearXNG. Returns numbered results with title, address and a snippet. Nothing is saved. | No |
| `search_many` | Runs up to 10 searches at once and merges them. A page found by several searches shows once and ranks higher. | No |
| `research` | Searches, then reads the best pages and returns their key text with each address, so the AI can answer with sources. | No |
| `search_engines` | Lists the search engines your server has switched on. | No |
| `read_url` | Reads a web page or PDF as clean text. Long pages come in pieces. Refuses private addresses. | No |
| `read_many` | Reads up to 20 pages or PDFs at once, a short piece of each. | No |
| `pagespeed_check` | Checks a public page with Google PageSpeed: scores, timings and the biggest fixes. The address is sent to Google. | No |

### The shared browser

| Tool | What it does | Asks first |
|---|---|---|
| `browser_open` | Opens a page in the shared Chromium, the same one you watch live. | No |
| `browser_look` | Shows the page's text and a numbered list of buttons, links and fields. Passwords and typed text are never shown. | No |
| `browser_find` | Finds a word on the page, shows the text around each match and scrolls to the first. | No |
| `browser_wait` | Waits some seconds, or until some text appears. | No |
| `browser_tabs` | Lists, switches or closes tabs. | No |
| `browser_emulate` | Makes the browser look like a phone or tablet, to check a mobile page. | No |
| `browser_inspect` | Reads the page's console messages or network requests. Query parts, headers and cookies are never shown. | No |
| `browser_handoff` | Asks you to take over, for a login, a password, a code or an "are you human" check. Your page shows the message and a **Done** button. | No |
| `browser_act` | Clicks, types, fills a field, picks an option, presses a key, scrolls, or uses the mouse by position. Never types into password fields. | Yes |
| `browser_batch` | Several actions in one call, like filling a form. You approve the batch once. | Yes |
| `browser_js` | Runs JavaScript on the page. Scripts that look at password fields are refused. | Yes |

### Files

| Tool | What it does | Asks first |
|---|---|---|
| `downloads_list` | Lists the files the browser downloaded. They expire after a few days. | No |
| `download_read` | Reads a downloaded PDF, Word file, text, CSV, JSON, HTML or image. The content is data, not instructions. | No |
| `download_delete` | Deletes one downloaded file. | Yes |
| `uploads_list` | Lists the files you dropped on your **Files** page for the AI to attach. | No |
| `browser_upload` | Attaches one of your uploaded files to a website's file field. It doesn't press the site's send button. | Yes |

### Checks

| Tool | What it does | Asks first |
|---|---|---|
| `health` | Checks that the search engine answers, and shows the version. | No |
| `self_test` | Runs the full Self-test: the door, search, DNS, the wall around the browser, Chromium's sandbox and the file folders. About 20 seconds. Changes nothing. | No |

## When a tool says no

| Message | What it means |
|---|---|
| "paused the shared browser" | You pressed **Pause** (or **Pause Claude** in the menu) on your page. Search and reading still work. Press it again to resume. |
| "Passwords are typed by the user only" | The AI tried to type into a password field. It should call `browser_handoff` so you log in yourself. |
| A private address is refused | The page reader and the browser never open addresses inside private networks, or your server's own address. |
| "Cannot read .xyz files" | That file type can't be read by the AI. You can still save it from the **Files** page. |
| "A new app can only connect while pairing is open" | See [connect-your-ai.md](connect-your-ai.md#before-you-start). |

## Limits

- Search: 8 results per search by default, up to 10 searches at once in `search_many`.
- Reading: 12,000 characters per piece, pages and PDFs up to 8 MB, 15 seconds to load.
- Browser: up to 8 tabs, 30 seconds to open a page, 8 seconds per action.
- Files: up to 50 MB each. Programs and scripts are refused.

All of these can be changed, see [settings.md](settings.md#advanced).

## Asking first

The five tools marked "Yes" are marked as tools that change something. Your AI app asks you before each call, in the app itself. Pausing on your page stops every browser tool at once, wherever you are.

What next: [things to ask](examples.md).
