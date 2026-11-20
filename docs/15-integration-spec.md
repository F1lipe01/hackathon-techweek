# ThingTracker · integration with the Cognitive Home platform

Version 4, Friday 20 November 2026 (the final design, fully local, in the next section). For Altice Labs engineers. It describes what ThingTracker adds to the platform, what it reuses unchanged and what it needs from Altice. The overall design is in the [architecture document](14-architecture.md), whose figures this document reuses.

## Final design (20 Nov): fully local

The final design is stated at the top of the [architecture document](14-architecture.md): the home device (the router, if it has an NPU, or a dedicated box) does all the perception and inference, the rules engine and the language model included; the Altice platform is the control and data plane, text only. For the integration, this fixes what crosses the boundary between the home and the platform: events, labels, rules and commands, as text.

| Direction | What crosses, as text |
|---|---|
| Home → platform | Events as structured text (for example "book, desk, 18:02"); labels: a thing's name, a family member's name, "unknown face" or "face not visible"; alerts (title and message) for the push notification |
| Platform → home | Rules and scenarios; the metadata of things and people (names only), ownership links; door and Wi-Fi events; the family's commands from the app |
| Platform → devices | Device actions through the Connected Home MCP, after a "Yes" in the app |
| Never | Images, video, image regions, visual fingerprints, face templates |

Registration photos go from the phone to the home device: directly on the home Wi-Fi, or through an end-to-end-encrypted relay that Altice cannot read. The device builds the fingerprint. Where a section below sends image regions, photos or thumbnails to Altice, or runs vision, the rules or the language model at Altice, it describes the hybrid design of 19 Nov, the alternative evaluated, not chosen, because images would leave the home.

## In short

- ThingTracker turns the home's camera into a sensor configured with sentences: the user registers their things and writes rules such as "tell me if I leave home without my book".
- It adds a home device (the router with an NPU, or a dedicated box) that runs the cameras' vision, opt-in faces, the memory, the rules engine and the language model; a ThingTracker service at Altice that handles text only (metadata, the event log, alerts, the relay to the home); four MCP ("Model Context Protocol") tools for things, a new type of scenario trigger, and a proposed read-only tool for the phones on the home Wi-Fi.
- Device commands still go through the MCP tools the platform already has, after a "Yes" in the app. No new path to the devices is opened.
- To reach production, eight items are needed on Altice's side, listed in section 9. The most important are a way to receive door and Wi-Fi events without polling the MCP server, and knowing whether the routers have an NPU.

## 1. Glossary

| Term | Meaning |
|---|---|
| Home agent | A program on the Altice router's CPU (no AI accelerator). It applies the privacy masks, runs a cheap motion gate, cuts out the region that changed and, if the household opted in, recognises faces with YuNet and SFace. Face templates never leave the home |
| Vision workers | Hybrid alternative, not chosen: GPU servers at Altice (NVIDIA L4) that would run OWLv2 (detection) and DINOv2 (vectors) on the regions the homes send. In the final design, these models run on the home device |
| ThingTracker service | The platform component, stateless instances behind a load balancer. It is the MCP host and the only caller of the language models; it matches vectors with the fingerprints, tracks things and people, and runs the presence engine and the rules engine for each home |
| Presence engine | The part of the service that decides, for each home, OCCUPIED, LEAVING, EMPTY or UNSURE, from the family's phones on the Wi-Fi, the door sensor and the cameras |
| Rules engine | The part of the service that evaluates each home's compiled rules on every event and timer, and sends an alert when one is met |
| Visual fingerprint | Up to 8 numeric vectors (DINOv2 embeddings), one per photo, that tell a particular thing apart from others of the same kind; built and kept on the home device, never sent to Altice |
| Things tools | The four new MCP tools, described in section 5 |
| `thingTracker` trigger | A new type of scenario trigger, whose condition is about things or people and is evaluated by the rules engine in the ThingTracker service (section 7) |
| `get_home_wifi_clients` | A proposed read-only MCP tool that lists the devices connected to the home Wi-Fi (section 8) |

