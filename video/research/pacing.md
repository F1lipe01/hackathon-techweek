# Editing pace of strong product films (measured)

Measured on 19 Nov 2026 for the ThingTracker film (Remotion, 30 fps, music at 120 BPM: a beat is 15 frames, a bar 60), to set a faster pace than the v5.1 cut. No one publishes shot-by-shot numbers for these films, so we measured them.

## How we measured

- **Sources.** Six official uploads, downloaded at 720p with `yt-dlp`. Every web page and download was treated as untrusted.
- **Cut candidates.** `ffmpeg` scored every frame for scene change in one pass per film. Candidates were the frames above 0.3 and above 0.15. A third look at 0.07–0.15 found two dark cuts in the Anthropic film that 0.15 had missed.
- **Manual check.** We checked every candidate by eye on contact sheets, 3 frames before and 3 after.
  - Dropped: camera flashes, 1-frame flash inserts, photo flicker, fast motion inside one take, and UI changes.
  - Added: missed cuts, found on full-film sheets with one tile every 4–8 frames.
- **Soft transitions.** Fades, dips and dissolves were timed from the mean brightness of each frame.
- **Camera moves in UI films.** Timed from the share of pixels that change between frames.
- **Text.** Timed frame by frame at the film's own frame rate, on 640×360 frames, from counts of bright text pixels plus a visual check.
- **Units.** All lengths are in frames at 30 fps ("f"), so they compare directly with our timeline. Native frame counts are in brackets where they matter. One second is 30 f, and at 120 BPM one beat is 15 f.
- **What counts as a shot.** A shot is the picture between two transitions.
  - The boundary of a dissolve is its midpoint. The boundary of a dip is the middle of the black.
  - Camera moves and UI animations inside one take are not cuts. We count them separately.
- **Beat check.**
  1. We found the tempo grid that best fits the cut times.
  2. We counted the share of cuts that fall within ±1.5 frames of an audio onset, a sudden rise in sound, and compared it with the share for random times.

## 1. Google, "Fixed on Pixel" (Pixel 7, Super Bowl, Feb 2023)

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=ZYEQ1f1e8Dg (Google Canada, verified channel). The link in our brief, `zkHdpA-drz0`, is now private. |
| Duration | 90.1 s (23.976 fps) |
| Shots | 52 (35 per minute) |
| Average shot | 1.73 s = 52 f |
| Median shot | 1.19 s = 36 f |
| Shortest / longest | 8 f (press conference, wide) / 234 f (opening text card) |
| Average shot per quarter | Q1 116 f · Q2 36 f · Q3 41 f · Q4 59 f |
| The fast middle (23–81 s) | 43 shots, average 41 f, median 34 f (8–105) |
| Transitions | 51 in all. 45 hard cuts (88 %), 5 of them through 2–4 black frames. Soft transitions: 1 dissolve of 34 f (text to photo), 3 cuts to black then fade up of 34–43 f, 1 fade to black of 58 f under text, and 1 whip pan of 9 f [7]. All the soft transitions except the whip are in the first 23 s. |
| Shots by type | Action: median 49 f (16–86). Phone UI inserts: 29–66 f, median 42 f. Photo inserts: median 34 f (13–105). Establishing: 8–60 f. Product shot: 104 f. Logo: 55 f. |
| Beat | 67 % of cuts land on an audio onset (chance 30–41 %). The cut times fit a grid of about 109 BPM (51 % of cuts within ±1 frame; chance 23 %). The audio tempo estimate is 110 BPM. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "For years, our phones have captured our memories." | 8 | Phrase by phrase: 48 f for the first phrase, 34–39 f for each of the next three | 16–29 f between phrases; 234 f for the whole card (7.8 s) | Dissolves into the first photo, 34 f | Slow fade per phrase, on black |
| "Now, it's time to fix them." | 6 | Word by word, 6–10 f per word, at uneven gaps | 186 f for the whole card | 6 f glitch, then 29 f of black before the hard cut to the first fix | Fade per word, over a photo that fades out |
| "Little mistakes" / "Big mistakes" / "Huge mistakes" | 2 each | Cut | 20 / 23 / 25 f | Cut | Cut in, cut out. The holds lengthen and the type grows. |
| "Fixed / on / Pixel." | 3 | One word cuts on every 33–35 f (about 2 beats of the 109 BPM grid) | 101 f in all | Cut | Word by word, cut on |
| "Google Pixel 7" | 3 | Cut | 33 f | Cut to the next line | Over the product shot |
| "The only phone engineered by Google" | 6 | Cut | 56 f | Cut with the shot | Over the product shot |
| G logo + URL | 1 + URL | Builds in 15 f | 38 f | End | Logo animation |

