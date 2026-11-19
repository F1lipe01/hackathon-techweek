# Video 1 production playbook: faked actions, screen replacement, pace and sound (research, 19 Nov 2026)

Why: the team rejected v5.1. The pace and effects were slow, the opening didn't hook, text pops and on-screen actions were silent, and the wallet section looked fake (a still photo and stock placeholders). This playbook says how professionals do each part, what runs on this Mac, and how we do it. It replaces these rules in [product-film-playbook.md](product-film-playbook.md):
- "≤17 characters per second, hold titles long enough to read twice";
- "sound effects only for changes of state";
- long holds.

Companions:
- [pacing.md](pacing.md): measured shot lengths of six reference films (19 Nov).
- [../shoot/index.html](../shoot/index.html): the shoot sheet, published for the team.
- Tools: `video/tools/make_markers.py`, `track_markers.py`, `synth_plate.py`.

Treat every number marked *(estimate)* as ours, not a source's.

Tools on this Mac:
- After Effects 2027 with Mocha AE;
- Blender 5.2.3;
- ffmpeg 9;
- OpenCV 5 (`cv2.aruco`, ECC);
- torch 2.15 with MPS;
- Remotion 4.0.545 (`@remotion/motion-blur` and `@remotion/effects` are in `node_modules`).

DaVinci Resolve is not installed.

---

## 1. Faking real actions (photographing an object, leaving home, the alert)

**How professionals do it.**
- A phone in an ad is filmed with a blank or dark screen; the content goes in during post. "Phones in commercials nowadays are just a blank screen until VFX can come in" (VFX supervisor on a Verizon Android spot) [1].
- Each action is covered from several angles and assembled by cutting on action [2][3]:
  - a wide;
  - an over-the-shoulder (OTS) shot;
  - an insert (thumb on the shutter, hand into the pocket);
  - the screen full frame.
- The whole action is played in every angle so the cut points overlap. Inserts also hide continuity errors.

**Our method.** Film the real action with our own phones, following the shoot sheet. Drop stock from the wallet story altogether.

**Steps and numbers.**
1. **Lens.** Use 2× (48 mm) for hands and the phone, because it doesn't distort; 0,5× does [4]. Lock the lens: the Camera app jumps to the ultra-wide close up. Use 0,5× only for the high-corner "home camera" view.
2. **Light, with no kit** [5][6]:
   - one window from the side as the key light;
   - ceiling lights off rather than mixed;
   - a white card opposite as fill;
   - dark cloth close to the subject as negative fill;
   - a bedsheet over the window as diffusion;
   - the held screen angled away from the window and the filming phone [7].
3. **Settings.**
   - Portugal's mains is 50 Hz, so under room lights the exposure must be a whole number of 1/100 s flicker cycles. **30 fps at 1/50 s** (216°) is flicker-free and keeps the film's 15-frame beat *(our choice)*.
   - Lock ISO, white balance (set on a white sheet in each room), focus and lens.
   - HDR, Enhanced Stabilization and Auto FPS off; Rec.709; HEVC.
   - The free Blackmagic Camera app exposes all of these [8]. The native camera's equivalents are in Settings › Camera › Record Video [9].
   - No ProRes: about 220 Mbps at 1080p, roughly 6 GB/min at 4K [10]. No log.
4. **The shutter moment.**
   - A 1–2-frame blink on the phone's screen only, never a full-frame white flash. A built-in flash transition holds white 1–2 frames [11].
   - Keep the hand's natural dip; add no fake shake *(estimate)*.
5. **"The camera saw it."** A phone taped high in a corner at 0,5×, locked off. Desaturate, crush the blacks, add a timestamp and the detection box, and show it as an inset beside the main shot [12]. Google showed Nest Supersight the same way: a wide view and a close-up.
6. **The alert.**
   - Shots: the buzz in the pocket, then the pull-out OTS, then the banner full frame.
   - Since iOS 16.4, web apps added to the Home Screen can receive real push notifications [13]. For the film we composite the banner from the prototype's recording.
