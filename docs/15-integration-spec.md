# ThingTracker · integration with the Cognitive Home platform

Version 1, Wed 18 Nov 2026. Audience: Altice Labs engineers. What ThingTracker adds to the platform, and what it needs from it. The overall design is in [14-architecture.md](14-architecture.md).

## 1. Summary

| ThingTracker adds | ThingTracker uses, unchanged |
|---|---|
| Four MCP tools for things: `list_things`, `create_thing`, `get_thing_last_seen`, `get_thing_timeline` | `update_device_capabilities` (light, plug) |
| An edge service per home, connected to the platform over one authenticated channel | `patch_home_security_status` (alarm), always behind a user confirmation |
| A Things tab in the Altice app | `post_new_scenario`, `get_home_scenarios` (rules shown as scenarios) |
| | `get_home_devices`, `get_home_security_status` (context for rules) |

No new path to devices: every device command still goes through the platform's existing tools.

## 2. The four Things tools

They follow the existing tools' conventions: JSON arguments, scoped to the authenticated user's home, JSON text results. They are read-mostly; only `create_thing` writes.

### `list_things`

Lists the things a home tracks, with their last sighting.

| Argument | Type | Required | Notes |
|---|---|---|---|
| `homeId` | string | no | Defaults to the user's current home, like the other tools |

Result:
```json
{ "things": [
  { "id": "keys", "name": "Keys", "photo": "https://…/things/keys.jpg",
    "lastSeen": { "place": "Hall table", "camera": "Living room", "at": "2026-11-18T08:42:10Z" } },
  { "id": "phone", "name": "Phone", "photo": null, "lastSeen": null }
] }
```

### `create_thing`

Starts tracking a thing. Fingerprints are made on the edge during enrolment (§4); this tool registers the name and starts that flow.

| Argument | Type | Required | Notes |
|---|---|---|---|
| `name` | string, 1–40 | yes | "Keys", "Mia's water bowl" |
| `category` | string | no | Hint for the detector: "keys", "wallet", "mug"… |
| `enrol` | enum `camera` / `photos` / `none` | no | Default `camera`: the app then asks the user to show the thing to a camera |

Result: `{ "id": "keys", "status": "enrolling" }`. Errors: `409` if the name exists, `422` if the home has no camera.

### `get_thing_last_seen`

Answers "where is X?".

| Argument | Type | Required |
|---|---|---|
| `thing` | id or name | yes |

Result:
```json
{ "thing": "keys", "place": "Hall table", "camera": "Living room",
  "at": "2026-11-18T08:42:10Z", "confidence": 0.86,
  "position": "next to the bowl", "thumbnail": "https://…/sightings/9f2c.jpg" }
```
`null` fields and `"seen": false` if it was never seen. The thumbnail is a crop of the thing only, never the full frame.

### `get_thing_timeline`

Where a thing has been over a period: "when did I last have my glasses?".

| Argument | Type | Required | Notes |
|---|---|---|---|
| `thing` | id or name | yes | |
| `from`, `to` | ISO 8601 | no | Default: the last 24 h; at most 30 days |

Result: `{ "thing": "glasses", "sightings": [ { "place": "Desk", "from": "…", "to": "…" }, … ] }`, with consecutive sightings in the same place merged.

## 3. Edge service ↔ platform

| Aspect | Proposal |
|---|---|
| Connection | The edge opens **one outbound** connection to the platform (WebSocket or MQTT over TLS); no inbound ports in the home |
| Identity | One credential per home edge, issued when the camera is added in the app; revocable from the app |
| Edge → platform | Events (`thing.seen`, `thing.moved`, `sensor.fired`), thumbnails of things, answers to the Things tools |
| Platform → edge | Rules (compiled sensors), Things tool calls, "enrol now" requests, masks and places |
| Offline | The edge keeps tracking and evaluating local rules; events queue and are sent when the link returns; device actions need the platform |
| Language model | Called by the platform, never by the edge. The platform decides which model and region are used |

## 4. Enrolment and the app

1. App: Things → (+) → name (or pick a suggestion) → "Show it to the camera".
2. Platform → edge: `enrol(thing, camera)`.
3. Edge: for about 3 s, detects the thing in the frames, keeps ~8 crops, computes the fingerprint, and returns a photo.
4. App: shows the photo; the user confirms or retries.

The fingerprint stays on the edge. Deleting the thing deletes it.

## 5. Sensors and scenarios

A sensor from a sentence is compiled by the language model into a rule (see [14-architecture.md §5](14-architecture.md)).

- **Device conditions and actions** (door contact, light colour, plug) map onto the platform's scenario model, so the rule appears in the app's Scenarios list.
- **Conditions on things and people** ("mug on the desk for 10 min") have no equivalent in today's scenario triggers. We propose a new trigger type, `thingTracker`, evaluated by the edge. The edge reports `sensor.fired`, and the platform runs the scenario's start actions.

Proposed trigger, in the same shape as today's device triggers:
```json
{ "type": "thingTracker",
  "condition": { "thing": "mug", "in_place": "desk", "for": "10m", "home": "empty" } }
```

## 6. What we need from the platform

| # | Need | Why | Today |
|---|---|---|---|
| 1 | An **event or push API**, or webhooks | Sensors must react to the door opening without polling | MCP has no events; we would have to poll |
| 2 | **Local RTSP access** to the camera | Video should stay on the home network | Stream goes through a cloud relay (go2rtc) |
| 3 | **Edge compute** in the home | Perception needs about 0.5 s per frame on a laptop GPU | The kit's LTE hub can't run vision models |
| 4 | A way to **register new MCP tools** | For the four Things tools | Unknown |
| 5 | **Delete scenarios** | Users must be able to remove sensors | No delete tool today |
| 6 | **Push notifications** to the app | Alerts | Unknown which service the app uses |
| 7 | **Language model contracts** | No training on data, DPA, EU processing | Unknown which providers Altice already uses |

## 7. Status of the prototype

| Spec item | In the prototype (`prototype/`) |
|---|---|
| Things tools | As HTTP endpoints of our server (`/api/state`, `/api/things`, `/api/ask`), same data and behaviour |
| Sensors | Created from a sentence; stored as rules; device actions through our MCP client, dry run unless switched on |
| Enrolment | Planned; zone crops are used today |
| Edge ↔ platform channel | One local server plays both roles |
