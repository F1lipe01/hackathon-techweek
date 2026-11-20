# Journal

What was done each day. The git history has every step; this page is the summary. Newest day first.

## Fri 20 Nov: the hand-in

- Engineering Q&A and what-is-real: the proof runs settle each claim that had been marked "to confirm" (left behind fired by the rule; faces judged in the replays; the nobody-home alert with both device cards).
- Face thresholds made consistent across the documents: the prototype's three bands (known at 0,40 or more, unknown below 0,25, not sure in between).
- The event's format confirmed from the participants' guide: 3 + 2 min intermediate pitch from 16:00, 3 finalists per challenge, the presentation as PPT or PDF naming the tools used.
- Pitch decks on the organisers' template: 3-minute and 5-minute PPTX files with PDFs and notes, and a new opening (motivation first, then ThingTracker).
- App: things belong to a person, and a person can be added from one photo.
- A pitch website served by the prototype, with a live demo on the laptop's webcam, the use cases, how memory works, the documents and the films. Fonts are served locally so it works offline.
- A full film of about 90 s joining the three examples.
- Documents cleaned for delivery (PT and EN).

## Thu 19 Nov: three real examples, proof runs and the hybrid architecture

**Film research**
- Research before rebuilding the presentation film, with sources: compositing a phone screen, pace measured shot by shot on six product films, and sound on every visual event ([video/research/](video/research/)).
- A green-screen and marker tracker for phone screens (`track_green.py`; 2,2 px median error on a synthetic test).
- Video 1 is built from licensed stock footage and new recordings of the real prototype; no shoot.

**Three examples filmed in the lab with the kit camera**
- Example 1, the book left behind: the lab take, the detector's boxes, the book's box from the system's own recognition with its score, and the alert.
- Example 2, the unknown person: adding a person from a short video of their face, a Home security suggestion, the alarm and the police suggestion (112; the app never dials).
- Example 3, nobody home: two rules about the empty home, the people counter from four takes, the alert with the devices to turn off.
- App changes recorded for them: a person added from a face video, two simulated devices outside the Altice kit (the lights' plug and an AC integration), one screen at a time.

**The prototype**
- A presence engine that fuses the family's phones (simulated), the real door through the read-only MCP and the cameras.
- Faces on the home device (YuNet + SFace, opt-in), "in hand" sightings, active checks and photo fingerprints on the edge.
- Rules read the presence engine, and alerts are structured events.
- Replay mode: a lab take stands in for the camera, through the real pipeline.
- Proof runs: each film's take replayed through the real pipeline, unedited (`video/tools/proof_run.py`).
- A local vision-language judge for ambiguous checks (Qwen2-VL-2B, Apache-2.0); its answer becomes a question to the family, never an action.

**The architecture, redrawn**
- The design is hybrid, following the operator-cost study (docs/17): motion, the changed region and opt-in faces at home; OWLv2 and DINOv2 on Altice's L4 servers behind queues; presence and rules in a stateless ThingTracker service. A box in every home and full frames to the cloud are recorded as rejected alternatives, with their numbers.
- Twelve views in PT and EN (`docs/architecture/build_views.py`): C4 levels 1–3, deployment, presence states, three sequences, two data models, the data flow with trust boundaries, and the app flows.
- docs/14 rewritten around them; the integration spec (v3) and the business case updated to match.
- Engineering questions and answers (EN and PT), and what is real in each film ([docs/24-what-is-real.md](docs/24-what-is-real.md)).

## Wed 18 Nov: report submitted, prototype running

**Product and prototype**
- The direction is set: the home's camera becomes a source of information. Name: ThingTracker, under the Altice Labs brand.
- First prototype in the morning; by the afternoon the edge service runs on the kit camera, idles until motion, registers things by sight and draws live boxes.
- A copy of the Altice app with the new *Things* tab, the assistant and a local SQLite store; a local text model (Qwen3-1.7B) answers offline.
- The yellow book recognised on the kit camera at 0,70 against a 0,62 threshold, from phone photos.
- The MCP connected read-only: the real door and light reach the prototype.
- A lock that runs heavy jobs one at a time (`video/tools/heavy.sh`), after the laptop stopped under several renders at once.

**Report and documents**
- The 2-page report rewritten around camera plus AI and fact-checked. After the mentor checkpoint (safety-led use cases), Figure 1 follows a child at risk in the kitchen. Submitted at 18:51 (v2).
- Architecture, integration spec and business case in English and Portuguese.
- Operator costs (about 0,49 € per home per month in the hybrid option), 34 use cases with 10 scored, the product spec, the lab-test checklist, and PDFs in PT and EN.

**Pitch material**
- First pitch deck and its run of show for 3 and 5 minutes ([docs/pt/21-pitch.md](docs/pt/21-pitch.md)).
- Research playbooks with sources on craft, how launch films present products, and how to run a short pitch ([video/research/](video/research/)).
- Video 2, the real lab example (37 s), with the real score of 0,70 against 0,62.

## Tue 17 Nov: evidence before ideas

- Sourced market research for Portugal, France and the EU: damp and cold homes, older people living alone, fires, burglary, adoption. Every figure has a primary source ([docs/12-market-research.md](docs/12-market-research.md)).
- A top-5 use-case report scored against the jury's criteria.

## Mon 16 Nov: the kit and the platform

- Hackathon material filed, with the organiser files kept as untrusted.
- The kit mapped: the devices, the network and the missing 12 V camera adapter.
- The Altice app and its APK analysed, with the platform's capability model.
- The Connected Home MCP connected through our own OAuth client: live read tests, and one supervised write test of the plug.
- A project baseline: what works, what doesn't, and the decisions to make.