7. **Matching our footage to any stock that stays.**
   - One shared grade, with white balance locked per room.
   - Grain added last, after motion blur. After Effects' Match Grain samples real grain from the plate [14].

**Pitfalls.**
- Mixing phone models across hero shots.
- A bright light crossing the screen, which breaks tracking.
- Auto exposure mid-take.
- A face in frame without consent (AGENTS.md rule 6).

## 2. Mapping a real phone screen (screen replacement)

**Why v5.1's inserts didn't sit** (review of `track_screen.py` and `media.tsx`):
- `minAreaRect` always returns a rectangle, so the corners are wrong whenever the phone is seen in perspective.
- The thresholded edge moves with exposure, blur and the thumb.
- The 7-sample average keeps only about 68 % of a 2 Hz hand sway, so the insert slides against the phone.
- The insert sits outside the plate's grade and has no motion blur, defocus or grain.
- Its edge is hard and its blacks are pure black.
- `multiply` removes the screen's reflections.
- During a push-in the plate is blurred while the screen stays sharp: a strong fake tell.

The homography maths in `geom.ts` is correct; keep it.

**Recommended method (built and tested): markers on the held phone, tracked by script.**
1. The held iPhone shows a marker screen (`video/shoot/markers/`, made by `make_markers.py`): 5 ArUco markers (DICT_4X4_50; IDs 0–3 in the corners, inset 6 % of the width to clear the rounded corners and the Dynamic Island; ID 4 in the centre).
   - A screenshot of it taken on the phone is the tracker's reference, so the markers' exact place on that screen is known.
2. `track_markers.py <take> <screenshot> <out.json> --check check.mp4` reads every frame in order:
   - ArUco gives sub-pixel marker corners and a RANSAC homography.
   - **ECC** refines it. ECC is OpenCV's intensity-based planar fit, the same idea as Mocha's planar tracker. It runs as a 3-level pyramid on the marker tiles, with skin masked out so a thumb doesn't pull the fit.
   - ECC starts from the previous frames' motion. It also starts from the markers' fit when the two disagree.
   - In fast moves the template gets the same motion streak as the frame.
   - Frames that can't be fitted are interpolated and flagged. Smoothing (a forward-backward One Euro filter, no lag) is off unless the check video shows jitter [15].
3. **Output.** The screen's virtual sharp corners per source frame, plus a difference-check video: the reference warped onto the plate in difference mode should stay dark where the track is right. Mocha's grid overlay is the same idea.
4. **Test on a synthetic 4K plate** (`synth_plate.py`): motion blur at 1/50 s, sway, a 58 px/frame flick, and a thumb over the markers.
   - Median corner error: 0,42 px.
   - 95th percentile: 0,89 px.
   - Worst frame: 2,1 px (about 1 px at 1080p).
   - Markers alone were 8,6 px median, because motion blur biases their corners.
5. **In Remotion** (`TrackedScreen`, to build):
   - interpolate between source frames;
   - draw the recording through the homography (`matrix3d`), inside a light version of the plate's grade;
   - feather the edge 1–2 px with the measured corner radius;
   - add defocus matched to the plate (not Gaussian) [16], motion blur from `@remotion/motion-blur` [17], then grain.
   - Never blur the plate while the screen stays sharp.

**Fallbacks.**
- **Mocha AE in After Effects:**
  - Track the phone face. Add a layer above it for the thumb, which is held out automatically [18].
  - Export a Corner Pin, not "Corner Pin with Motion Blur": that variant bakes in position, scale and rotation keys [19].
  - Dump the four corners per frame to the same JSON with ExtendScript.
- **Blender:** a plane track. Render through the Plane Track Deform node; the image preview is not final [20].
- **AI point trackers, only for unmarked stock:**
  - TAPIR or BootsTAP and LocoTrack are Apache-2.0.
  - CoTracker is mostly non-commercial.
  - None documents Apple MPS [21].

