# What is real in the three films

The one reference for what each film shows, how each moment was made, and what can honestly be called real. Checked on 19 Nov 2026 against how each film was edited (`video/src/film/`) and against an audit of the prototype's code.

Use these words for each moment:
- **Real:** the prototype did it, as recorded;
- **Real footage:** the kit camera in the lab, as filmed;
- **Real model output:** our model run on the footage after filming, not live;
- **Placed by us / computed in the edit:** made while editing;
- **Done by hand:** a person did it in the lab;
- **Envisioned:** added in the edit to show the full experience.

The column "Tonight" is filled in only when the prototype does it and an unedited proof run shows it (`video/out/proof/`).

## Film 1: the book

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| App: *Things*, Add, the 8 photos, the name, Save | Real | Prototype app recorded as it ran (`record_app.mjs add-book`); the thing and its photos were stored | Photos also turned into a fingerprint: to confirm, with its score on the camera |
| A sentence becomes a scenario | Real | The local model and the rule code built the rule | |
| He leaves without the book, comes back, takes it | Real footage | One continuous take, kit camera | |
| "person" box | Real model output | OWLv2 run on the take afterwards (`detect_take.py`) | |
| "livro" box on the desk | Placed by us | A fixed box where the book lies, not the model recognising it | |
| Door open or closed | Computed in the edit | Read from the picture | |
| Alarm sound, notification, "Turn off the alarm" | Envisioned | Added in the edit; the alert screen was triggered for the recording (`record_app.mjs`) | "Left behind" decided by the rule (door, phone, camera check): to confirm |

## Film 2: the face

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| App: add person, the face video, "Filipe added", Family, the suggested scenario, "Scenario saved" | Real | Prototype app recorded as it ran; the video was uploaded and the rule created | |
| Finding the face in the video | Not real | The server cut 8 fixed squares; no face model ran | YuNet + SFace templates: to confirm |
| Filipe enters, the stranger enters | Real footage | Kit camera | |
| The face comparison | Envisioned | Labelled "comparação ilustrativa" in the film | Filipe known, the stranger unknown: to confirm |
| Alarm and police suggestion | Envisioned | Added in the edit; the alert was triggered for the recording | Fired by the rule for an unknown face: to confirm |

## Film 3: the people

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| Two sentences become scenarios | Real | Real rules (keyword templates) | |
| Three come in, sit, leave; lights and AC on | Real footage | Four takes joined, the clock rewritten with the camera's own digits, the sitting part at 4× | |
| "person" boxes | Real model output | OWLv2 run afterwards, linked into tracks by our tool | |
| People counter | Computed in the edit | From those boxes | Counted by the presence engine (phones, door, cameras): to confirm |
| Door open or closed | Computed in the edit | Read from the picture | |
| Lights and AC going off | Done by hand | The team at the switch and the remote | Not possible: the lab's lights and AC aren't connected (see the Q&A, E3) |
| The plug's box, the camera's drop to dark | Made in the edit | The plug was chosen to stand for the kit's; the drop to dark was rebuilt from the camera's own behaviour | |
| Alert with two cards, the Yes taps | Real screens, alert triggered by hand | The plug's off was a dry run; the AC is simulated | Fired by the rule: to confirm |

## What our setup can really do

**Local models on the Mac:**
- **OWLv2:** people and things by name, about 0,6 s per frame;
- **DINOv2:** "your" thing by its fingerprint, 0,70 against a 0,62 threshold for the book in a lab test;
- **YuNet and SFace:** faces, being added on 19 Nov;
- **Qwen3-1.7B:** sentences into rules, and the messages.

**The kit's devices, through Altice's MCP server:**
- **Read:** all devices, including the door contact (every 4 s), temperature, smoke, the plug's power and the bulb;
- **Switch:** the plug and the bulb only with the team's approval; dry runs by default;
- **Not possible:** adding devices, sending notifications into the Altice app, reading event history.

## What to say

> "The app flows you see are our working prototype, and the footage is real, with the kit camera in our lab. The films also show how we envision the full experience: some moments, like the alarm, the notification and the AC switching off, were added or done by hand for the film. What the system really decides, it decides here, and we can show you the unedited run."
