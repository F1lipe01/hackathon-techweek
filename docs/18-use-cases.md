# ThingTracker use cases

Version 1, Wednesday 18 November 2026. For the jury, the Altice Labs mentors and the team. It answers three questions: what ThingTracker does in a real home, with which cameras and devices, and how each case answers the competition's evaluation criteria. The Portuguese version, shared on Drive, is [`pt/18-casos-de-uso.md`](pt/18-casos-de-uso.md).

## How to read this document

Each case starts from a sentence the client says, or from a proposal the app makes from what the camera learns about the home (there is a child, a dog, a cat or, if the family says so, an older person living alone). The client accepts a proposal with one tap.

For each case:
- the sentence or the proposal;
- what the camera looks for (the query to the OWLv2 detector, in English, or the registered thing, enrolled with 8 views and recognised by its DINOv2 visual fingerprint) and the place;
- the shape of the rule, which runs at home;
- the devices, marked "kit" (those in the challenge kit: camera, door contact sensor, smoke sensor, temperature and humidity sensor, smart plug, security hub and light) or "other IoT" (devices the kit does not have);
- the action;
- feasibility and limits.

Three terms used throughout:
- Place: each camera is one place ("Kitchen 1", "Living room 1"). There are no zones drawn inside a place; surfaces (the counter, the stove) are found by name in every frame.
- Feasibility: "today" means the prototype already does it; "small extension" means a new detector query or a new rule kind, with no new hardware; "future" means a new model, or a device the Altice platform would still have to support.
- Actions: alerts reach the phone through the app's notification service, because the MCP server has no notification tool (to confirm with Altice). Device actions (light, plug) go through the MCP, with `update_device_capabilities`. The siren and the alarm act only after the user says "yes"; in the prototype neither is wired, and light and plug actions are simulated unless enabled.

## 1. Catalogue, in priority order

Safety first, then care, then everyday convenience.

| # | Case | Place | Devices | Feasibility |
|---|---|---|---|---|
| S1 | Knife on the counter with a cat, dog or child nearby | Kitchen | Kit | Small extension |
| S2 | Child with a knife, or near the stove or oven | Kitchen | Kit; other IoT optional | Small extension; "holding" is future |
| S3 | Stove or oven on with nobody in the kitchen | Kitchen | Kit (plug, smoke) or other IoT (hob, oven) | Small extension (plug); future (hob) |
| S4 | Smoke: who is at home and where | All | Kit | Small extension |
| S5 | Medicines or cleaning products out of place with a child at home | Kitchen, living room | Kit | Small extension |
| S6 | Window open with a child in the room | Living room | Kit; more sensors are other IoT | Small extension |
| S7 | Unknown person at home | Entrance, living room | Kit and the home router | Partly today |
| S8 | Door or window left open when leaving or at night | Entrance | Kit; other IoT optional | Small extension |
| S9 | Water leak | Kitchen | Other IoT | Future |
| C1 | Pet not going to the food bowl or the water bowl | Kitchen | Kit | Today |
| C2 | Older person: nobody in the kitchen by midday | Kitchen | Kit | Today (fixed time) |
| C3 | Medication box not moved by the usual hour | Kitchen, living room | Kit | Small extension |
| C4 | Cold home with a person in the living room | Living room | Kit | Small extension |
| C5 | Person lying on the floor | Kitchen, living room | Kit | Future |
| C6 | A child arrives home | Entrance | Kit | Today |
| C7 | Pet leaving when the door opens | Entrance | Kit | Small extension |
| V1 | Leaving home without the keys, the wallet or the book | Entrance | Kit | Today |
| V2 | Parcel or mail delivered | Outdoor, at the door | Other IoT | Small extension plus new hardware |
| V3 | "Where is the book?" | All | Kit | Today |
| V4 | Appliance on in an empty room | Living room | Kit | Today |