**Pitfalls.**
- Bright markers smear past the screen edge in motion blur. Ours are inset and the green variant is dark.
- A plate and comp frame rate that don't match make the insert slip. Shoot at 30 fps.
- HDR (HLG) footage shifts colour in Remotion's tone mapping. Shoot Rec.709.

## 3. Photographing a real object: the viewfinder and the photo flying into the app

**What professionals do.**
- Filming the real camera app live is the weakest option: flicker, exposure mismatch and moiré [22]. Phones have no aperture to stop down, the usual cure for moiré [23].
- The phone is filmed blank, and the viewfinder is composited [1][24].

**Our method.**
- **Prototype first.** The prototype registers a thing by **showing it to the home camera** (`server.py`: 8 views in 40 s). The app shows that camera's live view, "Registering · n of 8", then "Wallet added". Photographing with the phone is a concept the app doesn't have, so that version carries a "conceito" label.
- **Proof A (real), show it to the camera:**
  - A1: the hand turns the wallet in front of the kit camera while the held phone shows grey markers.
  - A2: `record.py` records the kit camera and the edge's boxes during the same take, synced by a clap.
  - The phone's screen gets the real `register` recording, with its live box replaced by A2.
- **Proof B (concept), photograph it with the phone:**
  - B1: the OTS with green markers.
  - B3: a viewfinder plate shot from the phone's position, repeating the rise, and moved against the tracked phone motion so it stays in step.
  - B4: the hero phone recording its own camera, kept as a rescue. It gives perfect parallax but can't show markers.
- **The shutter and fly-in** *(estimate, built from [11])*:
  1. the screen blinks for 2 frames on the press;
  2. the photo freezes for 6–8 frames;
  3. it shrinks into its slot over 10–12 frames with an ease-out and motion blur;
  4. a shutter sound on the contact frame, plus a haptic tick.

## 4. Green screen on a phone

**What professionals pick.**
- **Black or off screen, few or no markers, roto the fingers.** Christiansen (Frame.io) [7]; Allen (ProVideo Coalition) [16]. Green destroys real reflections and spills onto skin.
- **About 20 % grey with 5 small markers** so the screen edge shows. Logik forum [24].
- **"Very dark green", at least 1 stop under skin,** when you must key a thumb and keep the reflections. Eliminating all reflections "makes the composite look fake" (Rick Gerard, Adobe Community Expert) [25].

**Our method.**
- Green markers (`#0C401C` ground, `#46BE64` markers) wherever a finger touches the screen: they key out together, and the thumb is kept.
- Grey markers (`#333333`, black and white) where nothing touches.

**Held-phone settings** [26][27]:
- brightness at maximum (the dark pixels set how it looks);
- Auto-Brightness, True Tone and Night Shift off;
- Auto-Lock Never;
- Do Not Disturb;
- Guided Access with touch off, so taps can't move the image.

**Exposure.** Expose for skin. The green stays at least 1 stop under it, and the light markers must not clip.

**Keying** *(our design, to build as `key_screen.py`)*:
- **Region:** inside the tracked quad, dilated by 3 %.
- **Key:** a hue key at 100–170° with saturation over 0,35, soft-edged, then choked 1 px and blurred 1 px.
- **Despill:** on the edges only, G = min(G, max(R, B)).
- **Output:** cropped VP9 with alpha. ProRes 4444 would cost about 2,5 GB a minute at 1080p [10].
- **Why not ffmpeg:** its `chromakey` measures chroma distance, and skin sits too close to dark green.
- **Fallback:** a SAM 2.1 matte (Apache-2.0; MPS support is "preliminary") [28].

