# IT-Porto · Aveiro Tech City Hackathon 2026

Workspace of team **IT-Porto** for **Challenge #3 — Altice Labs: Connected Homes Reimagined (AI at the service of the home)**, 4th edition of the Aveiro Tech City Hackathon.

Everything received or discussed so far is filed here: organiser material, kick-off notes, our brainstorm, access details and the deliverable templates.

## Status — Mon 16 Nov 2026 (kick-off day)

- Done: registered as a team of three, hardware kit collected and inventoried from photos, team credentials received, MCP guide and templates received, kick-off and challenge Q&A attended.
- Done since: **MCP connected and tested** (our own client, `mcp/client/`), kit Wi-Fi up via the Redmi hotspot, Plug online.
- Not done: Camera (no power adapter) and Light (not reaching the cloud) online, idea chosen, mentor checkpoint booked, executive summary written.
- This repo is private on GitHub at `F1lipe01/hackathon-techweek`. Simon and Mushahid have been added as collaborators.
- Gaps and to-dos are listed in [docs/07-open-questions.md](docs/07-open-questions.md).

## Deadlines

| When | What | Format |
|---|---|---|
| **Wed 18 Nov afternoon** | Mandatory checkpoint with the Altice mentors | Book it with them on Slack |
| **Wed 18 Nov, 19:00** | 1st deliverable: succinct 2-page report (PDF) | Via Google Form |
| **Fri 20 Nov, 08:30–20:00** | In-person day, Fábrica Centro Ciência Viva de Aveiro | Attendance mandatory |
| **Fri 20 Nov, afternoon → 16:30–17:30** | Intermediate pitches; finalists selected | 3 min + 1 min Q&A; **up to 6** per challenge advance |
| **Fri 20 Nov, 17:30** | Executive summary (PDF) + presentation (PPT) + repo link (optional) | Templates in `deliverables/` |
| **Fri 20 Nov, 18:00–19:30** | Final pitches on stage, for the finalists | 5 min + 3 min Q&A |
| **Fri 20 Nov, 20:00** | Winners announced + cocktail | |

No extensions (late = possible disqualification), pitch time cut strictly. Full criteria and rules in [docs/01-event.md](docs/01-event.md). The kick-off said 3 finalists / 3+2 min; the written rules say up to 6 / 3+1 — confirm with mentors.

## Map

| Path | What is in it |
|---|---|
| [docs/01-event.md](docs/01-event.md) | Timeline, evaluation, deliverables, prizes, rules, organiser advice |
| [docs/02-challenge.md](docs/02-challenge.md) | The Altice challenge, what the mentors want, constraints |
| [docs/03-mcp-connected-home.md](docs/03-mcp-connected-home.md) | Connecting to the Connected Home MCP server, the 16 tools, example prompts |
| [docs/04-kit-and-access.md](docs/04-kit-and-access.md) | Hardware kit, Wi-Fi, mobile app, camera feed, where each credential lives |
| [docs/05-ideas.md](docs/05-ideas.md) | Whiteboard brainstorm, Slack discussion, references |
| [docs/06-people.md](docs/06-people.md) | Team, mentors, organisers, jury |
| [docs/07-open-questions.md](docs/07-open-questions.md) | What is missing and what to do next |
| [docs/08-app-and-apk.md](docs/08-app-and-apk.md) | The mobile app and APK analysis; confirmed device roster |
| [docs/09-platform-capabilities.md](docs/09-platform-capabilities.md) | The platform's full capability model (devices, automation, security, energy), reverse-engineered from the app |
| [docs/10-mcp-in-practice.md](docs/10-mcp-in-practice.md) | **The MCP tested live:** the real 18 tools, write payloads, safety findings, every device's capabilities |
| [deliverables/](deliverables/) | Official templates and our drafts |
| [mcp/](mcp/) | MCP client config templates from the official guide |
| [assets/](assets/) | Clean device images for diagrams and slides, and screens of Altice's own app |
| [sources/](sources/) | Raw material exactly as received, with an index |

## Links

| What | Link |
|---|---|
| Executive summary submission form | https://docs.google.com/forms/d/e/1FAIpQLSepZIiXKm-tQaNF-1UmPIh4Z3IapeybneKr7N5W47Qs1Vf7dQ/viewform |
| Templates folder (Drive) | https://drive.google.com/drive/folders/1rYi1o8HWRieewvc4dZwyyiTYM_o9bOyT |
| MCP guide PDF (Drive) | https://drive.google.com/file/d/1ocJduMcWFHUK_dsg9ykesaJ9H88l8mvu/view |
| Registration form (closed 4 Nov) | https://techweek.aveirotechcity.pt/form_hackaton/ |
| Challenge resources folder | Not filed: the link was in the organisers' email |

## Secrets

Credentials are kept out of git. Real values live in `.env` (gitignored); `.env.example` lists what exists. Tracked copies of the Slack threads have the values replaced by a pointer to the matching `.env` variable.

MCP client config files hold the API key in plain text, so `.mcp.json` and `.vscode/mcp.json` are gitignored too. Start from the templates in `mcp/`.

## Before sharing this repo

`sources/` holds raw Slack threads and a meeting transcript with the names and words of colleagues, organisers and other participants. The kit photos show device serial numbers and people in the background of the lab. Review or drop that folder before making the repository public or submitting it to the jury.

Some images in `assets/` come from other sites and are not ours. Sources are listed in `assets/README.md`.

## Language

Working notes are in English, the language the team uses on Slack. The event's official language is Portuguese, so the executive summary, slides and pitch are in Portuguese.
