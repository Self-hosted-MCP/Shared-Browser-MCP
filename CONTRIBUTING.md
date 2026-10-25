# Contributing

Thanks for wanting to help. Shared-Browser-MCP is free and open source under the [Apache-2.0](LICENSE) license. Bug reports, fixes, translations and clearer docs are all welcome. Small, focused changes are the easiest to review.

## Reporting a problem

Click **New issue** on GitHub and pick a form:

| Form | Use it when |
|---|---|
| **Something doesn't work** | You hit a bug or an error message |
| **Question or idea** | You want to know how to do something, or have an idea |
| **Idea or feature** | You want something new or different |
| **Report a security problem, privately** | Someone could misuse the project or reach private data. Only the maintainer sees it. See [SECURITY.md](SECURITY.md) |

Each form asks for what's needed to help you, such as how you run it and which AI app you use.

**Leave out passwords, keys, tokens and private data before posting.** Issues are public. For security problems, don't open an issue: follow [SECURITY.md](SECURITY.md).

## Changing the code

1. Read [AGENTS.md](AGENTS.md). It explains the code and the rules that must never break.
2. Install [Docker](https://docs.docker.com/get-docker/) to run the stack, and [uv](https://docs.astral.sh/uv/) for the Python part in `mcp/`.
3. Make your change. Try it on your computer with [docs/setup-computer.md](docs/setup-computer.md). Tests use test data only. Never use real data or a real secret in a test.
4. Run the checks. Everything must pass:

   ```bash
   pytest -q
   ```

   The tests check that every tool is in `docs/tools.md`, every setting is in `docs/settings.md` and `.env.example`, every link in the docs works, and no doc has an em dash. With the stack running, `scripts/smoke-test.sh shared-browser` checks the browser, the wall and the login.
5. If people will notice the change, update the matching page in `docs/` and add a line to [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request saying what changed and why.

## Rules

- **Never weaken the safety rules** in [AGENTS.md](AGENTS.md). A change that touches one needs a very good reason, a test, and a clear note in the pull request.
- No tool may ever take a password, a key or a passphrase.
- Don't add new runtime dependencies without a strong reason.
- Keep third-party GitHub Actions pinned to a commit.

## Releases (maintainers)

1. Set the new version in `mcp/pyproject.toml` and `CITATION.cff`. Move the notes in [CHANGELOG.md](CHANGELOG.md) under that version, with the date.
2. Wait for the **Tests** and **images** workflows on GitHub to pass.
3. Tag it `vX.Y.Z` and publish a GitHub Release with the changelog notes.

Every push to `main` builds the six images and publishes them as `latest`. A release tag marks the version people should use.

## Writing docs

The docs are for people who have never used a terminal.

- Short sentences (8 to 20 words), everyday words, "you". Explain any technical word the first time.
- Headings in sentence case, phrased the way a reader would ask ("If something goes wrong").
- One command per code block, and show what the reader should see when it works.
- Button and page names in **bold**, exactly as on the page. Example questions for the AI in *italics*. Commands, settings and file names in `code`.
- No em dashes. Use colons, commas or brackets.
- Never write that something was tested unless it was. Say "not supported" with the reason.
- Where it matters: "Works with Cloudflare Zero Trust. Not made by or affiliated with Cloudflare."

## Credit and license

By contributing, you agree that your work is shared under the [Apache-2.0](LICENSE) license, the same as the rest of the project. Keep the original credit ([LICENSE](LICENSE), [NOTICE](NOTICE), `CITATION.cff`) and add yourself to the changelog entry if you like.
