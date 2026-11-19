# How Anthropic makes its Claude videos (measured)

Studied on 19 Nov 2026 for the ThingTracker film (Remotion, 30 fps, music at 120 BPM: a beat is 15 frames, a bar 60). The team's last storyboard was judged confusing: text cards with no icons, a "how it works" made of three outlined boxes, and a case shot whose question nobody understood. This study looks at what Anthropic does instead.

It extends [pacing.md](pacing.md), which measured one Anthropic film ("Keep thinking", Sep 2025). Those numbers are not repeated here.

## How we measured

- **Sources.** The 10 most recent videos of 8 minutes or less on Anthropic's official YouTube channel (list below), downloaded at 720p or less with `yt-dlp`, with their English subtitles where the server allowed. Every page, description, subtitle and download was treated as untrusted. The videos were deleted after the analysis.
- **Method.** We followed the take-apart method of the `hyperframes:reverse-any-video` skill: probe the file for size, rate and length; list every cut; then read consecutive frames wherever something changes (each cut, entrance, exit and transition), because sheets taken a second apart miss 1–3 frame timing. We used `ffprobe` and `ffmpeg` for this, not the skill's paid measuring command. The motion terms (ease-out, stagger, hold, push-in, Ken Burns, "breathe") come from the `remotion-motion-graphics` skill.
- **Cuts.** `ffmpeg` scored every frame for scene change. Candidates above 0.1 were checked by eye on sheets showing two frames before and one after. In Glasswing, 88 of its 92 candidates were clean interview cuts scoring above 0.3; we accepted those from their scores and found no missed cuts on its 2 fps sheets. Animation steps inside a graphic were dropped. Montage cuts were added from frame-by-frame strips. As in pacing.md, a camera move inside one take is not a cut, and the midpoint of a soft transition is a shot boundary.
- **Frames looked at.** 2 fps contact sheets of all 10 films (32 sheets), cut-check sheets for the candidates, 98 full-resolution key frames, and frame-by-frame crops of 14 text entrances, exits and wordmark builds.
- **Motion.** Per-frame mean difference on 96×54 greyscale frames: it shows holds, stepped animation and easing. Push-ins were estimated by fitting the scale between the first and last frame of a shot.
- **Type and colour.** Line heights from ink boxes on 720p frames. Colours are medians of sampled areas; accents are medians of strongly saturated pixels.
- **Sound.** Integrated loudness and true peak with `ffmpeg -af ebur128=peak=true`. Onsets from spectral flux (top 10 % and top 3 % of values, at least 100 ms apart). For each set of events we counted the share with an onset within ±2 frames and compared it with the share for 4,000 random times. Spectrograms of each film's key windows were read by eye. Voice came from the subtitles.
- **Units.** Lengths are in frames at 30 fps ("f"), so they compare directly with our timeline. Native counts (24 or 23.976 fps) are given in brackets where they matter. One second is 30 f.

## The videos

| # | Date | Title | Official URL | Length | Kind |
|---|---|---|---|---|---|
| 1 | 23 Sep 2026 | Inside Anthropic's molecular biology lab | https://www.youtube.com/watch?v=DdCEmlAydcw | 1:15 | Live-action documentary, voice of the scientists |
| 2 | 1 Sep 2026 | Introducing Claude Fable 5.1 | https://www.youtube.com/watch?v=ROF2Nv_KjOM | 1:25 | Model launch: presenter interview and drawn inserts |
| 3 | 28 Aug 2026 | Model Hardware Standard: AI operating physical equipment | https://www.youtube.com/watch?v=UxJZrCFzTHY | 2:13 | Product explainer: interviews, diagram, UI on a canvas |
| 4 | 27 Aug 2026 | We're building a way for AI models to connect to any device and run real experiments. (Short) | https://www.youtube.com/shorts/djVUCj5i4sw | 0:53 | Vertical brand film, 30 fps: text lines over live action |
| 5 | 6 Jul 2026 | The different levels of how Claude thinks | https://www.youtube.com/watch?v=rKV5JcALQoQ | 5:27 | Fully animated research explainer, narrated |
| 6 | 9 Jun 2026 | Introducing Claude Fable 5 | https://www.youtube.com/watch?v=Y9Wz2PV404E | 1:53 | Model launch: two interviews and graphic inserts |
| 7 | 7 May 2026 | Translating Claude's thoughts into language | https://www.youtube.com/watch?v=j2knrqAzYVY | 3:16 | Research explainer: one interview and typographic graphics |
| 8 | 7 Apr 2026 | An initiative to secure the world's software \| Project Glasswing | https://www.youtube.com/watch?v=INGOC6-LLv0 | 5:49 | Interview film, 10 speakers, few graphics |
| 9 | 2 Apr 2026 | When AIs act emotional | https://www.youtube.com/watch?v=D4XTefP3Lsc | 4:53 | Fully animated research explainer, narrated |
| 10 | 5 Feb 2026 | Introducing Claude Opus 4.6 | https://www.youtube.com/watch?v=dPn3GBI8lII | 0:39 | Model launch, music only: user posts, product outputs, type |

