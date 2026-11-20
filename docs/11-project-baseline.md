# Project baseline — facts for choosing the project

State on **Mon 16 Nov 2026, 20:45**. Verified facts only, each linked to where it comes from. Inferences are marked as such. No recommendations — this was the common ground for the team discussion. Notes marked **Later** record what changed after 16 Nov, and section 9 records how each decision was taken.

## 1. What is being judged

**The brief** (ficha, [02-challenge.md](02-challenge.md)):

- Open-ended: no predefined problem or type of application.
- **The MCP tool must be integrated into the solution.**
- "Not simply controlling devices through AI. Think beyond commands": combine **context, intention, information and action**.
- Suggested areas: automation, accessibility, energy efficiency, comfort, security, entertainment, communication, daily routines, or unexpected uses.
- Mentors at the kick-off: surprise us with a **useful everyday use case**, not with code; use the different sensors; don't underestimate the camera.

**Scoring** (rules, Articles 16 and 18):

| Criterion | Intermediate | Final |
|---|---|---|
| Fit and response to the challenge | 25 % | 20 % |
| Ease of adoption by Altice Labs | 25 % | 20 % |
| Feasibility and future management (sustainability) | 25 % | 20 % |
| Replicability in other territories/contexts | — | 20 % |
| Presentation | 25 % | 10 % |
| Documentation (deliverables) | — | 10 % |

