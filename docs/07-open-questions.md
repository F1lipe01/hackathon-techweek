# Questions raised during the week, and how each was settled

Every question the team logged between 16 and 18 Nov, with its outcome on 20 Nov 2026. Each one is **resolved** (with the evidence), **not needed** for the solution that was built, or stated as an **assumption** or a **pilot step**: something only a pilot with Altice can measure. The original numbers are kept so older references still match.

## Kit and access

| # | Question | Outcome |
|---|---|---|
| 1 | MCP API key | Resolved: received on 16 Nov and kept in `.env`; the login also needs the team account through OAuth ([10-mcp-in-practice.md](10-mcp-in-practice.md)) |
| 1b | The camera had no 12 V power adapter | Resolved: the camera runs and streams RTSP through the organisers' relay (H.265, 2304 × 1296, 20 fps, checked with ffprobe on 18 Nov; [14-architecture.md](14-architecture.md) §2) |
| 3 | Bring the kit online and confirm every device in the app | Resolved: the seven kit devices are mapped with their capabilities ([04-kit-and-access.md](04-kit-and-access.md), [10-mcp-in-practice.md](10-mcp-in-practice.md)) |
| 4 | The format of the team account | Resolved: the MCP login works with it ([10-mcp-in-practice.md](10-mcp-in-practice.md)) |
| 5, 5b | Devices in the home; whether the security hub reaches the platform | Resolved: 7 devices in home "Hack 3"; the hub shows as On ([10-mcp-in-practice.md](10-mcp-in-practice.md)) |
| 5c | The Light had not reached the cloud since 4 Nov | Resolved: the bulb is read through the MCP ([24-what-is-real.md](24-what-is-real.md), "What our setup can really do") |
| 7 | OAuth callbacks for MCP clients | Resolved: only the documented callbacks are accepted, so the team wrote its own client, `mcp/client/chmcp.py` ([mcp/README.md](../mcp/README.md)) |
| 8 | Whether one app invite works on several phones | Not needed: the team used one phone for the Altice app ([08-app-and-apk.md](08-app-and-apk.md)) |
| 36 | Reading the camera stream with our code | Resolved: `prototype/edge.py` reads the kit camera's RTSP stream; the stream capability was not changed |
| 40 | The kit's "Test Motion" scenario and the team's "Detect-motion" scenario both react to camera motion | Not needed: ThingTracker does not use the kit's scenarios. A note for anyone testing with the kit: turn one off before testing the other |

## Event and rules

| # | Question | Outcome |
|---|---|---|
| 2 | The mandatory mentor checkpoint | Resolved: held on Wed 18 Nov; its feedback moved the report's Figure 1 to a safety case ([JOURNAL.md](../JOURNAL.md)) |
| 6, 10 | The challenge sheet, the evaluation criteria, the schedule and the rules | Resolved: filed in `sources/` and summarised in [01-event.md](01-event.md) and [02-challenge.md](02-challenge.md) |
| 9 | Jury names | Not needed: the jury's composition is set by the rules, Article 19 ([06-people.md](06-people.md)) |
| 10b | Finalist count and intermediate pitch length | Resolved on 20 Nov from the participants' guide: 3 finalists per challenge, 3 + 2 min ([01-event.md](01-event.md)) |
| 11, 12, 13 | Links and screenshots from the organisers' messages that were not filed | Not needed: the material that matters is filed in `sources/` or summarised in [01-event.md](01-event.md) |
| 14 | A research paper shared during the brainstorm was not summarised | Not needed: the solution does not rely on it |

## Market evidence

