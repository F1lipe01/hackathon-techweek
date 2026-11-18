# Track Things · prototype

A working copy of the idea: **the camera as a source of information, and a sentence creates a sensor.**

- **Left of the screen: the camera.** Webcam, a recorded clip played as if live, or the kit camera. You draw the zones the system may look at.
- **Right of the screen: the Altice app**, with its colours taken from our screenshots and a new **Coisas** (Things) tab. It holds a free question box, your things with when and where they were last seen, sensors created from a sentence, and alerts.

```
browser: camera → zones → crops (only zones that changed)
   → server: Claude Haiku 5.5 (what is visible, sensor answers) → memory → rules → MCP action
   → app: Coisas tab, alerts
questions and new sensors: Claude Sonnet 5.5
```

## Run it

```bash
python3 -m venv prototype/.venv && prototype/.venv/bin/pip install -r prototype/requirements.txt   # once
prototype/.venv/bin/python prototype/server.py
```

Open http://127.0.0.1:8765 in Chrome and allow the camera. The server reads `ANTHROPIC_API_KEY` and `CAMERA_RTSP_URL` from the repo's `.env` and never sends them to the browser.

## Demo in five steps

1. **Draw zones.** Press *Desenhar zonas*, drag over a table or the door, and name the zone.
2. **Add things** in the app ("Chaves", "Caneca"), or let a sensor add them.
3. **Create a sensor with a sentence**, for example «Avisa-me se a caneca ficar na secretária».
4. **Start observing.** Put the mug on the desk: the alert slides into the phone.
5. **Ask** «Onde estão as chaves?». The answer comes with the last image.

*Analisar agora* forces one analysis. *Câmara do kit* asks the server for a frame from the RTSP stream; on 18 Nov the stream did not answer.

## Safety and cost

| What | Default | Change it with |
|---|---|---|
| Device actions (Light, Plug) | **Dry run.** The MCP call is shown in the activity log but not sent | `TT_LIVE_ACTIONS=1`. Needs `python3 mcp/client/chmcp.py login` first; the 16 Nov session has expired. The alarm is not wired on purpose |
| Spending cap | **3.00 USD per data folder.** The server refuses AI calls once it is reached, and a demo reset does not lift it | `TT_BUDGET_USD=5` |
| Call rate | At most one analysis every 2.5 s (server-side). The browser analyses every 3 s, and only zones that changed or have been quiet for 45 s | `OBSERVE_EVERY`, `HEARTBEAT` in `web/app.js` |
| Image size | Crops of the zones only, up to 640 px | `web/app.js` |

**Measured cost, 18 Nov, one call each:**

| Call | Model | Tokens in / out | Cost |
|---|---|---|---|
| Analyse one zone | Haiku 5.5 | 1,522 / 311 | 0.00031 USD |
| Create a sensor from a sentence | Sonnet 5.5 | 1,201 / 121 | 0.0036 USD |
| Answer a question | Sonnet 5.5 | 988 / 57 | 0.0026 USD |

**Example estimate:** an hour of watching one changing zone every 3 s is at most 1,200 analyses, or 0.37 USD. In practice it is far less, because unchanged zones are not sent.

## Files

| File | What |
|---|---|
| `server.py` | API: observe, ask, sensors, zones, things, kit frame, reset |
| `brain.py` | The three Claude calls, with structured JSON output and the spending cap |
| `store.py` | Memory in `data/state.json`, seeded with demo data (marked `demo`) |
| `actions.py` | MCP actions through `mcp/client/chmcp.py`; dry run unless `TT_LIVE_ACTIONS=1` |
| `web/` | The page: camera and zones (left), the Altice app with the Coisas tab (right) |
| `data/` | Runtime memory and zone crops. Gitignored; delete it to start fresh. The spending record lives here too |

**Privacy.** Only the drawn zones leave the browser, and only when they change. Crops are kept locally in `data/crops/` so the app can show "where it was seen". Nothing identifies people: the prompt forbids it.

**Not done yet:**
- deadline sensors («até às 18h») are implemented but untested;
- live MCP actions are untested on the kit (they need the login);
- the kit camera stream isn't answering;
- the demo clip for plan B hasn't been recorded.
