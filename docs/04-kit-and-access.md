# Hardware kit and access

Sources: photos of the kit taken on 16 Nov ([`sources/kit/`](../sources/kit/)), challenge-room Q&A in the kick-off transcript (lines 164–293), Slack DM with Rui Mendes, team Slack.

## The kit

- Collected from Altice Labs in Aveiro. The pick-up was arranged for Fri 13 Nov.
- Every device is already provisioned on Altice's platform and linked to our team account. No pairing is needed.
- The table says what the hardware is. What the platform exposes for each device is **not confirmed yet**: fill in the last column once the kit is online, from the app or from `GET_HOME_DEVICES`.

The home is named **"Hack 3"** in the app, with all seven devices "Without room". The states below were read from the app on 16 Nov, with the gateway cabled to ethernet but no Wi-Fi network up yet.

| Device (app name) | State, 16 Nov | Hardware | Radio / link | Capabilities |
|---|---|---|---|---|
| **Security hub** | On | LTE IoT Gateway **MS-WES1AS** (label 424) | RJ45 / Wi-Fi 2.4 / LTE uplink; **Zigbee + 433/868 MHz** down to the devices | The hub the sensors run through, and the security system itself. Not a Wi-Fi access point |
| **Temperature sensor** | On — **20.8 °C, 48.3 %** | Nedis **ZBSC10WT** (label 689) | Zigbee, via the hub | Temperature + humidity, live. Only **one** unit is paired (the app lists one), even though two round discs were in the kit |
| **Smoke sensor** | On | Photoelectric, EN 14604 (label 349) | via the hub | Smoke events; 85 dB siren, test/hush, low-battery warning |
| **Contact sensor** | **Open** | **MS-D3D** oval (label 685) | RF, via the hub | Open / closed state of a door or window. **Confirmed a contact sensor** |
| **Camera** | Disconnected | Tuya **SC034-WNV3** (label 346) | **Wi-Fi 2.4 GHz only**, IP65 | RTSP feed; HD video, motion detection, two-way audio, SD/cloud. Needs the Wi-Fi network |
| **Plug** | Disconnected | Unbranded Schuko plug | **Wi-Fi** | On/off **and energy metering** (the app has an Energy page for it). Needs the Wi-Fi network |
| **Light** | Disconnected | Unbranded E27 bulb | **Wi-Fi** | On/off; colour vs white still to confirm. Needs the Wi-Fi network |

**The connected/disconnected split proves the two radio paths.** The four devices that were *On* (hub, temperature, smoke, contact) talk to the Security hub over Zigbee/RF, and the hub is online via its ethernet cable — so they work with no Wi-Fi. The three that were *Disconnected* (camera, plug, light) are **Wi-Fi** devices and stay offline until we create the 2.4 GHz network.

What the kit does not have: a thermostat, any valve or pump, a soil-moisture sensor, a motion sensor, a siren other than the smoke alarm's own. The single smart plug is the only general-purpose actuator.

Clean images of each device, for diagrams and slides, are in [`assets/devices/`](../assets/devices/).

## How it connects

```mermaid
flowchart LR
  subgraph KIT["Our kit"]
    CS["Climate sensor"]
    SA["Smoke alarm"]
    DS["MS-D3D sensor"]
    PB["Smart plug and bulb"]
    GW["LTE IoT Gateway<br/>MS-WES1AS"]
    CAM["Camera<br/>SC034-WNV3"]
  end
  WIFI["2.4 GHz Wi-Fi we provide<br/>hotspot or access point"]
  ETH["Wired internet<br/>lab ethernet"]
  PLAT["Altice platform"]
  MCP["Connected Home<br/>MCP server"]
  RTSP["RTSP relay<br/>go2rtc"]
  APP["Mobile app"]
  AGENT["Our agent"]

  CS -. "Zigbee" .-> GW
  SA -. "Zigbee or 868 MHz" .-> GW
  DS -. "Zigbee or 868 MHz" .-> GW
  PB -. "if Zigbee" .-> GW
  PB -. "if Wi-Fi" .-> WIFI
  GW -- "RJ45" --> ETH
  GW -. "or Wi-Fi, or LTE" .-> WIFI
  CAM -- "Wi-Fi" --> WIFI
  ETH --> PLAT
  WIFI --> PLAT
  PLAT --> MCP --> AGENT
  PLAT --> RTSP --> AGENT
  PLAT --> APP
```

Solid lines are known. Dotted lines are inferred and still to confirm.

The point that tripped us up on 16 Nov: **the gateway does not create a Wi-Fi network.** Plugging it into ethernet gives the gateway its own uplink and nothing else. The camera still needs a Wi-Fi network that we provide.

## Bringing it online

### 1. Gateway

Power it and give it an uplink. The simplest is a cable into a port with internet access.

Its front panel has four lights: power, Wi-Fi, a padlock and a link symbol. On 16 Nov, cabled to the lab's ethernet, power was green, link was blue, and Wi-Fi and the padlock were off. We have no manual, so the reading is ours: link shows the wired uplink, and the padlock probably shows whether the security system is armed.

The back panel has, from left to right: a speaker grille, the RJ45 port, a SIM-card slot, two recessed buttons marked with a link symbol and a power symbol, and the DC power input (`sources/kit/gateway-back.jpg`). Cable in the RJ45 port and power in DC is all it needs. Leave the SIM slot empty and **do not press the recessed buttons**: one of them is probably what reset another team's gateway.