## 2. What is new and what is reused

New components:

| Component | Where it runs | What it does |
|---|---|---|
| Home agent | In the home, on the Altice router's CPU (the team's laptop in the demo) | Masks, motion gate, the changed region (at most 640 × 640, about once a second during motion), opt-in faces; reads a region on request, even without motion |
| Vision workers | Hybrid alternative, not chosen: Altice, on L4 GPUs. Final design: on the home device | OWLv2 boxes and DINOv2 vectors for the regions, the registration photos and the active checks |
| ThingTracker service | Altice platform | Turns sentences into rules and answers questions; matching, tracking, the presence engine and the rules engine, per home; alerts and MCP calls |
| Things tools | The platform's MCP server | `list_things`, `create_thing`, `get_thing_last_seen` and `get_thing_timeline` |
| `thingTracker` trigger | The platform's scenario model | Lets a scenario start when a condition on things or people is met |
| `get_home_wifi_clients` (proposed) | The platform's MCP server, from the router | Which family phones are on the home Wi-Fi, for presence |
| "Things" tab | Altice app | Registered things and people, sensors and suggestions, built from the same components as the other four tabs |
| Assistant button | Altice app, on every tab | Questions ("where is the book?") and sensors described in one sentence |

Existing MCP tools, used unchanged:

| Tool | Use |
|---|---|
| `update_device_capabilities` | Actions on the light, the plug and the camera's siren (`sirenSwitch`), after a "Yes" |
| `patch_home_security_status` | Arming the alarm, always after the user confirms |
| `post_new_scenario`, `get_home_scenarios` | Saving rules as scenarios and showing them in the app's scenario list |
| `get_home_devices` | The door contact sensor's state (polled today, until there is an event feed) and the devices that are on; context for the language model |
| `get_home_security_status` | The alarm's status, as context |

Alerts reach the phone through the Altice app's own notification service: the MCP server has no notification tool.

## 3. First example: "tell me if I leave home without my book"

Figure 1 shows the messages exchanged when the rule is met: the door, the phone, the active check, the alert and the optional judge.

![Sequence: the book left behind](architecture/seq-livro-esquecido.en.png)

**Figure 1** – The book left behind: messages between the home device, the door sensor and router, the Altice platform and the app.

In the final design, the language model and the rules engine run on the home device: the app sends the sentence there (through the relay when the family is away), and the platform keeps the resulting scenario as text. The steps below keep the names of the design of 19 Nov.

Creating the rule:
1. The user writes the sentence in the assistant. The app sends it to the ThingTracker service.
2. The service sends the language model the sentence, the registered things (the result of `list_things`), the home's devices (`get_home_devices`) and the list of available MCP tools.
3. The model returns a structured rule: when the front door closes after an opening and a family member has left, check the book's usual place; if the book is still there, alert the user.
4. The service saves the rule as a scenario, with `post_new_scenario`, using the new `thingTracker` trigger (section 7). The rule appears in the app's scenario list. In the final design, it is evaluated by the rules engine on the home device; the platform keeps the scenario as text.

When it is met (Figure 1):
5. The door sensor reports "open" and then "closed" to the platform (`sensorState: alarm` means open), and the service receives both events (today by polling `get_home_devices` every 4 s). The presence engine moves from OCCUPIED to LEAVING.
6. A family member's phone leaves the home Wi-Fi; the service learns it through the proposed `wifi.left` event (or `get_home_wifi_clients`). A family member has left.
7. The home device looks at the book's usual place, 3 frames about 1 s apart, regardless of motion, and analyses them itself; no image leaves the home.
8. Its vision finds the "book" boxes and their DINOv2 vectors and matches them with the book's 8 photos (cosine ≥ 0.62). Seen in at least 2 of the 3 frames, the rule is met and the app shows the alert with the book's thumbnail. Seen in fewer, the result is "unsure": no alert, or, if the book may be partly hidden, the rules engine may call the vision-language judge, whose "unsure" makes the app ask the family.

