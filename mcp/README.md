# MCP access

## Our own client: `client/chmcp.py`

A small Python client (standard library only) that logs in to the Connected Home MCP and calls its tools. Use it from the terminal, from our own code, or plug it into Claude Code.

```bash
python3 mcp/client/chmcp.py login                 # opens the browser; sign in with the team account
python3 mcp/client/chmcp.py tools                 # list the tools and their parameters
python3 mcp/client/chmcp.py call get_home_status_brief '{}'
python3 mcp/client/chmcp.py serve                 # stdio MCP proxy (see below)
```

Reasons for writing our own client:

- The server's Keycloak client (`mcp-client`) only accepts two OAuth callbacks: `http://mcp-redirect.futurelabsinnovations.com:5434/callback` (that host resolves to 127.0.0.1) and `https://vscode.dev/redirect`. **Any `localhost` callback gets a 403.** Claude Code and most generic MCP clients log in with a `localhost` callback, so they can't connect natively. This client uses the allowed callback on port 5434.
- Every request also needs the `X-API-Key` header, which the client reads from `.env`.
- Our solution has to call the MCP from code anyway. This is that building block.

Tokens are saved to `mcp/client/.tokens.json` (gitignored, mode 600) and refreshed automatically. When the refresh token expires, run `login` again.

**In Claude Code:** `claude mcp add connected-home -- python3 /absolute/path/mcp/client/chmcp.py serve` exposes the server's tools (the 18 in `tools-schema.json`) as native tools. The proxy forwards `tools/list` and `tools/call` upstream, adding the token and API key. It forwards the write tools too (`update_device_capabilities`, `patch_home_security_status`, the scenario and timer tools): they change the real home, and are called only with the team's explicit approval (rule 1 in [AGENTS.md](../AGENTS.md)).

## Config templates for the guide's clients

Copied from the official guide (`sources/challenge/desafio3-altice-mcp-guide.pdf`). Each one needs the real API key in place of `<API_KEY>`.

| Template | Copy to | Client |
|---|---|---|
| `vscode.mcp.json.example` | `.mcp.json` in the folder opened in VS Code | Visual Studio Code with Copilot Chat |
| `hermes.config.yaml.example` | merge into `~/.hermes/config.yaml` | Hermes |
| `codex.config.toml.example` | merge into `~/.codex/config.toml` | Codex CLI |

The filled-in files contain the API key in plain text. `.mcp.json` and `.vscode/mcp.json` are gitignored in this repo for that reason. Never commit a filled-in copy.

Step-by-step instructions: [`docs/03-mcp-connected-home.md`](../docs/03-mcp-connected-home.md).