Notes:
- The film opens slowly: text and four old photos with fades for 23 s. Then it cuts hard, on sound, for about 58 s.
- The fast part starts with a ladder of three 2-word cards (20, 23, 25 f) between the demos.

## 2. Apple, "iPhone 17: Track Your Apple Devices with Find My" (Apple India, Apr 2026)

We substituted this film. "Introducing AirTag" and the other AirTag ads are no longer on any Apple channel; only re-uploads by others exist. This Find My spot is the only official Find My film we found. It is 20 s long, so its numbers are thin.

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=SjW_Molimx0 (Apple India, verified) |
| Duration | 20.0 s (25 fps) |
| Shots | 12 (36 per minute) |
| Average shot | 1.67 s = 50 f |
| Median shot | 1.18 s = 35 f |
| Shortest / longest | 19 f (palace windows) / 150 f (Apple logo on black) |
| Average shot per quarter | Q1 33 f · Q2 35 f · Q3 72 f · Q4 150 f |
| Before the end card (0–11.8 s) | 10 shots, average 35 f, median 26 f (19–64) |
| Transitions | 11, all hard cuts (100 %) |
| Shots by type | Action: median 28 f (24–56). UI inserts: 23 f (phone in hand) and 43 f (screen close-up). Establishing: 19–97 f. First shot: 24 f. |
| Beat | 36 % of cuts on an onset (chance 24 %). With only 11 cuts, this is too few to judge. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "Find My on iPhone 17" | 5 | Cuts in with the shot | 59 f | Cut, swapping to the Apple logo over the picture (38 f) | No animation |
| Apple logo on black | 0 | Cut | 150 f (5 s) | End | Still |

## 3. Anthropic, "Keep thinking with Claude" (Sep 2025)

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=FDNkDBNR7AM (Anthropic) |
| Duration | 90.0 s (25 fps) |
| Shots | 99 (66 per minute) |
| Average shot | 0.91 s = 27 f |
| Median shot | 0.76 s = 23 f |
| Shortest / longest | 6 f (a cut hidden in motion) / 131 f (final shot under the logo) |
| Average shot per quarter | Q1 18 f · Q2 28 f · Q3 33 f · Q4 38 f |
| Opening montage (0–20 s) | 36 shots, average 17 f, median 16 f (10–34). 15 of the 36 last 15 f or less; 4 last 12 f or less. |
| Story section (22–76 s) | 55 shots, average 29 f, median 28 f (6–80) |
| Transitions | 98, all hard cuts (100 %). 2 of them are hidden in fast motion. After the montage comes a 71 f near-black rest shot (2.4 s). |
| Shots by type | Montage: median 16 f. Action: median 29 f (6–58). UI inserts: median 28 f (20–72). Establishing: average 37 f (18–80). Graphics: average 26 f. |
| Beat | 43 % of cuts on an onset (chance 39 %). We measured no link between cuts and the music. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "PROBLEMS" (title box) | 1 | 10 f: a line grows into a box | 13 f | 11 f glitch, then the word sits over the next shot for 16 f | Screen-style reveal; 49 f in all |
| "Problems" written into the scene (13 shots) | 1 | With the cut | The length of the shot, 10–34 f | Cut | Letters typed on a surface, a label maker, a magnifier, neon signs |
| "Keep [Creating / Researching / Learning / Coding]" | 2 | Cut | 38–44 f per label. The label changes every second cut. | Cut | Over the picture; the verb sits in a small box |
| "Keep thinking." | 2 | Cut | 55 f | Cut | Card on dark teal |
| Claude logo + "The AI for problem solvers" | 5 | Cut | 104 f (3.5 s) to the end | End | Over the last shot |

Notes:
- This film is the fastest at the start and slows down steadily.
- The hook is a montage of the word "problems" in 13 forms, mixed with other images.

