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
- Place: each camera is one place ("Kitchen 1", "Living room 1", "Garden 1"). There are no zones drawn inside a place; surfaces (the counter, the stove) are found by name in every frame.
- Feasibility: "today" means the prototype already does it; "small extension" means a new detector query or a new rule kind, with no new hardware; "future" means a new model, or a device the Altice platform would still have to support.
- Actions: alerts reach the phone through the app's notification service, because the MCP server has no notification tool (to confirm with Altice). Device actions (light, plug) go through the MCP, with `update_device_capabilities`. The siren and the alarm act only after the user says "yes"; in the prototype neither is wired, and light and plug actions are simulated unless enabled.

## 1. Catalogue, in priority order

Indoors: safety first, then care, then everyday convenience. The outdoor cases (E1 to E9) have their own section, also in priority order, and the two home-timeline cases (T1 and T2) follow it.

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
| S10 | Smoke, flame or water on the floor seen by the camera | Kitchen | Kit; other IoT optional (valve) | Future |
| C1 | Pet not going to the food bowl or the water bowl | Kitchen | Kit | Today |
| C2 | Older person: nobody in the kitchen by midday | Kitchen | Kit | Today (fixed time) |
| C3 | Medication box not moved by the usual hour | Kitchen, living room | Kit | Small extension |
| C4 | Cold home with a person in the living room | Living room | Kit | Small extension |
| C5 | Person lying on the floor | Kitchen, living room | Kit | Future |
| C6 | A child arrives home | Entrance | Kit | Today |
| C7 | Pet leaving when the door opens | Entrance | Kit | Small extension |
| V1 | Leaving home without the keys, the wallet or the book | Entrance | Kit | Today |
| V2 | "Where is the book?" | All | Kit | Today |
| V3 | Appliance on in an empty room | Living room | Kit | Today |
| V4 | Pet on the forbidden sofa | Living room | Kit | Today (alert); small extension (plug) |
| V5 | Presence and posture: light and heating | Living room | Kit; other IoT (thermostat) | Small extension (presence); future (posture) |
| V6 | Gestures: light, TV, coffee machine | Living room, kitchen | Kit | Future |
| E1 | Break-in: someone forcing a door or window | Door, back of the house | Other IoT (outdoor camera); kit | Small extension |
| E2 | A person in the garden or at the gate at night | Garden, gate | Other IoT (outdoor camera, floodlights, blinds, speaker) | Small extension |
| E3 | Gate open with the dog or a child in the garden | Garden, gate | Other IoT | Small extension |
| E4 | Theft: the bike or the parcel stops being seen | Garden, door | Other IoT; kit | Small extension |
| E5 | Parcel or mail delivered | Door | Other IoT; kit light | Small extension |
| E6 | The car arrives home | Garage | Other IoT | Small extension; the plate is future |
| E7 | Things left outside: bike, garden hose, bin | Garden | Other IoT | Small extension |
| E8 | Animals in the garden: sprinkler for 5 s | Garden | Other IoT | Small extension |
| E9 | The dog at the back door: open the pet door | Back of the house | Other IoT | Future |
| T1 | Too late: what was near the child, and when | Kitchen | Kit | Small extension; "ate or drank" is future |
| T2 | What happened at 4 a.m.? | All, outdoor | Kit; other IoT optional (outdoor camera) | Small extension; the bark and "unusual" are future |

Of the 34 cases, 24 work with kit devices alone, and the 9 outdoor ones need an outdoor camera (other IoT). Seven already work in the prototype, 22 need a small extension (S7 partly works already) and 5 are future.

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

#### S10. Smoke, flame or water on the floor seen by the camera

- Sentence: "If the camera sees flames in the empty kitchen, switch the air fryer off" or "if it sees water on the floor, shut the water off". One of the IoT ideas proposed within the team.
- The camera looks for: `"smoke"`, `"fire"`, `"a puddle of water"`, in Kitchen 1; in doubtful cases the language model checks a single crop.
- Rules: `seen_in(flame, Kitchen 1) for 5 s and nobody_for(Kitchen 1, 5 min)`; `seen_in(water on the floor, Kitchen 1) for 30 s`.
- Devices: camera (kit); plug (kit), with the appliance; water shut-off valve (other IoT); smoke sensor (kit), which stays the reference alarm.
- Action: alert with the crop; switch the plug off or close the valve, after confirmation.
- Feasibility: future. OWLv2 accepts these queries, but their reliability has not been measured; a model trained for smoke and flame would be safer.
- Limits: steam from a pan looks like smoke; a reflection on the floor can look like water; a gas hob's flame is a flame too, so the rule only holds with the kitchen empty; the camera never replaces the smoke sensor or the leak sensor.

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

#### V2. "Where is the book?"

- Question: "Where is the book?"
- The camera looks for: the registered book, in all places.
- Rule: none; the answer comes from the last sighting (place, time and photo).
- Devices: camera (kit).
- Action: answer in the app, with the photo.
- Feasibility: today.
- Limits: it can only answer with what a camera saw; "last seen" does not mean "is there now".

#### V3. Appliance on in an empty room

- Sentence: "If nobody has been in the living room for 30 minutes, switch the heater off."
- The camera looks for: the absence of `"a person"`, in Living room 1.
- Rule: `nobody_for(Living room 1, 30 min) and power(Plug) > 50 W`.
- Devices: plug with energy metering (kit); camera (kit).
- Action: switch the plug off through the MCP.
- Feasibility: today (`nobody_for` and plug-off already exist; the power condition is a small extension).
- Limits: energy management is already part of Altice's offer; see, under the common limits, people sitting still.

#### V4. Pet on the forbidden sofa

- Sentence: "If the dog gets on the sofa, switch the deterrent on." One of the IoT ideas proposed within the team.
- The camera looks for: `"a dog"` or `"a cat"` and the surface `"a sofa"`, in Living room 1.
- Rule: `seen_in(dog, sofa) for 5 s`.
- Devices: camera (kit); plug (kit), with a deterrent, for example a device that makes a sound.
- Action: alert; switch the plug on for a few seconds.
- Feasibility: the alert works today (the prototype already ties each animal to the surface it is on, and the sofa is in the vocabulary); switching the plug on from a rule is a small extension.
- Limits: a dog lying still on the sofa makes no motion, so the models may not even run; the deterrent should be gentle, such as a sound, and never anything that could hurt the animal.

#### V5. Presence and posture: light and heating

- Sentences: "When someone comes into the living room at night, turn the light on, warm white" and "if someone falls asleep on the sofa, turn the heating down". One of the IoT ideas proposed within the team.
- The camera looks for: `"a person"`, in Living room 1; for posture (sitting, lying down), a pose model.
- Rules: `someone_arrives(person, Living room 1) after sunset` → light; `lying(person, sofa) and still for 20 min` → thermostat.
- Devices: light (kit); thermostat or connected heating (other IoT).
- Action: turn the light on through the MCP (power, brightness and colour temperature); turn the thermostat down.
- Feasibility: presence is a small extension (the prototype already detects a person arriving; the action of turning the light on in white is missing); posture is future, because it needs a pose model.
- Limits: "asleep" cannot be seen in an image, and the most that can be measured is "lying down and still"; a person who is still makes no motion, so a frame would have to be analysed at fixed intervals; ordinary motion sensors already switch lights on as people walk in, which reduces the value of this case.

