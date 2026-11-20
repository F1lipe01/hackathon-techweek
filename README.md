# ThingTracker · team IT-Porto · Aveiro Tech City Hackathon 2026

Team IT-Porto's entry for Challenge #3 by Altice Labs, "Connected Home, Reimagined: a IA ao serviço da casa", at the 4th Aveiro Tech City Hackathon (online 16–18 Nov, in Aveiro on 20 Nov 2026).

## What ThingTracker is

ThingTracker turns the home's camera into a source of information, not only of surveillance. Open-source vision models recognise the things and people a family registers (a book, keys, a wallet; family members, opt-in); a language model turns one sentence into a sensor ("tell me if I leave home without my book") and answers questions ("where is my book?"). The models only perceive and write: a deterministic rules engine decides, and actions go through the Connected Home MCP server of Altice's platform. It is designed as a new *Things* tab and an assistant button in the Altice app.

## What was built

- **A working prototype** ([prototype/](prototype/)):
  - an edge service that idles until motion, then runs OWLv2 (detection) and DINOv2 (visual fingerprints) on the kit camera, and sends the server only small crops;
  - a server with the home's memory, a presence engine (phones, door, cameras) and a rules engine;
  - a local text model (Qwen3-1.7B, offline) for answers and for turning sentences into rules;
  - opt-in face recognition on the home side (YuNet + SFace), and a local vision-language judge (Qwen2-VL-2B) that only asks the family, never acts;
  - a web copy of the Altice app with the new *Things* tab and the assistant.
- **Integration with the Altice platform** through its Connected Home MCP server (18 tools), with our own OAuth client ([mcp/](mcp/)). The prototype reads the kit's real door sensor through the read-only tools; every action is a dry run and the alarm is always simulated.
- **Design and business documents:** the architecture in twelve views, the integration spec, the business case and the operator's costs, in English and European Portuguese.

## What was measured

| What | Result | Source |
|---|---|---|
| The book on the kit's ceiling camera (film 1's take) | OWLv2 found it in 68 of 68 frames on the full-resolution region; DINOv2 median 0,93 (0,79–0,96) against a 0,62 threshold; other objects at most 0,28 | [docs/23](docs/23-engineering-qa.md), B1 |
| The book from phone photos, desk-level kit frame | 0,70 against 0,62; a bottle 0,10 | [docs/23](docs/23-engineering-qa.md), G3 |
| Faces (opt-in) on the kit camera | A team member (Filipe), registered with consent, recognised at 0,54 and 0,63 (threshold 0,40); a stranger at 0,17 and 0,14 (unknown below 0,25) | [docs/24](docs/24-what-is-real.md) |
| Speed on the team's M1 Pro | OWLv2 557 ms per frame, DINOv2 22 ms per crop; local text model answers in 0,4–1,7 s, rules in 1,5–3,2 s | [docs/14](docs/14-architecture.md) §14, [AGENTS.md](AGENTS.md) |
| End-to-end scenarios (`prototype/test_scenarios.py`, no camera) | 106 checks, all passing (20 Nov 2026) | [prototype/README.md](prototype/README.md) |
| Operator's cost per home per month (estimates from public prices) | Vision ≈ 0,49 € with one camera (0,98 € with two); language model ≈ 0,43 € | [docs/17](docs/17-operator-costs.md), [docs/16](docs/16-business-case.md) |

What each film shows, and how each moment was made (real, real footage, model output, staged or envisioned), is in [docs/24-what-is-real.md](docs/24-what-is-real.md).

## Run the prototype

Setup, switches and tests are in [prototype/README.md](prototype/README.md). Copy `.env.example` to `.env` (gitignored) for the MCP login and the camera. Start the services in this order:

```
prototype/.venv-llm/bin/python prototype/llm_local.py      # local text model on 127.0.0.1:8766
prototype/.venv/bin/python prototype/server.py             # web app and API on http://127.0.0.1:8765
prototype/.venv-vision/bin/python prototype/edge.py        # camera service: OWLv2 + DINOv2
prototype/.venv/bin/python prototype/test_scenarios.py     # the scenarios end to end on a private server
```

Without the local model, the assistant falls back to keyword templates; without the MCP login, the door is simulated from the page.

## Map