Of the 20 cases, 18 work with kit devices alone; 6 already work in the prototype, 12 need a small extension (S7 partly works already) and 2 are future.

### Safety

#### S1. Knife on the counter with a cat, dog or child nearby

- Sentence: "Tell me if the cat jumps onto the counter when there is a knife on it." Proposal from the app, when the camera sees a cat and a knife in the kitchen: "Alert if the cat is near a knife on the counter?"
- The camera looks for: `"a knife"`, `"a cat"` (or `"a dog"`, `"a child"`) and the surface `"a kitchen counter"`, in Kitchen 1.
- Rule: `near(knife, cat, Kitchen 1) for 3 s`, where "near" means both boxes are on the same counter or within a fixed distance in the image. Optionally only when no person is in the kitchen, so it stays quiet while someone cooks.
- Devices: camera (kit); light (kit).
- Action: alert with a crop of the counter; red light; the siren only after the user confirms.
- Feasibility: small extension. The prototype already detects cats, dogs and children and finds surfaces by name; it lacks the `"a knife"` query, the counter in the surface vocabulary and the `near` rule kind. The video shows this case as an illustration, not as real detection.
- Limits: at 3 m a knife covers a few dozen pixels of the image the detector analyses (team estimate, not measured); a blade seen edge-on, covered or in a knife block may be missed; "near" in the image does not mean "touching" or "at the same depth", because there is one camera; cooking with the cat around raises alerts unless the rule excludes a person being present.

#### S2. Child with a knife, or near the stove or oven

- Sentence: "Tell me if the child goes near the stove or picks up a knife." Proposal (child profile): "Alert if a child goes near the stove or a knife?"
- The camera looks for: `"a child"`, `"a knife"`, `"a stove"`, `"an oven"`, in Kitchen 1.
- Rules: `near(child, stove, Kitchen 1) for 5 s`; `near(knife, child, Kitchen 1) for 2 s`.
- Devices: camera (kit); light (kit); a connected hob or oven (other IoT), to alert only when it is on; a smart speaker (other IoT), for a voice warning in the kitchen itself.
- Action: alert to the parents with the crop; red light; a voice warning if there is a speaker. The siren is not recommended here: startling a child holding a knife may be worse.
- Feasibility: "near" is a small extension, the same as S1. Knowing whether the child holds the knife needs a pose or hand model, which the architecture plans for a later phase: future.
- Limits: the detector can confuse a child with a short adult and vice versa; "near" is not "holding"; a child helping an adult cook raises alerts, so the parents choose the hours when the rule is active.

#### S3. Stove or oven on with nobody in the kitchen

- Sentence: "Tell me if the hob stays on with nobody in the kitchen for 15 minutes." Proposal, when the home has a connected hob or a cooking appliance on the plug.
- The camera looks for: the absence of `"a person"` in Kitchen 1, without identifying anyone.
- Rules: `on(hob) and nobody_for(Kitchen 1, 15 min)`; for countertop appliances, `power(Plug) > 500 W and nobody_for(Kitchen 1, 15 min)`; the smoke sensor stays as the last line of defence.
- Devices: connected hob or oven (other IoT); plug with energy metering (kit), for an air fryer or a countertop electric oven, if its power fits the plug (to confirm); smoke sensor (kit).
- Action: alert; switch the plug off through the MCP, after confirmation, or automatically if the client chose that when creating the rule; switch the hob off, if the manufacturer and the platform allow it (to confirm).
- Feasibility: through the plug, small extension (the prototype already reads devices through the MCP and already has `nobody_for` and plug-off; they are not combined yet). Through the hob or oven, future, because it depends on the Altice platform supporting those appliances.
- Limits: a slow stew may be intentional, so by default the rule alerts and does not cut power; a person in the dining room, outside the camera's view, counts as "nobody"; the power threshold must be set per appliance.

#### S4. Smoke: who is at home and where