## 4. Linear, "Linear Asks" (Oct 2023)

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=jZvZfBl3VOw (Linear) |
| Duration | 118.6 s (30 fps). This is longer than our 60–90 s. |
| Shots | 13 (7 per minute) |
| Average shot | 9.12 s = 274 f |
| Median shot | 9.77 s = 293 f |
| Shortest / longest | 25 f (Slack, wide) / 428 f (Linear triage view) |
| Average shot per quarter | Q1 293 f · Q2 240 f · Q3 250 f · Q4 358 f |
| Transitions | 12 in all. 3 hard cuts (25 %). 6 dips to black, 11–35 f long (out 6–19 f, in 5–16 f). 1 slow fade up from black of 90 f. 2 fades to black, 27 and 35 f. |
| Inside shots | 10 animated camera moves (push-ins, pull-outs, pans) on the UI. 9 of them last 14–25 f; the opening zoom-out lasts 47 f. UI changes (menus, typing, a new form) happen in place, with no cut. |
| Shots by type | UI: median 293 f (25–428). Logo animation: 188 f. End card: 422 f. |
| Beat | Only 3 cuts, so we could not test. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "LINEAR.APP/ASKS" | 1 (URL) | Fades in over about 65 f | About 280 f | Fades out over about 50 f | Slow push-in of about 12 % over the hold |

Notes:
- This is a calm screen demo. Its pace comes from UI events and camera moves, not from cuts.
- It has no title cards. The words are the product's own UI.

## 5. Ring, "Search Party | A New Way to Neighbor" (Oct 2025), a home-camera brand film

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=nQMuDtsLv0g (Ring, verified) |
| Duration | 91.4 s (29.97 fps container; the picture is 24 fps with repeated frames) |
| Shots | 28 (18 per minute) |
| Average shot | 3.27 s = 98 f |
| Median shot | 2.19 s = 66 f |
| Shortest / longest | 28 f (hand and glass insert) / 516 f (full-screen app flow) |
| Average shot per quarter | Q1 59 f · Q2 71 f · Q3 293 f · Q4 186 f |
| Before the first alert (0–21.7 s) | 11 shots, average 59 f, median 57 f (28–107) |
| Transitions | 27 in all. 25 hard cuts (93 %). 1 dip to black of 89 f to show time passing (37 f out, 20 f black, 32 f in). 1 fade to black of 45 f before the end card. |
| UI | Five UI shots: an alert on white (slides in over 6 f, holds 48 f), the camera's own footage (40 f), the phone in the car (41 f), and two full-screen app flows (145 f and 516 f). The long flow has 7 steps. Each step holds 21–133 f (median 42 f, average 56 f), and the steps change with animated scrolls of 11–25 f. A typed message runs at 33 characters in about 41 f. |
| Shots by type | Action: median 63 f (28–304; the reunion is one handheld take of 304 f). Establishing: 57–226 f. |
| Beat | 24 % of cuts on an onset (chance 28 %). Cuts follow the story, not the music. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "Millions of pets go missing every year." | 7 | Fade, 26 f | On screen 136 f in all (4.5 s) | Fade, about 10 f, as the picture fades out | Over an aerial pull-up |
| "Search Party uses AI to ensure none stay lost." | 9 | Fade, about 19 f | About 34 f at full strength; 63 f in all | Fade, about 10 f | Second line, under the first |
| Ring logo, then "Making neighborhoods safer" | 3 | Logo fades in over 30 f; the tagline fades in over 30 f, starting 25 f after the logo | About 75 f to the end | End | Slow push-in |

## 6. Google, "Meet the Google Nest Cam Indoor (wired, 3rd gen)" (Oct 2025), a home-camera brand spot

| Measure | Value |
|---|---|
| Official URL | https://www.youtube.com/watch?v=2RTVFTOh8vo (Made by Google, verified) |
| Duration | 30.0 s (23.976 fps) |
| Shots | 11 (22 per minute) |
| Average shot | 2.73 s = 82 f |
| Median shot | 2.21 s = 66 f |
| Shortest / longest | 24 f (dog end tag) / 243 f (camera view with alert, question and search) |
| Average shot per quarter | Q1 74 f · Q2 154 f · Q3 58 f · Q4 64 f |
| Transitions | 10, all hard cuts (100 %). One line of text stays on screen across a cut. |
| Shots by type | Camera-view UI shots: 41–243 f (median 76 f). Product: 31–114 f. Action: 24 and 65 f. Logo: 44 f. |
| Beat | 50 % of cuts on an onset (chance 50 %). No link measured. |

| Text | Words | In | Hold | Out | Motion |
|---|---|---|---|---|---|
| "Google Nest Cam Indoor" | 4 | Fade, 8 f | 59 f | Slides up and out, 4 f | Over the product |
| "Sharper" → "Sharper 2K resolution" | 1 → 3 | Letter by letter, 6 f | 14 f, then shrinks into the longer line over 5 f, which holds 83 f across a cut | Cut | Large word, then a small line |
| "Get more details" | 3 | Letter by letter, 9 f | 51 f | Cut | Over the picture |
| "Ask what happened" | 3 | Letter by letter, 8 f | 50 f | 5–6 f, morphing into a search bar | The search is then typed |
| "Busted." | 1 | 4 f | 36 f | Cut | Lands as the dog jumps out |
| "More insight inside" → "... with 2K and Gemini" | 3 → 7 | Letter by letter, 8 f | 10 f, then shrinks and extends over 12 f; the long line holds 59 f | Cut | Large, then small |
| End title + G logo | 8 + logo | Cut | 99 f title card, 44 f logo | Cut to a 24 f end tag | Logo animation |