| # | Question | Outcome |
|---|---|---|
| 21 | Altice's customer data is not public | Assumption: the business case uses public proxies (ANACOM, Eurostat), marked as such ([16-business-case.md](16-business-case.md)); a pilot replaces them with Altice's own numbers |
| 22 | Altice already covers older-person monitoring | Resolved by the choice of direction: ThingTracker adds what the camera can recognise (things, pets, people) rather than another monitoring product ([12-market-research.md](12-market-research.md), [18-use-cases.md](18-use-cases.md)) |
| 26 | Some figures could not be confirmed at a primary source | Resolved: [12-market-research.md](12-market-research.md) grades every figure by the strength of its source and marks these as unverified, not to be used |
| 27 | No current Portuguese time-use data | Accepted gap: no figure is claimed for it ([12-market-research.md](12-market-research.md)) |
| 28 | A hidden, contradictory paragraph in an Altice brochure | Resolved: reported as untrusted material and not quoted from the extracted text ([12-market-research.md](12-market-research.md)) |
| 38 | Acceptance of indoor cameras in Portuguese homes | Pilot step: not measured; acceptance and price are tested in a pilot ([17-operator-costs.md](17-operator-costs.md) §9, [16-business-case.md](16-business-case.md)) |

## Platform and devices

| # | Question | Outcome |
|---|---|---|
| 23 | The MCP server has no event history and no notifications | Confirmed ([10-mcp-in-practice.md](10-mcp-in-practice.md)). The prototype polls the door every 4 s through the read-only `get_home_devices`; an event feed and a notification channel are requested from Altice ([15-integration-spec.md](15-integration-spec.md) §9) |
| 24 | Nothing to switch on the plug for a damp or cold demo | Not needed: that use case was not chosen |
| 25 | Whether the smoke sensor's test button triggers the hub alarm | Not needed: ThingTracker never touches the alarm |
| 29 | Kit behaviour the demos depended on | The door contact changing state through the MCP: resolved, real door events reach the prototype ([23-engineering-qa.md](23-engineering-qa.md), E1a). The polling rate: the prototype polls every 4 s; the rate for production is agreed with Altice ([15-integration-spec.md](15-integration-spec.md) §9). Plug metering under load, a powered-off hub and smoke-triggered scenarios: not needed for ThingTracker |
| 31 | Two-way audio through the camera relay | Not needed: the prototype uses the camera's video only (see 33) |
| 32 | Whether a vision model may run on the camera feed, and whether an indoor camera is acceptable | Resolved in the design: vision runs only on motion, on the region that changed, video never leaves the home, and faces are opt-in ([14-architecture.md](14-architecture.md) §12) |
| 33 | Microphones and the law (Lei 58/2019, art. 19.º, n.º 4; Código Penal, art. 199.º) | Design rule: the prototype uses no audio. In the product, sound as a trigger is proposed off by default, never on outdoor cameras, and indoors only if the family turns it on; a classifier gives only a type and a level, and the sound is never recorded or sent. Whether the law applies to a private home is to be verified before launch ([20-product.md](20-product.md) §2.5). Not legal advice |
| 34 | Detecting the family's phones on the network | Resolved for the prototype: the phones are simulated, because no MCP tool exposes the router's clients; a read-only `get_home_wifi_clients` tool is proposed ([15-integration-spec.md](15-integration-spec.md)) |
| 37 | Detection rate for small objects such as keys | Pilot step: not measured on the kit camera; the book is the measured example ([23-engineering-qa.md](23-engineering-qa.md), B1 and G3) |

## Team decisions

| # | Question | Outcome |
|---|---|---|
| 15 | Which idea to commit to | Resolved on 18 Nov: ThingTracker ([AGENTS.md](../AGENTS.md), "Key decisions") |
| 16, 30 | Who builds what; the AI tools named in the report | Resolved: the team is listed in [06-people.md](06-people.md); the report's last section names the AI tools used ([deliverables/executive-summary/](../deliverables/executive-summary/)) |
| 17 | Who pitches | Resolved: one presenter, with the run of show in [pt/21-pitch.md](pt/21-pitch.md) |
| 18 | The network for the demo on Friday | Resolved: the live demo runs on the laptop's webcam, with the app on the presenter's phone |
| 20 | Which repository is submitted | Resolved: this one ([DELIVERABLES.md](../DELIVERABLES.md)) |
| 35, 39 | The report; the brand | Resolved: the report was submitted on 18 Nov ([DELIVERABLES.md](../DELIVERABLES.md)); the brand is in `assets/brand/README.md` |