A managed lab network may refuse an unregistered device even though the cable is in and a light is on. **The test is the app:** if the gateway shows offline there, either get the device allowed on the lab network or unplug the cable so it falls back to Wi-Fi.

### 2. Wi-Fi for the camera

Create a network with exactly the name and password in `.env` (`KIT_WIFI_SSID`, `KIT_WIFI_PASSWORD`). All kits were provisioned on one access point at Altice Labs, so they all look for that network.

- It has to be on **2.4 GHz**. The camera's box says "Connect with 2.4G Wi-Fi".
- Name and password are case-sensitive.
- Use WPA2 security.

Ways to create it:

| Option | How |
|---|---|
| Android hotspot | Settings → hotspot and tethering → Wi-Fi hotspot. Set the name and password, and set the band to 2.4 GHz. Menu names vary by brand |
| iPhone hotspot | The hotspot name is the phone's name: Settings → General → About → Name. Set the password under Personal Hotspot and turn on Maximise Compatibility, which forces 2.4 GHz |
| Spare router or access point | Set the SSID and password, enable 2.4 GHz, and plug it into a port with internet access. A Ubiquiti UniFi access point showing a steady white light is in factory-default state: it broadcasts nothing until it is adopted and given a Wi-Fi network in the UniFi Network app or controller |
| Mac | Only if the Mac itself is on wired ethernet: System Settings → General → Sharing → Internet Sharing, from Ethernet to Wi-Fi, with the same name and password |

The phone that hosts the hotspot can still run the app. Whatever the camera streams travels over that phone's mobile data, so a router on wired internet is the better choice for long sessions.

### 3. Check every device in the app

Each one should show as online. Note what the app calls each device and its room, and fill in the table above.

### 4. Camera

In VLC, open a network stream and paste `CAMERA_RTSP_URL`.

### 5. MCP

Connect an MCP client and log in with the team account. See [03-mcp-connected-home.md](03-mcp-connected-home.md).

## Things to know

- **The climate sensor is slow by design.** Its box gives an update interval of 5 to 30 minutes, so a temperature change will not show up live in a demo.
- **If every device is online in the app and something fails through the MCP, the devices are not the problem.** This is the mentors' rule of thumb.
- **Do not reset the gateway.** It happened to another team: the devices then have to be added again through the app. If it happens, ask the mentors. Someone called Marta on the Altice side knows this process well.
- The camera's serial number and MAC address are on its label and on the back of its box (`sources/kit/camera-box-back.jpg`).

## Mobile app

- Distributed through Firebase App Distribution. The invite was emailed to the team representative (Filipe). The link is in `.env` as `APP_INVITE_URL`. It is unclear whether one invite works on several phones.
- **More invites:** message Hugo Dias on Slack. He offered to send invites to other team members.
- **iPhone:** the app is blocked at first as an untrusted enterprise developer. The mentors said to mark the developer (Altice Labs) as trusted and to look up a guide online. The usual place, from general iOS knowledge rather than from them, is Settings → General → VPN & Device Management. The mentors thought the build had only gone out for Android, so iOS may need extra help.
- Name: the transcript calls it the "Connectathon" app, which is probably a transcription error. The login page in the MCP guide is titled `SMARTHOME-PRO-BETA-APP`.
- Screenshots of Altice's own Connected Home app, from their public product page, are in [`assets/altice-app/`](../assets/altice-app/). The build we were given may look different.

## Camera

- Protocol: RTSP, served from `go2rtc.futurelabsinnovations.com:8554`. Each team has its own URL.
- **There is no authentication.** The URL is the only protection, so do not paste it anywhere shared.
- Once the feed shows in VLC it can be connected to any system we use to process images.

## Event day (Fri 20 Nov)

- Altice Labs will bring an access point with a 4G router broadcasting the same SSID. They are not sure it can serve all seven teams.
- **Bring our own access point or hotspot** configured with the kit's SSID and password, and an ethernet cable for the gateway.
- Parts of the venue have no mobile signal, which rules out relying on a phone hotspot there. The organisers said they may seat the Altice teams near the entrance for that reason.

## Credentials

Values are in `.env`, which is gitignored. All of them reached us on 16 Nov.

| What | `.env` variable | What you do with it | Came from |
|---|---|---|---|
| Kit Wi-Fi | `KIT_WIFI_SSID`, `KIT_WIFI_PASSWORD` | **You do not look for this network, you create it.** Give a hotspot or router this name and password and the kit devices join by themselves. Same values for every team | Rui Mendes, Slack DM |
| Team account | `CONNECTED_HOME_USERNAME`, `CONNECTED_HOME_PASSWORD` | Type it into the login page that opens when an MCP client connects. Try it for the app login too. It was sent as one line, "A - B"; reading that as username and password is our interpretation | Rui Mendes, Slack DM |
| Camera feed | `CAMERA_RTSP_URL` | Paste it into VLC to watch the camera, or hand it to our own vision code. No authentication | Rui Mendes, Slack DM |
| MCP API key | `CONNECTED_HOME_API_KEY` | Paste it into the MCP client config in place of `<API_KEY>` | Rui Mendes, Slack, 16 Nov |
| App invite | `APP_INVITE_URL` | Open it on the phone to install the app | Email to Filipe |

None of these is typed into the gateway. The gateway has nothing for us to configure.