## Summary across the films

| Film | Length | Shots | Shots per min | Average shot | Median | Shortest–longest | Hard cuts | Shape of the pace |
|---|---|---|---|---|---|---|---|---|
| Pixel "Fixed on Pixel" | 90 s | 52 | 35 | 52 f | 36 f | 8–234 f | 88 % | Slow 23 s opening, fast middle (41 f), slower end |
| Apple Find My (India) | 20 s | 12 | 36 | 50 f | 35 f | 19–150 f | 100 % | Even (33–35 f), then a 5 s end card |
| Anthropic "Keep thinking" | 90 s | 99 | 66 | 27 f | 23 f | 6–131 f | 100 % | Fastest first (18 f), slows each quarter (38 f) |
| Linear "Linear Asks" | 119 s | 13 | 7 | 274 f | 293 f | 25–428 f | 25 % | Even and slow; long screen takes and dips to black |
| Ring "Search Party" | 91 s | 28 | 18 | 98 f | 66 f | 28–516 f | 93 % | Story cuts first (59–71 f), then long UI and reunion takes |
| Nest Cam Indoor | 30 s | 11 | 22 | 82 f | 66 f | 24–243 f | 100 % | Text carries the pace inside long shots |

What the films share:

- **No film speeds up toward the end.** They put their speed at the start (Anthropic, Apple, Ring) or in the middle (Pixel), and end on a held card.
- **The ads with music cut hard almost every time** (88–100 %). Soft transitions appear only at section changes: the opening, time passing, and the end.
- **Two films rest in the dark after the hook.** Pixel holds 29 f of black before its first fix; Anthropic holds a 71 f near-black shot after its montage.
- **Text comes in fast and usually leaves with a cut.** Entrances take 4–10 f. Most text leaves with the shot, or morphs into the next text in 4–6 f.
- **Only Pixel lands its cuts on sound hits.** Two thirds of its cuts land on an onset, and its cut times fit a grid of about 109 BPM. In the other films we found no link between cuts and the beat.

## Targets for ThingTracker (30 fps, 120 BPM: beat 15 f, bar 60 f)