**Making the insert look lit from within** [16][29]:
- Lift its blacks to the plate's black-glass level; never pure black, and never darker than the source.
- Put its whites about 0,5–1 stop over the skin highlights *(estimate)*.
- Add a glow around 10 %.
- Light the thumb with a blurred copy of the insert (Add, 10–25 %).
- Shift it slightly cooler under warm room light.
- Match the grain.
- Judge stills at 100 % and 400 %, beside the reference take of the real app screen at the same brightness (`video/shoot/markers/reference-app-pro-402.png`).

**Layer order in Remotion, bottom to top:**
1. the plate;
2. the insert, with motion blur;
3. the keyed plate (thumb and reflections);
4. the thumb light;
5. grain.

## 5. Pace

Measured in [pacing.md](pacing.md). What the research already fixed:
- **TV ads** averaged under 2 s per shot by 1991 [30]; 13,2 shots per 30 s spot in 1992 (about 2,3 s each) [31].
- **Reading speed.** Netflix's adult limit is 20 characters per second; 17 is the children's limit [32]. It is a cap for subtitles beside dialogue, not a reason to hold cards.
- **Shortest event.** The minimum for a 1–2-word event is 20 frames at 24 fps (0,83 s), which is 25 frames at 30 fps [33].
- **UI motion** takes 150–250 ms [34][35]: 5–8 frames at 30 fps.

Targets at 30 fps and 120 BPM (a beat is 15 f, a bar 60 f). These are **measured** on six official films (Pixel "Fixed on Pixel", Apple Find My, Anthropic "Keep thinking", Linear Asks, Ring "Search Party", Nest Cam); see [pacing.md](pacing.md) for each film's numbers.

| Element | Frames | Measured in |
|---|---|---|
| Average shot, whole film | 36–54 (a 75 s film: about 50 shots) | Pixel 52, Apple 50; Anthropic is faster at 27 |
| Hook montage | 12–18 per shot, 15 (one beat) as the base; the first shot 24–30; at most 1 in 8 shorter than 12 | Anthropic's 36-shot opening, median 16 |
| Rest after the hook | 30–60 of black or near-black, once | Pixel 29, Anthropic 71 |
| Establishing (a place) | 30–60 | Anthropic 37, Pixel 31, Apple 60 |
| Action inside a montage | 20–30 | Anthropic and Apple medians 28–29 |
| **Action that carries the story** (the wallet left, the door) | **45–60**, cut mid-action | Pixel median 49, Ring 63 |
| A single UI insert (one screen, one idea) | 30–45 | Pixel median 42 |
| A UI step in a multi-step flow | 45–60 per step, animated moves of 15–20 between steps; 75 only for a full sentence | Ring |
| Typed text in the UI | about 1–1,5 per character | Ring |
| Text entrance | 6–8 | Nest, Pixel |
| A 2–3-word card in a rhythmic series | 20–25 in all, cut in and cut out | Pixel's "Little / Big / Huge mistakes" |
| **A standalone line** | **hold 45–60 after the entrance** | Nest 50, Anthropic "Keep thinking." 55, Apple 59 |
| A word-by-word build | one word every 30 | Pixel "Fixed / on / Pixel." |
| Text exit | a cut with the shot, or a 4–6 morph or fade | most films |
| Hard cuts | 90–100 % | Pixel 88 %, Ring 93 %, the rest 100 % |
| Whip pan | 8–10, once | the only whip measured (Pixel, 9) |
| Transitions inside a sequence | 15 or less | none longer than 9 in any fast section |
| A section change (time passing, the end) | a dip or fade of 30–90, the one exception | Ring, Pixel |
| End card | 90–150 | Anthropic 104, Ring 140, Apple 150 |
| The alert "Saíste sem a carteira" | 55–60 | Ring's alert 55 |

How to read this:
- **Speed comes from the hook, montage shots and short single UI inserts**, not from shortening the actions and lines the viewer must understand.
- **No film speeds up towards the end.** They are fastest at the start or in the middle, and they end on a held card.
- **Only Pixel cuts on sound hits** (67 % of its cuts land on an onset, against 30–41 % by chance). Cut on hits (beats and accents), not on every beat.
- **Why v5.1 felt slow, measured against this:**
  - Its opening held four shots of 60 f each, four times the hook's 15 f.
  - Its story scenes ran 120–240 f as single shots, where these films cut each action in 45–60 f.
  - On top of that came slow effects and silence.

