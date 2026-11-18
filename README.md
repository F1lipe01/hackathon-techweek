# IT-Porto · Aveiro Tech City Hackathon 2026

Workspace of team **IT-Porto** for **Challenge #3 — Altice Labs: Connected Homes Reimagined (AI at the service of the home)**, 4th edition of the Aveiro Tech City Hackathon.

Everything received or discussed so far is filed here: organiser material, kick-off notes, our brainstorm, access details and the deliverable templates.

## Status — Wed 18 Nov 2026

- **Solution chosen: ThingTracker.** The home's camera becomes a source of information: it learns the things a family registers and finds them again. A sentence becomes a sensor, and the assistant answers "where is my book?". Read [AGENTS.md](AGENTS.md) first.
- **Report (1st deliverable, due today 19:00):** 2 pages, fact-checked, on the official template: `deliverables/executive-summary/sumario-executivo-IT-Porto.pdf`. Submitted through the Google Form by the team.
- **Prototype:** runs end to end on the kit camera.
  - Visual registration (8 views → a DINOv2 fingerprint) and recognition (OWLv2 candidates matched to the fingerprint).
  - Live boxes, a local rules engine and a local SQLite database.
  - An exact copy of the Altice app, with the new *Things* tab and the assistant button.
- **Documents:** architecture, integration spec and business case in English (`docs/14–16`) and in Portuguese (`docs/pt/`), the versions on Google Drive. The business case also comes as a 9-page PDF with charts.
- **Next (Fri 20 Nov):**
  - the executive summary and the deck;
  - the product video, from screen recordings of the use case with the yellow book;
  - pitch practice.

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
| [docs/10-mcp-in-practice.md](docs/10-mcp-in-practice.md) | **The MCP tested live:** the real 18 tools, write payloads, test results, safety findings, every device's capabilities |
| [docs/11-project-baseline.md](docs/11-project-baseline.md) | **Start here for the project discussion:** verified facts, what works and what doesn't, ideas against the facts, decisions to make |
| [docs/12-market-research.md](docs/12-market-research.md) | **Evidence for choosing the use case:** sourced figures for Portugal, France and the EU (damp, cold homes, older people living alone, fires, burglary, adoption), kit fit, overlap with Altice, scored candidates, pitch-ready figures in Portuguese |
| [docs/14-architecture.md](docs/14-architecture.md) | **ThingTracker architecture:** components, flows, the sensor language, data model, privacy, measured performance and cost, decisions with alternatives, open questions. Diagram in [docs/architecture/](docs/architecture/) |
| [docs/15-integration-spec.md](docs/15-integration-spec.md) | **Integration with the Altice platform:** the four Things MCP tools, the edge ↔ platform channel, enrolment, scenarios, what we need from Altice |
| [docs/16-business-case.md](docs/16-business-case.md) | **Business case:** market funnel, pricing, unit economics, operator revenue, risks; model in `16-business-case-model.csv` |
| [DELIVERABLES.md](DELIVERABLES.md) | **What we hand in and when:** the official deliverables and deadlines, the pitches, the supporting material, Thursday's plan, the Drive folders |
| [AGENTS.md](AGENTS.md) | **Read first:** the project, where things live, how to run the prototype, conventions, the rules that must not be broken, key decisions |
| [prototype/](prototype/) | **The working prototype:** server and rules engine, edge service (OWLv2 + DINOv2 on the kit camera), SQLite database, the Altice app copy with the Things tab and the assistant |
| [deliverables/executive-summary/](deliverables/executive-summary/) | **The 2-page report** (PT-PT) built on the official template, with its figures |
| [docs/pt/](docs/pt/) | Architecture, integration spec and business case in European Portuguese (the Drive versions) |
| [docs/business-case/](docs/business-case/) | Business-case charts and the 9-page PDF (`viabilidade-negocio.pdf`) |
| [deliverables/use-case-report/](deliverables/use-case-report/) | **Top 5 use cases** as a PDF report: problem, what we have, what to build, why, pitch and Q&A for each |
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