The language model is called only once, in step 2. From then on, the rule is evaluated by plain code, with no model in the decision unless the judge is called for an ambiguous moment.

## 4. Second example: "where is my book?"

In the final design, the question goes to the home device (through the relay when the family is away), whose language model and memory answer it; no sighting picture leaves the home.

1. The user writes the question in the assistant, a button on every tab of the app, which sends it to the ThingTracker service.
2. The service sends it to the language model, with the Things tools available.
3. The model calls `list_things`. If more than one thing matches the question (for example, two wallets), it answers with a question: "Which one?".
4. Once the thing is identified, the model calls `get_thing_last_seen`. The service answers from the last sighting stored in PostgreSQL for that customer.
5. The model answers in natural language ("On the desk, at 15:02"), and the app shows the cropped thumbnail of the thing.

## 5. The four Things tools

The new tools follow the conventions of the existing ones: JSON arguments, scope limited to the authenticated user's home, and results as JSON text. Only `create_thing` changes data.

### `list_things`

Lists the things registered in a home, with the last sighting of each one.

| Argument | Type | Required | Notes |
|---|---|---|---|
| `homeId` | string | No | Defaults to the user's current home, as in the other tools |

Result:
```json
{ "things": [
  { "id": "book", "name": "Book", "photo": "https://…/things/book.jpg",
    "lastSeen": { "place": "Living room 1", "surface": "desk", "at": "2026-11-19T18:02:10Z" } },
  { "id": "phone", "name": "Phone", "photo": null, "lastSeen": null }
] }
```

### `create_thing`

Registers a new thing. It saves the name and starts the registration of its photos (section 6).

| Argument | Type | Required | Notes |
|---|---|---|---|
| `name` | string, 1 to 40 characters | Yes | Name shown in the app, for example `"Book"` |
| `category` | string | No | English name the detector uses as its search term, for example `"book"`. Defaults to the name itself |
| `enrol` | enum: `photos`, `camera` or `none` | No | Defaults to `photos`: the app asks the user for 6 to 8 photos; `camera` asks them to show the thing to a camera |

Result: `{ "id": "book", "status": "enrolling" }`. Errors: `409` if the name already exists; `422` if `enrol` is `camera` and the home has no camera.

### `get_thing_last_seen`

Answers the question "where is X?".

| Argument | Type | Required | Notes |
|---|---|---|---|
| `thing` | Identifier or name | Yes | If the name matches several things, it returns the list so that the model can ask which one |

Result:
```json
{ "thing": "book", "place": "Living room 1", "surface": "desk",
  "at": "2026-11-19T18:02:10Z", "match": 0.70,
  "thumbnail": "https://…/sightings/9f2c.jpg" }
```
`match` is the similarity to the thing's visual fingerprint (from 0 to 1). If the thing has never been seen, the result is `{ "thing": "book", "seen": false }`. The thumbnail is a crop that shows only the thing, never the full image, served through a short-lived signed link.

In the final design, `photo` and `thumbnail` refer to pictures kept on the home device; the platform stores only the text fields. How the app fetches the picture while images stay in the home, for example over the end-to-end-encrypted relay, is still to be designed (document 14).

### `get_thing_timeline`

Shows where a thing has been over a period, for questions such as "when did I last have my glasses with me?".

| Argument | Type | Required | Notes |
|---|---|---|---|
| `thing` | Identifier or name | Yes | As in `get_thing_last_seen` |
| `from`, `to` | ISO 8601 date and time | No | Defaults to the last 24 h; at most 30 days |

Result: `{ "thing": "glasses", "sightings": [ { "place": "Living room 1", "from": "…", "to": "…", "state": "placed" }, … ] }`. Consecutive sightings in the same place are merged into one; `state` is `placed`, `in_hand`, `taken` or `moved`.

## 6. Registering a thing