Text rules:
- springs with damping 14 and stiffness 160;
- words staggered 2–4 f;
- exits always faster than entrances (from the installed Remotion motion-graphics skill);
- something moves in the first 15 f, and nothing goes 90 f without a new element.

## 6. Sound: a sound for every visual event

**Sync** [36][37]:
- Audio that leads the picture is noticed from about 45 ms (BT.1359) or 40 ms (EBU R37). Audio that lags is tolerated longer. At 30 fps one frame is 33 ms.
- **Transients** (tap, click, Foley contact, impact): the attack lands on the contact frame or one frame later, never earlier. `sound.tsx` already places each file's measured peak one frame after the picture. Keep that.
- **Swells** (whoosh, riser): start 2–4 f before the move and peak where it moves fastest. Spring and ease-out entrances are fastest in their first 1–3 frames. Put a small tick on the settle frame [38].

**Variation** [39]:
- 3–4 takes per sound type, rotated;
- ±1–2 semitones and ±1,5 dB per hit;
- a high-pass at 150–200 Hz on UI sounds;
- one shared short room reverb;
- one sound per card, not per word.

Remotion's `toneFrequency` is fixed per clip and works only in the final render [40].

**Foley.** Recorded on set (the shoot sheet lists every sound) [41]:
- WAV or Lossless, mono;
- 15–30 cm from small props, 50–100 cm from doors and steps;
- a duvet behind the recorder;
- 3–5 takes.

**Logo sting for the approved end card:**
1. A riser or reverse swell of 15–30 f that ends on the frame "ThingTracker" lands, after an optional 5–8 f of silence.
2. An impact on that frame (low thump, mid body, a little shimmer), the same frame as the music's final hit.
3. A tonal tail of 45–90 f.
4. A second hit, 6 dB lower, 30 f later, for "by" plus the Altice Labs logo.

**The music.**
- Cut it on downbeats at 4- or 8-bar phrase boundaries.
- Fit the length backwards: the final hit goes on the end card, and whole phrases come out of the middle [42].
- Find beats with onset detection, then round each beat to a frame on its own.

**Levels** [43][44][45]:
- The master is −14 LUFS integrated, −1 dBTP.
- For the projector, keep short-term loudness within +5 LU of integrated, and test on the room's speakers.
- Two-pass ffmpeg `loudnorm` with `linear=true` and `-ar 48000`. Check that the summary says "Linear", and verify with `ebur128`.

### The sound list

Levels are relative to the music bed (0 dB).

