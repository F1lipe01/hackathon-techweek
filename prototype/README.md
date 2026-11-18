# ThingTracker · prototype

The camera becomes the home's source of information, and one sentence creates a new sensor.

- **Left: the camera.** Use the webcam, a recorded clip played as if it were live, or the kit camera. You draw the zones the system may look at.
- **Right: a copy of the Altice app,** in its light theme, in English, with its colours and device icons taken from our screenshots. It has a new fifth tab, **Things**:
  - an "Ask" box;
  - your things, with where and when each was last seen;
  - sensors created from one sentence;
  - alerts.

```
browser: camera → zones → crops (only zones that changed)
   → server: Claude Haiku 5.5 (what is visible, sensor answers) → memory → rules → MCP action
   → app: Things tab, alerts
questions and new sensors: Claude Sonnet 5.5
```

## Run it

```bash
python3 -m venv prototype/.venv && prototype/.venv/bin/pip install -r prototype/requirements.txt   # once
prototype/.venv/bin/python prototype/server.py            # AI OFF: simulated answers, costs nothing
TT_AI=1 prototype/.venv/bin/python prototype/server.py    # real Claude calls (costs money, capped)
```

Open http://127.0.0.1:8765 in Chrome and allow the camera. `#devices` or `#menu` at the end of the address opens that tab.

**The AI is off by default.** Every analysis, answer and new sensor is then simulated from local data and marked "(simulated)". Use this mode to test the layout and the whole flow for free. The badge at the top right says which mode is on.

## Demo in five steps

1. **Draw zones.** Press *Draw zones*, drag over a table or the door, and name the zone.
2. **Add things** with the (+) at the top of the Things tab, or let a sensor add them.
3. **Create a sensor with one sentence**, for example "Turn the light red if the mug is left on the desk". Portuguese works too.
4. **Start watching** and put the mug on the desk. The alert slides into the phone.
5. **Ask** "Where are my keys?". The answer comes with the last picture of them.

*Analyse now* forces one analysis. *Kit camera* asks the server for a frame from the kit's RTSP stream; on 18 Nov the stream did not answer.

## Safety and cost

| What | Default | Change it with |
|---|---|---|
| AI | **Off.** Simulated answers, nothing sent to Claude | `TT_AI=1` |
| Device actions (Light, Plug) | **Dry run.** The MCP call is shown in the activity log but not sent | `TT_LIVE_ACTIONS=1`. Needs `python3 mcp/client/chmcp.py login` first. The alarm is not wired on purpose |
| Spending cap with the AI on | **$3 per data folder.** A demo reset does not lift it | `TT_BUDGET_USD=5` |
| Call rate | At most one analysis every 2.5 s (enforced by the server). The browser analyses every 3 s, and only zones that changed or have been quiet for 45 s | `OBSERVE_EVERY`, `HEARTBEAT` in `web/app.js` |

**Measured cost with the AI on, 18 Nov:**

| Call | Model | Cost |
|---|---|---|
| Analyse one zone | Haiku 5.5 | $0.0003 |
| Create a sensor from a sentence | Sonnet 5.5 | $0.0036 |
| Answer a question | Sonnet 5.5 | $0.0026 |

An hour of watching one zone that keeps changing is at most 1,200 analyses, about $0.37.

## Icons

| Icons | Licence |
|---|---|
| Tabler Icons 3.19.0 (outline, for navigation): `web/icons/tabler/` | MIT |
| Microsoft Fluent Emoji, flat style (for things): `web/icons/fluent/` | MIT |
| TV remote: `web/icons/remote.svg` | Drawn by us in the same style; Fluent has no remote |
| Device icons: `web/icons/app/` | Cropped from our screenshot of the Altice app, to copy their screen |

## Files

| File | What |
|---|---|
| `server.py` | API: observe, ask, sensors, zones, things, kit frame, reset |
| `brain.py` | The three Claude calls (structured JSON output, spending cap) and the simulated versions |
| `store.py` | Memory in `data/state.json`, seeded with demo data (keys, wallet, glasses, phone, mug, laptop, TV remote) |
| `actions.py` | MCP actions through `mcp/client/chmcp.py`; dry run unless `TT_LIVE_ACTIONS=1` |
| `web/` | The page: the camera and zones on the left, the Altice app with the Things tab on the right |
| `data/` | Runtime memory and zone crops. Gitignored; delete it to start fresh |

**Privacy.** Only the zones you draw leave the browser, and only when they change. Crops are kept locally in `data/crops/` so the app can show where a thing was seen. The AI is told never to identify people.
