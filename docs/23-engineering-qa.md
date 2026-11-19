# ThingTracker · engineering questions and answers

The questions an engineer on the jury, or at Altice Labs, is likely to ask, each with:
- a one-line answer, to say out loud;
- the detail behind it;
- where it is shown: a diagram in `docs/architecture/`, a section of [14-architecture.md](14-architecture.md), or a file and line in `prototype/`.

Use the short answer, then the detail only if asked. Two rules for every answer:
1. Separate the **design** from what the **prototype** does today.
2. Never claim a figure that is not in the documents.

Status markers:
- **[target]**: the design;
- **[prototype]**: what the code on the demo laptop does;
- **[to confirm]**: still being implemented on 19 Nov, to be checked before the pitch.

---

## A. Where things run

**A1. What runs where?**
- **Short answer:** "The home sees, Altice's servers decide, and the language model only writes."
- **At home [target]:** the hardware Altice already installs (camera or router, no AI chip), running:
  - the motion check;
  - privacy masks;
  - cutting out only the region that changed;
  - face recognition, opt-in;
  - the router's list of family phones on the Wi-Fi.
- **At Altice [target]:**
  - vision servers (OWLv2 and DINOv2 on NVIDIA L4 GPUs, fed by queues);
  - the ThingTracker service, stateless behind a load balancer, running the presence engine and the rules engine;
  - PostgreSQL with pgvector, a Redis cache, object storage for thumbnails;
  - a language-model pool that receives text only;
  - the existing MCP server and notifications.
- **On the phone:** the Altice app, with the new *Things* tab and the assistant button.
- **Diagram:** `implantacao.png`.

**A2. What did the MacBook do in the demo?**
- **Short answer:** "All three roles at once: the home, Altice's servers and the language model."
- **[prototype]:**
  - `edge.py` plays the home agent and Altice's vision servers (OWLv2 and DINOv2 on the Mac's GPU);
  - `server.py` plays the ThingTracker service: app, API, presence and rules engines, with SQLite standing in for PostgreSQL;
  - `llm_local.py` plays the language-model pool (Qwen3-1.7B).
- In the demo, the kit camera's stream reached the Mac through the organisers' cloud relay. That is a property of the hackathon setup, not of the product.

**A3. Why not a box in every home, with everything local?**
- **Short answer:** "Because it costs €100–140 M up front for 500 000 homes."
- **Detail:**
  - running costs of €6,55–8,64 per home a month (Raspberry Pi 5 with an AI HAT+, or a Jetson Orin Nano);
  - every model update ships to 500 000 boxes;
  - the language model would need even more memory.
- **Source:** [17-operator-costs.md](17-operator-costs.md); the side panel of `implantacao.png`.

**A4. Why not send the video to the cloud?**
- **Short answer:** "Too much traffic and too much privacy exposure, for no gain."
- **Detail [estimate in the diagram]:**
  - continuous video at 2 Mbps is about 657 GB per camera a month;
  - full frames during motion still cost €2,41 per home a month on Altice's own servers, and €3,93–4,26 on hyperscaler GPUs.
- **Our path** sends only the region that changed, about once a second while there is motion: **≈ €0,49 per home a month** with one camera, €0,98 with two (docs/17).

**A5. Where are the load balancers, and why there?**
- **Short answer:** "At Altice, in front of the stateless service and the vision and language pools; the home has nothing to balance."
- **Detail [target]:**
  - each home keeps **one outbound** mTLS connection to a connection broker (MQTT, one topic per home);
  - the load balancers spread the homes' connections and the app's HTTPS calls across N service instances;
  - per-home state lives in PostgreSQL and Redis, so any instance can serve any home;
  - vision and the language model sit behind **queues**: urgent rule checks first, everything else batched at quiet hours, so the GPUs are not sized for the evening peak.
- **Diagram:** `implantacao.png`.

**A6. How does it scale to 500 000 homes?**
- **Short answer:** "Horizontally, and the costs are already counted."
- **Detail:** the business case sizes 1 427 L4 cards (€6,4 M of hardware) for 500 000 homes with one camera, because only motion triggers analysis and only the changed region is analysed (docs/17).

**A7. What if the internet goes down?**
- **Short answer:** "The home keeps its events in a queue and sends them when the link returns; the security alarm doesn't depend on us."
- **[target]:**
  - the home agent buffers events (the "fila de saída" in `implantacao.png`);
  - rules that need vision pause;
  - the alarm and the door sensor keep working through Altice's security hub, as today.

**A8. How fast is an alert?**
- **Short answer:** "The target is under 3 seconds; the prototype takes about 10 seconds on the door path."
- **Detail:**
  - the budget is: motion, then the region uploaded, then the urgent vision queue, then the rule, then the notification;
  - measured on the Mac's GPU: OWLv2 0,57 s per frame, DINOv2 22 ms per crop (docs/14 §3);
  - the prototype's 10 s comes from polling the door sensor through MCP every 4 s, plus the rule's wait (docs/19 §6.4).

## B. Perception: what the models do, and only that