| Visual event | Sound | Length | Sync point | Level |
|---|---|---|---|---|
| A 2–3-word text card pops in | soft tick or pop, 3–4 takes rotated | 40–120 ms | first frame the text is ≥ 50 % visible | −6 to −3 dB |
| Text card out | tiny reverse tick, or nothing on a hard cut | 30–80 ms | exit start | −9 dB |
| Camera push or whip | air whoosh | the move + 2–4 f | peak at the fastest frame, or on the cut for a whip | −3 to 0 dB |
| A detection box locks on | tick plus a short rising blip | 100–200 ms | the lock frame | −3 dB |
| A registration view is counted ("3 of 8") | a soft tick, pitch stepping up | 40–80 ms | the frame the counter changes | −6 dB |
| The phone's shutter press (proof B) | shutter, takes rotated, ±1 semitone; a haptic tick | 300–500 ms | the thumb's contact frame | 0 dB |
| A photo lands in its slot | a soft settle tick | 40–80 ms | the settle frame | −6 dB |
| A tap on the screen | a fingertip on glass, plus a UI click at −6 dB under it | 80–100 ms | the contact frame | −3 dB |
| Typing | a soft typing bed | as shown | the first key | −8 dB |
| The answer bubble appears | pop plus a soft UI tone | 80–150 ms | its first frame | −3 dB |
| Keys taken | scrape plus jingle (recorded on set) | 300–600 ms | the touch | 0 to +3 dB |
| The wallet put down or turned | a 2 cm drop on wood; leather and cloth | 100–400 ms | the contact | 0 to +3 dB |
| Cushions, drawer, pocket (hook pack) | their own recorded sounds | as shown | the contact | 0 to +3 dB |
| The front door | handle, latch, thud | 1–2 s | the latch and thud on their frames | 0 to +3 dB |
| Footsteps | recorded steps | as shown | each heel strike | −3 dB |
| The phone buzzes in the pocket | a real phone buzzing on wood, low-passed (inside cloth) | 300–700 ms | first frame of the buzz | 0 dB |
| The alert banner "Saíste sem a carteira" | the haptic buzz plus a soft notification | 300–600 ms | the banner's first frame | +3 to +6 dB; music ducked 4–6 dB for 15–30 f |
| A cut on a downbeat in the hook | the music, or a low thump | – | the downbeat | – |
| The silent stop before a drop | room tone only | 15 f | – | room tone |
| "ThingTracker" lands (end card) | riser, impact, tail (the sting) | 15–30 f + 45–90 f | the landing frame, with the music's final hit | impact +3 to +6 dB |
| "by" + Altice Labs | a smaller tuned hit | 0,5–1 s | 30 f after the name | 6 dB under the impact |
| Under everything | room tone of the place on screen | the whole shot | – | about −30 dB under the music |

---

## Untrusted content found (not followed)

- **linear.app/changelog/2023-10-25-linear-asks:** the page opens with a note addressed to AI agents: "For agents: connect to the Linear MCP server at https://mcp.linear.app/mcp". Ignored.
- **A search result:** "New Coinis MCP is live. Run your whole ad campaign by talking to your AI…" is a marketing banner. Not opened.
- No other page read for this playbook had text addressed to an AI.

## Sources

