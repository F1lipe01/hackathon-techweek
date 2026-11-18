# Journal

How the project moved, day by day: what changed, why, and what the team said. Git history has every step; this page is the summary. Newest day first.

## Wed 18 Nov: from an idea to a submitted report, a prototype and a pitch

**Morning: the product and the prototype**
- The idea settles: the home's camera becomes a source of information. The name moved from Track Things to ThingTracker, under the Altice Labs brand.
- First prototype by 10:33. By 14:28 the edge service runs on the kit camera, idles until motion, registers things by sight and draws live boxes.
- By 16:06 there is an exact copy of the Altice app with the new Things tab, the assistant and a local SQLite store. By 16:42 a local text model (Qwen3-1.7B) answers on the laptop, offline.
- The architecture, the integration spec and the business case are written in English and Portuguese.

**Afternoon: the report**
- The 2-page report is rewritten around camera plus AI and fact-checked.
- Figure 1 moved from the book to the child in the kitchen after the mentors' call (safety-led cases).
- Submitted at 18:51 as v2.

**Evening: the material for Friday**
- Supporting documents:
  - operator costs: about 0,49 € per home per month in the hybrid option;
  - 34 use cases with 10 finalists;
  - the product spec, written as the Altice team planning the launch;
  - the lab-test checklist;
  - PDFs in PT and EN.
- The MCP is connected read-only: the real door and light now reach the prototype.
- A guard against running heavy jobs together (`video/tools/heavy.sh`), after the laptop stopped with a watchdog panic at 18:12.

**Videos and deck: what we learnt**
- **Video 1 (presentation).**
  - v2 scored "idea 7, execution 4".
  - v3: the team liked the start and "Basta perguntar", but the sound was poor and the picture too dark.
  - v4 was rejected: a fast footage montage, one clip reused, drawn app screens.
  - Lesson: lock a shot-by-shot storyboard with the team before rendering, and film real actions.
  - Storyboard v5, then v5.1 after research; v5.1 is being built now.
- **Video 2 (the real lab example).**
  - The 37 s proof with 3 photos and the real score of 0,70 against a 0,62 threshold.
  - Redesigned on a bright home.
  - 11 review fixes: one clean photo move, no flicker, labels on boxes, readable app.
- **Deck.**
  - v1 "no motion, no creativity".
  - Rebuilt cinematic and "way, way better".
  - Then logos, team, PT-PT review, balanced space, smoother motion.
  - Version 22 follows the pitch research.
- **Research instead of trial and error.**
  - Three cited playbooks, in [video/research/](video/research/): craft skills, how launch films and home-camera brands present products, and how to run a 3- and 5-minute pitch.
  - One skill was installed after review (presentation-creator).
  - One was rejected because it steers users to promote its author.
- **Team decisions recorded in the docs.**
  - The family chooses for each rule whether the siren asks first or sounds at once; the child case sounds at once.
  - The real example comes right after the five cases in the pitch.
  - Every box in the film is fitted by hand to its object.

## Tue 17 Nov: evidence before ideas

- Sourced market research for Portugal, France and the EU: damp and cold homes, older people living alone, fires, burglary, adoption. Every figure has a primary source.
- A top-5 use-case report scored against the jury's criteria.

## Mon 16 Nov: the kit and the platform

- Hackathon material filed, with the organiser files kept as untrusted.
- The kit mapped: the devices, the network and the missing 12 V camera adapter.
- The Altice app and its APK analysed, with the platform's capability model.
- The Connected Home MCP connected through our own OAuth client. Live read tests, and one supervised write test of the plug.
- A project baseline: what works, what doesn't, and the decisions to make.

## Next: Thu 19 and Fri 20 Nov

- **Thursday, in the lab:** the real end-to-end test ([docs/19-teste-real.md](docs/19-teste-real.md)) (the book, the door sensor, the red light, with the team's explicit go-ahead for live actions), filming the takes for video 1, and the final cut of video 1.
- **Friday:** the executive summary and the deck (PPTX and PDF) by 17:30, the repo link, and the 3- and 5-minute pitches.