Registration follows the pattern the app already uses to add a device (screen recording of the Altice app beta, 18 November 2026): the (+) button, a full-screen step with an illustration, a title and a main button fixed at the bottom, and the "Cancel installation" dialog on exit.

| Adding a device (today) | Adding a thing (proposal) |
|---|---|
| (+) on "Devices" | (+) on "Things" |
| List of device types and nearby Matter devices | What the cameras see ("Looking through your cameras…"), or a typed name |
| "Choose a security hub" panel | "Take photos" or "Show it to a home camera" |
| "No smart hub installed" panel | "No camera installed" panel, when showing it to a camera (error `422` from `create_thing`) |
| Serial number or "Scan label" | The photos, or the camera with live progress |
| Final step | The learned photos and the name, followed by "Done" |

The photos are made in one of two ways:
1. **Phone photos.** The app sends 6 to 8 photos from different sides (or frames of a short video) to the home device, directly on the home Wi-Fi or through an end-to-end-encrypted relay that Altice cannot read. The home device finds the thing in each photo with OWLv2, using the English name as the search term, and DINOv2 makes a vector of each crop.
2. **Shown to a camera.** The user holds the thing about 50 cm from a camera and turns it slowly for 10 to 20 seconds. The home device finds the thing and makes a vector of each crop; a photo is kept only if it differs from the previous ones (cosine below 0.97), until there are 8.

The photos make up the visual fingerprint, kept on the home device, and the best crop becomes the thing's photo; neither leaves the home. The platform keeps the thing's metadata as text (name, owner, scenarios), so a replaced box gets back the list of things, but their photos are registered again. The fingerprint is deleted when the thing is deleted.

After registration, whenever there is motion, the home device finds candidates of the same kind and compares each vector with the photos. Only a candidate that is similar enough (cosine ≥ 0.62) counts as "your book"; the others are ignored.

## 7. Sensors and scenarios

Each sentence from the user becomes a rule, compiled once by the language model.

- Conditions and actions on devices (door contact, light colour, plug) already map onto the platform's scenario model.
- Conditions on things and people ("book still on the desk after someone left", "no one in the living room for 30 minutes") have no equivalent among today's triggers. We therefore propose the `thingTracker` trigger, evaluated by the rules engine in the ThingTracker service. When the condition is met, the service marks the trigger as met (`sensor.fired`) and the platform runs the scenario's start actions; an action the family chose to confirm waits for a "Yes" in the app.

The scenario of the first example, in the `post_new_scenario` format. The tool's schema types `triggerLogic` and `operator` as free strings and lists no accepted values ([`mcp/tools-schema.json`](../mcp/tools-schema.json)), so the values below are an assumption to agree with Altice:
```json
{ "name": "Left without the book", "isActive": true, "triggerLogic": "AND",
  "triggers": [
    { "type": "thingTracker",
      "condition": { "door": "<front door contact sensor>", "on": "closed_after_open", "leaver": "family",
                     "thing": "book", "check": "usual_place", "seen_at_least": "2/3" } } ],
  "startActions": [
    { "type": "notification", "message": "Your book stayed at home." } ] }
```

The door is part of the `thingTracker` condition, because "closed after an opening" and "a family member left" are worked out by the service from the door's reports and the presence engine. The door contact sensor reports an open door as `sensorState` with the value `alarm`, as observed on the challenge kit. The family marks which contact sensor is the entrance door. The alert is delivered by the app's notification service, not by an MCP tool. Today's scenario actions carry only a device and capability values, with no notification type ([document 10](10-mcp-in-practice.md)), so the `notification` action above is part of the proposed extension.

## 8. Connection between the home agent and the platform