| Element | Target | In beats | Comes from | Working target | Verdict |
|---|---|---|---|---|---|
| Average shot, whole film | 36–54 f | 2.5–3.5 | Pixel 52 f (41 f in its fast middle), Apple 50 f. Anthropic is faster at 27 f. | 36–54 f | Confirmed |
| Hook montage shots | 12–18 f, base 15 f; first shot 24–30 f; at most 1 shot in 8 at 10 f | 1 (first shot 2) | Anthropic hook: median 16 f, 10–34 f, only 4 of 36 at 12 f or less. Apple's first shot: 24 f. | 8–15 f | Changed: 8–11 f is rare even in the fastest film. Use 1 beat as the base. |
| Establishing (a place) | 30–60 f | 2–4 | Anthropic: average 37 f. Pixel: 31 f. Apple: 60 f. Ring is slower: 57–226 f. | (none) | New |
| Action inside a montage | 20–30 f | 1.5–2 | Anthropic: median 29 f. Apple: median 28 f. | 15–30 f | Confirmed, at the upper half |
| Action that carries the story (someone leaves with a book) | 45–60 f | 3–4 | Pixel action: median 49 f. Ring action: median 63 f. | 15–30 f | Changed: a real action that must be understood is held 3–4 beats |
| Single UI insert (one screen, one idea) | 30–45 f | 2–3 | Pixel: median 42 f (29–66). Anthropic: median 28 f. Apple: 23 and 43 f. Ring alert: 55 f. | 45–75 f | Changed: shorter than our working target |
| UI step in a multi-step flow | 45–60 f per step, with 15–20 f animated moves between steps | 3–4 per step; about 1 per move | Ring: median 42 f, average 56 f per step, moves 11–25 f. Linear camera moves: 14–25 f. | 45–75 f | Confirmed at 45–60 f. Use 75 f only when the viewer must read a full sentence. |
| Text: entrance | 6–8 f | about ½ | Nest: 4–9 f per line. Pixel: 6–10 f per word. | 6–8 f | Confirmed |
| Text: 2–3-word card inside a rhythmic series | 20–25 f in all, cut in and out | 1.5 | Pixel "mistakes" ladder: 20, 23, 25 f | 30 f (in 6–8, hold 18–20, out 4) | Confirmed for series. The Pixel cards have no in/out animation. |
| Text: standalone 2–3-word line | Hold 45–60 f after the entrance | 3–4 | Nest: 50–51 f. Anthropic "Keep thinking.": 55 f. Apple, 5 words: 59 f. | Hold 18–20 f | Changed: a line that stands alone is held 2–3 times longer |
| Text: exit | Cut with the shot (0 f), or a morph or fade of 4–6 f | 0–½ | Pixel, Anthropic, Apple and Nest mostly cut. Nest morphs in 4–6 f. Ring fades in about 10 f. | 4 f | Confirmed |
| Word-by-word build | One word every 30 f | 2 per word | Pixel "Fixed / on / Pixel.": 33–35 f per word | (none) | New |
| Hard-cut share | 90–100 % | (n/a) | Pixel 88 %, Ring 93 %, Anthropic, Apple and Nest 100 % | about 85 % | Confirmed; the data allows even more cuts |
| Whip pan | 8–10 f, once | about ⅔ | Pixel: 9 f (7 native). It is the only whip in the six films. | 6 f | Changed slightly: 6 f is shorter than the one whip we measured |
| Longest transition inside a sequence | 15 f or less | 1 or less | No soft transition longer than 9 f inside any fast section | No transition over 15 f | Confirmed inside sequences |
| Transition at a section change (time passing, the end) | Dip or fade of 30–90 f | 2–6 | Ring dip: 89 f. Ring end fade: 45 f. Pixel fades up from black: 34–43 f. Linear dips: 11–35 f. | (not allowed) | Add as the one exception |
| Rest after the hook | 30–60 f of black or near-black, once | 2–4 | Pixel: 29 f of black before its first fix. Anthropic: 71 f near-black shot. | (none) | New |
| End card | 90–150 f | 6–10 | Anthropic logo: 104 f. Ring: 140 f. Apple: 150 f. Pixel: 104 f product line, then a 55 f logo. | (none) | New |
| Typed text in a UI | About 1–1.5 f per character | (n/a) | Ring: 33 characters in about 41 f | (none) | New |
| Cutting to the music | Cut on hits (beats and sound accents), not on every beat | (n/a) | Pixel: 67 % of cuts on an onset, against 30–41 % by chance | (none) | New |

**Reading the targets together.** A 75 s film at an average of 45 f has about 50 shots. The data supports this order:

1. A hook of 12–18 f cuts.
2. A rest of 2–4 beats.
3. Story actions of 3–4 beats.
4. UI steps of 3–4 beats.
5. An end card of 3–5 s.

Speed should come from short montage shots and short single UI inserts, not from shortening the actions the viewer must understand.

## Limits

- **Apple AirTag.** We could not measure an AirTag film. "Introducing AirTag" (2021) and the later AirTag ads are not on any Apple channel; only re-uploads by others exist, which we did not use. Apple India's 20 s Find My spot replaced them, and 20 s gives few shots.
- **Pixel.** The link in our brief is private. We used Google Canada's official upload of the same 90 s film.
- **Raycast.** Not measured. We chose Linear for the software launch film.
- **Linear Asks.** At 119 s it is longer than our range, and it is a screen demo. Use its numbers for UI sections only.
- **Shot boundaries are judgement calls**, applied the same way in every film:
  - Pixel: photo animations, flicker and 1-frame flashes are counted inside their shots.
  - Anthropic: two cuts hidden in motion are counted as cuts.
  - Ring: the reunion is counted as one handheld take.
  - Linear: camera moves on the UI are not counted as cuts.
- **Frame accuracy.**
  - The 720p uploads are re-encoded copies. Counts are ±1 frame.
  - Ring is 24 fps picture in a 29.97 fps file, so its animation counts are ±1–2 frames.
  - Fade starts are hard to see on busy backgrounds. Ring's first line was timed by eye.
- **Animation curves.** We measured durations only, not easing curves, camera speeds, or the size of type moves.
- **Sound.** We could not separate the music, voice and effects. The tempo figures come from the mixed track, so they are rough.
  - The beat-grid test from the audio was inconclusive in every film; a small tempo error drifts over a minute.
  - The onset test cannot tell a music hit from a sound effect.
  - We did not measure whether each cut carries a sound effect, or the timing of the voiceover words.
- **Shot types.** The labels (hook, action, UI, establishing) are ours, given while we watched.
