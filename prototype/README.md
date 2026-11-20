# ThingTracker · prototype

The home's camera finds the things a family registered (a book, keys, a wallet), remembers where and when it saw them, and turns one sentence into a sensor: "tell me if I leave home without my book". Actions go to the Altice kit through its MCP server.

The page at http://127.0.0.1:8765 shows the kit camera on the left, with the boxes the models draw, and on the right a copy of the Altice app with a new **Things** tab and an **assistant** button. The activity log underneath shows what happened, including the exact MCP calls.

For the real end-to-end test in the lab, follow [docs/19-teste-real.md](../docs/19-teste-real.md).

## Run it

Start the three services in this order, each in its own terminal:

```bash
prototype/.venv-llm/bin/python prototype/llm_local.py      # 1. local text model, 127.0.0.1:8766
prototype/.venv/bin/python prototype/server.py             # 2. web app and API, http://127.0.0.1:8765
prototype/.venv-vision/bin/python prototype/edge.py        # 3. camera service on the kit camera
```

Optional: `prototype/.venv-vlm/bin/python prototype/judge.py` (the local vision-language judge, 127.0.0.1:8767).

The pitch site runs all of it on one page, on a demo home of its own (`data/demo/`), with the laptop's webcam as the camera:

```bash
prototype/.venv/bin/python prototype/site.py               # http://127.0.0.1:8780/site  (--fresh rebuilds the demo home)
```

One-time setup (Apple silicon; `ffmpeg` on the PATH):

```bash
python3 -m venv prototype/.venv && prototype/.venv/bin/pip install -r prototype/requirements.txt
python3.13 -m venv prototype/.venv-llm && prototype/.venv-llm/bin/pip install mlx-lm
python3 -m venv prototype/.venv-vision && prototype/.venv-vision/bin/pip install torch transformers pillow numpy opencv-python-headless
python3 -m venv prototype/.venv-vlm && prototype/.venv-vlm/bin/pip install mlx-vlm      # optional, for judge.py
```

The face models (YuNet and SFace, from opencv_zoo) are not in git: fetch them into `prototype/models/` and check their hashes as described in [AGENTS.md](../AGENTS.md). Without them the camera service reports every person as `not_visible`.

The server reads `ANTHROPIC_API_KEY` and `CAMERA_RTSP_URL` from the repo's `.env`. Never print or commit that file.

**One heavy job at a time.** The team laptop has 16 GB of memory. Renders, model runs on video clips and long encodes go through `video/tools/heavy.sh <command>`, and never run at the same time as a live test. See rule 5 in [AGENTS.md](../AGENTS.md).

## What each part does

| Part | File | What it does |
|---|---|---|
| Server | `server.py` | Serves the page and the API, keeps the home's memory, runs the rules engine, reads the door and sends actions. It is the only part that calls a language model (`brain.py`). |
| Camera service | `edge.py` | The part that would run in the home. It stays idle until a cheap motion check sees a change, then runs OWLv2 (detection) and DINOv2 (visual fingerprints) for a few seconds. It registers a thing from 8 views and recognises it again. It sends the server small crops of things and, for people, who, where and when, never the full frame. Two exceptions, both for alerts: one picture of the room when no person is in view, and the crop of an unknown face, which the server keeps only if a security rule fires. |
| Faces | `faces.py` | Opt-in, on the home device. YuNet finds a face inside a person box and SFace compares it with the family's templates, kept in the device's own `data/edge.db`. The server gets only the result: a person's id, `unknown` or `not_visible`. |
| Presence | `presence.py` | Who is home, from three signals: the family's phones on the Wi-Fi (simulated: no MCP tool exposes the router's clients), the door's contact sensor, and the faces each camera sees. States OCCUPIED, LEAVING, EMPTY, UNSURE, with a count and the reason. Every rule about an empty home reads it. |
| Judge | `judge.py` | Optional. Qwen2-VL-2B (4-bit, MLX, Apache-2.0). Asked only when an active check finds no match, on one tight crop of the place. Its "yes" or "unsure" becomes a question to the family; it never acts. |
| Replay | `replay.py` | A recorded lab take stands in for the camera (`TT_REPLAY=prototype/replays/<name>.json`). Only the door, the phones and hand-switched devices are replayed, each labelled "Replayed" in the activity; detection, presence and rules run live. |
| Pitch site | `site.py` | Builds the demo home and starts the server for the pitch page. |
| Local text model | `llm_local.py` | Qwen3-1.7B (4-bit, MLX, Apache-2.0), offline and free. It writes the assistant's answers and turns sentences into rules. The code decides the facts; the model only writes the words. |
| Kit camera | `kitcam.py` | Keeps one RTSP connection to the kit camera open while someone is watching and hands out the latest frame. |
| Actions | `actions.py` | Calls the MCP through `mcp/client/chmcp.py`: device reads (`get_home_devices` only) and the light and plug actions (dry runs by default). The alarm is always simulated. |
| Database | `store.py` | One SQLite file, `data/home.db` (below). |
| Web app | `web/` | The page: `index.html`, `app.js`, `app.css`. |