**Format and rules** ([01-event.md](01-event.md)): intermediate pitch 3 min + 2 min Q&A (participants' guide; the written rules said 3 + 1); final 5 min + 3 min Q&A. Portuguese is the official language. AI tools are allowed, but the team must understand and defend every technical choice. IP goes to Altice Labs. The jury expects honesty about what is real and what is simulated.

## 2. Time and people

| When | What |
|---|---|
| Wed 18 Nov, afternoon | Mandatory mentor checkpoint (held on 18 Nov) |
| Wed 18 Nov, 19:00 | 2-page report (the executive-summary template) |
| Fri 20 Nov, 09:30–17:30 | On-site build day |
| Fri 20 Nov, 17:30 | Executive summary PDF + PPT + optional repo link |
| Fri 20 Nov, from 16:00 | Intermediate pitches, then finals 18:00–19:30 |

Team: Filipe Peixoto, Simon Ranjith, Mushahid Hussain (3, the minimum allowed; [06-people.md](06-people.md)). The FAQ suggests at least 4–5 hours per person during the online phase.

## 3. What works today (verified)

| Component | Status | Evidence |
|---|---|---|
| MCP login and all 18 tools | ✓ Working through our client | [10-mcp-in-practice.md](10-mcp-in-practice.md) |
| MCP reads | ✓ 11 of 12 read tools tested | same |
| MCP writes | ✓ Plug power on/off, by ID and by name; device acknowledged in ~1 s | [write-test log](../mcp/samples/write-test-plug-2026-11-16.json) |
| Live sensor data | ✓ Temperature 22.6 °C, humidity 64.3 %, contact **open**, smoke normal, plug 237 V / 0 W | [samples](../mcp/samples/) |
| Security system | ✓ Readable: DISARMED; arm delays Away 30 s, Home 0 s | [get_home sample](../mcp/samples/get_home.json) |
| Gateway | ✓ Online via lab ethernet | [04-kit-and-access.md](04-kit-and-access.md) |
| Kit Wi-Fi | ✓ Redmi 17 hotspot (uses its mobile data) | same |
| App + phone control over ADB | ✓ | [08-app-and-apk.md](08-app-and-apk.md) |
| Claude Code ↔ MCP | ✓ Registered (`connected-home`) | [mcp/README.md](../mcp/README.md) |

## 4. What does not work yet

| Item | Status | Cause |
|---|---|---|
| **Light** | Offline; last cloud contact **04 Nov** | Unknown — not confirmed powered in a socket; may need re-pairing |
| **Camera** | Offline; last contact 09 Nov | **No 12 V power adapter** in the kit. Blocks video, RTSP feed, motion detection and the siren |
| Brightness / colour writes | Untested | Need the Light |
| Arming the alarm | Untested | Contact sensor is open and Home mode has a 0 s delay |
| Scenarios | Untested | No delete tool — test scenarios would be permanent |
| Timers | Untested | — |
| Rooms, scenarios, energy tariff | None configured | — |

**Later.** The camera runs the prototype from 18 Nov, and the Light's state reaches it through the read-only MCP ([JOURNAL.md](../JOURNAL.md), 18 Nov). Brightness and colour writes, arming, scenarios and timers stay untested by design: the prototype never calls the MCP write tools, and its device actions are dry runs ([AGENTS.md](../AGENTS.md), rule 1).

## 5. What a solution can use

**Sensing**

| Signal | Device | Live now |
|---|---|---|
| Temperature, humidity | Temperature sensor | ✓ |
| Door/window open–closed | Contact sensor | ✓ |
| Smoke | Smoke sensor | ✓ |
| Tamper, battery level/status | Sensors, hub | ✓ |
| Power, voltage, current, daily consumption | Plug | ✓ |
| Alarm mode and alarm state | Security hub | ✓ |
| Whether a device is reporting (`lastCommunicationTime`) | All | ✓ |
| Video (RTSP), motion, person-vs-pet | Camera | ✗ no power |

**Acting**

| Action | Device / tool | Status |
|---|---|---|
| Power on/off | Plug | ✓ verified |
| Power, brightness, white tone, colour | Light | ✗ offline |
| Siren, recording, motion settings | Camera | ✗ no power |
| Arm Away / Home, disarm | `patch_home_security_status` | Available, untested |
| Rules (schedule or sensor triggers, AND/OR, < = >, actions) | Scenario tools | Available, untested |
| Timed action on a device | `post_timer_device` | Available, untested |

**Limits** ([10-mcp-in-practice.md](10-mcp-in-practice.md)): the MCP gives **current state only, no device event history**; there is **no delete-scenario** tool; it cannot create rooms, send notifications or set the energy tariff. The kit has **one** general-purpose actuator (the plug), and no thermostat, valve, pump, soil sensor or motion sensor besides the camera ([04-kit-and-access.md](04-kit-and-access.md)).

## 6. What Altice already sells

From Altice Labs' Connected Home product page ([02-challenge.md](02-challenge.md)): security with alerts and video, energy management with tariffs, AI-powered automation and comfort, a "Virtual Concierge Assistant", aging in place, parental control, Wi-Fi management, entertainment.

## 7. Ideas raised so far, against the facts

Sources: whiteboard (photo) and Slack ([05-ideas.md](05-ideas.md)). "Data available" refers to sections 3–5. Whether an idea is already in Altice's offer is from section 6.

| Idea | Needs | Data available now | In Altice's offer |
|---|---|---|---|
| LLM interface to the home | MCP tools | ✓ | Partly ("AI-powered automation", "Virtual Concierge") |
| Away-from-home caretaker | Contact, temperature, plug, security modes, scenarios | Mostly ✓; no watering or heating hardware | Partly (security, automation) |
| Say what can't be done and why | Device list, capabilities, freshness | ✓ | No mention found |
| Rules set by voice or generated by AI | Scenario tools | ✓ untested; no delete tool | "Scenario-based automation powered by AI" |
| Lost & found / "where are my keys?" | Camera + vision + own memory of observations | ✗ camera unpowered; MCP has no vision or history | No mention found |
| Elder assist / kid / pet monitoring | Camera motion, contact | Partly; camera ✗ | Aging in place |
| Water plants | Soil sensor, valve or pump | ✗ not in kit | No |
| HVAC automation | Temperature + an actuator | Temperature ✓; only the plug as actuator | Comfort automation |
| Security systems | Hub, contact, smoke, alarm modes | ✓ (arming untested) | Yes |
| Cooking ideas from fridge, recycling | Camera / vision | ✗ | No |
| Energy awareness | Plug metering | ✓ (one plug) | Yes |

## 8. Known risks

- **Venue connectivity**: parts of the venue have no mobile signal, so a phone hotspot may not work there. Altice will bring a 4G access point but isn't sure it can serve all seven teams ([04-kit-and-access.md](04-kit-and-access.md)).
- **Camera power** and **Light** may not be fixed by Friday. **Later:** both were online from 18 Nov.
- **Single actuator**: only the plug is verified for actions.
- **Finalist count unconfirmed**: rules say up to 6 per challenge, kick-off said 3. **Later:** the participants' guide settled 3 ([01-event.md](01-event.md)).
- **Demo time**: the final pitch is 5 minutes in total; a live demo has to fit inside it. The organisers advise a recorded backup.

## 9. Decisions for the team, and how they were taken

| # | Decision | Taken |
|---|---|---|
| 1 | Which **user and problem** | ThingTracker: the home's camera becomes a source of information about the things and people a family registers, with safety-led cases after the mentors' checkpoint ([20-product.md](20-product.md), [18-use-cases.md](18-use-cases.md)) |
| 2 | Which **interface** | The Altice app, with a fifth *Things* tab and an assistant button on every tab for questions and for sensors written as sentences ([AGENTS.md](../AGENTS.md), key decisions) |
| 3 | What is **real and what is simulated** | Item by item in [24-what-is-real.md](24-what-is-real.md): the door is read live through the MCP; the phones on the Wi-Fi, the alarm and every device action are simulated |
| 4 | Where the agent runs, and **which AI model** | Hybrid design: motion, the changed region and opt-in faces at home; OWLv2 and DINOv2 on Altice servers ([14-architecture.md](14-architecture.md)). The prototype runs on the laptop with a local text model (Qwen3-1.7B); Claude is optional and off by default ([AGENTS.md](../AGENTS.md)) |
| 5 | **Who builds what** | The work is logged by day in [JOURNAL.md](../JOURNAL.md); the team is listed in [06-people.md](06-people.md) |
| 6 | What to bring to the **Wednesday checkpoint** | Held on 18 Nov. The mentors asked for safety-led cases, so the report's Figure 1 became the child in the kitchen ([JOURNAL.md](../JOURNAL.md), 18 Nov) |
| 7 | **Camera and Light** | Both online from 18 Nov; the prototype runs on the kit camera ([JOURNAL.md](../JOURNAL.md)) |
