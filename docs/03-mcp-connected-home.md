# Connected Home MCP server

Source: *Guia de ligação ao MCP Connected Home — Visual Studio Code, Hermes e Codex*, 11 pages, in `sources/challenge/`. This page is an English digest. The PDF has the screenshots.

## Connection parameters

| Parameter | Value |
|---|---|
| Server URL | `https://cognitive-home.futurelabsinnovations.com` |
| Transport | HTTP |
| Header `X-Client-Type` | `core` |
| Header `Content-Type` | `application/json` |
| Header `X-API-Key` | Key supplied by the organisers. **Received** 16 Nov, stored in `.env` as `CONNECTED_HOME_API_KEY` (format `cgh_live_…`) |
| Auth | OAuth through Keycloak, client id `mcp-client` |
| OAuth redirect host | `mcp-redirect.futurelabsinnovations.com` |
| OAuth callback (Codex) | `http://mcp-redirect.futurelabsinnovations.com:5434/callback`, port 5434 |
| Login | The team account, see `.env` |

The guide notes that the OAuth redirect details depend on the hackathon's Keycloak setup. Only the three clients below are documented.

Config templates for all three are in [`mcp/`](../mcp/). The real config files contain the API key, so they are gitignored.

## Visual Studio Code

1. Open a folder and create `.mcp.json` from `mcp/vscode.mcp.json.example`.
2. `Cmd+Shift+P` → **Browse MCP Servers** → **MCP Servers** → start `connected-home`.
3. Accept the first authentication window with **Allow**.
   - If a **403 page** appears: go back to VS Code, cancel that first login attempt and accept the **URL Handler** alternative the editor offers. The guide says this is specific to the hackathon setup.
4. Sign in with the team account.
5. Check the connection: `Cmd+Shift+P` → **List MCP Servers** → `connected-home` → **Show Output**.
6. Use the tools from Copilot Chat.

## Hermes

1. Open or create `~/.hermes/config.yaml` and add the block from `mcp/hermes.config.yaml.example`.
2. Restart Hermes or reload its MCP config, then run `hermes mcp login connected-home`.
3. Finish the OAuth login and confirm the Connected Home tools are listed.

## Codex

1. Open or create `~/.codex/config.toml` and add the block from `mcp/codex.config.toml.example`.
2. Run `codex mcp list` to check the server is registered. If port 5434 is taken, change it in the config and repeat.
3. If no login prompt appears, run `codex mcp login connected-home` and finish the login in the browser.
4. Run `codex mcp list` again, then `/mcp` inside a Codex session to see the server and its tools.

## Other clients

Claude Code and other MCP clients are not covered by the guide. Whether they work depends on which redirect URLs the Keycloak client accepts. Ask the mentors before spending time on it. Gonçalo's team built the server.

## The 16 tools

### Home

| Tool | Returns |
|---|---|
| `GET_HOME` | Home details and general information |
| `GET_HOME_DEVICES` | All devices of the home with their information and current state |
| `GET_HOME_ROOMS` | Rooms, with their details and devices |
| `GET_HOME_STATUS_BRIEF` | Short summary of the home: devices, rooms, security |
| `GET_HOME_DETAIL_REPORT` | Full report: devices, rooms, states, configuration |

### Device

| Tool | Does |
|---|---|
| `GET_DEVICE_DETAILS` | Details of one device: general information, current state, available capabilities |
| `UPDATE_DEVICE_CAPABILITIES` | Changes a device's capabilities and their settings. This is how you actuate, for example light colour |
| `GET_DEVICE_RECOMMENDATIONS` | Recommendations based on the current state of the home, rooms and devices |

### Security

| Tool | Does |
|---|---|
| `GET_HOME_SECURITY_STATE` | Current state of the security system: armed `STAY`, armed `AWAY`, or disarmed |
| `PATCH_HOME_SECURITY_STATUS` | Changes the security state |
| `GET_HOME_SECURITY_ALARM_HISTORY` | History of the security system |

### Scenarios

| Tool | Does |
|---|---|
| `GET_HOME_SCENARIOS` | Lists configured scenarios with their state |
| `GET_SCENARIO` | Details of one scenario: state, schedule, actions |
| `POST_NEW_SCENARIO` | Creates a scenario with actions, conditions and devices |
| `PATCH_SCENARIO_ACTIVATION` | Activates or deactivates a scenario |
| `POST_EXECUTE_SCENARIO` | Runs a scenario now |

## Example prompts from the guide

These come from Altice's own demo home, so the devices named are theirs, not necessarily ours.

| Group | Prompt | What the agent did |
|---|---|---|
| Home | "Dá-me detalhes sobre os dispositivos da minha casa." | Listed devices by room with state, battery, signal |
| Home | "Quais as divisões da minha casa?" | Listed rooms with device counts |
| Home | "Dá-me um resumo da casa." | Summarised security, devices and alerts; can give the detailed report too |
| Device | "Qual o estado atual da luz Light?" | On, room Showroom, brightness 100%, colour mode, warm white |
| Device | "Altera a cor da luz Light para verde." | Updated the device capability and confirmed |
| Device | "Que recomendações me podes dar sobre a minha casa?" | Prioritised list: temperature sensor at 1% battery, exterior siren tamper alert, sirens with low battery, Security Hub cellular link problems, energy optimisation ideas |
| Security | "Qual o estado de segurança da casa?" | Disarmed, no active alarm |
| Security | "Quero armar a casa no modo STAY." | **Asked for confirmation**, then armed in STAY |
| Security | "Dá-me o histórico de segurança da casa." | Recent arm and disarm events |
| Scenarios | "Que cenários estão disponíveis na casa?" | Four scenarios, including Abertura and Fecho, with state and schedule |
| Scenarios | "Como é o cenário Abertura?" | Scheduled 09:00, turns Light on at 100% brightness, warm tone |
| Scenarios | "Quero um novo cenário para mudar a cor da luz Light para verde às 12h." | Created "Light verde às 12h", active, daily at 12:00 |
| Scenarios | "Executa o cenário Abertura." | Scenario was inactive, so it **asked for confirmation** before running |
| Scenarios | "Ativa o cenário Abertura." | Activated; now runs daily at 09:00 |

Things the examples show about the platform:

- Devices report battery, signal and tamper state, not just on or off.
- Scenarios support daily schedules.
- The demo agent asks for confirmation before arming security and before running an inactive scenario.
- The demo home had a colour light, a temperature sensor, sirens and a Security Hub with a cellular link.

## Reference links from the guide

- https://code.visualstudio.com/docs/agents/reference/mcp-configuration
- https://code.visualstudio.com/docs/agent-customization/mcp-servers
- https://learn.chatgpt.com/docs/extend/mcp