Claude is off by default. With `TT_AI=1`, Claude answers and compiles instead of the local model, capped by `TT_BUDGET_USD` (default 3 USD). With `TT_LLM=off`, keyword templates answer, at no cost.

## The data

`data/home.db` (SQLite). Everything in `data/` is runtime data and is never committed.

- **A copy of what the Altice platform holds:** `home`, `rooms` and `devices`. It starts as the app's state on 18 Nov 2026. While the MCP session is live, it is refreshed every 4 s.
- **What ThingTracker adds**, which in production would live in the platform's database, per customer:
  - `things`: what the user registered;
  - `fingerprints`: 8 DINOv2 vectors per thing;
  - `sightings`: where and when each thing was seen, with a small crop;
  - `presence`: where and when a person, child, dog or cat was seen, with no picture;
  - `phones` and `presence_state`: the simulated Wi-Fi phones and the presence engine's state;
  - `sensors`: the rules;
  - `events`: the activity log and notifications;
  - `spend`: what Claude calls cost.

The face templates live apart, in the home device's own `data/edge.db` (table `face_templates`), never in the server's database.

Each camera stands for one place, named after its room ("Work Room", "Kitchen 1").

## Sensors from one sentence

The assistant decides whether a sentence is a request or a question. A request ("tell me", "avisa-me", "notify me", "turn the light…") becomes a sensor. Anything else is a question, answered from the memory: "Where is my book?", "Onde está o livro?", "What did the camera see today?". The model compiles a sentence once. The rules engine then checks the rule locally, every few seconds, at no cost.

| Kind | Fires when | Example sentences |
|---|---|---|
| `leave_without` | The door opens and the thing's last known place is still at home. It also turns the light red. | "Tell me if I leave home without my book" · "Avisa-me se eu sair de casa sem o livro" · "Tell me if I forget my keys" |
| `not_by` | A dog, a cat, a person or a thing has not been at a place by a time, or within a window | "Tell me if the dog has not been at the food bowl by 20:00" · "Tell me if the cat has not been at the water bowl in 12 hours" |
| `nobody_by` | Nobody was in a place between two times (from 06:00 if no start time is given) | "Tell me if nobody has been in the kitchen by midday" · "Avisa-me se ninguém estiver na cozinha até ao meio-dia" |
| `left_for` | A thing stays on a place for N minutes | "Turn the light red if the book stays on the table for 30 minutes" |
| `nobody_for` | No movement and no people for N minutes | "Tell me if nobody moves for 30 minutes" |
| `someone_arrives` | A person (or a child, dog or cat) appears after none was seen for a while | "Tell me when someone arrives" · "Tell me when a child arrives home" |
| `seen_in` | A thing, or a dog, cat or person, is seen, optionally on a place | "Tell me when the dog is on the sofa" |

The sentence's own words set the kind, the times, the places and the action ("turn the light red", "switch the plug off"). The model writes only the title and the message.

The Things tab also suggests sensors for who lives at home:
- a dog or a cat seen clearly three times: food bowl by 20:00, and water bowl within 12 hours;
- a child seen clearly three times: tell me when a child arrives home;
- an older person living alone: nobody in the kitchen 06:00–12:00. This one is suggested only when the family declares it (`POST /api/profile {"kind": "older_alone"}`); the camera never guesses age.

`leave_without` has known limits, listed in `check_leave_without()` in `server.py`:
- the contact sensor says the door opened, not who opened it or which way they went;
- without a camera at the entrance, a thing that went out with its owner still counts as at home, so the rule also fires then.

## The door

The front door is the kit's Contact sensor (`sensorState` `alarm` means open).