**B1. How does it know it's *your* book, not any book?**
- **Short answer:** "Two models: one finds 'a book', the other checks it is yours."
- **Detail:**
  - **OWLv2** (open vocabulary) boxes anything described in words, here "a photo of a yellow book";
  - **DINOv2** turns each box into a fingerprint (384 numbers) and compares it with the 8 stored views by cosine similarity;
  - 0,62 or more counts as yours;
  - in the lab, on the kit camera, the book scored 0,70 and a bottle 0,10;
  - `edge.py` (matching around lines 195-208).

**B2. How do you register a thing?**
- **Short answer:** "Photos from the phone, or showing it to a camera; the result is 8 views and a fingerprint."
- **Detail:**
  - **phone photos:** OWLv2 crops the thing in each photo, then DINOv2 makes the vectors [to confirm: implemented on 19 Nov];
  - **showing it to the camera:** the edge keeps 8 views, each different enough from the others (cosine below 0,97) (`edge.py` `enrol_step`);
  - the fingerprint is stored per customer in the platform's database.

**B3. How does it know someone picked up the book?**
- **Short answer:** "No model decides that: it is a rule on boxes."
- **[target, to confirm in the prototype]:**
  - the book's box overlapping a person's box makes an "in hand" sighting, with who, if the face is registered;
  - the book then gone from its place for 3 analyses or more makes "taken by…";
  - the book seen somewhere else makes "moved to…".

**B4. How does it know the book was left behind?**
- **Short answer:** "When the door closes after someone from the family left, the camera checks that the book is still there."
- **[target, to confirm in the prototype]:**
  - trigger: the door **closes** after opening, and presence shows a family member left (a phone left the Wi-Fi, or fewer people);
  - then an **active check**, a forced analysis of the book's place over a few frames, even without motion;
  - an alert only if the book is seen; if it isn't visible, the result is "unsure", with no alarm;
  - arrivals don't trigger it;
  - **diagram:** `seq-livro-esquecido.png`.
- **[prototype before 19 Nov]:** the door opening plus the book's last sighting. That was weaker, and the reason for the change.

**B5. How do faces work? Isn't that biometric data?**
- **Short answer:** "Yes, so it is opt-in, with consent, and the face templates never leave the home."
- **Detail:**
  - **YuNet** finds the face and **SFace** compares it; both are small models that run on an ordinary processor [licences: to confirm];
  - a known face scores 0,363 or more, OpenCV's recommended value;
  - only a label leaves the house: "Filipe", "unknown face" or "face not visible";
  - biometric data used to identify a person is a special category under GDPR (Article 9), which needs explicit consent;
  - **diagram:** `seq-pessoa-desconhecida.png`.
- **[prototype before 19 Nov]:** there was no face model; any person triggered the rule. Being fixed on 19 Nov [to confirm].

**B6. And when someone with no visible face comes in?**
- **Short answer:** "It asks, it doesn't alarm."
- **Detail:**
  - the alarm sounds only for a **visible** unknown face on several consecutive analyses (3 in the design), and never for a family member;
  - a person whose face isn't visible, while the family is away, makes the home "unsure" and sends a question.

**B7. False detections, like a jacket taken for a person?**
- **Short answer:** "Thresholds, tracks and a ladder of responses, and the family chooses what is disruptive."
- **Detail:**
  - minimum scores (a person at 0,2 for OWLv2);
  - a detection must persist across analyses before it counts;
  - alarms need consecutive confirmations;
  - every alert carries the photo of the moment;
  - for each risk, the family chooses between "ask first" and "sound at once" when creating the rule.
- No accuracy in real homes is measured yet; the pilot measures it.

**B8. In the dark?**
- **Short answer:** "The kit camera switches to infrared night vision, and the models work on it; in total darkness nothing is detected, and we don't claim otherwise."
- **Detail:** the films show the camera's own drop to black for a fraction of a second, then night vision. No boxes appear while the picture is too dark.

**B9. Blind spots and occlusion?**
- **Short answer:** "Each camera is one place; what no camera sees is covered by the phones and the door sensor, not guessed."
- **Detail:** a person hidden behind a monitor keeps their track while still. Zones inside a camera are a later feature.

## C. Presence and rules: who decides

**C1. How do you know nobody is home?**
- **Short answer:** "Not from the camera alone: three signals must agree."
- **Detail [target]:** a state machine per home, in the ThingTracker service, fusing:
  - the family's **phones on the Wi-Fi** (the router knows; a new MCP tool proposed to Altice);
  - the **door sensor** (open and close events, which the platform already receives);
  - the **people the cameras see**, with a name if the face is registered.
- **States:**
  - OCUPADA: a phone is home, or someone was seen recently;
  - A SAIR: the door opened and closed, and the service checks who left;
  - VAZIA: all phones away, the door cycled, nobody seen for a set time;
  - INCERTA: the signals disagree.
- **Timings:** demo values in seconds, production values in minutes (for example "empty" after 20 s in the demo, 3 min proposed in production).
- **Diagram:** `presenca-estados.png`.

**C2. A room without a camera? Someone sitting still?**
- **Short answer:** "The phones cover it."
- **Detail:** if Filipe's phone is on the Wi-Fi, he is home even in a room with no camera. A person sitting still is covered by the phones, and by a periodic refresh analysis while presence depends on a camera alone.