- Sentence: "If the smoke sensor goes off, tell me whether anyone is in the kitchen." Automatic proposal in any home with a smoke sensor and a camera.
- The camera looks for: `"a person"` in each place, over the last few minutes, without identifying anyone.
- Rule: `state(Smoke sensor) = alarm`, together with the presence recorded in each place.
- Devices: smoke sensor (kit), which has its own siren; camera (kit); light (kit).
- Action: an alert such as "The kitchen smoke sensor went off; the kitchen camera saw a person 1 minute ago", with no pictures of people; red light; the hub's siren only after confirmation.
- Feasibility: small extension. The prototype already polls the device list through the MCP, read-only, to follow the door, and the smoke sensor's state comes in the same reply.
- Limits: smoke alerts are already part of Altice's offer; ThingTracker adds context and does not detect fire. The camera never replaces the smoke sensor.

#### S5. Medicines or cleaning products out of place with a child at home

- Sentence: "Tell me if the bleach is out of the cupboard while the child is in the kitchen." Proposal (child profile): "Register the dangerous products in the home?"
- The camera looks for: the registered things (the bleach, the medicine box) and `"a child"`, in Kitchen 1 or Living room 1.
- Rule: `seen_in(bleach, Kitchen 1) and seen_in(child, Kitchen 1)`. If the bleach lives in a closed cupboard, seeing it already means it is out of place.
- Devices: camera (kit).
- Action: alert with a crop of the object.
- Feasibility: small extension. `seen_in` with a thing already works in the prototype; the child condition is missing.
- Limits: an object kept on an open shelf is always visible, so the rule must become "away from its usual place"; similar bottles can confuse the fingerprint; the camera only sees what is in its view.

#### S6. Window open with a child in the room

- Sentence: "Tell me if the living-room window is open and the child is in the living room."
- The camera looks for: `"a child"`, in Living room 1.
- Rule: `state(Window sensor) = open and seen_in(child, Living room 1) for 10 s`.
- Devices: contact sensor (kit; the kit has one, and each extra window needs another unit, other IoT); camera (kit); smart speaker for a voice warning (other IoT).
- Action: alert; red light; voice warning.
- Feasibility: small extension.
- Limits: the client has to say which place each sensor belongs to; the camera may not see the window; the detector can confuse a child with an adult.

#### S7. Unknown person at home

- Sentence: "Tell me if someone comes in when nobody from the family is at home."
- The camera looks for: `"a person"`, in Entrance 1 or Living room 1. Family presence comes from known phones on the home Wi-Fi, as the architecture describes.
- Rule: `someone_arrives(person, Entrance 1) and no family phone at home`.
- Devices: camera (kit); security hub (kit); the home router.
- Action: alert with a photo of the person; the user can arm the alarm, only after an explicit "yes". The MCP alarm tool (`patch_home_security_status`) is labelled read-only although it arms the alarm, so confirmation is always required.
- Feasibility: partly today (the prototype alerts when a person appears in a room that was empty); family phones are a small extension; recognising family members is future, opt-in and needs consent.
- Limits: a visitor or a cleaner while the family is out raises an alert; a phone left at home fools the rule; recognising people needs a legal review (EU AI Act, GDPR Article 9).

#### S8. Door or window left open when leaving or at night

- Sentence: "Tell me if the balcony door is still open after 23:00" or "when I leave home".
- The camera looks for: `"a person"` in Entrance 1, to know when the last person leaves.
- Rule: `state(Contact sensor) = open for 10 min and (time > 23:00 or nobody_for(home, 10 min))`.
- Devices: contact sensor (kit); light (kit), as a reminder by the door; smart lock (other IoT).
- Action: alert; amber light; lock the door only after confirmation.
- Feasibility: the prototype already reads the door sensor live, through the MCP. The night version can already be done with the platform's own scenarios; "when the last person leaves" is a small extension.
- Limits: the camera adds little to a scenario the platform already allows; the kit has one contact sensor.

