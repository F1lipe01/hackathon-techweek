# Platform capability model

What the Connected Home platform can actually do, reverse-engineered from the app's own UI string catalogs (`strings_enus.json`, `strings_ptpt.json`) inside the APK. This is static research from the app the organisers gave us — no credentials, no secrets, just the feature vocabulary. It tells us what the agent can read and drive through the MCP, and what each kit device exposes (confirmed live in [10-mcp-in-practice.md](10-mcp-in-practice.md)).

Source: 2009 UI strings across sections — `deviceDetails` (233), `onboardDevice` (223), `addScenario` (120), `securitySettings` (73), `energy` (33), `cameraRecordings` (19), plus Wi-Fi/parental-control features that are out of scope for us.

## Device capabilities

Capabilities the platform models on devices (from `addScenario_triggerCard_*` and `deviceDetails_*`). Each can be **read** (state/trigger) and, where it makes sense, **written** (action):

| Capability | Read | Write | On our kit |
|---|---|---|---|
| Power (on/off) | ✓ | ✓ | Plug, Light |
| Brightness | ✓ | ✓ | Light |
| Color | ✓ | ✓ | Light (a colour bulb, confirmed through the MCP) |
| Temperature value | ✓ | — | Temperature sensor |
| Humidity value | ✓ | — | Temperature sensor |
| Motion detected / motion-detection switch | ✓ | ✓ (switch) | Camera |
| Sensor state (open/closed) | ✓ | — | Contact sensor |
| Smoke detected | ✓ | — | Smoke sensor |
| Alarm state (alarm/normal) | ✓ | ✓ | Security hub |
| Tamper state | ✓ | — | Sensors, hub |
| Battery status / battery level | ✓ | — | Battery sensors |
| SD-card recording (state, type) | ✓ | ✓ | Camera |
| Volume | ✓ | ✓ | Camera |
| Multi-switch (multiplug) | ✓ | ✓ | — (we have a single plug) |

## Event / notification types

Things the platform can notify on (`deviceDetails_common_subscription*`, `_history_*`). These are the hooks an agent can react to:

- Motion is detected
- Contact sensor opened / closed
- Smoke detected
- Device tampered
- Device battery low
- Switched to 4G cellular backup / battery backup
- Charge state / network mode / sensor state switched
- Remote-controller buttons: Arm away, Arm home, Disarm, **SOS**
- Alarm state changed (alarm / normal)

## Automation engine (scenarios)

The platform has a real rules engine, reachable through the scenario MCP tools (`POST_NEW_SCENARIO`, `POST_EXECUTE_SCENARIO`, etc.).

- **Triggers:**
  - **Schedule** — a time, repeated on chosen weekdays, with optional start/end date and time.
  - **Device capability** — any readable capability above (power, brightness, temperature, humidity, color, alarm state, sensor state, motion, battery status/level, tamper, SD recording).
- **Operators** on numeric capabilities: **less than**, **equal to**, **greater than**.
- **Trigger logic:** *any* of the triggers (OR) or *all* of them (AND).
- **Actions:** set device capabilities (power, brightness, color, temperature, alarm state, recording, …). Multiple actions per scenario.

So "if humidity > 70 % then turn the plug on", or "every weekday at 08:00 set the light to warm white", are native. The agent's job is to turn intent into these.

## Security model

- **Modes:** **Away**, **Home** (the API's `STAY`), **Off** (disarmed). Arming runs a countdown.
- **Per-mode device sets:** "Away mode devices", "Home mode devices", and "Always active (24h)" devices that trigger regardless of mode.
- **Alarm trigger types:** intrusion / motion, **fire** (smoke), tamper, low battery, emergency / SOS.
- On alarm: live cameras, emergency contacts, "False alarm" to dismiss.
- Maps to MCP tools `GET_HOME_SECURITY_STATE`, `PATCH_HOME_SECURITY_STATUS`, `GET_HOME_SECURITY_ALARM_HISTORY`.

## Energy model

- Per-device and whole-home: consumed energy, produced energy (solar), current, power, voltage, live/instant measures.
- Costs: monthly/yearly cost, configurable **tariff** and currency.
- Warning about double-counting if both an energy meter and an energy device are selected.
- Our **plug meters energy**, so this is live data we can use.

## Camera model

- Recording to **SD card** and **cloud**; **continuous** or **motion-triggered**.
- Motion sensitivity, **pet immunity** (humanoid filter), volume, live view.
- Cloud recording can be triggered by events (e.g. on alarm).

## Protocols and onboarding

- The platform speaks **Matter**, **Thread** and **Zigbee** (`common_matter/thread/zigbee`), plus Wi-Fi for cameras/plugs/lights and the SmartWiFi mesh.
- Devices onboard by QR code or serial number. Our kit is pre-provisioned, so we skip this.

## What this means for our solution

- The agent is not limited to on/off. It can **read** temperature, humidity, motion, contact state, smoke, battery, tamper and energy, and **act** by setting device capabilities, creating/executing scenarios, and arming/disarming security.
- The richest real signals on our kit: **temperature + humidity** (live), **contact open/closed**, **smoke**, **security arm state**, and **plug energy**. The camera adds vision once it is on Wi-Fi.
- The ficha asks us to go "beyond commands" and combine **context, intention, information and action**. The platform already supplies the information (sensor states, energy, events) and the action surface (capabilities, scenarios, security) — our value is the reasoning layer on top.

See [08-app-and-apk.md](08-app-and-apk.md) for how this was extracted, and [03-mcp-connected-home.md](03-mcp-connected-home.md) for the MCP tools these map onto (18 on the live server, [10-mcp-in-practice.md](10-mcp-in-practice.md)).
