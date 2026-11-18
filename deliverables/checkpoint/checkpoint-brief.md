# Mentor checkpoint · IT-Porto · Wed 18 Nov 2026

<p class="lead">Challenge #3, Altice Labs. Our product: <b>Track Things</b>, the home that remembers the things that matter. Bring this page to the call; the questions are ranked, so start at the top.</p>

## Say this first (30 seconds)

> Today the kit's camera tells the platform one thing: "motion detected". We turn it into the home's memory. You tell the home which things matter, such as your keys, wallet, the cat or the coffee machine. It remembers where and when it last saw each one, answers "where are my keys?", warns you at the door if you're leaving without them, and acts on the plug, light and alarm through the MCP. It looks only at the zones you choose, and it never identifies people. It lives as a tab in Altice's existing app, with four new MCP tools.

## Where we are

| Item | State |
|---|---|
| Our own MCP client reads all 7 devices; it switched the plug off and on | Done, 16 Nov; the plug acknowledged in about 1 s |
| A rule written through the MCP (camera motion → light blue) | Done, 17 Nov; saved and read back, not yet seen firing |
| Camera powered and online on the platform | Done, 17 Nov |
| Reading the camera stream with our code | **Open**: our probe this morning got no answer |
| Privacy filter, detector, memory, two rules, web prototype of the tab | By Friday |

## What we'll show on Friday, on the real kit

1. "Where are my keys?" → "On the hall table, at 08:42", with the image crop as proof.
2. Leaving without the keys: the door opens, the home warns you and the light blinks.
3. The house is empty and the coffee machine is on: the plug switches off and the home reports the energy saved.
4. Someone in the hall and no known phone at home: a snapshot with two buttons, siren or alarm. Nothing sounds without a yes.

Plan B: a recorded video of the same four moments.

## Questions for you, most important first

1. **May we run vision models on the camera feed?** Is an indoor camera acceptable to Altice if it remembers things, not people?
2. **Why might the stream not answer?** Our RTSP probe through the go2rtc relay got no reply. The camera exposes a `streamingSwitch` capability. Does it need to be on? We haven't changed it.
3. **Where does the video go today?** The camera box says "Powered by Tuya", with Tuya cloud storage. Could a privacy filter run on the camera or the hub?
4. **What else does the platform offer?** Can the MCP sound the siren or the hub alarm directly? Is there an event or push API, so we don't have to poll? Can we delete the scenarios we create?
5. **Would Altice consider "things" tools in the MCP?** We propose `list_things`, `create_thing`, `get_thing_last_seen` and `get_thing_timeline`.
6. **Who would buy this?** Which customers and price points do MEO and SFR aim add-ons at? In Portugal, NOS and Vodafone sell monthly alarm plans with indoor cameras, and MEO sells an alarm kit with no camera.
7. **May we test arming the alarm in the lab?** The tool is labelled read-only but changes state, and Home mode has a 0 s delay.
8. **Logistics.** How many teams reach the final, and how long is the intermediate Q&A? (Rules: up to 6 teams, 3 + 1 min; kick-off: 3 teams, 3 + 2 min.) Is today's report the same document as Friday's executive summary?

## Risks we already know about

- **Camera stream not yet read by our code.** Everything depends on it; it's tomorrow's first job.
- **Detection of small objects such as keys is unmeasured.** We measure it on Thursday, with the camera in its demo position.
- **No data on whether Portuguese households accept an indoor camera.** We plan to ask 20 people before Friday.
- **Anthropic's own API has no EU-only processing.** Production would use Claude in Amazon Bedrock's EU regions, or an open model hosted by Altice.