#### S9. Water leak

- Sentence: "If there is a leak by the dishwasher, show me the kitchen and switch the dishwasher off."
- The camera looks for: nothing specific; it sends the latest crop of the place for the user to judge. There is no claim that the camera sees water.
- Rule: `state(Leak sensor) = alarm`, with the crop and who is at home.
- Devices: leak sensor (other IoT; Altice Labs' Connected Home product page mentions water-leak alerts); plug (kit), if the appliance's power fits the plug (to confirm); solenoid valve (other IoT).
- Action: alert; switch the plug off or close the valve, after confirmation.
- Feasibility: future, because the kit has no leak sensor; the rule itself is simple.
- Limits: the camera adds little; Altice already sells this.

### Care

#### C1. Pet not going to the food bowl or the water bowl

- Sentence: "Tell me if the cat has not been to the water bowl in 12 hours." Proposal (cat or dog profile), which the prototype already makes: food by 20:00 and water within 12 hours.
- The camera looks for: `"a cat"` or `"a dog"`, and the bowls, registered as things or found by name, in Kitchen 1.
- Rules: `not_by(cat, food bowl, 20:00)`; `not_by(cat, water bowl, 12 h)`; for "has not eaten in a day", `not_by(cat, food bowl, 24 h)`.
- Devices: camera (kit).
- Action: alert.
- Feasibility: today, including the automatic proposal when the camera sees the pet.
- Limits: being at the bowl is not eating or drinking; with three cats the rule means "a cat", and telling them apart would mean registering each one as a thing, which has not been tested; a bowl outside the camera's view is not seen.

#### C2. Older person: nobody in the kitchen by midday

- Sentence: "Tell my daughter if nobody goes into the kitchen by midday." Proposal (older person living alone): it appears only if the family declares this profile; the camera never infers it.
- The camera looks for: `"a person"`, in Kitchen 1, without identifying anyone.
- Rules: `nobody_by(Kitchen 1, 07:00–12:00)`; for "no movement at the usual time", `nobody_for(home, 2 h)` within the home's usual hours.
- Devices: camera (kit); presence sensors without images (other IoT), for bedrooms, where there are no cameras; smart speaker (other IoT), to ask "is everything all right?".
- Action: alert to a relative.
- Feasibility: today, with a fixed time. Learning the home's usual hours is future.
- Limits: a visitor counts as "someone"; the person may be in a room with no camera, which raises an alert (better than silence); never a siren.

#### C3. Medication box not moved by the usual hour

- Sentence: "Tell me if the pill box has not moved by 10:00."
- The camera looks for: the box, registered as a thing with 8 views, in Kitchen 1 or Living room 1.
- Rule: `not_moved_by(box, 10:00)` (new): the box has been seen in the same place since the morning.
- Devices: camera (kit); smart speaker (other IoT), for a spoken reminder.
- Action: reminder to the person, or alert to a relative.
- Feasibility: small extension. The prototype already records each change of place of a thing; the rule kind is missing.
- Limits: moving the box is not taking the medicine; with a weekly organiser the camera cannot tell which compartment was opened; the box must stay where the camera sees it, not in the bedroom.

#### C4. Cold home with a person in the living room

- Sentence: "If the living room is below 18 °C and someone is in it, tell me." The family chooses the threshold.
- The camera looks for: `"a person"`, in Living room 1.
- Rule: `temperature(Sensor) < 18 °C and seen_in(person, Living room 1) for 15 min`.
- Devices: temperature and humidity sensor (kit, read live through the MCP); plug (kit), with a heater, if its power fits the plug (to confirm).
- Action: alert to the family; switch the plug on only after confirmation.
- Feasibility: small extension. The MCP already gives the temperature; the prototype does not combine it with presence yet.
- Limits: the sensor must be in the camera's room; switching a heater on remotely carries risk, so only with someone present and after confirmation.
- Context: in Portugal, 22.2 % of people aged 65 or over cannot keep their home adequately warm (Eurostat, `hlth_dhc140`, 2025).

#### C5. Person lying on the floor

- Proposal (older person profile): "Alert if someone stays lying on the kitchen or living-room floor for more than 1 minute?"
- The camera looks for: the person's posture, with a pose model the architecture plans for a later phase.
- Rule: `lying(person, Kitchen 1) for 60 s`.
- Devices: camera (kit); smart speaker (other IoT), to ask "are you all right?".
- Action: alert to the family; never a siren.
- Feasibility: future.
- Limits: someone lying on the sofa or playing on the floor raises alerts; falls in bedrooms or bathrooms are not covered, because there are no cameras there.

#### C6. A child arrives home

- Sentence: "Tell me when the child gets home." Proposal (child profile), which the prototype already makes.
- The camera looks for: `"a child"`, in Entrance 1.
- Rule: `someone_arrives(child, Entrance 1, 30 min)`: a child seen after 30 minutes with none.
- Devices: camera (kit); door contact sensor (kit).
- Action: alert, with no photo.
- Feasibility: today.
- Limits: any child counts, a friend included; there is no identification unless the family turns it on.

#### C7. Pet leaving when the door opens

- Sentence: "Tell me if the dog goes out when the door opens." Proposal (dog or cat profile).
- The camera looks for: `"a dog"` or `"a cat"`, in all places, above all Entrance 1.
- Rule: `leave_without(dog, 5 min)`: the door opens and, in the next 5 minutes, the dog is not seen again in any place.
- Devices: door contact sensor (kit, read live through the MCP); camera (kit).
- Action: alert with the time the door opened and the last place the dog was seen.
- Feasibility: small extension. The prototype already has `leave_without` for things and already detects dogs and cats; the rule has not been applied to an animal yet.
- Limits: a dog asleep in a bedroom, with no camera, stops being seen without having left; a walk also raises an alert, unless the rule ignores exits where the dog and a person are seen together at the door.

### Everyday convenience

#### V1. Leaving home without the keys, the wallet or the book

- Sentence: "Tell me if I leave home without my book." This is the demo's example.
- The camera looks for: the book, registered with 8 views and recognised by its fingerprint, in any place.
- Rule: `leave_without(book, 60 s)`: the door opens and, 60 seconds later, the book was last seen at home.
- Devices: door contact sensor (kit, read live through the MCP); camera (kit); light (kit), as a reminder; smart speaker by the door (other IoT).
- Action: alert with the book's photo and last place; light.
- Feasibility: today, with the real door sensor or the simulated door.
- Limits: the door also opens when someone arrives; a thing taken out without the camera seeing it still counts as "at home"; small things in a pocket or a bag are not seen.

#### V2. Parcel or mail delivered

- Sentence: "Tell me when a parcel is left at the door" or "when mail arrives".
- The camera looks for: `"a cardboard box"` or `"a parcel"`, in the place "Door" (outdoor).
- Rules: `appears(parcel, Door) and stays 1 min` (new); for mail, `state(Mailbox) = open`.
- Devices: outdoor camera at the door (other IoT; the kit camera is IP65 and could in principle sit at a covered entrance, an assumption to confirm with Altice); mailbox sensor (other IoT), or the kit's contact sensor on the mailbox flap if it is within the hub's range (to confirm).
- Action: alert with a crop of the parcel, and only of the parcel.
- Feasibility: small extension (detecting an object class without enrolment, and an "appears" rule kind), plus new hardware.
- Limits: the framing must leave out the street and the neighbours; night, rain and backlight reduce detection; there is no claim that the system detects parcel theft.

#### V3. "Where is the book?"

- Question: "Where is the book?"
- The camera looks for: the registered book, in all places.
- Rule: none; the answer comes from the last sighting (place, time and photo).
- Devices: camera (kit).
- Action: answer in the app, with the photo.
- Feasibility: today.
- Limits: it can only answer with what a camera saw; "last seen" does not mean "is there now".

#### V4. Appliance on in an empty room

- Sentence: "If nobody has been in the living room for 30 minutes, switch the heater off."
- The camera looks for: the absence of `"a person"`, in Living room 1.
- Rule: `nobody_for(Living room 1, 30 min) and power(Plug) > 50 W`.
- Devices: plug with energy metering (kit); camera (kit).
- Action: switch the plug off through the MCP.
- Feasibility: today (`nobody_for` and plug-off already exist; the power condition is a small extension).
- Limits: energy management is already part of Altice's offer; see the next section on people sitting still.

### Limits common to every case

- The models run only when there is motion or sound. Absence rules (`nobody_for`, `nobody_by`, `not_by`) measure "no motion seen", not "nobody there": a person reading, sitting still, may count as absent.
- Small objects at a distance (a knife, a pill box, the keys) cover a few dozen pixels; the camera has to be close to the spot that matters.
- "Near" is measured in the image, in two dimensions. The depth model planned in the architecture reduces this error but does not remove it.
- In the prototype the surface vocabulary is desk, table, shelf, sofa and workbench; adding kitchen counter, stove and oven is a small extension.
- Each rule has a cooldown between alerts so it does not repeat itself; doubtful cases can be checked by the language model from a single crop.
- Event to action takes about 2 to 3 s, measured on the team's laptop.
- The MCP server has no push notifications and no event feed; the prototype polls the sensors.
- A device that is not in the kit is only usable if the Altice platform supports it and can provision it, which Altice does not guarantee.

## 2. Cameras: how many, where and under which rules

### 2.1 How many

Two or three cameras per home is the plan (team assumption):
- one in the kitchen, where 9 of the 20 cases happen (S1 to S5, C1, C2, C3 and C5);
- one in the living room or the entrance, for presence, things and leaving home;
- optionally one outdoors, at the door, for parcels.

Each camera is one place. Two cameras in the same room are two places ("Kitchen 1", "Kitchen 2").

Three facts bear on the number of cameras:
- A full perception cycle takes about 0.65 s per frame on the team's laptop, about 1.5 frames per second. With three cameras seeing motion at once, the home device alternates between them, and the rate per camera falls in proportion (estimate, not measured).
- Because the models run only on motion, the electricity cost follows the hours of motion, not the number of cameras.
- The kit camera uses 2.4 GHz Wi-Fi only and streams H.265 at 2304 × 1296 and 20 frames per second (checked on 18 November).

### 2.2 Indoor and outdoor

| | Indoor | Outdoor, at the door |
|---|---|---|
| What it is for | Kitchen safety, care, things, presence | Parcels, visitors at the door |
| Cases | S1 to S9, C1 to C7, V1, V3, V4 | V2 and part of S7 |
| Care needed | Never in bedrooms or bathrooms | Frame only the home's own entrance; the street and the neighbours stay out; legal sign-off rests with Altice |
| Hardware | The kit camera | An outdoor camera (other IoT), or the kit camera at a covered entrance if Altice confirms it |

### 2.3 Where to put them

- Kitchen: high in a corner, with the counter, the stove and the pet bowls in view; no window behind the scene; as close to the counter as possible (2 to 3 m, an assumption to measure) so a knife stays visible.
- Entrance: facing the door from inside, with the table or dish where the keys go.
- Living room: with the sofa, the table and the window that has the contact sensor.
- Outdoor: only the doormat, sheltered from rain, without the street.

### 2.4 What each place unlocks

| Place | Cases | Devices that add value |
|---|---|---|
| Kitchen | S1, S2, S3, S4, S5, C1, C2, C3, C5 | Smoke sensor and plug (kit); connected hob or oven, leak sensor, smart speaker (other IoT) |
| Living room | S5, S6, S7, C3, C4, C5, V3, V4 | Temperature sensor and plug (kit); window contact sensors (other IoT) |
| Entrance, inside | S7, S8, C6, C7, V1, V3 | Door contact sensor and light (kit); smart lock (other IoT) |
| Outdoor, at the door | V2 | Mailbox sensor (other IoT) |

### 2.5 Privacy rules

- The client chooses where the cameras go. The solution does not plan cameras in bedrooms or bathrooms; there, presence sensors without images (other IoT) cover the care cases.
- The models run only when there is motion or sound; the rest of the time the camera is idle.
- Real-time cropping option: everything except the tracked object is removed from the image before any analysis. This is an option proposed by the team; today the prototype already sends the server only small crops, never full frames.
- People are detected as "a person" or "a child", without identification. Recognising family members is opt-in, turned on person by person, with consent, and done on the home device.
- The client can set masks: areas of the image that are never analysed.
- ThingTracker records no video; observations stay 30 days on the home device.
- Only the unknown-person case (S7) sends a photo of a person. The others send a crop of an object or no image at all (C6, for instance, never sends a photo).

## 3. Use cases and evaluation criteria

### 3.1 The criteria

Criteria and weights from Articles 16 and 18 of the participation rules (`sources/rules/normas-2026.pdf`). The criterion names are the rules' own Portuguese wording, with an English gloss.

| Criterion | Intermediate | Final | How ThingTracker answers it | Where the evidence is |
|---|---|---|---|---|
| Enquadramento e resposta ao Desafio (fit and response to the challenge) | 25 % | 20 % | The camera becomes a source of information; one sentence becomes a sensor, "beyond commands"; the cases combine the camera with the kit's sensors; the MCP is integrated (reads the door, acts on the plug and the light); the kitchen-safety cases answer what the mentors asked for | Prototype (`prototype/`); report (Figure 1 and the list of cases); video (`video/`, in progress); this document |
| Facilidade de adoção do Projeto por parte dos Desafiadores (ease of adoption by the challenger) | 25 % | 20 % | A fifth tab in the existing app; actions go through the MCP Altice already has; rules are saved as platform scenarios; 18 of the 20 cases use kit devices only | Architecture (`docs/14-architecture.md`, §3 and D5); integration spec (`docs/15-integration-spec.md`); the app replica in the prototype |
| Viabilidade de implementação e gestão futura (sustentabilidade) do Projeto (feasibility and sustainability) | 25 % | 20 % | Open-source models free for commercial use; vision only on motion, on the router or on Altice servers; the language model is called only to create a rule or answer a question; about €0.43 per home per month on the language model and €0.49 on vision (the report's estimate); 6 cases work today and 12 are small extensions | Report ("Ferramentas de IA"); architecture (§8); business case (`docs/16-business-case.md`) |
| Possibilidade de replicação em outros territórios e contextos (replication in other territories and contexts) | — | 20 % | A platform service for any operator; no data is specific to Portugal; the language model speaks the user's language; France is the second market analysed | Business case (France section); architecture (requirement N5) |
| Apresentação da solução (presentation) | 25 % | 10 % | Live demo with the kit camera and the book; video with the knife-and-cat case (illustration); cases told in one sentence | Video; prototype; pitch |
| Documentação (Entregáveis) da solução (documentation) | — | 10 % | Two-page report; architecture, integration spec, business case and use cases, in Portuguese and English | `deliverables/`, `docs/pt/`, `docs/` |

### 3.2 Matrix

The team's self-assessment, for discussion. Scale per criterion:
- Fit: strong if the camera is a source of information combined with another sensor or an action, in a case the mentors asked for or outside Altice's current offer; medium if the camera only adds context to an alert that already exists.
- Adoption: strong if the kit is enough; medium if it needs more kit units or a device Altice already mentions in its offer; weak if it needs a new kind of device on the platform.
- Feasibility: strong if it works in the prototype; medium if it is a small extension; weak if it is future.
- Replication: strong if it depends on neither country nor home; medium if it depends on local rules or a third-party device.
- Presentation: strong if it can be shown live or in the video; medium if it is only described.
- Documentation: strong if it is also in the report or the architecture; medium if it is only in this document.

| Case | Fit | Adoption | Feasibility | Replication | Presentation | Documentation |
|---|---|---|---|---|---|---|
| S1 Knife and pet or child | strong | strong | medium | strong | strong | strong |
| S2 Child, knife, stove | strong | strong | medium | strong | strong | medium |
| S3 Stove with nobody | strong | medium | medium | medium | medium | strong |
| S4 Smoke: who is there | medium | strong | medium | strong | medium | medium |
| S5 Dangerous products | strong | strong | medium | strong | medium | medium |
| S6 Window and child | strong | medium | medium | strong | medium | medium |
| S7 Unknown person | strong | strong | medium | medium | medium | strong |
| S8 Door left open | medium | strong | medium | strong | medium | medium |
| S9 Water leak | medium | medium | weak | strong | medium | medium |
| C1 Pet bowls | strong | strong | strong | strong | strong | strong |
| C2 Older person | strong | strong | strong | strong | medium | strong |
| C3 Medication | strong | strong | medium | strong | medium | medium |
| C4 Cold home | strong | strong | medium | strong | medium | medium |
| C5 Fall | strong | strong | weak | strong | medium | medium |
| C6 Child arrives | medium | strong | strong | strong | medium | medium |
| C7 Pet leaves by the door | strong | strong | medium | strong | medium | strong |
| V1 Leaving without the book | strong | strong | strong | strong | strong | strong |
| V2 Parcels | strong | medium | medium | medium | medium | strong |
| V3 "Where is it?" | strong | strong | strong | strong | strong | strong |
| V4 Energy | medium | strong | strong | strong | medium | medium |

"Strong" for Documentation on S1, S3, C7 and V2 assumes the report adopts the new list of cases.

## 4. Value proposition

- For the family: the camera already in the home starts warning about dangers nobody is watching (the knife within the cat's reach, the forgotten stove, the grandmother who has not come into the kitchen) and answers "where is it?".
- For the family: every alert comes from a sentence or from a proposal accepted with one tap; the siren never sounds without a "yes", and no full image leaves the home for analysis.
- For Altice and MEO, differentiation: the cameras and sensors they already sell become a new service, inside the app and the MCP that already exist.
- For Altice and MEO, revenue: an add-on of €3.99 a month, of which about €1.74 per home remains, and about 19,000 MEO homes in the expected case (business-case assumptions).
- For Altice Labs: a platform service for any operator, and a reason to sell more sensors (connected hob, leak sensor, smart lock).

## 5. Assumptions and open questions

1. Two or three cameras per home is a team assumption, to validate with customers.
2. Notification service: the MCP has no tool for alerts; which service the app uses is unknown.
3. Siren: the MCP write tool accepts power, brightness, colour temperature and colour; how to sound the camera's or the hub's siren is still to confirm. In any case, only after a "yes".
4. Other devices (connected hob or oven, leak sensor, smart lock, mailbox sensor, smart speaker, presence sensors): which ones the platform supports is unknown.
5. Kit camera outdoors (IP65): to confirm with Altice.
6. Maximum power of the kit plug: unknown.
7. Detection reliability for knives, parcels and pill boxes at a distance: not measured.
8. Legal review: outdoor camera framing and recognition of family members.

Sources: Aveiro Tech City Hackathon 2026 participation rules, Articles 16 and 18; Eurostat, `hlth_dhc140` (2025, read on 18 November 2026, see `docs/12-market-research.md`); Altice Labs' Connected Home product page (see `docs/02-challenge.md`); business case (`docs/16-business-case.md`); team measurements, 18 November 2026.