**C3. And if the phone stays at home, or a visitor has no phone?**
- **Short answer:** "Then the signals disagree, the home is 'unsure', and the rules ask instead of acting."
- **Detail:**
  - a phone at home with no sighting and no door use for a long time (3 h proposed) means a phone left behind;
  - a person seen with no phone home is someone without a registered phone: a visitor, a child, or a stranger;
  - the face decides which, if registered; otherwise the family is asked.

**C4. Is it the language model that decides?**
- **Short answer:** "No. The models only perceive; a deterministic rules engine decides."
- **Detail:**
  - OWLv2 gives boxes with scores; DINOv2 says how close a crop is to a fingerprint; SFace says whose face it is;
  - every conclusion ("left behind", "nobody home", "unknown person") is code in the rules and presence engines, re-evaluated on each event and timer;
  - the language model does only three jobs: turn a sentence into a rule, phrase answers and messages, and rarely judge an unclear crop;
  - **[prototype]:** `server.py` `rules_engine`; the language model in `brain.py`.

**C5. What if the language model makes a mistake?**
- **Short answer:** "It can't act on its own: its rule is validated, shown to the user in plain words, and the code checks answers against the memory."
- **[prototype]:**
  - an invalid rule falls back to keyword templates;
  - an answer that disagrees with the memory is replaced by a plain sentence built from the memory (`brain.py`, see AGENTS.md).

**C6. How are actions carried out?**
- **Short answer:** "Through Altice's MCP server, the family's choice decides what is disruptive, and arming the alarm always asks."
- **[prototype]:** every action is a dry run unless `TT_LIVE_ACTIONS=1`, which the team never sets, so the real home is never changed (`actions.py`).

## D. Data, security, privacy

**D1. Which database?**
- **Short answer:** "SQLite in the prototype; in production PostgreSQL with pgvector at Altice, and a small local store at home."
- **Detail:**
  - **at Altice, per customer:** things, fingerprints, rules, events, sightings and presence, plus Redis for live state and object storage for thumbnails (30 days, proposed);
  - **at home:** face templates, encrypted, and the outbound event queue;
  - **[prototype]:** `store.py` (SQLite). There is no PostgreSQL in the prototype.

**D2. Is video recorded or sent?**
- **Short answer:** "No. Only the region that changed is sent, while there is motion, and deleted after analysis, except the thumbnail of a sighting."
- The lab recordings used in the films were made for the films, locally, with the people's agreement or blurred.

**D3. Security?**
- **Short answer:** "One outbound mutually authenticated link per home; no open ports at home."
- **Detail:** mTLS from the home agent to the broker, one MQTT topic per home, HTTPS for the app, face templates encrypted at rest at home.
- **Diagram:** the data-flow diagram with trust boundaries.

**D4. GDPR?**
- **Short answer:** "Minimisation by design: no video leaves, faces only with explicit consent and stored at home, and retention limits."
- The language-model provider must guarantee no training on our data, a DPA and processing in the EU (docs/14 §3).

## E. Altice integration

**E1. What does Altice need to add?**
- **Short answer:** "A *Things* tab, an assistant button, four MCP tools for things, one for Wi-Fi presence, and the service."
- **The tools:** `list_things`, `create_thing`, `get_thing_last_seen`, `get_thing_timeline`, plus the proposed Wi-Fi presence tool. Actions use the 18 tools that already exist (docs/14 §3, docs/15).

**E2. Notifications?**
- **Short answer:** "Through the notification service the Altice app already uses."
- In the prototype, alerts show inside the app [to confirm: from the rules, not injected].

## F. Costs and models

**F1. Cost per home?**
- **Short answer:** "About €0,49 a month for vision with one camera, and about €0,43 for the language model."
- These are team estimates from public prices (docs/16, docs/17), to be measured in the pilot.

**F2. Licences?**
- **Short answer:** "All open and free for commercial use."
- **Detail:** OWLv2 and DINOv2: Apache-2.0. Qwen3-1.7B: Apache-2.0. YuNet and SFace: [to confirm].

## G. The films and the demo

**G1. Is what the films show real?**
- **Short answer:** "The footage is the real lab and kit camera, the app is our prototype, and the boxes come from our models run on that footage; some moments were shortened, and the films say so."
- **Detail, say it plainly if asked:**
  - the alerts were triggered for the recording [to confirm: since 19 Nov the same rules fire them in the prototype];
  - the stretch where people sit is shown at 4×;
  - a cut skips time where the room is empty;
  - the camera's drop to black when the lights went off was rebuilt from the camera's own behaviour;
  - the smart plug's box was placed on a chosen plug because the kit had been packed.

**G2. What can you show live?**
- [to confirm after the code work] the rules firing from a simulated door and simulated phones, the presence state changing, and a face recognised or not.

**G3. What is measured, and what isn't?**
- **Measured, in the lab on the kit camera:** the book at 0,70 against 0,62; a bottle at 0,10.
- **Not measured:** accuracy and false alarms in real homes. The pilot is the place for that.
