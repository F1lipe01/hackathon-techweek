# Open questions and next steps

Last reviewed: Mon 16 Nov 2026.

## Blocking

| # | What | Who can resolve it |
|---|---|---|
| ~~1~~ | ~~MCP API key~~ **Received** 16 Nov from Rui Mendes, stored in `.env`. The MCP client still needs the OAuth login (team account) on top of it | Done |
| 2 | **Book the Wednesday mentor checkpoint.** It is mandatory and must happen on Wed 18 Nov | The Altice mentors, on Slack |
| 3 | **Bring the kit online** and confirm every device shows in the app. The gateway is cabled to the lab ethernet; the camera still needs a 2.4 GHz Wi-Fi network with the kit's name and password, which the gateway does not provide | Us. See [04-kit-and-access.md](04-kit-and-access.md) |

## To confirm

| # | What | Why it matters |
|---|---|---|
| 4 | The team account arrived as a single line, "A - B". We read it as username and password | First login will tell |
| 5 | **What each kit device exposes through the MCP.** The hardware is inventoried from photos. Still unknown: whether the MS-D3D sensor is a door contact, whether the plug and bulb are Wi-Fi or Zigbee, whether the bulb does colour, whether the plug reports energy use, whether smoke alarm and camera events are visible | Decides which ideas are buildable. Extra devices cannot be added |
| 5b | Whether the lab network lets the gateway reach the internet. A light on the gateway is not proof; the app showing it online is | If not, it needs registering with whoever runs the lab network, or a different uplink |
| 6 | Exact challenge title and whether a written statement exists | Goes in the header of the executive summary |
| 7 | Whether Claude Code, or any client beyond VS Code, Hermes and Codex, can authenticate | The OAuth redirect may be restricted to the documented clients |
| 8 | Whether one app invite works on several phones | Otherwise ask Hugo for invites for Simon and Mushahid |
| 9 | Jury names and affiliations | Transcript is unreliable on names |

## Missing from this repo

| # | What | Where it probably is |
|---|---|---|
| 10 | **Participant guide.** Evaluation criteria for both rounds, venue address, mentor list, checkpoint slot | Organisers' email |
| 11 | The links from the organisers' email of 16 Nov: session room, challenge resources folder, Slack invite. Only the text was pasted, the links were lost | Same email |
| 12 | Two Slack screenshots: `Screenshot 2026-11-02 at 11.43.36.png` and `Screenshot 2026-11-16 at 17.51.54.png` | Team Slack channel |
| 13 | `Desafio#3_Altice_Hackathon_MCP_ATC2026.pdf - Google Drive.html` was not found in Downloads. The PDF itself is filed, so nothing is lost | |
| 14 | The MDPI paper Ana shared has not been read or summarised | [05-ideas.md](05-ideas.md) |

## Decisions the team has to make

| # | What | By when |
|---|---|---|
| 15 | Which idea, or combination, we commit to | Before the Wednesday checkpoint |
| 16 | Who does what: data and devices, interface, pitch | Now. The organisers' first piece of advice |
| 17 | Who pitches in Portuguese on Friday | Before rehearsals |
| 18 | Which access point or hotspot we take to Aveiro | Before Friday |
| 19 | Whether anyone needs an absence declaration for Friday | Ask Rui or Marta |
| 20 | Whether the repository we submit on Friday is this one, cleaned of `sources/`, or a separate code-only one | Before Fri 17:30 |
