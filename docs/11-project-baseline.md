# Project baseline — facts for choosing the project

State on **Mon 16 Nov 2026, 20:45**. Verified facts only, each linked to where it comes from. Inferences are marked as such. No recommendations — this is the common ground for the team discussion.

## 1. What is being judged

**The brief** ([ficha](../sources/challenge/desafio3-ficha.pdf), [02-challenge.md](02-challenge.md)):

- Open-ended: no predefined problem or type of application.
- **The MCP tool must be integrated into the solution.**
- "Not simply controlling devices through AI. Think beyond commands": combine **context, intention, information and action**.
- Suggested areas: automation, accessibility, energy efficiency, comfort, security, entertainment, communication, daily routines, or unexpected uses.
- Mentors at the kick-off: surprise us with a **useful everyday use case**, not with code; use the different sensors; don't underestimate the camera.

**Scoring** ([rules](../sources/rules/normas-2026.pdf), Articles 16 and 18):

| Criterion | Intermediate | Final |
|---|---|---|
| Fit and response to the challenge | 25 % | 20 % |
| Ease of adoption by Altice Labs | 25 % | 20 % |
| Feasibility and future management (sustainability) | 25 % | 20 % |
| Replicability in other territories/contexts | — | 20 % |
| Presentation | 25 % | 10 % |
| Documentation (deliverables) | — | 10 % |

**Format and rules** ([01-event.md](01-event.md)): intermediate pitch 3 min + 1 min Q&A; final 5 min + 3 min Q&A. Portuguese is the official language. AI tools are allowed, but the team must understand and defend every technical choice. IP goes to Altice Labs. The jury expects honesty about what is real and what is simulated.

## 2. Time and people

| When | What |
|---|---|
| Wed 18 Nov, afternoon | Mandatory mentor checkpoint (not booked yet) |
| Wed 18 Nov, 19:00 | 2-page report (the executive-summary template) |
| Fri 20 Nov, 09:30–17:30 | On-site build day |
| Fri 20 Nov, 17:30 | Executive summary PDF + PPT + optional repo link |
| Fri 20 Nov, from ~16:30 | Intermediate pitches, then finals 18:00–19:30 |

Team: Filipe, Simon, Mushahid (3; the minimum allowed). The FAQ suggests at least 4–5 hours per person during the online phase.

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

Sources: whiteboard ([photo](../sources/brainstorm/whiteboard.jpg)) and Slack ([05-ideas.md](05-ideas.md)). "Data available" refers to sections 3–5. Whether an idea is already in Altice's offer is from section 6.

| Idea | Needs | Data available now | In Altice's offer |
|---|---|---|---|
| LLM interface to the home (Ana) | MCP tools | ✓ | Partly ("AI-powered automation", "Virtual Concierge") |
| Away-from-home caretaker (Filipe) | Contact, temperature, plug, security modes, scenarios | Mostly ✓; no watering or heating hardware | Partly (security, automation) |
| Say what can't be done and why (Filipe) | Device list, capabilities, freshness | ✓ | No mention found |
| Rules set by voice or generated by AI (Mushahid) | Scenario tools | ✓ untested; no delete tool | "Scenario-based automation powered by AI" |
| Lost & found / "where are my keys?" | Camera + vision + own memory of observations | ✗ camera unpowered; MCP has no vision or history | No mention found |
| Elder assist / kid / pet monitoring | Camera motion, contact | Partly; camera ✗ | Aging in place |
| Water plants | Soil sensor, valve or pump | ✗ not in kit | No |
| HVAC automation | Temperature + an actuator | Temperature ✓; only the plug as actuator | Comfort automation |
| Security systems | Hub, contact, smoke, alarm modes | ✓ (arming untested) | Yes |
| Cooking ideas from fridge, recycling | Camera / vision | ✗ | No |
| Energy awareness | Plug metering | ✓ (one plug) | Yes |

## 8. Known risks

- **Venue connectivity**: parts of the venue have no mobile signal, so a phone hotspot may not work there. Altice will bring a 4G access point but isn't sure it can serve all seven teams ([04-kit-and-access.md](04-kit-and-access.md)).
- **Camera power** and **Light** may not be fixed by Friday.
- **Single actuator**: only the plug is verified for actions.
- **Finalist count unconfirmed**: rules say up to 6 per challenge, kick-off said 3.
- **Demo time**: the final pitch is 5 minutes in total; a live demo has to fit inside it. The organisers advise a recorded backup.

## 9. Decisions for the team

1. Which **user and problem** do we solve?
2. Which **interface**: voice, chat, app, web, or something proactive with no interface?
3. What is **real and what is simulated** in the demo?
4. Where does the agent run, and **which AI model** does it use?
5. **Who builds what** (agent/MCP, interface, pitch and documents)?
6. What do we bring to the **Wednesday checkpoint**?
7. **Camera and Light**: chase the fixes, or design without them?