#### V6. Gestures: light, TV, coffee machine

- Sentence: "When I raise an open hand in the living room, turn the light off." One of the IoT ideas proposed within the team.
- The camera looks for: hand gestures, with a gesture model.
- Rule: `gesture(open hand, Living room 1)` → action.
- Devices: light (kit); plug (kit), with the coffee machine; TV or set-top box (not in the kit; the Altice Labs page mentions managing set-top boxes).
- Action: switch on or off through the MCP.
- Feasibility: future, because it needs a gesture model.
- Limits: an involuntary gesture fires an action; voice or a button in the app do the same with fewer errors; it risks looking like a trick, when Altice asked at the kick-off for something that is "not just a gimmick".

### Outdoor

The following cases need an outdoor camera (other IoT): at the door, in the garden, at the gate or at the garage entrance. Here too safety comes first. All of them are subject to the rules in section 2.6: the camera may only cover the property and, where strictly necessary, the access to it. Limits specific to outdoors: at night the camera uses night vision and detection gets worse (not measured); rain, wind in the trees and animals cause motion and therefore analyses; objects are further from the camera.

#### E1. Break-in: someone forcing a door or window

- Sentence: "Tell me if someone tampers with the back window when nobody is at home."
- The camera looks for: `"a person"`, at Back 1, without identifying anyone.
- Rule: `seen_in(person, Back 1) and no family phone at home`, reinforced by `state(Window sensor) = open`.
- Devices: outdoor camera (other IoT); window contact sensor (kit; more units are other IoT); security hub (kit); floodlight (other IoT).
- Action: alert with a photo of the person; floodlight on; arm the alarm or sound the siren only after a "yes".
- Feasibility: small extension (the rule combines `seen_in`, the phones' presence and the contact sensor).
- Limits: a gardener or a known neighbour raises an alert; the system shows what it saw and does not prove a break-in; Altice's alarm already detects the window opening, and ThingTracker adds the photo and the context.

#### E2. A person in the garden or at the gate at night

- Sentence: "If someone is in the garden after midnight, turn the floodlights on." The idea proposed within the team adds the blinds and a speaker that imitates a barking dog.
- The camera looks for: `"a person"`, in Garden 1 or at Gate 1, without identifying anyone.
- Rule: `seen_in(person, Garden 1) for 30 s and time between 00:00 and 06:00`; the minimum time avoids alerts for someone just passing.
- Devices: outdoor camera, floodlights, blind motors, outdoor speaker (other IoT); light (kit), switched on inside.
- Action: floodlights on at once, because they make no noise; alert with the crop; blinds and the barking speaker, if the client chose them when creating the rule; the siren only after a "yes".
- Feasibility: small extension (`seen_in` with a person already exists; the time window and the minimum time are missing).
- Limits: without recognition (opt-in, with consent) the system cannot know it is a stranger, so the rule says "a person"; a relative coming home late triggers it unless their phone is already on the home network; a barking dog at 3 a.m. disturbs the neighbours.

#### E3. Gate open with the dog or a child in the garden

- Sentence: "Tell me if the gate is left open with the dog in the garden."
- The camera looks for: `"a dog"` or `"a child"`, in Garden 1. The gate's state comes from a contact sensor or, without one, from a visual check of a crop of the gate by the language model.
- Rule: `state(Gate sensor) = open and seen_in(dog, Garden 1)`.
- Devices: outdoor camera (other IoT); contact sensor on the gate (other IoT, the kit's type, if within the hub's range, to confirm); light (kit).
- Action: alert with a crop of the gate; amber light inside.
- Feasibility: small extension.
- Limits: the visual check depends on angle and light; the sensor is more reliable; a child in the garden with an adult beside them raises an alert.

#### E4. Theft: the bike or the parcel stops being seen

- Sentence: "Tell me if the bike leaves the garden when nobody is at home."
- The camera looks for: the bike, registered with 8 views like the book, in Garden 1; and `"a person"` in the minutes before.
- Rules: `missing(bike, Garden 1) for 2 min and no family phone at home` (new); for the parcel, `missing(parcel, Door 1) and the front door did not open`.
- Devices: outdoor camera (other IoT); door contact sensor (kit).
- Action: alert with the last crop of the bike and, if there is one, of the person seen next to it.
- Feasibility: small extension (the prototype already keeps each thing's last sighting; the "stopped being seen" rule is missing).
- Limits: the alert says what the camera saw ("stopped being seen"), not that there was a theft; a neighbour taking the parcel in for safekeeping raises an alert; a bike hidden behind a car counts as gone.

#### E5. Parcel or mail delivered

- Sentence: "Tell me when a parcel is left at the door" or "when mail arrives". The idea proposed within the team adds an announcement on a speaker inside and the light turning blue.
- The camera looks for: `"a cardboard box"` or `"a parcel"`, at Door 1 (outdoor).
- Rules: `appears(parcel, Door 1) and stays 1 min` (new); for mail, `state(Mailbox) = open`.
- Devices: outdoor camera at the door (other IoT; the kit camera is IP65 and could in principle sit at a covered entrance, an assumption to confirm with Altice); mailbox sensor (other IoT), or the kit's contact sensor on the mailbox flap if it is within the hub's range (to confirm); light (kit); smart speaker inside (other IoT).
- Action: alert with a crop of the parcel, and only of the parcel; blue light (the prototype already has this action); speaker announcement: "A parcel has arrived at the door."
- Feasibility: small extension (detecting an object class without enrolment, and an "appears" rule kind), plus new hardware.
- Limits: the framing must leave out the street and the neighbours; night, rain and backlight reduce detection; a parcel disappearing is case E4.

#### E6. The car arrives home

- Sentence: "Tell me when the car arrives." The idea proposed within the team goes further: read the plate and open the garage door.
- The camera looks for: `"a car"`, at Garage 1, the garage entrance inside the property. Reading the plate would need a model of its own.
- Rules: `appears(car, Garage 1)` → alert; `plate(registered plate, Garage 1) and the owner's phone on the home network` → open the door (future).
- Devices: outdoor camera (other IoT); garage door motor (other IoT).
- Action: alert "The car has arrived"; open the garage door only if the client turns this on and, preferably, after confirming on the phone.
- Feasibility: the car is a small extension; the plate is future.
- Limits and legal questions: a licence plate is personal data (EDPB, Guidelines 3/2019, para. 8), and the camera also reads visitors' plates; so reading plates is opt-in only, at the home's own garage entrance only, and after a legal assessment (to verify). A plate is easy to copy: opening the garage on the plate alone would be unsafe, hence the owner's phone presence as well.

#### E7. Things left outside: the bike, the garden hose, the bin

- Sentences: "Remind me at 22:00 if the bike is still in the garden"; "tell me if the hose is left on the lawn at night"; "if the bin is still in its place at 21:00 on Tuesday, remind me to put it out".
- The camera looks for: the registered things (the bike, the hose, the bin), in Garden 1.
- Rules: `seen_in(bike, Garden 1) at 22:00`; `not_moved_by(bin, Tuesday 21:00)` (new, the same kind as C3).
- Devices: outdoor camera (other IoT); smart speaker (other IoT), for a spoken reminder.
- Action: reminder on the phone or the speaker.
- Feasibility: small extension (a time condition on `seen_in` and the `not_moved_by` kind are missing).
- Limits: the bin is seen where it is kept, inside the property, not on the street, which the camera must not film; a hose on the ground is thin and long, and detection at a distance is uncertain (not measured). The gate left open is case E3.

#### E8. Animals in the garden: sprinkler for 5 s

- Sentence: "If a cat comes into the garden, turn the sprinkler on for 5 seconds." One of the IoT ideas proposed within the team.
- The camera looks for: `"a cat"`, `"a dog"` or `"a bird"`, in Garden 1; the home's own pets, registered as things, are excluded.
- Rule: `seen_in(cat, Garden 1) and not the home's cat` → sprinkler for 5 s, at most once every 10 minutes.
- Devices: outdoor camera; solenoid valve or irrigation controller (other IoT).
- Action: run the sprinkler for 5 s.
- Feasibility: small extension (the rule) plus new hardware; telling the home's pet from a similar animal by its fingerprint has not been tested.
- Limits: if recognition fails, the sprinkler soaks the home's own pet, or a person in the garden; each trigger uses water.

#### E9. The dog at the back door: open the pet door

- Sentence: "When the dog is at the back door, unlock the pet door for it." One of the IoT ideas proposed within the team.
- The camera looks for: the home's dog, registered as a thing with 8 views, at Back 1.
- Rule: `seen_in(registered dog, Back 1) for 3 s` → unlock the pet door for 30 s.
- Devices: outdoor camera (other IoT); pet door with an electric latch (other IoT).
- Action: unlock the pet door, and only for the registered animal.
- Feasibility: future. Recognising one particular animal, not "a dog", by its fingerprint has not been tested and would have to be very reliable, because it opens a way into the home.
- Limits: a similar dog or a wild animal could get in; microchip pet doors already solve this without a camera, and the camera could simply report it ("the dog came in at 15:00").

### The home timeline

The memory that finds things (the place, time and crop of each sighting) can also tell what happened. The two cases below, proposed by a member of the team, raise no alert: they answer a question asked afterwards, with a list of events, each with its type, time, place and image, kept for a limited time and then deleted (proposal in section 2.5).

#### T1. Too late: what was near the child, and when

- Question: "What was near the child this afternoon?" or, after an alert from the child-in-danger case: "Show me what happened in the kitchen between 16:00 and 16:30."
- The camera looks for: the same as in the child-in-danger case (S2 and S5): the child near a detergent, a medicine, food or a drink, in Kitchen 1. Each event keeps its type, time, place and a crop.
- Rule: nothing new; a query on the timeline, for example `timeline(child, Kitchen 1, 16:00–16:30)`, which the language model summarises in plain words.
- Devices: camera (kit).
- Action: the app shows the sequence with the crops ("16:28, next to a detergent; 16:29, next to a glass"), so the parents can decide what to tell the doctor.
- Feasibility: small extension. The prototype already keeps, for each thing, the place, the time and a crop, and keeps the child's presence without an image; the "near" event with a crop is missing, the same as in S2 and S5. Knowing whether the child ate or drank needs an action model, which is future: the app shows what was near, and the parents judge.
- Limits: "near" is not "ate"; what happens outside the camera's view does not appear; keeping crops of a child raises the privacy risk, so only with the parents' consent and the time limit of section 2.5.

#### T2. What happened at 4 a.m.?

- Question: "What happened tonight between 3:00 and 5:00?", after an alarm at home or a burglary nearby.
- The camera looks for: events that are unusual for that home: the dog barking at an hour when it never barks, a person at a window (`"a person"`, on the outdoor camera), a door open (contact sensor). Each event keeps its type, time, place and an image; for sound only the label is kept ("bark, 4:02"), never the audio (proposal).
- Rule: a query, for example `timeline(home, 03:00–05:00, unusual only)`, where "unusual" is measured against the home's own pattern.
- Devices: camera (kit), whose microphone serves as a trigger; contact sensor (kit); security hub (kit), whose alarm history the MCP already reads (`get_home_security_alarm_history`); outdoor camera (other IoT), for the window.
- Action: the app shows the list with the images; the family can pin events to keep them longer, and export them.
- Feasibility: the prototype's timeline already keeps people and animals with place and time, without images; adding images to security events and an "unusual only" view are small extensions. Recognising a bark by its sound needs an audio model, and knowing what is unusual needs learning the home's pattern (like C2's usual hours): future. Today the prototype does not handle sound.
- Limits: sound raises a legal question, because Article 19(4) of Lei n.º 58/2019 forbids capturing sound where video surveillance is allowed, except while the premises are closed or with the CNPD's prior authorisation; whether it applies to a private home is to verify (section 2.6). The outdoor camera follows the rules of section 2.6. Handing images to a neighbour or the authorities: to verify. With a dog that barks a lot almost everything is unusual, and the list only helps if it is short.
- The story behind the case: a team member's neighbour was burgled; the team member's dog barked at 4 a.m., and that time helped the neighbour search the recordings of her own camera.

### IoT ideas proposed within the team: where they fit

Nine ideas proposed within the team combine the camera with other devices. The table gives the catalogue case where each one fits, what the architecture already has and what is missing. Three need models beyond OWLv2 and DINOv2 (pose, licence plates and gestures) and are future; so are smoke and flame, until a trained and measured model exists.

| Idea | Case | What exists | What is missing | Feasibility |
|---|---|---|---|---|
| Parcel detected: announcement on an indoor speaker and the light turning blue | E5 | Detection by name (OWLv2); the "blue light" action through the MCP | Outdoor camera; speaker on the platform; "appears" rule | Small extension plus hardware |
| Car or plate recognised: garage door | E6 | Detection of `"a car"` | Plate model; garage door motor on the platform; opt-in and legal assessment | Car: small extension; plate: future |
| Stranger loitering at night: floodlights, blinds, barking speaker | E2 | Person detection; the `seen_in` rule; phone presence (architecture) | Outdoor camera; floodlights, blinds and speaker on the platform; time window and minimum time in the rule | Small extension plus hardware |
| The dog at the back door: pet door, only for the registered pet | E9 | Visual fingerprint (DINOv2) | Reliability for one particular animal, not measured; pet door on the platform | Future |
| Animals in the garden: sprinkler for 5 s | E8 | Animal detection | Sprinkler on the platform; excluding the home's own pets | Small extension plus hardware |
| Pet on the forbidden sofa: deterrent on the plug | V4 | Animals tied to surfaces, the sofa included; plug through the MCP | Switching the plug on from a rule | Today (alert); small extension (plug) |
| Presence or posture (sitting, asleep): light and thermostat | V5 | Person detection; light through the MCP | Pose model; thermostat on the platform | Presence: small extension; posture: future |
| Smoke, flame or water pooling seen: plug off or water shut-off valve | S10 | Query by name; visual check of a crop | Smoke and flame model with measured reliability; valve on the platform | Future |
| Gestures: TV, light, coffee machine | V6 | Light and plug through the MCP | Gesture model | Future |

All of these devices would have to exist on the Altice platform. The MCP write tool accepts power, brightness, colour temperature and colour today: enough for a valve, a sprinkler or a floodlight exposed as switches, but not for blinds or doors with a position (to confirm with Altice).

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

Two or three cameras indoors and, in a house, one or two outdoors is the plan (team assumption):
- one in the kitchen, where 11 of the 34 cases happen (S1 to S5, S10, C1, C2, C3, C5 and T1);
- one in the living room or the entrance, for presence, things and leaving home;
- in a house, one at the door or the gate (parcels, the car, break-ins) and, with a garden, one in the garden or at the back;
- in a flat, none outdoors: the front door opens onto the landing, which is a common part of the building and not the client's exclusive domain (section 2.6).

Each camera is one place. Two cameras in the same room are two places ("Kitchen 1", "Kitchen 2").

Three facts bear on the number of cameras:
- A full perception cycle takes about 0.65 s per frame on the team's laptop, about 1.5 frames per second. With three cameras seeing motion at once, the home device alternates between them, and the rate per camera falls in proportion (estimate, not measured).
- Because the models run only on motion, the electricity cost follows the hours of motion, not the number of cameras.
- The kit camera uses 2.4 GHz Wi-Fi only and streams H.265 at 2304 × 1296 and 20 frames per second (checked on 18 November).

### 2.2 Indoor and outdoor

| Aspect | Indoor | Outdoor, at the door |
|---|---|---|
| What it is for | Kitchen safety, care, things, presence | Break-ins, people at night, parcels, the car, things left outside |
| Cases | S1 to S10, C1 to C7, V1 to V6, T1, T2 | E1 to E9, part of T2 |
| Care needed | Never in bedrooms or bathrooms | Only the property and, where strictly necessary, the access to it; neither the street nor the neighbours; a sign on display (to verify); motion only as the trigger, no sound (section 2.6) |
| Hardware | The kit camera | An outdoor camera (other IoT), or the kit camera at a covered entrance if Altice confirms it |

### 2.3 Where to put them

- Kitchen: high in a corner, with the counter, the stove and the pet bowls in view; no window behind the scene; as close to the counter as possible (2 to 3 m, an assumption to measure) so a knife stays visible.
- Entrance: facing the door from inside, with the table or dish where the keys go.
- Living room: with the sofa, the table and the window that has the contact sensor.
- Outdoor: at the door, only the doormat and the door itself; in the garden, facing into the property, not towards the street or the neighbour; sheltered from rain; with night vision or a floodlight.

### 2.4 What each place unlocks

| Place | Cases | Devices that add value |
|---|---|---|
| Kitchen | S1, S2, S3, S4, S5, S10, C1, C2, C3, C5, V6, T1 | Smoke sensor and plug (kit); connected hob or oven, leak sensor, solenoid valve, smart speaker (other IoT) |
| Living room | S5, S6, S7, C3, C4, C5, V2, V3, V4, V5, V6 | Temperature sensor, plug and light (kit); window contact sensors, thermostat (other IoT) |
| Entrance, inside | S7, S8, C6, C7, V1, V2 | Door contact sensor and light (kit); smart lock (other IoT) |
| Outdoor, at the door | E1, E4, E5 | Light (kit); mailbox sensor, indoor speaker (other IoT) |
| Garden and gate | E2, E3, E4, E7, E8 | Floodlights, blinds, outdoor speaker, gate sensor, sprinkler (other IoT) |
| Garage entrance | E6 | Garage door motor (other IoT) |
| Back of the house | E1, E9, T2 | Contact sensor (kit); pet door with an electric latch (other IoT) |

### 2.5 Privacy rules

- The client chooses where the cameras go. The solution does not plan cameras in bedrooms or bathrooms; there, presence sensors without images (other IoT) cover the care cases.
- The models run only when there is motion or sound; the rest of the time the camera is idle.
- Real-time cropping option: everything except the tracked object is removed from the image before any analysis. This is an option proposed by the team; today the prototype already sends the server only small crops, never full frames.
- People are detected as "a person" or "a child", without identification. Recognising family members is opt-in, turned on person by person, with consent, and done on the home device.
- The client can set masks: areas of the image that are never analysed.
- ThingTracker records no video; observations stay 30 days on the home device.
- Retention of timeline events (proposal): 30 days by default, then deleted; events the family pins, for example those of an alarm, are kept longer, until the family deletes them or up to a maximum still to be set. For sound only the label is kept ("bark, 4:02"), never the audio. The log of actions taken in the home, planned in the architecture, is kept 90 days.
- Only the safety cases involving people (S7, E1, E2 and E4) send a photo of a person. The others send a crop of an object or no image at all (C6, for instance, never sends a photo).

### 2.6 Outdoor cameras in Portugal: privacy and the law

This is not legal advice: it summarises the primary sources the team checked on 18 November 2026 and flags what remains to be verified.

- What the camera may film. Lei n.º 58/2019, which implements the GDPR in Portugal, says in Article 19(2)(a) that cameras may not cover "vias públicas, propriedades limítrofes ou outros locais que não sejam do domínio exclusivo do responsável, exceto no que seja estritamente necessário para cobrir os acessos ao imóvel" (public roads, neighbouring properties or other places not under the controller's exclusive domain, except as strictly necessary to cover the access to the property; Diário da República, 1st series, no. 151, 8 August 2019).
- When the GDPR applies. A camera that films only the home's own fenced garden is, in principle, covered by the household exemption of GDPR Article 2(2)(c); it stops being covered if it extends, even partly, to public space or a neighbour's property (European Data Protection Board, Guidelines 3/2019, version 2.0, paras. 12 and 13; Court of Justice of the EU, Ryneš, C-212/13, 11 December 2014).
- Sound. Article 19(4) of the same law forbids capturing sound where video surveillance is allowed, except while the premises are closed or with the CNPD's prior authorisation. Because the solution uses sound as a trigger for analysis, outdoor cameras use motion only; whether the rule applies to a private home is still to verify. For the same reason, case T2 keeps only the sound's label, never the audio.
- Signage. Article 19(1) refers to the requirements of Article 31 of Lei n.º 34/2013, which, according to secondary sources, include a sign on display; the current wording of that article and how it applies to a private home are to verify. Where the GDPR applies, Guidelines 3/2019 (section 7.1) make the warning sign the first layer of information.
- Plates and faces. A licence plate is personal data (Guidelines 3/2019, para. 8). Reading plates or recognising faces is opt-in only, after a legal assessment and a data protection impact assessment (DPIA).
- The CNPD's own guidance for home cameras: to verify.

What the product would do (team proposals):
- When an outdoor camera is installed, the app asks the client to take the street and the neighbour's house out of the picture, and reminds them about the sign.
- ThingTracker's masks stop the rest from being analysed, but they do not change what the camera captures; correct framing comes first.
- No photo of a person leaves the home except in the safety cases E1, E2 and E4, and nobody is identified without consent.

## 3. Use cases and evaluation criteria

### 3.1 The criteria

Criteria and weights from Articles 16 and 18 of the participation rules (`sources/rules/normas-2026.pdf`). The criterion names are the rules' own Portuguese wording, with an English gloss.

| Criterion | Intermediate | Final | How ThingTracker answers it | Where the evidence is |
|---|---|---|---|---|
| Enquadramento e resposta ao Desafio (fit and response to the challenge) | 25 % | 20 % | The camera becomes a source of information; one sentence becomes a sensor, "beyond commands"; the cases combine the camera with the kit's sensors; the MCP is integrated (reads the door, acts on the plug and the light); the kitchen-safety cases answer what the mentors asked for | Prototype (`prototype/`); report (Figure 1 and the list of cases); video (`video/`, in progress); this document |
| Facilidade de adoção do Projeto por parte dos Desafiadores (ease of adoption by the challenger) | 25 % | 20 % | A fifth tab in the existing app; actions go through the MCP Altice already has; rules are saved as platform scenarios; 24 of the 34 cases use kit devices only, and the 9 outdoor ones add an outdoor camera | Architecture (`docs/14-architecture.md`, §3 and D5); integration spec (`docs/15-integration-spec.md`); the app replica in the prototype |
| Viabilidade de implementação e gestão futura (sustentabilidade) do Projeto (feasibility and sustainability) | 25 % | 20 % | Open-source models free for commercial use; vision only on motion, on the router or on Altice servers; the language model is called only to create a rule or answer a question; about €0.43 per home per month on the language model and €0.49 on vision (the report's estimate); 7 cases work today and 22 are small extensions | Report ("Ferramentas de IA"); architecture (§8); business case (`docs/16-business-case.md`) |
| Possibilidade de replicação em outros territórios e contextos (replication in other territories and contexts) | — (not assessed at this stage) | 20 % | A platform service for any operator; no data is specific to Portugal; the language model speaks the user's language; France is the second market analysed; the rules for outdoor cameras differ by country and would have to be reviewed in each | Business case (France section); architecture (requirement N5) |
| Apresentação da solução (presentation) | 25 % | 10 % | Live demo with the kit camera and the book; video with the knife-and-cat case (illustration); cases told in one sentence; five cases for the pitch and the video, one of them live (section 5) | Video; prototype; pitch |
| Documentação (Entregáveis) da solução (documentation) | — (not assessed at this stage) | 10 % | Two-page report; architecture, integration spec, business case and use cases, in Portuguese and English | `deliverables/`, `docs/pt/`, `docs/` |

### 3.2 Matrix

The team's self-assessment, for discussion. Scale per criterion:
- Fit: strong if the camera is a source of information combined with another sensor or an action, in a case the mentors asked for or outside Altice's current offer; medium if the camera only adds context to an alert that already exists.
- Adoption: strong if the kit is enough; medium if it needs more kit units or a device Altice already mentions in its offer; weak if it needs a new kind of device on the platform.
- Feasibility: strong if it works in the prototype; medium if it is a small extension; weak if it is future.
- Replication: strong if it depends on neither country nor home; medium if it depends on local rules or a third-party device.
- Presentation: strong if it can be shown live or in the video, or is one of the pitch cases (sections 4 and 5); medium if it is only described.
- Documentation: strong if it is also in the report or the architecture; medium if it is only in this document.

| Case | Fit | Adoption | Feasibility | Replication | Presentation | Documentation |
|---|---|---|---|---|---|---|
| S1 Knife and pet or child | strong | strong | medium | strong | strong | strong |
| S2 Child, knife, stove | strong | strong | medium | strong | strong | medium |
| S3 Stove with nobody | strong | medium | medium | medium | strong | strong |
| S4 Smoke: who is there | medium | strong | medium | strong | medium | medium |
| S5 Dangerous products | strong | strong | medium | strong | medium | medium |
| S6 Window and child | strong | medium | medium | strong | medium | medium |
| S7 Unknown person | strong | strong | medium | medium | medium | strong |
| S8 Door left open | medium | strong | medium | strong | medium | medium |
| S9 Water leak | medium | medium | weak | strong | medium | medium |
| S10 Smoke, flame, water seen | strong | strong | weak | strong | medium | medium |
| C1 Pet bowls | strong | strong | strong | strong | strong | strong |
| C2 Older person | strong | strong | strong | strong | strong | strong |
| C3 Medication | strong | strong | medium | strong | medium | medium |
| C4 Cold home | strong | strong | medium | strong | medium | medium |
| C5 Fall | strong | strong | weak | strong | medium | medium |
| C6 Child arrives | medium | strong | strong | strong | medium | strong |
| C7 Pet leaves by the door | strong | strong | medium | strong | medium | strong |
| V1 Leaving without the book | strong | strong | strong | strong | strong | strong |
| V2 "Where is it?" | strong | strong | strong | strong | strong | strong |
| V3 Energy | medium | strong | strong | strong | medium | medium |
| V4 Pet on the sofa | strong | strong | strong | strong | medium | medium |
| V5 Presence and posture | medium | medium | medium | strong | medium | medium |
| V6 Gestures | medium | strong | weak | strong | medium | medium |
| E1 Break-in | strong | medium | medium | medium | medium | medium |
| E2 Person at night | strong | medium | medium | medium | strong | medium |
| E3 Gate open | strong | medium | medium | medium | strong | medium |
| E4 Outdoor theft | strong | medium | medium | medium | strong | medium |
| E5 Parcels | strong | medium | medium | medium | strong | strong |
| E6 Car and plate | medium | weak | medium | medium | medium | medium |
| E7 Things left outside | strong | medium | medium | medium | medium | medium |
| E8 Garden sprinkler | medium | weak | medium | medium | medium | medium |
| E9 Pet door | medium | weak | weak | medium | medium | medium |
| T1 Too late | strong | strong | medium | strong | strong | medium |
| T2 What happened at 4 a.m. | strong | strong | medium | medium | strong | medium |

"Strong" for Documentation follows the report, which mentions S1, S3, C1, C2, C6, C7, V1, V2 and E5, and the architecture.

## 4. The 8 cases for the pitch

The eight strongest cases for the slides and the video: safety first, four indoors and four outdoors. Only C2 and V1 work in the prototype today; the others are shown as concepts, and the video should say so, for example with a "conceito" caption. Section 5 narrows the choice to 10 finalists and the 5 for the pitch; the scenes in this section stay as a reserve. The hooks are in Portuguese, as they will appear on the slides, with an English gloss.

| # | Hook | Gloss | Case | Where |
|---|---|---|---|---|
| 1 | Uma faca na bancada. O gato salta. | A knife on the counter. The cat jumps up. | S1 | Indoor |
| 2 | Alguém no jardim às três da manhã. | Someone in the garden at 3 a.m. | E2 | Outdoor |
| 3 | A placa ligada e ninguém na cozinha. | The hob on and nobody in the kitchen. | S3 | Indoor |
| 4 | Portão aberto, cão no jardim. | Gate open, dog in the garden. | E3 | Outdoor |
| 5 | A bicicleta já não está no jardim. | The bike is no longer in the garden. | E4 | Outdoor |
| 6 | Meio-dia, e a avó não veio à cozinha. | Midday, and grandma has not come into the kitchen. | C2 | Indoor |
| 7 | A encomenda chegou; a luz fica azul. | The parcel arrived; the light turns blue. | E5 | Outdoor |
| 8 | Ia sair sem o livro. | I was about to leave without the book. | V1 | Indoor |

### 4.1 A knife on the counter. The cat jumps up. (S1)

- Scene: the kitchen camera, from above, sees a knife on the counter (box "faca"). The cat jumps onto the counter (box "gato"); after 3 seconds both boxes turn red and so does the kitchen light. Variant: a child instead of the cat.
- Phone alert: "Há uma faca na bancada e o gato está perto." (There is a knife on the counter and the cat is close), with the crop and the buttons "Tocar a sirene" (sound the siren) and "Ignorar" (ignore).
- Devices: camera and light (kit).
- Status: small extension; in the video, an illustration.

### 4.2 Someone in the garden at 3 a.m. (E2)

- Scene: a black-and-white night image of the garden; a person (box "pessoa") by the side gate; a counter reaches 30 seconds; the floodlights come on and the blinds go down.
- Phone alert: "Está uma pessoa no jardim há 30 segundos e não está ninguém da família em casa." (A person has been in the garden for 30 seconds and nobody from the family is at home), with the crop and the buttons "Tocar a sirene", "Ladrar na coluna" (bark on the speaker) and "Ignorar".
- Devices: outdoor camera, floodlights, blinds and speaker (other IoT); security hub (kit).
- Status: small extension plus new hardware; concept.

### 4.3 The hob on and nobody in the kitchen. (S3)

- Scene: a pan on the hob; the last person leaves the kitchen and the "pessoa" box disappears; a counter climbs to 15 minutes.
- Phone alert: "A placa está ligada e não está ninguém na cozinha há 15 minutos." (The hob is on and nobody has been in the kitchen for 15 minutes), with the button "Desligar" (switch off).
- Devices: camera, plug and smoke sensor (kit); connected hob (other IoT).
- Status: small extension; concept.

### 4.4 Gate open, dog in the garden. (E3)

- Scene: the garden by day; the gate ajar (box "portão aberto") and the dog on the lawn (box "cão").
- Phone alert: "O portão ficou aberto e o cão está no jardim." (The gate was left open and the dog is in the garden), with a crop of the gate; inside, the light turns amber.
- Devices: outdoor camera and gate contact sensor (other IoT); light (kit).
- Status: small extension; concept.

### 4.5 The bike is no longer in the garden. (E4)

- Scene: the registered bike (box "bicicleta", with the registered-thing mark) leaning on the wall; a person approaches (box "pessoa"); shortly after, the bike's box disappears.
- Phone alert: "A bicicleta deixou de ser vista às 14h05 e não está ninguém da família em casa." (The bike stopped being seen at 14:05 and nobody from the family is at home), with the bike's last crop and that of the person seen next to it.
- Devices: outdoor camera (other IoT).
- Status: small extension; concept.

### 4.6 Midday, and grandma has not come into the kitchen. (C2)

- Scene: the empty kitchen; a timeline from 07:00 to 12:00 with no "pessoa" box; at 12:00 the clock turns red.
- Alert on the daughter's phone: "Ninguém passou na cozinha desde as 7h." (Nobody has been in the kitchen since 7:00.)
- Devices: camera (kit).
- Status: works in the prototype today.

### 4.7 The parcel arrived; the light turns blue. (E5)

- Scene: the door camera sees a cardboard box on the doormat (box "encomenda"); inside, the light turns blue and the speaker says "Chegou uma encomenda à porta." (A parcel has arrived at the door.)
- Phone alert: "Deixaram uma encomenda à porta às 11h20." (A parcel was left at the door at 11:20), with a crop of the parcel, and only of the parcel.
- Devices: outdoor camera and speaker (other IoT); light (kit).
- Status: small extension plus new hardware; concept (the blue light already exists in the prototype).

### 4.8 I was about to leave without the book. (V1)

- Scene: real footage from the kit camera; the book on the table (box "livro", recognised by its fingerprint); the door opens (contact sensor) and, 60 seconds later, the book is still at home.
- Phone alert: "Saíste sem o livro. Está na mesa." (You left without the book. It is on the table), with the photo and the last place.
- Devices: door contact sensor, camera and light (kit).
- Status: works in the prototype today; it is the video's real example.

## 5. The 10 finalists and the 5 for the pitch

The team wants at most 10 strong cases and, of those, 5 for the pitch and the video. The choice starts from the catalogue (section 1) and from the case the report submitted on 18 November uses: the child in danger in the kitchen, with the rule "avisa-me se a criança estiver em perigo" (tell me if the child is in danger), where the language model defines the danger (a detergent, a knife, the stove). In the catalogue this case combines S2 and S5.

### 5.1 How the scores work

Each criterion runs from 1 to 5:
- Impact: what the family gains or avoids.
- Novelty: how surprising it is; using the camera as a source of information counts in favour.
- Feasibility: with the kit and at most one extra device; 5 if it already works in the prototype.
- Demo: 5 if it works live with the kit; 4 if it films easily; 3 if it needs staging or waiting time.
- Criteria: fit with the criteria of Articles 16 and 18 of the rules (fit, adoption, feasibility, replication).
- Privacy: the risk, from 1 (low) to 5 (high). It enters the total inverted, as 6 minus the risk.

The maximum total is 30. It is the team's self-assessment, for discussion.

### 5.2 The 10 finalists

Chosen to cover the child at risk, pets, the older person, security, lost and found, and the cases that show the camera as a source of information (C3, V2, T1 and T2). The two home-timeline cases, T1 (24 points) and T2 (22), took the places of the parcel at the door (E5, 19) and the person in the garden at night (E2, 18). Outdoors and security are represented by T2.

| # | Case | Catalogue | Impact | Novelty | Feasibility | Demo | Criteria | Privacy (risk) | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Leaving without the book, the wallet or the keys | V1 | 3 | 4 | 5 | 5 | 5 | 1 | 27 |
| 2 | Knife on the counter with the cat nearby | S1 | 4 | 4 | 4 | 4 | 5 | 1 | 26 |
| 3 | Nobody in the kitchen by midday | C2 | 5 | 4 | 5 | 3 | 5 | 2 | 26 |
| 4 | The pill box has not moved | C3 | 4 | 5 | 4 | 4 | 4 | 1 | 26 |
| 5 | "Where is the wallet?" | V2 | 3 | 4 | 5 | 5 | 5 | 2 | 26 |
| 6 | The child in danger: detergent, knife, stove | S2 + S5 | 5 | 5 | 3 | 4 | 5 | 4 | 24 |
| 7 | The hob on and nobody in the kitchen | S3 | 5 | 3 | 4 | 3 | 5 | 2 | 24 |
| 8 | Too late: what was near the child | T1 | 4 | 5 | 4 | 4 | 5 | 4 | 24 |
| 9 | The cat has not been to its bowl | C1 | 3 | 3 | 5 | 3 | 4 | 1 | 23 |
| 10 | What happened at 4 a.m.? | T2 | 4 | 5 | 3 | 4 | 4 | 4 | 22 |

### 5.3 The reason for each score

#### V1. Leaving without the book, the wallet or the keys – 27

- Impact 3: saves an everyday slip, but prevents no danger.
- Novelty 4: the camera remembers the object and the door sensor closes the loop.
- Feasibility 5: works today, with the kit alone.
- Demo 5: live, with the yellow book, the door and the kit light.
- Criteria 5: shows the MCP reading a sensor and acting; it is the deliverables' real example.
- Privacy (risk) 1: follows an object; nobody is identified.

#### S1. Knife on the counter with the cat nearby – 26

- Impact 4: keeps a pet from cutting itself; it is the mentors' own example.
- Novelty 4: the camera relates two things, the knife and the cat, not just motion.
- Feasibility 4: kit only; the "knife" query and the "near" rule are missing.
- Demo 4: films well; live it would need a cat on site.
- Criteria 5: safety asked for by the mentors, the camera as a source of information, kit only.
- Privacy (risk) 1: no person in the alert's image.

#### C2. Nobody in the kitchen by midday – 26

- Impact 5: warns someone whose father or mother lives alone hours earlier; 517,146 people aged 65+ lived alone in 2021.
- Novelty 4: the home's routine becomes a signal, with no camera in the bedroom and nobody identified.
- Feasibility 5: works today, with the kit alone.
- Demo 3: an absence is shown with a timeline, not live.
- Criteria 5: fits Altice's "aging in place" line and replicates in any country.
- Privacy (risk) 2: detects "a person", with no photos; needs the person's own agreement.

#### C3. The pill box has not moved – 26

- Impact 4: a forgotten medicine can have serious consequences.
- Novelty 5: the camera turns an object that did not move into information; the clearest example of the idea.
- Feasibility 4: kit only; the "has not moved" rule is missing.
- Demo 4: staged on a table with the kit camera; registering the box already works.
- Criteria 4: care and aging in place; moving the box does not prove the dose was taken.
- Privacy (risk) 1: follows an object.

#### V2. "Where is the wallet?" – 26

- Impact 3: saves time every day.
- Novelty 4: the answer brings the place, the time and the photo: the camera as the home's memory.
- Feasibility 5: works today.
- Demo 5: live, straight after V1.
- Criteria 5: it is the core of ThingTracker and uses the language model beyond commands.
- Privacy (risk) 2: keeps 30 days of object sightings, which reveal routines.

#### S2 + S5. The child in danger: detergent, knife, stove – 24

- Impact 5: detergents, knives and the stove are real dangers for a small child.
- Novelty 5: a vague sentence becomes several concrete rules, written by the language model.
- Feasibility 3: kit only; "near" is a small extension, but "in the hand" or "in the mouth" needs a pose model (future); a pod is small at a distance.
- Demo 4: filmed staged or illustrated; filming a real child needs the parents' agreement.
- Criteria 5: it is the submitted report's case: safety, perception and action in one story.
- Privacy (risk) 4: stores a child's visual fingerprint and sends the child's photo in the alert; only with the parents' consent.

#### S3. The hob on and nobody in the kitchen – 24

- Impact 5: a forgotten stove can start a fire.
- Novelty 3: a forgotten-stove alert is not new; what is new is the camera knowing the kitchen is empty.
- Feasibility 4: the kit plug serves countertop appliances; a connected hob would be the only extra device.
- Demo 3: needs an appliance on and 15 minutes of waiting, sped up in the video.
- Criteria 5: shows a real MCP action: switching the plug off, the only write already tested.
- Privacy (risk) 2: detects "a person", with no photos.

#### T1. Too late: what was near the child – 24

- Impact 4: in an emergency, knowing what and when helps the doctor; fortunately it is rare.
- Novelty 5: the home's memory answers "what happened?" with images, not only with alerts.
- Feasibility 4: kit only; the timeline exists; tying the child and the object into one event with a crop is missing.
- Demo 4: filmed as the epilogue of the child-in-danger scene.
- Criteria 5: completes the report's case and uses the language model to answer a question.
- Privacy (risk) 4: keeps crops of a child for days; only with the parents' consent and a time limit.

#### C1. The cat has not been to its bowl – 23

- Impact 3: a pet that stops eating or drinking may be ill, and the alert comes the same day.
- Novelty 3: the automatic proposal surprises; the rest is simple.
- Feasibility 5: works today, including the proposal when the camera sees the cat.
- Demo 3: needs a cat and hours of waiting; mostly the proposal on the phone is shown.
- Criteria 4: asked for by the mentors; kit only.
- Privacy (risk) 1: no person.

#### T2. What happened at 4 a.m.? – 22

- Impact 4: after a burglary, the family and the neighbours know where to look.
- Novelty 5: the unusual (the dog barking at 4 a.m.) becomes information; it comes from a real story.
- Feasibility 3: the timeline exists; the bark and "unusual" need new models (future), and the window needs the outdoor camera.
- Demo 4: a night-time timeline films well, and the real story is quick to tell.
- Criteria 4: security is already in Altice's offer, but the timeline is new; sound raises a legal question.
- Privacy (risk) 4: sound, an outdoor camera and images of people; for sound only the label is kept.

### 5.4 The 5 for the pitch and the video

| Order | Case | Role in the story |
|---|---|---|
| 1 | The child in danger (S2 + S5), with the "too late" epilogue (T1) | Opens with fear and with the new idea, a vague sentence the language model turns into rules; the epilogue shows the home's memory |
| 2 | Knife on the counter and the cat (S1) | Pets; the mentors' own example |
| 3 | Nobody in the kitchen by midday (C2) | Care for someone who lives alone; works today |
| 4 | What happened at 4 a.m.? (T2) | Night and security, told through a true story |
| 5 | Live: leaving without the book, and "where is the book?" (V1 and V2) | The proof: the yellow book, the kit's door sensor and the light turning red |

Why, together, they tell the best story:
- Variety: a child, a pet, an older person, security at night and everyday things; alerts in the moment and the home's memory afterwards.
- Emotional arc: it starts with fear (the child), moves through tenderness (the cat, the grandmother) and the unease of the night (the dog that barked at 4 a.m.), and ends with proof that it works.
- One thread: in every scene the camera sees something and the home understands what it means and remembers it; four of the five scenes need only the kit (T2 uses the outdoor camera for the window), and two already work in the prototype (C2 and V1).
- The live demo closes: after four cases on video, the jury sees the real kit working.
- Left out are well-scored cases that would repeat a theme: C3 (pills) repeats the older person and S3 (hob) repeats the kitchen; T1 and V2 come in as epilogues. The parcel at the door (E5), which left the 10, can come back as a light moment if the team prefers to end the video part with good news.

One storyboard line per scene (the on-screen text stays in Portuguese):
1. Child in danger: first, the sentence "avisa-me se a criança estiver em perigo" and the three rules the model wrote (detergent, knife, stove); then, in the kitchen, the child (box "criança") reaches for a detergent pod (box "detergente") and the boxes turn red; on the phone: "A criança está junto a um detergente. Cozinha, 16h30." (The child is next to a detergent. Kitchen, 16:30), with the photo and the buttons "Ligar alarme" (turn the alarm on) and "Tudo bem" (all fine). Epilogue (T1): the mother asks "o que esteve perto dela esta tarde?" (what was near her this afternoon?) and sees the sequence, each step with its crop: "16h28, junto a um detergente; 16h29, junto a um copo" (16:28, next to a detergent; 16:29, next to a glass).
2. Knife and cat: the kitchen camera, from above, sees a knife on the counter (box "faca"); the cat jumps up (box "gato") and, 3 seconds later, the boxes and the light turn red; on the phone: "Há uma faca na bancada e o gato está perto." (There is a knife on the counter and the cat is close.)
3. Grandmother: the empty kitchen and a timeline from 07:00 to 12:00 with no "pessoa" box; at midday the clock turns red; on the daughter's phone: "Ninguém passou na cozinha desde as 7h." (Nobody has been in the kitchen since 7:00.)
4. What happened at 4 a.m.: at night the family asks "o que aconteceu esta noite?" (what happened tonight?); the timeline shows two unusual events, "4h02, sala: o cão ladrou, o que nunca faz a esta hora" (4:02, living room: the dog barked, which it never does at this time; the label only, no sound recorded) and "4h05, traseiras: uma pessoa junto à janela" (4:05, back of the house: a person at the window; box "pessoa", with the crop); the family pins both to keep them.
5. Live, with the kit camera: the yellow book on the table (box "livro", recognised with a similarity of 0.70); the door opens (the kit sensor) and the light turns red; on the phone: "Saíste sem o livro. Está na mesa." (You left without the book. It is on the table); finally, the question "onde está o livro?" (where is the book?) and the answer with the photo.

Before filming:
- The report's Figure 1 shows the alert "A criança pôs um detergente na boca." (The child put a detergent in its mouth.) Today the camera can only say "next to"; "in the hand" or "in the mouth" needs a pose model (future). For the video, "junto a um detergente" (next to a detergent) is proposed, or a "conceito" caption.
- The child appears as an illustration, or in a staged scene with the parents' agreement.
- In T2, recognising the bark and "unusual" is future: in the video the scene is a concept. The true story is told without names.
- The light turning red live needs the prototype's real actions switched on, with the team's approval, and the light connected to the platform (on 16 November it had not reported since 4 November; to confirm). Without that, the app shows the simulated MCP call.
- The prototype waits 60 seconds after the door opens; in a 3-minute demo that wait should be shorter, and it is a parameter of the rule.

## 6. Value proposition

- For the family: the camera already in the home starts warning about dangers nobody is watching (the knife within the cat's reach, the forgotten stove, the grandmother who has not come into the kitchen, someone in the garden at night) and answers "where is it?".
- For the family: every alert comes from a sentence or from a proposal accepted with one tap; the siren never sounds without a "yes", and no full image leaves the home for analysis.
- For Altice and MEO, differentiation: the cameras and sensors they already sell become a new service, inside the app and the MCP that already exist.
- For Altice and MEO, revenue: an add-on of €3.99 a month, of which about €1.74 per home remains, and about 19,000 MEO homes in the expected case (business-case assumptions).
- For Altice Labs: a platform service for any operator, and a reason to sell more sensors (outdoor cameras, floodlights, connected hob, leak sensor, smart lock).

## 7. Assumptions and open questions

1. Two or three cameras per home is a team assumption, to validate with customers.
2. Notification service: the MCP has no tool for alerts; which service the app uses is unknown.
3. Siren: the MCP write tool accepts power, brightness, colour temperature and colour; how to sound the camera's or the hub's siren is still to confirm. In any case, only after a "yes".
4. Other devices (connected hob or oven, leak sensor, smart lock, mailbox sensor, smart speaker, presence sensors): which ones the platform supports is unknown.
5. Kit camera outdoors (IP65): to confirm with Altice.
6. Maximum power of the kit plug: unknown.
7. Detection reliability for knives, parcels and pill boxes at a distance: not measured.
8. Legal review: outdoor camera framing and recognition of family members.
9. Signage for outdoor cameras: the current wording of Article 31 of Lei n.º 34/2013 and how it applies to a private home are to verify.
10. Sound outdoors: whether the ban in Article 19(4) of Lei n.º 58/2019 applies to a home is to verify; until then, outdoor cameras use motion only as the trigger.
11. Licence plates: opt-in, a DPIA and legal advice before any pilot.
12. Devices from the IoT ideas proposed within the team (floodlights, blinds, sprinkler, pet door, garage door motor, thermostat, outdoor speaker): which ones the platform supports, and whether the MCP write tool is enough to drive them, is unknown.
13. Timeline retention: 30 days by default and longer for pinned events is a proposal, and the maximum is still to be set.
14. Sharing timeline images with neighbours or the authorities: to verify.

Sources: Aveiro Tech City Hackathon 2026 participation rules, Articles 16 and 18; Lei n.º 58/2019, Article 19 (Diário da República, 1st series, no. 151, 8 August 2019); Regulation (EU) 2016/679 (GDPR), Article 2(2)(c); Court of Justice of the EU, Ryneš, C-212/13, 11 December 2014; European Data Protection Board, Guidelines 3/2019 on processing of personal data through video devices, version 2.0, 29 January 2020 (paras. 8, 12 and 13, section 7.1); the legal sources were read on 18 November 2026; INE, Census 2021, table Q1.04 (age bands summed by the team, see `docs/12-market-research.md`); Eurostat, `hlth_dhc140` (2025, read on 18 November 2026, see `docs/12-market-research.md`); Altice Labs' Connected Home product page (see `docs/02-challenge.md`); business case (`docs/16-business-case.md`); team measurements, 18 November 2026.