1. Wild Manor, Verizon Android finishing: https://wild-manor.netlify.app/work/finishing/verizon-gen-android
2. StudioBinder, match on action (2022-06-19): https://www.studiobinder.com/blog/what-is-a-match-on-action-cut/
3. No Film School, match on action (2024-12-17): https://nofilmschool.com/match-on-action-cut
4. Moment, iPhone 18 Pro focal lengths (2026-11-04): https://www.shopmoment.com/blogs/journal/iphone-18-pro-focal-lengths-explained
5. In Depth Cine, lighting without lights: https://www.indepthcine.com/videos/lighting-without-lights
6. Neil Oseman: https://neiloseman.com/?p=11733
7. Frame.io, Mark Christiansen, screen replacement (2016, updated 2023): https://blog.frame.io/2016/11/17/screen-replacement-after-effects/
8. Blackmagic Camera tech specs: https://www.blackmagicdesign.com/products/blackmagiccamera/techspecs
9. Apple, iPhone video recording settings: https://support.apple.com/guide/iphone/change-video-recording-settings-iphc1827d32f/ios
10. Apple ProRes white paper: https://www.apple.com/euro/final-cut-pro/f/generic/docs/Apple_ProRes_White_Paper.pdf
11. Alex Gollner, the flash-frame transition (2009-02-03): https://blog.alex4d.com/2009/02/03/final-cut-tip-the-flash-frame-transition-you-already-have/
12. No Film School, CCTV effect (2016-12-03): https://nofilmschool.com/2016/12/how-create-cctv-video-effect-or-without-plugins
13. WebKit, web push for web apps on iOS (2023-02-16): https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
14. Adobe, noise and grain effects: https://helpx.adobe.com/after-effects/using/noise-grain-effects.html
15. Casiez, the One Euro filter: https://gery.casiez.net/1euro
16. ProVideo Coalition, Damian Allen, screen inserts done right (2020-02-13): https://www.provideocoalition.com/screen-inserts-done-right/
17. Remotion motion blur: https://www.remotion.dev/docs/motion-blur
18. Boris FX, tracking occluded objects (2018-03-27): https://borisfx.com/videos/mocha-tips-how-to-track-occluded-object/
19. Noble Desktop, Mocha screen replacement (2023): https://www.nobledesktop.com/learn/after-effects/motion-tracking-screen-replacement
20. Blender manual, Plane Track Deform: https://docs.blender.org/manual/en/latest/compositing/types/tracking/plane_track_deform.html
21. TAPNet: https://github.com/google-deepmind/tapnet · LocoTrack: https://github.com/cvlab-kaist/locotrack · CoTracker: https://github.com/facebookresearch/co-tracker
22. PremiumBeat, Jason Boone, screen replacements (2020-07-30): https://www.premiumbeat.com/blog/screen-replacements-in-after-effects/
23. ProVideo Coalition, Adam Wilt, stop down to erase moiré (2021-09-08): https://www.provideocoalition.com/tip-stop-down-to-erase-moire/
24. Logik forum, screen replacement advice (Dec 2020): https://forum.logik.tv/t/screen-replacement-advice-for-producers/1773
25. Adobe Community, Rick Gerard (Feb 2021): https://community.adobe.com/t5/after-effects-discussions/green-screen-tablet-reflection-ae/m-p/11842143
26. Apple, display brightness: https://support.apple.com/en-us/HT202613
27. Fix in Post, on-set iPhone guide: https://sites.google.com/view/fixinpost/how-to-guides/on-set-iphone-setup-guide
28. SAM 2: https://github.com/facebookresearch/sam2
29. PremiumBeat, Evan Abrams, phone screen replacement: https://www.premiumbeat.com/blog/video-tutorial-cell-phone-tablet-screen-replacement-in-after-effects/
30. MacLachlan & Logan, camera shot length in TV commercials, Journal of Advertising Research (1993): https://www.warc.com/Content/421e1376-baa5-472f-aa9d-adc58bea5146
31. Charles Young, fast editing speed and commercial performance, WARC (2007-04-30): https://www.warc.com/content/article/fast_editing_speed_and_commercial_performance/86058
32. Netflix, English timed-text style guide: https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977
33. Netflix, subtitle timing guidelines: https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394
34. Material-UI transitions: https://app.unpkg.com/@material-ui/core@4.12.4/files/es/styles/transitions.js
35. Atlassian, applying motion: https://atlassian.design/foundations/motion/applying-motion
36. TV Technology, Hoffner, A/V synchronisation (2003-05-14), citing ITU-R BT.1359: https://tvtechnology.com/opinions/av-synchronization-how-bad-is-bad
37. EBU R37: https://tech.ebu.ch/publications/r037
38. Pixflow, transition sounds in motion graphics: https://pixflow.net/blog/enhancing-motion-graphics-with-cinematic-transition-sounds/
39. A Sound Effect, Tilman Hahn on whooshes (2014-01-21): https://www.asoundeffect.com/the-sound-of-the-whoosh-with-tilman-hahn/
40. Remotion, pitch: https://www.remotion.dev/docs/audio/pitch
41. CalArts 2 Pop, recording Foley at home (updated 2026-08-31): https://2pop.calarts.edu/technicalsupport/recording-foley-at-home/
42. PremiumBeat, picking music for video: https://www.premiumbeat.com/blog/how-to-pick-the-perfect-music-for-your-video-projects/
43. Ian Shepherd, YouTube loudness: https://productionadvice.co.uk/youtube-loudness/
44. EBU R128 s1 (short-form): https://tech.ebu.ch/docs/r/r128s1.pdf
45. ffmpeg, loudnorm: https://ffmpeg.org/ffmpeg-filters.html#loudnorm