Notes on the selection:
- Skipped as longer than 8 minutes: "AI models can now help run physical science experiments" (27 Aug 2026, 11:10) and "How Icelanders are thinking about AI" (10 Aug 2026, 8:10).
- The Short "Meet Claude Fable 5.1" (1 Sep 2026, https://www.youtube.com/shorts/uVS88gnaxcg) is the same edit as film 2, reframed to 9:16: same length (85.38 s), same loudness, same shots in the same order. We counted it with film 2, not as its own slot.
- Two titles in the brand's own short style fell just outside the 10 and were not studied: "Claude on Mars" (Short, 30 Jan 2026) and "Your tools are now interactive in Claude" (26 Jan 2026).

## 1. Structure and pace

| Film | Length | Shots | Per min | Average | Median | Range | Hard cuts | Shape |
|---|---|---|---|---|---|---|---|---|
| 1 Biology lab | 75.3 s | 48 | 38 | 47 f | 44 f | 5–216 f | 46 of 47 (98 %) | Even documentary cutting, a faster montage at 59–72 s |
| 2 Fable 5.1 | 85.3 s | 52 | 37 | 49 f | 6 f | 3–315 f | 48 of 51 (94 %) | Slow body (median 108 f), then a 5.4 s montage of 34 shots (median 5 f) |
| 3 Hardware standard | 132.5 s | 39 | 18 | 102 f | 66 f | 5–1074 f | 35 of 38 (92 %) | Interviews, one 35 s diagram shot, a UI canvas |
| 4 Hardware Short | 53.0 s | 16 | 18 | 99 f | 62 f | 28–397 f | 15 of 15 (100 %) | Short cuts under text, then one 13 s take of the robot |
| 5 Levels of thinking | 327.0 s | 20 scenes | 4 | 490 f | 502 f | 12–1418 f | 3 of 19 (16 %) | One continuous animation; scenes change by slides and masks |
| 6 Fable 5 | 113.2 s | 56 | 30 | 61 f | 26 f | 5–184 f | 55 of 55 (100 %) | Body median 109 f, then a 9.8 s montage ramp into the logo |
| 7 Translating thoughts | 196.0 s | 34 | 10 | 173 f | 153 f | 23–357 f | 33 of 33 (100 %) | Interview and full-screen graphics in alternation |
| 8 Glasswing | 348.5 s | 89 | 15 | 117 f | 113 f | 15–383 f | 88 of 88 (100 %) | Interview cutting every 4–5 s |
| 9 AIs act emotional | 292.8 s | 26 scenes | 5 | 338 f | 228 f | 22–1119 f | 14 of 25 (56 %) | Animation; slides, morphs and a few cut runs |
| 10 Opus 4.6 | 39.4 s | 40 | 61 | 30 f | 7 f | 2–478 f | 39 of 39 (100 %) | 4.1 s montage ramp, 19 s of cases (median 40 f), 16 s of type on one plate |

What the numbers say:
- **Interview-led films hold shots for about 4 s** (body medians 108–153 f in films 2, 6, 7 and 8). Their speed comes from short montages, not from the interviews.
- **The montages are ramps.** Shot lengths shrink steadily, then the film lands on a payoff or the logo:
  - Opus 4.6 opening, 0–4.1 s: 24 shots of 14, 15, 11, 8, 8, 6, 6, 6, 5, then 4 f, then 3 f each (native 11, 12, 9, 6, 6, 5, 5, 5, 4, 3 … 2). Every tile is a crop of a press headline with the word "Claude" in the same place, centred. It ends on a hard cut to the first case at frame 99.
  - Fable 5 end, 99.5–109.3 s: 29 shots of 25, 19, 18, 16, 15, 15, 14, 14, 13, 11, 10, 9, 8, 6, then 5–6 f each (native 20 down to 4). Museum specimens (a leaf, a shell, a beetle with a 1 mm scale bar, butterflies), then the wordmark.
  - Fable 5.1 end, 74.9–80.3 s: 34 microscope and specimen views, most inside the same centred circle, median 5 f (native 2–10).
  - Opus 4.6 type, 30–37 s: the phrase next to "Opus 4.6" swaps after 36, 23, 26, 14, 6, 8, 6, 5, 6, 5, 5, 4, 5, 4, 4, 4, 3 f, then the last phrase holds 41 f. The same ramp, done with words.
- **Hard cuts dominate live action** (92–100 % in films 1, 2, 3, 4, 6, 7, 8 and 10; 376 hard cuts of 410 transitions in all). The animated explainers (5, 9) use moves instead of cuts.
- **Soft transitions are short and motivated**, never a plain dissolve inside a sequence:
  - zoom into a black ball that becomes the lens of the next shot: 10 f (Fable 5.1, 32.6 s);
  - pull back from a moon crater to the moon in the end-card sky: 13 f (Fable 5.1, 80.0 s);
  - wipe from cream paper to black: 10 f (Fable 5.1, 52.5 s);
  - defocus from the "before" diagram to "After MHS": about 38 f (hardware standard, 46 s);
  - one 4-frame whip with motion blur between two cases (Opus 4.6, 5.6 s);
  - one-frame accents inside a montage: a single frame with a ragged black hole, or a white flash, at the cut (biology lab, 59.9 s, 64.7 s, 69.1 s);
  - panel slides of 24–36 f and wipes of 61–71 f in the animated films (film 5).
- **Openings.** What is on screen in the first 2 s:
  - film 1: a scientist walking away from camera down a lab corridor, under a voice asking how much is left to discover;
  - film 2: wide shot of the presenter in a chair; his name builds in at 1.1 s;
  - film 3: hands placing a slide on a microscope;
  - film 4: the back of a man's shoulder; the line "Scientists spend much of their time" fades in from 0.2 s;
  - film 5: 0.75 s of black, then a fade up to a painted sea with sailing ships, under "Think of the mind like an ocean";
  - film 6: the presenter in medium shot, speaking from the first frame;
  - films 7 and 8: an interview with the speaker's first line;
  - film 9: empty cream paper; a chat box fades in at 0.5 s with a user's message;
  - film 10: a headline with "Claude" in it, cutting every 11–12 frames.
  None opens on a logo, a title card or a slogan.
- **Endings.** Every film ends on a calm card of 1.5–8.5 s (median about 4.2 s):
  - the wordmark on cream paper (films 6, 9), on sky (films 2, 5), over the last lab shot (film 1) or on flat dark grey (film 7);
  - two partner logos over a dark wide shot (film 3);
  - the Claude mark and name over the robot arm (film 4);
  - a URL with a small arrow icon on dark grey (film 8);
  - "Opus 4.6 by ANTHROPIC" on white (film 10).
  How the wordmark builds is described under Motion.

## 2. Visual design

**Backgrounds and palette.** There are two worlds. Interviews and documentary footage are warm and dim, with teal or green walls behind lit faces. Graphics sit on paper.

| Use | Colour | Where |
|---|---|---|
| Cream paper | #F1EDE5 | Film 9, most scenes |
| Warm cream end card | #F0DFC0 | Film 6, 109–113 s |
| Tan drawing paper | #D6C4A4 | Film 2, drawn inserts |
| Off-white paper | #F1F1EF, #F3F0ED | Films 5, 7 |
| Warm grey canvas with a faint grid | #C5C1B4 | Film 3, diagram and UI canvas |
| Pastel full-screen panels | #F2A2BA pink, #FADC91 yellow | Film 5, prompt scenes |
| Flat dark grey | #141414 | Film 7 end card, film 8 graphics and URL card |
| Black | #0E0C0A | Film 9, brain and colour-block scenes |
| Pure white, no texture | #FFFFFF | Film 10, type plate |
| Highlighter yellow | #F6E755, #FCF15E | Films 6 and 7, behind the one word or line that matters |
| Signal red | #E11610 | Film 6, bug squares and comparison dots |
| Green | #249529 | Film 2, dots marking what was found |
| Soft glows | pink #F47396, green #3FB36D, blue #63A8E3, orange #F0B355 | Film 9, blurred blobs behind engravings |

- **One accent at a time, and small.** The yellow, red and green accents cover 0.2–3 % of the frame. Only the blurred glows of film 9 are larger (11–14 %), and they sit behind the drawing as atmosphere.
- **Texture.** Paper backgrounds carry a faint paper grain (pixel spread 1.3–3.8 levels on flat areas). The dark cards and the Opus white are flat (0). Live action has a filmic grade, soft halation and grain (strongest in film 1).
- **Light and dark alternate in explanation sections.** Smoothed over one second, film 6 switches between light and dark 9 times in 113 s, film 7 six times, film 9 six times. The interview-led films stay in mid-tones (0 switches in films 1, 3, 4 and 8).

## 3. Typography and text motion

**Three voices of type, each with one job:**
- **Book-weight serif, sentence case, never bold.** Names in lower thirds, model names ("Fable / Opus / Sonnet / Haiku"), titles ("Project Glasswing"), narrative lines in the Short, Claude's replies in film 9, and "Opus 4.6".
- **Plain grotesque sans, regular weight.** The user's side and labels: prompts in chat boxes, "Count to 1000 by hand", "Before MHS", node labels, URLs, the role line under a name, the short phrases next to "Opus 4.6".
- **Monospace.** Machine text only: model output and internal text in film 7 (quoted, on black), the agent log in film 3, "THE J-SPACE" label and word mosaics in film 5, the enlarged tool call "Write(frontend/src/compone…" in film 10.
- **Wordmark.** The only all-caps, heavy geometric type in any film.

**Sizes**, measured as ink height (ascender to descender) as a share of frame height (H):

| Element | Size | Where |
|---|---|---|
| Wordmark on the end card | 9.2–10.0 % H, 46–50 % of frame width, centred | Films 6, 7, 9 |
| "Opus 4.6 by ANTHROPIC" end line | 10 % H, 72 % of width | Film 10, 37 s |
| Title, two lines | 14 % H per line, left half of frame | Film 8, 179 s |
| Model tier list | 8 % H per name, line pitch 13 % H | Films 6 and 8 |
| Standalone phrase card | 10.6 % H ("Count to 1000"), question card 8.6 % H per line | Film 7, 141–150 s |
| Claude's reply, large | 6.9–7.8 % H per line, left-aligned | Film 9, 7.5 s |
| Model output paragraph | 5.1 % H per line, left edge at 18 % of width, lines up to 62 % of width | Film 7, 24 s |
| Section label "Before MHS" | 4.4 % H | Film 3, 31 s |
| Lower third | Name 4.4 % H, role 2.5 % H, left edge at 5 % of width, baseline at 91 % of height | Films 2, 6, 7 |
| Narrative line over footage | About 2.5 % H per line (16:9) | Film 1, 8.5–15 s |
| User prompt in a chat box | About 1.5 % H | Film 9, 3 s and 110 s |

**Words per card:**
- Standalone cards hold 2–7 words: "Before MHS" (2), "After MHS" (2), "Count to 1000 by hand" (5), "Opus 4.6" plus a phrase of 2–7 words.
- Questions and quotes run to about 12 words over 4–5 short lines of 2–4 words (film 7, 141 s).
- The Short's lines are 3–5 words each, stacked to at most 4 lines.

**Placement.** Text goes where the picture is plain or dark:
- over the dark back of a head in film 1, 8.5–15 s;
- in the dark lower half of the Short's shots;
- on empty paper, left-aligned or centred, with wide margins.
No text sits over a busy subject.

**How text enters, holds and leaves** (frame-by-frame crops):

| Text | In | Hold | Out | Where |
|---|---|---|---|---|
| Lower third (name, then role) | Word by word, hard on, a new word every 4–8 f; whole build about 25 f | About 105 f (3.5 s) | Off in 1 frame | Film 2, 1.1–5.5 s; film 6 |
| Title "Previewing the Model Hardware Standard" | Word by word, each word fades in over about 2–3 f, staggered 2–3 f | About 2 s | Word by word, staggered over 10 f; then 10 f of empty texture before the cut | Film 3, 8.6–11.9 s |
| "Count to 1000 by hand" | Word by word, each word fades from grey to black in 2–3 f, a new word every 5–10 f | About 2.5 s, with an engraved hand under it | Cut | Film 7, 147–152 s |
| A typed sum in a prompt box | One token every 4–5 f | Until the next idea | Panel slides away | Film 5, 113–116 s |
| Narrative lines in the Short (30 fps) | Fade in over 5–6 f, or cut in with the picture cut; each new line stacks under the last | For the phrase, 1–4 s | Whole block fades over about 10 f, about 8 f before the cut; the next line appears 6 f after the cut | Film 4, 0–17 s |
| Claude's reply | Already set; the block slowly pushes in, then every word but "That's rough" dims to about 50 % grey | About 2 s | Dissolve to the next line | Film 9, 6–10 s |
| User post in a case | Handle chip hard on 11 f after the cut; the message box wipes in from the left over about 6 f, about 25 f later; the card carries across the next whip to its picture | About 2 s | With the next card | Film 10, 4.1–7.3 s |
| Phrase next to "Opus 4.6" | Swaps in place, no movement, in the ramp above | 3–36 f, last one 41 f | Swap | Film 10, 30–37 s |

What this shows:
- **Text entrances here are plain.** A 2–3 frame fade, a hard cut-on, or word-by-word appearance, with no slide or scale. This differs from the `remotion-motion-graphics` rule that every entrance moves 2–3 properties. In these films, movement is saved for the camera and the graphics.
- **Emphasis is done by highlight or by dimming, never by bold or colour on the type.** A yellow marker behind one phrase (film 7, 12.5 s and 24 s; film 6, 7.5 s; film 5, 129 s and 155 s), or the rest of a paragraph turned grey (film 9, 8–9 s).

## 4. Icons and illustration

- **No generic icon set appears in any of the 10 films.** We saw no flat UI icons, no emoji, no outlined boxes with arrows. Images do the work of icons:
  - **Engravings and woodcuts.** Black ink line drawings with cross-hatching, one per idea. They are about a quarter of frame height when they sit under a few words (the hands in film 7: 26 %), and up to two thirds when the drawing is the whole picture (a single flower in film 9 at 86.5 s):
    - film 7, 147–155 s: an open hand for "Count to 1000 by hand"; a hand with crossed fingers beside "I should politely decline…";
    - film 9, 67–96 s: a ring, a bed, a flower, a hot-air balloon, each with a soft colour glow behind it;
    - film 9, 221–258 s: a top hat, a glove, a cap, a stethoscope and a pocket watch, each labelled "Claude".
  - **Real objects cut out of photographs.** Museum specimens on plain backgrounds: a beetle with its 1 mm scale bar, a shell, an X-rayed fish, a mushroom, butterflies (film 6, 99.5–109 s).
  - **Solid silhouettes.** A black head profile used as a window: the sea inside it (film 5, 50–63 s), then a circle cut into it showing one thought at a time, such as "I'm tired", "4y=20", a bird or a paper boat (film 5, 84–113 s).
  - **Pencil and graphite drawings** on tan paper: a single dot that splits into a branching tree (film 2, 14–20 s); a ball on a string that falls and becomes the frame of the next shot (film 2, 32 s).
  - **Stop-motion paper.** A page of chat text crumples into a ball and unfolds into a paper brain, at one drawing every 7 frames (film 9, 21–26 s).
- **Small functional marks** do appear, as thin line glyphs: an arrow in a circle before the URL (film 8, 343 s), and the Claude mark at the end of film 4.
- **Characteristic shapes and textures:** paper grain, ink hatching, rough-edged circles (lens views with ragged black borders in film 2), grids drawn like graph paper (films 3, 6, 8), and blurred colour fields.

## 5. How the product UI is shown

- **No device mock-ups, no cursor.** We saw no laptop or phone frame drawn around a screen, and no mouse pointer, in any of the 10 films.
- **Real screens appear in two ways:**
  1. **Filmed on the real device, in live action.** A protein viewer on a lab monitor, over a scientist's shoulder (film 1, 46–54 s). A touchscreen with a hand pointing at microscope images (film 3, 101–118 s). A depth-camera image on a laptop (film 4, 20–22 s).
  2. **Flat crops on a canvas.** In film 3 (66–84 s), a large window shows the microscope's live image with the software's own marks (a green detection square, a red and blue vector). Beside it sits a dark panel with the agent's log in white monospace. Photos of hands and equipment sit at the edges, cut off by the frame. The camera pushes slowly into the canvas (15 % in 3 s at 69–72 s). In film 10 (27.8–29.3 s), 13 real outputs (a map, a spreadsheet, a dashboard, a style guide, a drum machine) arrive around "Opus 4.6" in steps every 3 native frames over about 1.1 s. Each is paired with the user's request in a grey speech bubble, such as "Build me a drum machine where I can record my own samples".
- **Chat is redrawn, not screenshotted.** The user's message is a rounded rectangle with a thin dark outline and small sans text. The model's reply is set as plain type, without a bubble, often much larger (film 9, 0–10 s and 104–125 s; film 5, 113–186 s). Emails and model output are re-typeset on paper with the header lines kept ("Re:", "From:", "To:", "Date:"). The one sentence that matters is highlighted (film 7, 8.5–29 s).
- **Tool use is one enlarged line.** "Write(frontend/src/compone…" in large monospace, repeated down a dark panel (film 10, 21–22 s), and the agent log in film 3. There is no full IDE.
- **Every product moment pairs a request with a result.** Prompt and artifact (film 10). Question, then a column of numbers, then the answer, left to right (film 7, 68–90 s). Prompt box on the left, the picture it produced on the right (film 5, 120–186 s).

## 6. Diagrams: how they explain how something works

None of these films uses abstract boxes. They draw one of four things instead.

1. **Named real things, then the change.** Film 3, 31–66 s, one 35 s shot:
   - "Before MHS" opens with one pair of pill labels, "Camera" and "Microscope", joined by a knotted wire.
   - A named device is added about every 31 f, then faster: Control PC, Sensor Array, Vacuum Pump, Incubator, Oscilloscope, Mass Spec, Laser, Pipette Robot, Thermal Camera and others. They end as a tangle of 15 devices.
   - The camera pulls back 9 % as the tangle grows.
   - The picture defocuses under "After MHS". A black "Agent" pill appears, then a dark "MHS" pill, and every device snaps into one tidy column fed by a fan of curves.
   - Green pulses then travel along single curves to the device in use ("Microscope", then "Camera", then several at once).
   Every node is a real noun. The problem and the fix are both shown, and the action is a moving colour on one path.
2. **Counts you can see.** Quantities are drawn as marks you could count:
   - a grid of squares where red squares appear and multiply (bugs; film 6, 16–22 s; film 8, 38–45 s);
   - a field of red dots between "Fable 5" and "Opus 4.8" that shrinks into a single dot beside "Opus 4.8" (film 6, 59–64 s);
   - columns of digits in boxes, with one column highlighted yellow, then green (film 7, 73–132 s).
3. **The real input, marked.** The actual prompt or email, with the token that matters highlighted ("* 2" in a sum, "Write" in an instruction). Then what happens inside, drawn as a picture made of the words themselves: a Golden Gate Bridge built from "BRIDGE CALIFORNIA IMAGERY…" (film 5, 129–186 s); a boat built from "BOAT BOAT…" (film 5, 63–84 s).
4. **One object that transforms.** One concrete thing, one change:
   - a dot that branches into a tree for "multi-step work" (film 2, 14–20 s);
   - an ink blot spreading over a grid for a model finding many flaws (film 6, 17–22 s);
   - a crumpled page that becomes a brain (film 9, 21–26 s);
   - a maze with a red path (film 9, 133–158 s).

## 7. People and cases

- **Interviews** are shot with two cameras, wide and close, and cut between them every 4–5 s (film 8: 89 shots in 5:49). Each speaker is named once by a serif lower third. Backgrounds are real rooms: bookshelves, lamps, workbenches.
- **B-roll favours hands and backs over faces.** Films 1, 3 and 4 open on a back or on hands at work. Faces come with speech.
- **Real users, real objects (film 10).** Each case is a short clip of the person or the thing they made. The user's own post sits on it as a white card: avatar, handle and one sentence. Examples: a woman laughing in a knitted sweater, "…vibe knit." Hands holding a home-made mini PC, "I built the ultimate retro mini PC". A chalkboard of equations, "Math just made a little more sense."
- **How a case is made clear in its first second:**
  - The first frame shows the object or the action itself, large: the sweater, the PC, the robot arm over a can.
  - Within about 1 s, one sentence names it, in the user's words or as a plain statement. In film 10 the user's handle is on screen 11 f after the cut and the message about 36 f after it. The card for the next case often arrives before the cut and carries across it, so its words are there on that case's first frame.
  - In the Short, the text leads the action by one line: "and asked it to pick something up." comes before the arm moves.
  - In the explainers, the case is the user's message, shown first in its box ("…should I take more?", film 9, 104 s).
  - No case is posed as an open question over an ambiguous picture.

## 8. Motion

- **Something moves in almost every shot.** Of about 330 shots of 12 f or more, 16 (5 %) showed no measurable motion: a few type plates and locked interview frames. The movement comes from:
  - a slow push-in on wide interviews: 9 % over 10.5 s in film 2's opening, about 0.9 % a second;
  - slow pushes on type plates: "Opus 4.5" grows 10.5 % in 4 s;
  - drifting backgrounds: clouds behind the end cards of films 2 and 5;
  - element builds;
  - handheld documentary footage.
  The Glasswing interviews are locked off (scale change 1 % or less).
- **Easing.**
  - Panels decelerate hard, a strong ease-out. In film 5 at 112.7 s the pink panel's per-frame movement runs 27, 32, 17, 13, 10, 6, 2, 1 over 20 f.
  - Larger wipes ease in and out, accelerating and then decelerating over 61–71 f (film 5, 62 s and 84 s).
  - Pushes on still plates are slow and steady.
  - We saw no springs or overshoot.
- **Animation on twos and threes.** Drawn and graphic elements change only every second or third frame, which gives a hand-made feel. Camera moves, footage and the diagram of film 3 stay on every frame. Measured from the frame differences (a change, then 1–2 identical frames):
  - films 6 and 10: on threes (8 drawings a second): the dot field, the collage, the screens around "Opus 4.6";
  - films 5 and 7: on twos (12 a second);
  - film 2's drawings: mixed twos and threes;
  - film 9's paper crumple: on sevens, like stop-motion; its sliding papers on threes.
- **Stagger.**
  - Screens around "Opus 4.6": 13 arrive in steps every 3 native frames over about 1.1 s, then all leave together in about 15 f.
  - Words in titles: every 2–3 f.
  - Lower-third words: every 4–8 f.
  - Letters in the wordmark: every 4–8 f.
  - Nodes in the film 3 diagram: about every 31 f at first, faster as the tangle grows.
- **Match transitions** link scenes through a shape:
  - the falling ball becomes the black frame of a circular lens (film 2, 32.6 s);
  - the last microscope circle is a moon crater, which pulls back to the moon in the end-card sky (film 2, 80.0 s);
  - a head silhouette slides in over the painted sea and contains it (film 5, 50 s);
  - a white circle opens to fill the screen as an iris before "Count to 1000 by hand" (film 7, 147 s).
- **The wordmark build** is the same in films 1, 2, 5, 6, 7 and 9:
  - The "A\" mark cuts in alone and holds 15 f (12 native).
  - The word then opens between the A and the backslash. Each new letter first appears as a small pictogram (a sprout, a flower, a cross) for 2–5 f, then becomes the letter.
  - A new letter comes every 4–8 f. The word is complete 51–60 f after the cut (41–48 native, film 2 at 80.3 s, film 7 at 192.0 s).
  - It then holds 2–3 s over a still or slowly drifting plate.

## 9. Sound

**Voice.**
- **Narrated or interview voice** carries 8 of the 10 films (1, 2, 3, 5, 6, 7, 8, 9). On-screen text never repeats the narration. Text is used for names, labels, prompts, quotes and the one highlighted sentence.
- **Film 4 (the Short) has no narrator.** Its serif lines tell the story. The only voices are the scientist's own location sound: a question to the robot, "Wait. Wait. What?", laughter, then his reaction. The text gives the facts; the live sound gives the feeling.
- **Film 10 has no voice at all** (no captions exist and the spectrogram shows no speech). Music and type carry it.

**Music.**
- Under voice, the beds are soft and tonal: sustained chords show as long horizontal partials in the spectrograms, with little percussion. Their tempo could not be measured under speech.
- Film 10's music is in front, with a pulse near 150 BPM (or 75 half-time; a beat of 12 f).
- Music changes land exactly on section cuts:
  - film 10: the full low end enters on the cut from the headline montage to the first case (4.1 s); the texture changes on the cut to the white type plate (23.5 s); the beat stops and a high ringing chord holds under "by ANTHROPIC" (37 s);
  - film 6: the music swells through the end montage, peaks during the wordmark build, and its top end cuts off as the word completes (111.2 s), leaving a 1.5 s low tail;
  - films 1 and 2: the music stops dead on the cut to the end card (71.9 s and 80.3 s), leaving a soft pad or ambience;
  - films 5, 7 and 9: the voice ends 1–2 s before the card and the chord decays under the wordmark.
  No film ends on a big percussive hit.

**Do cuts land on the music?**

| Events | On an onset (±2 f) | Chance | Verdict |
|---|---|---|---|
| Film 10, montage cuts (24) | 75 % | 54 % | Linked |
| Film 10, phrase swaps beside "Opus 4.6" (20) | 70 % | 53 % | Linked; 45 % on strong onsets against 37 % |
| Film 10, cuts between cases (15) | 53 % | 48 % | No link |
| Film 10, screens flying in on threes (14) | 50 % | 49 % | No link |
| Cuts in the 6 voiced live-action films | 27–64 % | 45–56 % | No link; at or below chance |

- **In voiced films, cuts fall in the gaps of speech.** The sound level at a cut is 2–4.6 dB below the level at random times. 29–40 % of cuts fall in the quietest quarter of moments, against 25 % by chance (films 1, 2, 3, 6, 7 and 8). The editor cuts between phrases, not on beats.

**Sound effects.**
- We found no separate whoosh, pop or click on text entrances, UI changes or cuts. The automatic test found too few still-then-change events in footage to judge (0–6 per film).
- In film 10, the phrase swaps and montage cuts sit on musical onsets, so the music itself supplies the hits.
- **Letter ticks.** The one clearly event-locked sound is in film 2's end card. After the music drops out, seven short high ticks fall within 1 frame of a letter change, at native frames 1938, 1944, 1950, 1955, 1959, 1962 and 1964 (80.8–82.0 s). Not every letter change has its own tick. Faint chirps, probably birds, follow under the sky.

**Loudness** (measured on YouTube's re-encoded audio):

| Film | Integrated | Range | True peak |
|---|---|---|---|
| 1 Biology lab | −16.0 LUFS | 4.4 LU | −1.6 dBTP |
| 2 Fable 5.1 | −14.8 LUFS | 2.6 LU | −1.7 dBTP |
| 3 Hardware standard | −15.8 LUFS | 3.4 LU | −0.7 dBTP |
| 4 Hardware Short | −17.0 LUFS | 11.2 LU | −2.0 dBTP |
| 5 Levels of thinking | −13.8 LUFS | 2.5 LU | −0.1 dBTP |
| 6 Fable 5 | −13.6 LUFS | 2.3 LU | 0.0 dBTP |
| 7 Translating thoughts | −13.8 LUFS | 2.3 LU | +0.1 dBTP |
| 8 Glasswing | −14.3 LUFS | 2.4 LU | 0.0 dBTP |
| 9 AIs act emotional | −14.3 LUFS | 2.1 LU | +0.1 dBTP |
| 10 Opus 4.6 | −13.7 LUFS | 7.6 LU | +0.8 dBTP |

- The median is −14.3 LUFS integrated.
- Narrated films keep a very narrow range (2.1–3.4 LU). The two films without a narrator swing more (7.6 and 11.2 LU).
- Peaks above 0 dBTP are probably from YouTube's lossy re-encode, not the masters.

## Rules for ThingTracker

Each rule can be checked on a still or a frame count. At 30 fps, 15 f is one beat of our 120 BPM track.

1. **Show an app step as the real screen element, never as a text-only card.**
   - Crop the one element that changes (the Things row, the alert card, the assistant's answer) so it fills 40–60 % of the frame width.
   - Put it on a plain paper or dark plate. No phone frame, no cursor.
   - Put the user's sentence beside it as a speech bubble.
   - From: film 10 at 28.5 s (13 outputs, each with its request); film 3 at 66–84 s (instrument image and agent log on a canvas); film 7 at 8.5–29 s (email and reply re-typeset).
2. **Mark the one thing that matters on every UI or text moment.**
   - Use a yellow highlighter bar (about #F6E755) behind one phrase, or dim everything else to about 50 % grey.
   - Never use bold or coloured type for emphasis.
   - From: film 7 at 12.5 s and 24 s; film 6 at 7.5 s; film 5 at 129 s and 155 s; film 9 at 8–9 s.
3. **Pair every request with its result, in one frame or in two consecutive shots.**
   - Example: "Avisa-me se sair sem as chaves" next to the rule card it created.
   - Example: "Onde está o meu livro?" next to the camera crop of the book on the shelf.
   - From: film 10 at 28.5 s; film 7 at 68–90 s (question, numbers, answer); film 5 at 120–186 s (prompt left, picture right).
4. **Draw "how it works" with named real things, not outlined boxes.**
   - Every node is a pill with a real noun, such as "Câmara da cozinha", "Chaves", "Carteira", "Livro" and "App".
   - Start with one pair joined by a line. Grow it.
   - Show the order the system brings, a hub with a column of things.
   - Move one green pulse along the single path in use, for example from the camera to "Chaves".
   - From: film 3 at 31–66 s.
5. **Show quantities as marks you can count**: one dot per sighting, one square per room, a column of fingerprint views (8 views, 8 tiles). No vague bars or arrows. From: film 6 at 16–22 s and 59–64 s; film 8 at 38–45 s; film 7 at 73–132 s.
6. **A metaphor is one object and one change**, such as one photo of the keys becoming eight views, or one camera frame shrinking to one small crop sent to the server. Never two ideas at once. From: film 2 at 14–20 s; film 6 at 17–22 s; film 9 at 21–26 s.
7. **Open every case on the object or the action, filling the frame, and name it within about 36 f.**
   - The first frame is the keys in a hand, or the child's hand near the detergent pod; the object is the largest thing in it.
   - The sentence that names it is on screen by about frame 36 of the shot, or carried in from the shot before so it is there on frame 0.
   - From: film 10 cases at 4.1–20 s (handle at 11 f, message at about 36 f, cards carried across cuts); film 4 at 13.5–20 s.
8. **Never pose a case as a question over a shot that does not show its subject.** The words on screen must name something visible in that frame; check every case frame by frame. From: all 10 films. The closest pattern is film 4, where "and asked it to pick something up." sits over the arm reaching for the can.
9. **Icons are engravings or cut-out photos, not a UI icon set or emoji.**
   - Monochrome ink drawings with hatching, or real objects photographed and cut out (our keys, wallet, book).
   - One per card: about a quarter of frame height when centred under 2–5 words, up to two thirds when the drawing is the whole picture.
   - A soft blurred colour glow behind is allowed.
   - From: film 7 at 147–155 s; film 9 at 67–96 s and 221–258 s; film 6 at 99–109 s.
10. **Type has three voices.**
    - Book-weight serif in sentence case for names, headlines and story lines.
    - Plain sans for UI text, prompts and labels.
    - Monospace only for machine output (the edge service's log, a rule's JSON).
    - No bold. All caps only in the logo.
    - From: all 10 films.
11. **Type sizes on a 1080-high frame:**
    - hero line 8–14 % of height (86–151 px);
    - end-card name about 10 % (108 px), about half the frame width;
    - story lines over footage about 2.5 % (27 px), left edge at 5–8 % of width;
    - lower third: name 4.4 % (48 px), role 2.5 % (27 px).
    - From: the measurements in section 3.
12. **Words per card: 2–7 for a standalone card, at most 4 stacked lines of 3–5 words for a story line.** From: films 3, 7 and 10 (cards); film 4 (story lines).
13. **Text timing.**
    - Words enter one at a time with a 2–3 f fade, one every 4–8 f.
    - A standalone card holds at least 60 f.
    - A lower third builds in about 25 f, holds about 105 f, and goes off in 1 frame.
    - Story lines fade in over 5–6 f and fade out over about 10 f, ending about 8 f before the cut; the next line comes 6 f after the cut.
    - From: film 3 at 8.6–11.9 s; film 7 at 147–152 s; film 2 at 1.1–5.5 s; film 4 at 0–17 s.
14. **Text entrances stay plain: a fade or a cut-on, no slide or bounce.** Movement belongs to the camera and to the graphics. From: all entrances measured in section 3.
15. **Place text on the plainest or darkest part of the shot**: a back, a wall, empty paper. If no area is plain, cut to a plate instead. From: film 1 at 8.5–15 s; film 4 throughout.
16. **Transitions.**
    - Hard cuts inside a sequence.
    - Between sections, one motivated move: a panel slide of 24–36 f with a strong ease-out, a zoom through a shape of 10–13 f, a defocus of about 38 f, or an iris circle.
    - No cross-dissolve inside a sequence.
    - From: films 2, 3, 5 and 7; the hard-cut shares in section 1.
17. **Use a montage ramp once, to open or to land on the end card.**
    - Shot lengths shrink from about 15 f to 3 f, for example 15, 15, 11, 8, 8, 6, 6, 6, 5, then 4, then 3.
    - Every tile is aligned on one fixed anchor: the same object in the same place, such as each "Thing" crop centred in a circle.
    - Then cut hard to the payoff.
    - From: film 10 at 0–4.1 s; film 6 at 99.5–109.3 s; film 2 at 74.9–80.3 s.
18. **Animate drawn and graphic elements on twos or threes; keep camera moves and UI on every frame.** Hold each drawing 2–3 frames at 30 fps (10–15 drawings a second). From: films 5, 6, 7 and 10 (stepped graphics); film 3 (smooth diagram).
19. **Something moves in every shot, slowly.**
    - Push 0.9–2.6 % a second on wide shots and type plates (a 4 s plate grows about 10 %).
    - Drift the background behind the end card.
    - At most 1 shot in 20 is fully still.
    - From: film 2 at 0–10.5 s; film 10 at 23.5–27.5 s; films 2 and 5 end cards; the 5 % static share.
20. **Palette.**
    - One paper background (cream #F1EDE5 or warm #F0DFC0) or flat dark #141414.
    - Near-black ink.
    - One saturated accent per frame covering under 3 % of it: green for "found", red for "danger", yellow for the highlight.
    - Alternate light and dark plates between ideas, about one switch every 10–15 s in explanation sections (film 6: 9 switches in 113 s).
    - From: section 2.
21. **Sound on events: short and quiet, exactly on the frame, and only where the eye needs it.**
    - A soft high tick within ±1 frame of a letter or a UI change.
    - Montage cuts and phrase swaps on musical onsets.
    - No whoosh on every text pop.
    - Under a voice, cut in the pauses between phrases, not on syllables.
    - From: film 2 at 80.8–82.0 s (letter ticks); film 10 (onset tests); the pause test in section 9.
22. **Change the music exactly on section cuts.** The full track drops in on the cut from the opening montage to the first case. The texture changes on the cut to the product. Use no drum hit at the very end. From: film 10 at 4.1 s, 23.5 s and 37 s; film 6 at 111.2 s.
23. **End card.**
    - Cut to a calm plate.
    - Show the mark first, alone, for about 15 f.
    - Build the name one letter every 4–8 f, complete in 50–60 f.
    - Hold 2–3 s. The whole card lasts 3.5–5 s.
    - The music stops or resolves on the cut to the card, with a 1.5–3 s tail. A soft tick per letter is the only sound that lands with it.
    - From: films 1, 2, 5, 6, 7 and 9 (build); film 2 (ticks); films 1, 2 and 6 (music).
24. **Let real sound carry feeling when there is no narrator.** Keep the live sound of the moment (a laugh, "onde estão as chaves?", a door closing) under the story lines, and let the lines carry the facts. From: film 4 at 33–48 s.
25. **Master at about −14 LUFS integrated, true peak no higher than −1 dBTP.** Keep the loudness range within about 3 LU if there is a voice. From: the loudness table (median −14.3 LUFS).

## Limits

- **Selection.** 4 of the 10 films are long research explainers (5:27, 3:16, 5:49, 4:53), and only 3 are product launches. The study is richer on explanation than on app demos. "Your tools are now interactive in Claude", the most UI-heavy recent film, fell outside the 10.
- **Subtitles.** The server refused subtitles for film 3 (rate limit). Its voice was judged from the picture (on-camera interviews) and the spectrogram. Film 4's subtitles came on a later try.
- **Shot boundaries are judgement calls**, made the same way in every film:
  - animation steps inside a graphic are not cuts;
  - the 35 s diagram of film 3 is one shot;
  - in films 5 and 9 we counted scenes, and their camera moves and in-place morphs are not boundaries.
  Counts are ±1–2 shots per film.
- **Frame accuracy.** The 720p uploads are re-encoded. Native rates are 24, 23.976 and 30 fps, and conversions to 30 fps round to whole frames. Timings are ±1 frame. Film 1 (1190×720) and film 3 (1048×720) are not 16:9, so their width shares are of their own frame.
- **Type.**
  - Sizes come from ink boxes on 720p frames; text over footage or textured paper is ±0.5 % of frame height.
  - Typefaces are described by style, not named.
- **Easing** was read from the per-frame amount of change, not from tracked positions. Push-in values come from a scale fit between two frames and can be biased by a subject moving.
- **Colours** are from compressed video, ±3 levels per channel.
- **Sound.**
  - We could not separate music, voice and effects.
  - The onset tests use the mixed track. Under voice they mostly find syllables, so their chance rates are high (45–56 %) and they cannot show a weak music link.
  - Tempo could not be measured under voice.
  - The automatic test for sounds on in-shot visual events found too few events in footage to judge.
  - Spectrograms were read by eye.
  - Loudness was measured on YouTube's re-encoded audio, not on the masters.
- **We measured durations and shapes, not intentions.** Why a team chose a move is our reading.