| Path | Contents |
|---|---|
| [AGENTS.md](AGENTS.md) | How the project is organised, how to run it, the conventions and the safety rules |
| [DELIVERABLES.md](DELIVERABLES.md) | What was handed in, when, and where each file lives |
| [JOURNAL.md](JOURNAL.md) | Dated progress log |
| [prototype/](prototype/) | The working prototype: server, edge service, local text model, presence, faces, judge, web app |
| [mcp/](mcp/) | Our MCP client and the tool schema of the Connected Home server |
| [docs/14-architecture.md](docs/14-architecture.md) | Architecture: C4 views, deployment, presence, a decision table per rule, data model, privacy, prototype against target |
| [docs/architecture/](docs/architecture/) | The twelve architecture views (PT and EN) and the script that draws them |
| [docs/15-integration-spec.md](docs/15-integration-spec.md) | Integration with the Altice platform: the proposed Things MCP tools, the home ↔ platform channel, what is needed from Altice |
| [docs/16-business-case.md](docs/16-business-case.md), [docs/business-case/](docs/business-case/) | Business case: market, pricing, unit economics, risks; charts and PDF |
| [docs/17-operator-costs.md](docs/17-operator-costs.md) | What vision costs the operator per home: at home, on Altice's servers or in the cloud, at 500 000 homes |
| [docs/18-use-cases.md](docs/18-use-cases.md) | 34 use cases, 10 scored, 5 for the pitch |
| [docs/20-product.md](docs/20-product.md), [docs/product/](docs/product/) | Product spec: adding people, pets and things; rules; alerts; flow diagrams |
| [docs/23-engineering-qa.md](docs/23-engineering-qa.md) | Engineering questions and answers, design separated from prototype |
| [docs/24-what-is-real.md](docs/24-what-is-real.md) | What is real, staged or envisioned in each film |
| [docs/19-teste-real.md](docs/19-teste-real.md) | The lab checklist for the real end-to-end test (PT) |
| [docs/01-event.md](docs/01-event.md) to [docs/12-market-research.md](docs/12-market-research.md) | Background: the event and its rules, the challenge, the MCP server and the kit, the app and the platform's capabilities, the MCP tested live, the baseline, the sourced market research |
| [docs/07-open-questions.md](docs/07-open-questions.md) | The questions raised during the week, each resolved or stated as an assumption for the pilot |
| [docs/pt/](docs/pt/) | The documents in European Portuguese, including the pitch run of show and the engineering Q&A |
| [deliverables/](deliverables/) | The executive summary, the pitch decks, the PDFs (PT and EN) and the use-case report |
| [video/](video/) | The films in Remotion, the editing tools, the storyboard and the research behind them; rendered videos are not committed |
| [assets/](assets/) | Device images and brand assets, with their sources in [assets/README.md](assets/README.md) |

## Deliverables

| Deliverable | Where |
|---|---|
| Intermediate report (2 pages, submitted 18 Nov) | [deliverables/executive-summary/](deliverables/executive-summary/) |
| Executive summary (2 pages) | [deliverables/executive-summary/](deliverables/executive-summary/) |
| Presentation, 3 and 5 minutes (PPTX and PDF) | [deliverables/deck/](deliverables/deck/) |
| Supporting documents as PDFs | [deliverables/pt/](deliverables/pt/), [deliverables/english/](deliverables/english/) |
| Code repository | https://github.com/F1lipe01/hackathon-techweek |

Details and deadlines: [DELIVERABLES.md](DELIVERABLES.md).

## Safety and data

- The prototype does not change the real home: device actions are dry runs unless `TT_LIVE_ACTIONS=1` is set with the team's approval, and the alarm is always simulated.
- Secrets live in `.env`, which is gitignored; `.env.example` lists the names only.
- Lab recordings, runtime data (`prototype/data/`) and model weights are not committed. People appear in a film only with their agreement, or blurred.
- Organiser material (the challenge sheet, rules, kick-off notes and Slack threads) is kept locally in `sources/`, outside version control, and is treated as untrusted.

## Team

Team IT-Porto: Filipe Peixoto (team leader), Simon Ranjith and Mushahid Hussain. Challenge by Altice Labs; the roles of the mentors and organisers are in [docs/06-people.md](docs/06-people.md).