| Aspect | Proposal |
|---|---|
| Connection | The home agent opens a single outbound connection to the platform (MQTT over mutual TLS), through a load balancer to a broker; the home needs no open inbound port |
| Identity | One certificate per home, issued when the camera is added in the app and revocable from it |
| From the home to the platform | Text only: events (for example "book, desk, 18:02"); labels (a thing's name, a family member's name, "unknown face" or "face not visible"); alerts for the push notification. Never images, video, image regions, fingerprints or face templates. (The hybrid alternative, not chosen, would have sent the changed region, at most 640 × 640, about once a second during motion) |
| From the platform to the home | Rules and scenarios; metadata (names of things and people, ownership links); door and Wi-Fi events; the family's commands; privacy masks; orders to delete face templates. The registration photos and the face video pass only through the end-to-end-encrypted relay, which Altice cannot read, when the phone is not on the home Wi-Fi |
| Door | Today, the service polls `get_home_devices` every 4 s; with an event feed, door events would arrive at once |
| Phones on the Wi-Fi | The proposed read-only `get_home_wifi_clients` tool (each client's MAC address, name, band and "connected since"), with `wifi.joined` and `wifi.left` events; the family pairs each phone with a person once, in the app |
| Offline | The analysis and the rules run on the home device; without internet, the notifications and the device actions, which are platform services, cannot reach the family. The home device keeps events and labels in a queue, as text, and sends them when the connection returns |
| Language models | On the home device (Qwen3-1.7B in the prototype), text only; it never decides. An external model (the user's own ChatGPT or Claude) is a possible future opt-in, text only; not now |

## 9. What we ask of Altice

| No. | Need | Why | Current situation |
|---|---|---|---|
| 1 | An event API, with push or webhooks, for the door and the Wi-Fi | Rules must react to the door closing without polling | The MCP has no push notifications and no general event feed; there is only the alarm history (`get_home_security_alarm_history`) |
| 2 | A read-only `get_home_wifi_clients` tool | Presence needs the family's phones; no camera sees someone who has left | The router sees the clients, but no tool exposes them |
| 3 | Local RTSP access to the camera from the router | Video should stay on the home network | Video goes through a cloud relay (go2rtc) |
| 4 | Whether the routers or cameras have an NPU | With one, the router is the home device (about €15 more per router, an estimate; option A1 in document 17); without one, the customer buys a dedicated box (document 17) | The kit's LTE hub cannot run vision models |
| 5 | A way to add tools to the MCP server | For the four Things tools and the `thingTracker` trigger | The server's 18 tools are set by Altice; a client cannot add tools |
| 6 | A tool to delete scenarios | Users must be able to remove sensors | The MCP can create scenarios but not delete them |
| 7 | Push notifications to the app | For the rules' alerts | The app has a notification service; the way ThingTracker calls it is to be agreed with Altice in the pilot |
| 8 | Contracts or GPU capacity for the models | Not needed in the final design: the models run on the home device. Only for the hybrid alternative, not chosen | The prototype runs a local model (Qwen3-1.7B) |

## 10. Status of the prototype

| Item | In the prototype (`prototype/` folder) |
|---|---|
| Home device | One program on the team's laptop (`edge.py`) plays the home device's eyes: the motion gate, faces with YuNet and SFace, and OWLv2 and DINOv2 on the laptop's GPU, on the whole frame |
| Registration | From phone photos and from 8 photos taken by the camera; the fingerprint is stored in a copy that stands for the platform's database |
| Presence engine | `presence.py`: the four states, from the simulated phones, the door and the cameras |
| Door | Read by polling `get_home_devices` every 4 s when the MCP session is live; a simulated door otherwise |
| Sensors | Created from a sentence and evaluated by the server's rules engine (`server.py`), in a loop every 2 s; actions on devices are a dry run unless switched on, and the alarm is always simulated |
| Things tools | Available as HTTP endpoints of the team's server (`/api/state`, `/api/things`, `/api/ask`), with the same data |
| Database | Local SQLite (`prototype/data/home.db`) in place of PostgreSQL |
| App | A faithful copy of the Altice app (screens, sizes, colours and transitions captured from the beta on 18 November 2026), with the "Things" tab, the assistant button and the alerts |
| Home ↔ platform connection | A single local server plays both roles; the camera stream comes through the organisers' relay |
