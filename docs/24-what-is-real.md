# What is real in the three films

The one reference for what each film shows, how each moment was made, and what can honestly be called real. Checked on 19 Nov 2026 against how each film was edited (`video/src/film/`) and against an audit of the prototype's code.

Use these words for each moment:
- **Real:** the prototype did it, as recorded;
- **Real footage:** the kit camera in the lab, as filmed;
- **Real model output:** our model run on the footage after filming, not live;
- **Placed by us / computed in the edit:** made while editing;
- **Done by hand:** a person did it in the lab;
- **Envisioned:** added in the edit to show the full experience.

The column "Tonight" is filled in only when the prototype does it and an unedited proof run shows it (`video/out/proof/`, made on the night of 19-20 Nov: each film's own take replayed through the real pipeline, `video/tools/proof_run.py`). The phones' moments in each replay were read off the footage, because the phones weren't logged in the lab. The proof videos show people from the lab: use them only with their agreement, or blurred.

## Film 1: the book

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| App: *Things*, Add, the 8 photos, the name, Save | Real | Prototype app recorded as it ran (`record_app.mjs add-book`); the thing and its photos were stored | Photos now become a real fingerprint (0,69 on a desk-level kit frame), but from the ceiling only camera views recognise it (0,91-0,94); the app adds them on confirmation |
| A sentence becomes a scenario | Real | The local model and the rule code built the rule | |
| He leaves without the book, comes back, takes it | Real footage | One continuous take, kit camera | |
| "person" box | Real model output | OWLv2 run on the take afterwards (`detect_take.py`) | |
| "livro" box on the desk, with its score | Real model output (from v12) | OWLv2 ("a photo of yellow book") on the full-resolution region around the desk, then DINOv2 against a fingerprint registered from the same camera in another take: found in 68 of 68 frames, median 0,93 (`video/tools/book_region.py`). The phone-photo fingerprint alone scores 0,23 from the ceiling and would not recognise it | |
| Door open or closed | Computed in the edit | Read from the picture | |
| Alarm sound, notification, "Turn off the alarm" | Envisioned | Added in the edit; the alert screen was triggered for the recording (`record_app.mjs`) | **Proof run:** on the same take replayed through the real pipeline, "left behind" fires from the rule (door, phone leaving, the camera's active check: the book seen at 0,94 over 3 frames). When he leaves with the book: "unsure", no alert, and the judge agrees. The alarm stays simulated |

## Film 2: the face

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| App: add person, the face video, "Filipe added", Family, the suggested scenario, "Scenario saved" | Real | Prototype app recorded as it ran; the video was uploaded and the rule created | |
| Finding the face in the video | Not real | The server cut 8 fixed squares; no face model ran | **Real now:** _YuNet_ finds the face and _SFace_ makes the templates, on the home side |
| Filipe enters, the stranger enters | Real footage | Kit camera | |
| The face comparison | Envisioned | Labelled "comparação ilustrativa" in the film | **Proof run:** Filipe recognised (0,54 and 0,63, threshold 0,40), the stranger unknown (0,17 and 0,14); nothing fires while Filipe is home |
| Alarm and police suggestion | Envisioned | Added in the edit; the alert was triggered for the recording | **Proof run:** fired by the rule in 2 of 4 replays. In the other 2, too few of the stranger's faces were clear enough to judge, so the system asked ("someone is home, face not seen") instead of alarming. The alarm is simulated; the app never dials |

## Film 3: the people

| Moment | Status | How it was made | Tonight |
|---|---|---|---|
| Two sentences become scenarios | Real | Real rules (keyword templates) | |
| Three come in, sit, leave; lights and AC on | Real footage | Four takes joined, the clock rewritten with the camera's own digits, the sitting part at 4× | |
| "person" boxes | Real model output | OWLv2 run afterwards, linked into tracks by our tool | |
| People counter | Computed in the edit | From those boxes | **Real now:** the presence engine counts and decides "nobody home" from the phones (simulated, read off the take), the door and the cameras |
| Door open or closed | Computed in the edit | Read from the picture | |
| Lights and AC going off | Done by hand | The team at the switch and the remote | Not possible: the lab's lights and AC aren't connected (see the Q&A, E3) |
| The plug's box, the camera's drop to dark | Made in the edit | The plug was chosen to stand for the kit's; the drop to dark was rebuilt from the camera's own behaviour | |
| Alert with two cards, the Yes taps | Real screens, alert triggered by hand | The plug's off was a dry run; the AC is simulated | **Proof run:** one alert fired by the rule, with both device cards and the door banner; Yes turns off the Plug (dry run) and the AC (simulated) |

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
