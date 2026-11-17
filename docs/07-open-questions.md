# Open questions and next steps

Last reviewed: Tue 17 Nov 2026.

## Blocking

| # | What | Who can resolve it |
|---|---|---|
| ~~1~~ | ~~MCP API key~~ **Received** 16 Nov from Rui Mendes, stored in `.env`. The MCP client still needs the OAuth login (team account) on top of it | Done |
| 1b | **Camera has no power adapter.** It needs 12 V ⎓ 2 A DC (barrel 5.5 × 2.1 mm, centre-positive — check the label). Ethernet does **not** power it: it is not PoE; its RJ45 is only a wired-network alternative to Wi-Fi. Don't borrow the gateway's 12 V 1 A adapter | Hugo or Rui on Slack, or any 12 V ≥ 2 A CCTV adapter in the lab |
| 2 | **Book the Wednesday mentor checkpoint.** It is mandatory and must happen on Wed 18 Nov | The Altice mentors, on Slack |
| 3 | **Bring the kit online** and confirm every device shows in the app. The gateway is cabled to the lab ethernet; the camera still needs a 2.4 GHz Wi-Fi network with the kit's name and password, which the gateway does not provide | Us. See [04-kit-and-access.md](04-kit-and-access.md) |

## To confirm

| # | What | Why it matters |
|---|---|---|
| 4 | The team account arrived as a single line, "A - B". We read it as username and password | First login will tell |
| ~~5~~ | **Resolved** (app + MCP, 16 Nov): 7 devices in home "Hack 3"; MS-D3D is a contact sensor; plug meters energy; **bulb does colour**; camera has a siren. Full capability map in [10-mcp-in-practice.md](10-mcp-in-practice.md) | Done |
| 5c | **The Light has not reached the cloud since 04 Nov**, even with the kit Wi-Fi up. Check it is in a socket that is switched on (steady, not blinking). If it still won't come online, ask the mentors — it may need re-pairing | Us, then mentors |
| ~~5b~~ | **Resolved.** The app shows the **Security hub as On**, so the gateway reaches the Cognitive Home platform over the lab ethernet | Done |
| ~~6~~ | **Resolved.** Official challenge sheet obtained and filed (`sources/challenge/desafio3-ficha.pdf`); summarised in [02-challenge.md](02-challenge.md) | Done |
| ~~7~~ | **Resolved.** Only the documented callbacks are accepted, so we wrote our own client (`mcp/client/chmcp.py`), which also plugs into Claude Code | Done |
| 8 | Whether one app invite works on several phones | Otherwise ask Hugo for invites for Simon and Mushahid |
| 9 | Jury names and affiliations | Transcript is unreliable on names |

## Missing from this repo

| # | What | Where it probably is |
|---|---|---|
| ~~10~~ | **Resolved.** Evaluation criteria, schedule, deliverables, IP and rules are in the official norms + FAQ, now filed (`sources/rules/`) and summarised in [01-event.md](01-event.md). Venue address is in the norms (maps link). Mentor list still only partial | Mostly done |
| 10b | **Confirm the finalist count and intermediate Q&A length.** Written rules say up to 6 teams / 3+1 min; the kick-off said 3 teams / 3+2 min | Ask the mentors |
| 11 | The links from the organisers' email of 16 Nov: session room, challenge resources folder, Slack invite. Only the text was pasted, the links were lost | Same email |
| 12 | Two Slack screenshots: `Screenshot 2026-11-02 at 11.43.36.png` and `Screenshot 2026-11-16 at 17.51.54.png` | Team Slack channel |
| 13 | `Desafio#3_Altice_Hackathon_MCP_ATC2026.pdf - Google Drive.html` was not found in Downloads. The PDF itself is filed, so nothing is lost | |
| 14 | The MDPI paper Ana shared has not been read or summarised | [05-ideas.md](05-ideas.md) |

## Gaps from the market research (17 Nov)

From [12-market-research.md](12-market-research.md). Mentor questions for the checkpoint are in its §9.

| # | What | Who can resolve it |
|---|---|---|
| 21 | **Altice's customer data is not public**: who uses Connected Home (now "Cognitive Home"), for what, and which segment MEO and SFR want to grow | Mentors, at the checkpoint |
| 22 | **Altice already covers older-person monitoring**: Family Care (motion sensors + Wi-Fi sensing), Aging in place (activity and fall alerts, per the brochure), eHealth Smart Assisted Living. An older-person use case has to add something they lack, e.g. home-condition health (damp, cold). The use-case report's checkpoint question targets this | Mentors, at the checkpoint |
| 23 | **The MCP has no event history and no notifications.** Any routine or trend feature means polling and keeping our own log; any alert needs our own channel | Ask mentors whether a platform event/push API exists |
| 24 | **Nothing to switch on the plug at the venue** for a damp/cold demo (a dehumidifier, heater or stand-in lamp) | Us; ask the mentors whether a heater is allowed |
| 25 | **Smoke sensor test button**: unknown whether it triggers the hub alarm or emergency contacts | Mentors |
| 26 | **Figures not confirmed at source**: excess winter mortality (only press citing DGS was found), "37.8 % of 80+ live alone" (a seminar talk, wider definition), ANACOM Q2 2026 operator shares (the page loads by JavaScript; Q4 2025 is used), share of fire deaths who are elderly (not published) | Only if needed |
| 27 | **No current Portuguese time-use data.** INE's survey is from 1999 and INUT (CESIS/CITE) from 2015, and Portugal is absent from EU HETUS. "People spend more time at home" cannot be backed by a number | Accept the gap; only RASI 2025 says it, qualitatively |
| 28 | **Altice brochure (2025) has a hidden contradictory paragraph** (pp. 1, 16). It is not an instruction, but don't quote the PDF's extracted text without looking at the page | Noted |
| 29 | **Untested kit behaviour the demos depend on**:
  - the contact sensor changing open → closed through the MCP;
  - plug metering under a load (and the daily counter's unit);
  - whether the plugged appliance resumes on power;
  - how fast the MCP may be polled;
  - how a powered-off hub shows up, and that it reconnects cleanly;
  - whether a smoke sensor can trigger a scenario.

  Full list: [use-case report §9](../deliverables/use-case-report/top5-use-cases.md) | Us, Wednesday morning or Thursday; the scenario question goes to the mentors |
| 30 | **Owners for the build streams** (engine, conversation, story) and the **LLM/coding-assistant names** for the Sumário's AI section | Team, before Wed 19:00 |

## Decisions the team has to make

| # | What | By when |
|---|---|---|
| 15 | Which idea, or combination, we commit to | Before the Wednesday checkpoint |
| 16 | Who does what: data and devices, interface, pitch | Now. The organisers' first piece of advice |
| 17 | Who pitches in Portuguese on Friday | Before rehearsals |
| 18 | Which access point or hotspot we take to Aveiro | Before Friday |
| 19 | Whether anyone needs an absence declaration for Friday | Ask Rui or Marta |
| 20 | Whether the repository we submit on Friday is this one, cleaned of `sources/`, or a separate code-only one | Before Fri 17:30 |