- **Live.** Log in with `python3 mcp/client/chmcp.py login` (browser, team account). The server picks up the session within 15 s, with no restart. It then reads the devices every 4 s with the read-only tool `get_home_devices`. A change from closed to open starts the `leave_without` checks. The header pill says "devices live from the MCP".
- **Simulated.** While the session is not live, the **Simulate: door opens** button in the activity header opens the door and closes it 3 s later. Its events say "Simulated". The button is hidden while the real sensor is live.

## Actions: dry run by default

The only write tool the prototype uses is `update_device_capabilities`, on the kit's Light and Plug. By default nothing is sent: the activity shows the exact calls with "MCP dry run, not sent". For example, a red light is two calls by device id, power on and then `color_rgb` 255/0/0.

`TT_LIVE_ACTIONS=1` really changes the home. Set it only after the team's explicit approval, given in conversation. The alarm, scenarios and timers are never wired.

## Tests

```bash
prototype/.venv/bin/python prototype/test_scenarios.py
```

The test starts a private server on port 8775 with its own empty data folder, so it never touches the demo's database. It uses the same code and the same local model (or the templates, if the model is not running). It plays the camera service, the door (simulated, and the live path through a devices file), the phones and the assistant, and prints PASS or FAIL for:
- the presence engine;
- each rule kind, firing and staying quiet;
- leaving without a thing, someone who isn't Family, nobody home with devices on;
- the suggested sensors;
- the routing of questions and requests;
- the red-light calls and the simulated alarm;
- European Portuguese answers.

On 20 Nov 2026, 107 of 107 checks passed in about 3 minutes.

```bash
prototype/.venv/bin/python prototype/test_scenarios.py --unit      # the presence engine alone, on a test clock: 21 checks, no server
video/tools/heavy.sh prototype/.venv-vision/bin/python prototype/test_scenarios.py --vision   # the models on the lab footage (heavy)
```

`--server http://127.0.0.1:8765` runs it on the live server instead, and writes test data into that server's database.

## Switches

| Variable | Default | Effect |
|---|---|---|
| `TT_LIVE_ACTIONS` | off | `1` sends device actions to the real home (team approval first) |
| `TT_AI` | off | `1` lets Claude answer and compile, within `TT_BUDGET_USD` |
| `TT_LLM` | — | `off`: templates only; `local`: the local model even with `TT_AI=1` |
| `TT_LEAVE_ACTION` | `light_red` | The action of `leave_without` sensors when the sentence names none |
| `TT_DOOR_POLL_S` | `4` | Seconds between device reads while the MCP is live |
| `TT_PORT`, `TT_DATA` | `8765`, `data/` | Run a second server with its own data folder |
| `TT_TIMINGS` | `demo` | `prod` switches the presence timings from seconds to minutes |
| `TT_REPLAY` | — | A replay file (`prototype/replays/<name>.json`): a lab take stands in for the camera |
| `TT_DEVICES_FILE` | — | Read the devices from a file in the shape of `get_home_devices` instead of the MCP (used by the test) |

## Other scripts

| Script | What it does |
|---|---|
| `record.py` | Records a take: the kit camera's video plus the camera service's boxes, in `data/recordings/` (`--seconds 120 --name take`) |
| `record_demo.mjs` | Records the scripted product video (`web/demo.html`) with headless Chrome |
| `build_doc_pages.py` | Renders the team's documents for the page's document links (`web/docs/`, generated) |
| `vision/benchmark.py` | Times the local vision models on one image |

## Privacy

- **Pictures of things:** only small crops of registered things reach the server.
- **People and pets:** stored as who, place and time, with no picture. The exceptions are for alerts: a picture of the room with no person in view, and the crop of an unknown face, kept only when a security rule fires.
- **Faces:** opt-in. The templates stay on the home device; the server receives only a person's id, `unknown` or `not_visible`.
- **Recordings:** they stay on this machine. Use a take in a pitch only with the agreement of everyone in it, or blur them.
- **Claude:** off by default. With it off, no image and no text goes to a cloud language model.

## Icons

| Icons | Licence |
|---|---|
| Tabler Icons 3.19.0 (outline, for navigation): `web/icons/tabler/` | MIT |
| Microsoft Fluent Emoji, flat style (for things): `web/icons/fluent/` | MIT |
| TV remote: `web/icons/remote.svg` | Drawn by us in the same style; Fluent has no remote |
| Device icons: `web/icons/app/` | Cropped from our screenshot of the Altice app, to copy its screens |
