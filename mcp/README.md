# MCP client config templates

Copied from the official guide (`sources/challenge/desafio3-altice-mcp-guide.pdf`). Each one needs the real API key in place of `<API_KEY>`.

| Template | Copy to | Client |
|---|---|---|
| `vscode.mcp.json.example` | `.mcp.json` in the folder opened in VS Code | Visual Studio Code with Copilot Chat |
| `hermes.config.yaml.example` | merge into `~/.hermes/config.yaml` | Hermes |
| `codex.config.toml.example` | merge into `~/.codex/config.toml` | Codex CLI |

The filled-in files contain the API key in plain text. `.mcp.json` and `.vscode/mcp.json` are gitignored in this repo for that reason. Never commit a filled-in copy.

Step-by-step instructions: [`docs/03-mcp-connected-home.md`](../docs/03-mcp-connected-home.md).
