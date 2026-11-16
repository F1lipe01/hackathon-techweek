# Hardware kit and access

Sources: challenge-room Q&A in the kick-off transcript (lines 164–293), Slack DM with Rui Mendes, team Slack.

## The kit

- Collected from Altice Labs in Aveiro. The pick-up was arranged for Fri 13 Nov.
- Every device is already provisioned on Altice's platform and linked to our team account. No pairing is needed.
- **Contents are not inventoried here yet.** From the Q&A we know there is a gateway, a light, a camera and "several types of sensors and equipment". Fill in the table below once the kit is online, from the app or from `GET_HOME_DEVICES`.

| Device | Type | Room | Capabilities | Online? |
|---|---|---|---|---|
| | | | | |

## Bringing it online

1. **Create the Wi-Fi network the kit expects.** All kits were provisioned on one access point at Altice Labs, so they all look for the same SSID and password (`KIT_WIFI_SSID` and `KIT_WIFI_PASSWORD` in `.env`). Set a home access point or a phone hotspot to those values and the devices should join and reach the internet by themselves.
2. **Check every device in the mobile app.** Each one should show as online.
3. **Check the camera** in VLC: open a network stream and paste `CAMERA_RTSP_URL`.
4. **Connect an MCP client** and log in with the team account. See [03-mcp-connected-home.md](03-mcp-connected-home.md).

Our own tip, not from the organisers and not verified on these devices: smart-home devices often only join 2.4 GHz networks, so if a phone hotspot is used and nothing connects, try its compatibility (2.4 GHz) mode.

## Troubleshooting

- **Rule of thumb from the mentors:** if every device is online in the app and something fails through the MCP, the devices are not the problem.
- **Gateway reset by accident** (it happened to another team): the devices have to be added again through the app once the network is up. Ask the mentors for help. Someone called Marta on the Altice side knows this process well.
- Use the app to test each device before blaming the MCP or our code.

## Mobile app

- Distributed through Firebase App Distribution. The invite was emailed to the team representative (Filipe). The link is in `.env` as `APP_INVITE_URL`. It is unclear whether one invite works on several phones.
- **More invites:** message Hugo Dias on Slack. He offered to send invites to other team members.
- **iPhone:** the app is blocked at first as an untrusted enterprise developer. The mentors said to mark the developer (Altice Labs) as trusted and to look up a guide online. The usual place, from general iOS knowledge rather than from them, is Settings → General → VPN & Device Management. The mentors thought the build had only gone out for Android, so iOS may need extra help.
- Name: the transcript calls it the "Connectathon" app, which is probably a transcription error. The login page in the MCP guide is titled `SMARTHOME-PRO-BETA-APP`.

## Camera

- Protocol: RTSP, served from `go2rtc.futurelabsinnovations.com:8554`. Each team has its own URL.
- **There is no authentication.** The URL is the only protection, so do not paste it anywhere shared.
- Once the feed shows in VLC it can be connected to any system we use to process images.

## Event day (Fri 20 Nov)

- Altice Labs will bring an access point with a 4G router broadcasting the same SSID. They are not sure it can serve all seven teams.
- **Bring our own access point or hotspot** configured with the kit's SSID and password.
- Parts of the venue have no mobile signal. The organisers said they may seat the Altice teams near the entrance for that reason.

## Credentials

Values are in `.env`, which is gitignored. All of them reached us on 16 Nov.

| What | `.env` variable | Came from | Note |
|---|---|---|---|
| Team account | `CONNECTED_HOME_USERNAME`, `CONNECTED_HOME_PASSWORD` | Rui Mendes, Slack DM | Sent as one line, "A - B". Reading it as username and password is our interpretation |
| MCP API key | `CONNECTED_HOME_API_KEY` | Not received | Goes in the `X-API-Key` header |
| Camera feed | `CAMERA_RTSP_URL` | Rui Mendes, Slack DM | No authentication |
| Kit Wi-Fi | `KIT_WIFI_SSID`, `KIT_WIFI_PASSWORD` | Rui Mendes, Slack DM | Same for every team |
| App invite | `APP_INVITE_URL` | Email to Filipe | Firebase App Distribution |
