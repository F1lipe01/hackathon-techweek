# The MCP in practice

What the Connected Home MCP server actually exposes, from connecting to it on 16 Nov 2026 with the team account. This supersedes the guide where they differ. How to connect: [`mcp/README.md`](../mcp/README.md).

Raw material in the repo:

- [`mcp/tools-schema.json`](../mcp/tools-schema.json) — the server's full `tools/list` response, with every input schema.
- [`mcp/samples/`](../mcp/samples/) — real responses from the read tools, usable as mock data for offline development or a demo plan B.

## 18 tools, not 16

Names are lowercase on the real server (`get_home_devices`, not `GET_HOME_DEVICES`). Two tools are missing from the guide: **`get_device_timers`** and **`post_timer_device`**.

### Read (12)

| Tool | Parameters | Returns |
|---|---|---|
| `get_home` | — | Home id, name, security config, energy tariff, all devices with capabilities |
| `get_home_detail_report` | — | **Same as `get_home`** (its description is a copy of the "brief" one) |
| `get_home_status_brief` | — | Alarm state + device list with type and last-contact time (compact) |
| `get_home_devices` | — | All devices with full capability states |
| `get_home_rooms` | — | Rooms (none configured yet) |
| `get_home_scenarios` | — | Scenarios (none yet) |
| `get_scenario` | `scenarioId`* | One scenario |
| `get_device_details` | `deviceId`*, `techInfo`, `vendor` | One device |
| `get_device_timers` | `deviceId`* | Timers on a device |
| `get_device_recommendations` | — | Device inventory for maintenance advice; its description tells the model to group findings into URGENT / PREVENT / OPTIMIZATION / SECURITY |
| `get_home_security_status` | — | `status` (DISARMED / STAY / AWAY), `isAlarmed` |
| `get_home_security_alarm_history` | `page`*, `size`*, `startDate`, `endDate` | Past alarms |

### Write (6) — these change the real home

| Tool | Payload |
|---|---|
| `update_device_capabilities` | Finds a device **by natural-language name** (`deviceName`) or `deviceId`. `body` is one of: `{type:"power", value:"on"\|"off"}`, `{type:"brightness", value:0–100}`, `{type:"temperature", value:n}`, `{type:"color_rgb", redValue, greenValue, blueValue}` |
| `patch_home_security_status` | `body: {status: "disarm"\|"stay"\|"away", armDelay: [], alarmDelay: []}` — delays only when explicitly asked |
| `post_new_scenario` | `name`, `isActive`, `triggerLogic`, `triggers[]`, `startActions[]`, `endActions[]` — actions carry device + capability values (see schema) |
| `patch_scenario_activation` | `scenarioId`*, `isActive` |
| `post_execute_scenario` | `scenarioId`* |
| `post_timer_device` | `deviceId`*, `body` (scheduled action) |

## Safety findings

- **`patch_home_security_status` is mislabelled `readOnlyHint: true`.** It arms and disarms the alarm. A client that auto-approves "read-only" tools would arm the house unprompted. Our agent must require explicit confirmation for it whatever the annotation says, as the guide's own example agent does.
- **The Security hub exposes `factoryReset` and `restart` capabilities.** The write tool's schema only accepts power, brightness, temperature and colour, so they should not be reachable — but never attempt them.
- **Readings can be stale.** Every device carries `lastCommunicationTime`. On 16 Nov the Light's was **04 Nov** and the Camera's **09 Nov** — their values (bulb "on, 100 %") were cached from provisioning, not live. Any agent should check freshness before trusting a value, and say so. This is a nice, honest behaviour to show in the demo.

## The home, as the platform sees it (16 Nov, evening)

Home **"Hack 3"**, alarm **DISARMED**. Arm/alarm delays: **Away 30 s, Home (STAY) 0 s**. No rooms, no scenarios, energy tariff not set.

| Device | `type` | Capabilities (current value) | Last contact |
|---|---|---|---|
| Security hub | `gateway` | `alarmState` normal · `networkMode` **ethernet** (wifi/cellular possible) · `cellularState` none (no SIM) · `batteryLevel` **0** (charging) · `tamperState` normal · signal strengths · `restart`, `factoryReset` | live |
| Temperature sensor | `temperatureSensor` | `temperatureValue` 22.6 (−50..60) · `humidityValue` 64.3 % · `batteryLevel` 78 % | live |
| Smoke sensor | `smokeSensor` | `sensorState` normal/alarm · `tamperState` · `batteryStatus` high · `signalStrength` | live |
| Contact sensor | `contactSensor` | `sensorState` **alarm (= open)** · `tamperState` · `batteryStatus` · `signalStrength` | live |
| Plug | `plug` | `power` on · `instantPower` 0 W · `instantVoltage` 237 V · `instantCurrent` 0 · `todayConsumption` / `yesterdayConsumption` · `multiPower` (1 switch) | live (since hotspot) |
| Light | `bulb` | `power` · `brightness` 1..100 · `temperature` (white tone) 0..100 · **`workMode` colour / white / music / scene** → **colour bulb, confirmed** | **04 Nov** — not online |
| Camera | `camera` | `motionAlarmSwitch` · `motionDetected` · `motionSensitivity` 0–2 · `motionHumanoidFilter` (pet immunity) · **`sirenSwitch`** · `nightVisionMode` · `sdRecording` / `sdRecordMode` · `streamingSwitch` · `volume` 0–10 · flip/OSD/indicator | **09 Nov** — not online |

## What this unlocks

- The **colour bulb** can be a status light (red alarm, amber door left open, green all clear).
- The **camera has a built-in siren** and person-vs-pet motion filtering — an actuator, not just a sensor.
- The **plug** gives voltage, current, power and daily consumption — real energy data.
- **Contact + temperature/humidity + smoke + alarm state** are live context an agent can reason over.
- **Freshness** (`lastCommunicationTime`) lets an agent know when it *doesn't* know — "the light hasn't reported since 4 November, so I can't confirm it's off".
