# Skills scout: the presentation film and the pitch deck

18 Nov 2026. Read-only research: nothing was installed, no `npx` was run, no downloaded code was executed. Online pages were read through a fetch tool that returns a summary, not the raw file. The video-shotcraft files are in Chinese, so its quoted numbers come from a translation.

## The short answer

- **Install two skills:** `video-shotcraft` for the film and `presentation-creator` for the deck. Nothing else cleared the bar.
- **The best film guidance is already installed.** The HyperFrames plugin's references, measured on that team's own launch films, cover the earlier cuts' problems more precisely than anything online: `story.md`, `motion.md`, `sound.md`, `spec.md`, `review.md`, `types/launch.md` and `types/explainer.md` (HyperFrames 0.8.230, `skills/hyperframes/references/`). Use them as craft references while building in Remotion, and ignore their HyperFrames commands.
- **The main Remotion skill disagrees with the measured sources.** `remotion-motion-graphics` says to synthesise a sound kit, to place sounds 2–3 frames early, to make idle elements "breathe", and to use mesh backgrounds with glow. The measured sources say the opposite on all four; see the conflicts table under (b).

---

## (a) The install shortlist

### 1. video-shotcraft (for the film)

| | |
|---|---|
| Install | `npx skills add https://github.com/vincentwei1021/video-shotcraft --skill video-shotcraft` |
| Source | https://github.com/Vincentwei1021/video-shotcraft (Apache-2.0) |
| Installs (skills.sh) | 9,7K, first seen 20 Jul 2026 |
| Stars | 21 265, 1 962 forks; repo created 19 Jul 2026, last push 18 Nov 2026 |
| Audits (skills.sh) | Gen Agent Trust Hub pass, Socket **warn**, Snyk pass |

**What it adds.** It is the only serious product-film skill that is native to Remotion. It brings:

- `references/aesthetic-rules.md`: numbered rules with values covering holds, beat hits, text height and glints;
- `references/sound-design.md` and `music-beat-sync.md`: sound placement that compensates measured offsets, with a ≤3-frame cut tolerance checked on the rendered file;
- `references/final-review.md`: a clean-context reviewer that must cite frame numbers;
- 124–157 shot recipe cards with Remotion demo source.

Its rules also draw on its users' feedback: "history feedback only ever said slower/hold, never too slow".

**Red flags.**

- **Self-promotion after delivery.** The SKILL.md tells the agent to promote the author and collect the user's video (quoted under "Text addressed to an AI" below). Tell the builder to ignore that section.
- **It wants to run a whole pipeline.** That means page capture with puppeteer, a Python beat analysis, downloading sound effects from an online library, a browser "workbench" and a social-media publisher. It also refuses to start production until the user picks a mode. Use it as a **reference library only**. Run nothing from it, and put any analysis it suggests through `video/tools/heavy.sh`.
- **Some rules clash with our bright look.** Q7 (dark brushed-metal backgrounds for close-ups) and Q8 (a finale with "gold particles") do not fit our film; skip both.
- **The repo is young.** It gained 21K stars in four months.

### 2. presentation-creator (for the deck)

| | |
|---|---|
| Install | `npx skills add https://github.com/mblode/agent-skills --skill presentation-creator` |
| Source | https://github.com/mblode/agent-skills/tree/main/skills/presentation-creator (MIT) |
| Installs (skills.sh) | 1,0K, first seen 12 Mar 2026 |
| Stars | 211; last push 14 Nov 2026 |
| Audits (skills.sh) | Gen Agent Trust Hub, Socket and Snyk all pass |

**What it adds.** We have no skill for the story and copy of a talk; `pptx` only covers the file format and visual polish. This one gives:

- a story spine ("write the ending first", "take a position a reasonable person could disagree with", the stakes);
- headline rules (4–12 words, sentence case, no full stop);
- contrast and type floors for a presented deck (4,5:1 minimum, 7:1 preferred, 30 pt body in a large room);
- a speaker-notes structure (key point, opener, talk track, transition);
- a per-slide QA table (3-second test, one message, layout variety, measured contrast).

None of its text is addressed to an AI beyond the task.

**Red flags.**

- **It wants to output its own formats** (Marp, Slidev, reveal.js or Next.js). Keep the team's existing deck format as the output and use only the skill's steps 2–6 and 8.
- **Its pitch framework is for investors** (10 slides, an ask slide, use of funds). Skip it for a hackathon pitch; follow the "live on stage" path.

### Already installed: read these, nothing to install

| Need | Read |
|---|---|
| Story, beats, hook, end card | hyperframes `references/story.md`, `types/launch.md` |
| Moves, eases, transitions, holds, title timing | hyperframes `references/motion.md`; `.claude/skills/motion-doctrine` in the same plugin |
| Sound | hyperframes `references/sound.md` |
| Banned defaults, numbers instead of adjectives | hyperframes `references/spec.md` |
| Review pass | hyperframes `references/review.md` |
| The 6-s diagram | hyperframes `types/explainer.md` ("one diagram that grows") |
| In-app UI motion inside the phone | `animate`, `emil-design-eng`, `apple-design` (springs: damping 1.0 by default, 0.8 only after a flick) |
| Remotion mechanics, video layout | `remotion:remotion-best-practices` → `remotion-create/video-layout.md` |
| Deck visual polish | `anthropic-skills:pptx` "Design Ideas" and "Avoid" lists (no accent lines under titles, no edge stripes, 36 pt+ titles) |
| Naming an effect for a prompt | `animation-vocabulary` |

### Considered and not adopted

| Candidate | Why not |
|---|---|
| `product-launch-video` and `motion-graphics` from the HyperFrames repo (539K and 514K installs on skills.sh) | Stale listings: the folders are gone from the repo's `main` (`skills/product-launch-video` returns 404). The current launch guidance is already in our installed `types/launch.md`. |
| `zarazhangrui/frontend-slides` (32,5K stars, 1,2K installs, Snyk warn) | Builds its own single-file HTML deck stack and would compete with the Slides artifact. It includes deploy steps for an external host. It sets no numbers for type or words. |
| `digitalsamba/claude-code-video-toolkit` → `video-design` (2,6K stars, 480 installs) | Good type rules (five sizes, a 28 px phone floor, one left edge, no crossfades between colour fields), but its timing rules sit in another file of the same toolkit that is not installed with it. The toolkit centres on AI voice and generated footage. |
| `broomva/skills` → `launch-video` (5 stars, 1 install) | A dark-void look with particles and tilted panels (all banned defaults), and it calls generative image and video APIs. |
| `bayramannakov/remotion-video-director` (45 stars, no licence); `everyinc/product-launch-video` (about 35 stars) | Too little use to trust. |
| `aaronvanston/skills-presentations` → `presentation-pitch-deck` (17 stars, 349 installs) | An investor deck meant to be read alone, not a live 3-minute pitch. |
| `dhruvjainin/absolute` → `presentation-design` (224 stars, 139 installs) | Snyk **fail**, plus an emoji directive (quoted below). |
| DevCon Hack Coach (tessl registry), `dylantarre/animation-principles` → `presentations` (162 stars, last update Dec 2025) | Too small to install; a few of their rules are adopted below with attribution. |
| `ailabs-393` → `pitch-deck` | An aggregator flags it as high risk; it outputs PPTX for investors. |
| All higgsfield skills | Excluded by the team. |

---

## (b) Rules for the film (storyboard v5, 30 fps, 120 BPM: a beat is 15 frames)

### What the earlier versions broke

| Problem in an earlier version | The rule it broke | Source |
|---|---|---|
| Fast flicks of footage | Footage shots average 1,8–3 s with motion inside them, and the main subject action gets at least 3 s; feedback "only ever said slower, never too slow" | hyperframes `motion.md`; shotcraft R3 |
| One clip reused | Repeated shots and repeated taglines are cut; each technique is the hero once per film | shotcraft SKILL.md, P4, review F2 |
| Drawn app screens in place of the real app | "Real UI, never a mockup"; "A camera move over a frozen screenshot is not the product performing an action" | hyperframes `types/launch.md`; shotcraft Q1 |
| Tiny unreadable phone screens | Isolate the element at 1,6–2× size; text ≥26 px at 1080p; "never a small window in the middle of an empty canvas, never product UI tilted in 3D" | hyperframes `types/launch.md` |
| Harsh flashes (v4's "one beat of white", light leaks) | ≤3 full-frame hits per film; glow, flares and light leaks are banned defaults | shotcraft R4; hyperframes `spec.md` |
| Beeping sound effects | "No synthesised tones, chimes or dings"; "synthetic UI bleeps are not allowed" | hyperframes `sound.md` §4; shotcraft S1, A7 |
| A boom on every montage cut | "The same whoosh on every cut is the most common tell"; rotate 2–3 takes | hyperframes `sound.md` §4 |

### Where the skills disagree, and which one wins

| `remotion-motion-graphics` says | The measured sources say | Follow |
|---|---|---|
| "Idle elements breathe: sin-wave micro-motion" | Breathing, floating and pulsing loops "look generated"; a landed title is dead still (hyperframes `motion.md`, motion-doctrine) | hyperframes |
| A sound "starting 2–3 frames BEFORE the visual lands" | The sound's peak lands one frame **after** its picture (hyperframes `sound.md`); compensate each file's peak lag and Remotion's AAC offset, measured at about 1,28 frames at 30 fps (shotcraft `sound-design.md`) | the measured offsets |
| "Synthesize a minimal kit as 16-bit WAVs" | No synthesised tones (hyperframes); real-object sounds only (shotcraft S1) | no synthesis |
| Five-layer stack with a "background mesh" and glow on the hero | Mesh gradients, glow, bloom and particles are banned defaults (hyperframes `spec.md`) | hyperframes |
| (hyperframes itself) "Use it unless another framework … is asked for" | We build in Remotion | Say "Remotion" in every brief |

### The rules (attributed)

1. **Footage holds.**
   - Every footage shot runs at least 2,5 s, cut on 4 or 8 beats (2 s or 4 s).
   - The main subject action (the drop on the hall table) gets at least 3 s.
   - Fast cutting (0,13–0,8 s) is for type only, never for footage.
   - Sources: shotcraft R3 and `music-beat-sync.md`; hyperframes `motion.md`.
2. **Every clip, take and tagline appears once.** In act 6, the cat, dog, mother and night cases each lock on in a different way (a mask, a carried label, a match cut, a slow push). Never the same lock-on four times. Sources: shotcraft P4 and review F2; hyperframes `story.md` §8 ("the same move beat after beat").
3. **Real UI on the phone.**
   - Record the running web app (our copy of the Altice app). Don't redraw it.
   - A screen we can't capture becomes a labelled placeholder.
   - In each beat the UI acts on camera: a result populates, the sensor card fills, the alert slides in. Don't just push in on a frozen frame.
   - Sources: hyperframes `types/launch.md` ("Real UI, never a mockup"); shotcraft Q1 and D3.
4. **A readable phone.**
   - The element the beat is about is shown at 1,6–2× its real size, and the hero fills at least 40 % of the frame height or width.
   - Text stays ≥26 px at 1080p after any push, which is ≥52 px in the 4K master. Narrative lines are ≥56 px at 1080p (≥112 px at 4K); secondary text is ≥32 px (≥64 px).
   - No phone floating small in an empty frame, and no 3D tilt on product UI. v4's "slight 3D tilt of the phone" goes.
   - Sources: hyperframes `types/launch.md` and `spec.md`; shotcraft Q11.
5. **A demo framing holds 7–10 s while the UI acts.** A finger or cursor is large (4–7 % of the frame), and its tap causes the next thing on the same frame. Source: hyperframes `motion.md` and `types/launch.md`.
6. **Titles.**
   - At most 6 words a line, one line on screen at a time, no full stop.
   - Hold each for 0,5 s plus 0,3 s a word (a 5-word line is 2,0 s); the film's last line holds at least 2 s.
   - Size 4–9 % of the frame height (86–194 px at 2160p).
   - Once landed, a title is dead still.
   - Source: hyperframes `story.md` §6 and `motion.md`.
7. **Act 2, the question burst.**
   - The first 3–4 questions are held long enough to read: at least one beat, by the word rule about 1,5–2 s each.
   - Only then does the cutting speed up, on half- and quarter-beat steps of the grid (for example cuts at beats 48, 49,5, 50,5, 51, 51,25).
   - The burst is the film's one accelerating run, followed by a full hold.
   - Sources: hyperframes `film.md` ("a word meant to be read holds at least one beat"); shotcraft `music-beat-sync.md`.
8. **No white flash.**
   - At most 3 full-frame hits in the whole film (a flash, scale pump, shake or negative frame), at least 16 beats (8 s) apart, matched to the music's strongest hits.
   - Never more than 3 flashes in any one second (W3C WCAG 2.3.1).
   - Do the "hard stop" as a hard cut to a held frame plus silence, or as a dip cut (the outgoing frame darkens about 40 % for 3 frames). Never a white frame.
   - Sources: shotcraft R4 and `music-beat-sync.md`; hyperframes `motion.md` (dip cut); W3C.
9. **Stillness before each payoff.** Hold 0,3–0,75 s before the drop's lock-on and before the alert lands, then play the payoff at normal speed. Source: hyperframes `motion.md`; motion-doctrine "stillness before climax".
10. **Transitions with a cause.**
    - Use 3–5 kinds in the film, each caused by something on screen: the photo grows into the hall table, the sensor card carries across, a whip, an iris from a tap, a dip cut.
    - At most a third of the seams between beats are hard cuts, and scenes never crossfade.
    - Cut mid-motion, with the same axis, direction and speed on both sides.
    - Sources: hyperframes `motion.md`; motion-doctrine "Vector Law".
11. **Ease by role.**
    - Arrivals land on a long tail (expo.out, power4.out); camera moves ease both ways (power2.inOut); exits and zoom-throughs accelerate (power3.in).
    - Exits are 40–50 % shorter than entrances.
    - Linear only for constant motion. Springs at damping 0,7–0,85 on position and scale, never on opacity or colour.
    - Sources: hyperframes `motion.md`; `remotion-motion-graphics` rule 1; `apple-design`.
12. **No idle motion.**
    - No breathing, floating or pulsing loops.
    - Pause at any second: something meaningful is mid-flight, whether the UI acting, footage playing or the camera travelling with intent.
    - Something new every 2–4 s.
    - Sources: hyperframes `motion.md` and `spec.md`; motion-doctrine.
13. **The brackets are the product, not decoration.**
    - "Corner brackets, HUD readouts as decoration" are a banned default.
    - Brackets appear only on real detector output (tightened by hand where the box is loose), attached to the image transform, with the label on the box.
    - At most one glint per shot, on the hero only.
    - Sources: hyperframes `spec.md`; shotcraft Q4.
14. **The 6-s diagram (act 5) grows.**
    - One part per bar (2 s), so at most 3 parts, each appearing as it is named.
    - Labels sit on the part, with no legend. Never the whole diagram at once.
    - Source: hyperframes `types/explainer.md`.
15. **The mark lands once.**
    - "The mark lands once, with weight, usually on the end card."
    - In act 3, close the brackets into the name as a title reveal, at about 20–30 % of the film (≈25 s fits). Keep the performed mark for act 7.
    - The end card lands in the last 5–10 % of the film. The lockup is 15–30 % of the frame width, carried or wiped in rather than faded, and held at least 1 s after it settles (1,5–3 s in all).
    - The music ends on a bar line with a short fade.
    - Sources: hyperframes `story.md` §4 and §7 and `types/launch.md`; shotcraft R1.
16. **Sound effects.**
    - Only real-object sounds tied to a visible action: shutter, door, phone tap, paper, keys.
    - No beeps, chimes, dings or game-style bleeps; the alert uses a real phone-vibration sound or nothing.
    - Rotate 2–3 takes of any repeated sound, stepping the volume down from 0,40 to 0,25 over repeated hits.
    - One riser into one impact in the whole film, on the drop.
    - Sources: hyperframes `sound.md` §4; shotcraft S1, S2 and A7.
17. **Sync and levels.**
    - Each sound's peak lands 1 frame after its picture.
    - Hits sit 3–6 dB over the bed.
    - The mix is −16 to −14 LUFS with true peak ≤ −1 dBTP.
    - Cuts are within 3 frames of the beat grid, checked on the rendered MP4, not the preview.
    - Sources: hyperframes `sound.md` §4–5; shotcraft `sound-design.md` and review A3 and A6.
18. **The sound tells the story.** The opening sits near silence or on a thin bed. The music opens when the product appears (the drop) and holds back until the payoff. Source: hyperframes `sound.md` §2.
19. **Banned look, by name.** Banned: a dark void with small floating things, glow, bloom, lens flares, light leaks, particles, purple or blue or mesh gradients, glass cards, three cards in a row, a title over a dimmed screenshot, and the logo docked in a corner. Add to this list whatever the first render shows. Source: hyperframes `spec.md` "BANNED by default".
20. **Review before every render.**
    - Render stills at each scene's start and middle, at every cut (−0,2 s and +0,2 s), and at phone width (360 px).
    - A fresh subagent gets only the storyboard and the sheets, and returns P0/P1 lines (`t=… · where · problem → change`) with frame numbers.
    - Fix every P0 before the 4K render. Never score the film out of 10.
    - Sources: hyperframes `review.md`; shotcraft `final-review.md`.

---

## (c) Rules for the pitch deck and its delivery

1. **One idea per slide, understood in 3 seconds.** If a stranger can't state the slide's point at a glance, split it or cut it. Sources: Duarte, "The Glance Test"; Hale (YC, 15 Nov 2015), "obvious"; presentation-creator QA.
2. **Few slides.**
   - 3-minute pitch: 5–7 slides. Hale gives "5 to 7" ideas for a 2 min 30 s Demo Day slot.
   - 5-minute pitch: at most 10, the 10/20/30 rule.
   - The film counts as one slide.
   - Sources: Hale, YC 2015; Kawasaki, 10/20/30 rule (2005, read via secondary summaries; the primary page refused access).
3. **Big type, and headlines that state the takeaway.**
   - Body text ≥30 pt in a large room. In 1920×1080 HTML slides, anything the audience must read is ≥40 px.
   - Headlines are 4–12 words, in sentence case, with no full stop, and say the conclusion.
   - Every chart carries its conclusion written on it.
   - Sources: presentation-creator `visual-design.md` and `writing-slides.md`; hyperframes `slideshow`; Hale.
4. **Contrast and room.**
   - At least 4,5:1 for everything below headline size, 7:1 preferred.
   - Ask about the room: a bright room gets a light background, a dark auditorium a dark one.
   - No accent lines under titles and no edge stripes.
   - Sources: presentation-creator `visual-design.md` (WCAG 1.4.3); `pptx` "Avoid".
5. **No raw app screenshots.**
   - "Screenshots … are usually illegible."
   - Crop to the one element and enlarge it, or show it moving in the film.
   - Demo slides are full-bleed with minimal chrome.
   - Sources: Hale; presentation-creator `visual-design.md`.
6. **Say what it is in the first 30 seconds.**
   - Open with one plain sentence: "O _ThingTracker_ é … para …".
   - Pick the one sentence a judge should repeat to another judge an hour later, and build the talk around it.
   - Rehearse the first 30 s out loud the most; "that is where the score is set".
   - Source: Kurbaitaev, "What judges actually score", DEV Community, Jul 2026.
7. **The demo is one complete path.**
   - Register → ask → sentence becomes a sensor → alert. Show only what works and describe the rest in one sentence.
   - Keep a 60-s screen capture and one screenshot as a fallback.
   - Map each slide to one judging criterion of the challenge.
   - Sources: Kurbaitaev 2026; hackathon judging guides.
8. **No motion for its own sake.** No slide transitions. A build, if one is needed, runs 0,3–0,5 s on a click, with eased timing and nothing linear. Sources: Hale ("animations, transitions" listed as distractions); presentation-creator; `dylantarre/animation-principles` (as a fallback for the numbers).
9. **Notes and rehearsal.**
   - Each slide gets notes with its key point, an opener and a transition to the next slide. Notes are not a verbatim script.
   - Run each version (3 min and 5 min) end to end out loud with a timer before the event.
   - Sources: presentation-creator `speaker-notes.md` and `story-structure.md` ("Story is testing, not refining"); DevCon Hack Coach.
10. **Q&A in one sentence each.**
    - Prepare one-line answers to the five standard questions: How does it scale? Why not the nearest existing tool? What happens when the model gets it wrong? Who pays? What's the moat?
    - Add 2–3 questions specific to us, for example privacy of footage and running on the router.
    - Name a known weakness before a judge does; in one judge's sheets that raised scores.
    - Sources: DevCon Hack Coach `pitch-template.md`; Kurbaitaev 2026.

---

## Text addressed to an AI (reported, not followed)

- **video-shotcraft SKILL.md, post-delivery section** (in Chinese): it tells the agent, after delivery and unprompted, to open the author's motion workbench, to suggest crediting the skill's author when the film is published, and to invite the user to submit the film to the author's showcase page through a form, dropping the request if the user declines. Not followed: our footage stays local (AGENTS.md rule 6).
- **`dhruvjainin/absolute` presentation-design:** it tells the agent to open every first response with an emoji. Not followed.
- **HyperFrames skills.** Vendor steering inside the skills: `reverse-any-video` routes people on screen to the vendor's paid service without stating a price; `media-use` tells the agent not to state prices or offer cheaper options unprompted; `hyperframes` prescribes how to name and promote the vendor's desktop app. Not followed.
- **`frontend-slides`:** deploy steps for an external host and sign-up links. Out of scope; not followed.

---

## Sources

**Skills, read locally**

- `remotion-motion-graphics` (SKILL.md, `references/design-rules.md`)
- Remotion 4.0.539 skills (best-practices router, create, `video-layout.md`)
- HyperFrames 0.8.230 skills (hyperframes and its references, reverse-any-video, slideshow, media-use; motion-doctrine, seam-craft, changelog-video)
- `animate`, `emil-design-eng`, `apple-design`, `animation-vocabulary`, `design-taste-frontend`
- `pptx` (SKILL.md)

**Online, read 18 Nov 2026**

- skills.sh leaderboard and skill pages (install counts, audits): https://skills.sh/
- video-shotcraft: https://github.com/Vincentwei1021/video-shotcraft (SKILL.md, `references/aesthetic-rules.md`, `sound-design.md`, `music-beat-sync.md`, `final-review.md`); GitHub API for stars and dates
- presentation-creator: https://github.com/mblode/agent-skills (SKILL.md, `references/writing-slides.md`, `visual-design.md`, `speaker-notes.md`, `pitch-decks.md`, `story-structure.md`)
- HyperFrames repo `skills/` listing (9 folders; `product-launch-video` returns 404); GitHub API: 86 489 stars, last push 18 Nov 2026
- digitalsamba toolkit `video-design` and `synthetic-ui-demo` SKILL.md; zarazhangrui/frontend-slides SKILL.md
- Kevin Hale, "How to Design a Better Pitch Deck", Y Combinator, 15 Nov 2015: https://www.ycombinator.com/blog/how-to-design-a-better-pitch-deck
- Duarte, "The Glance Test": https://www.duarte.com/resources/guides-tools/the-glance-test/
- Guy Kawasaki, 10/20/30 rule (2005); primary page returned 403, figures from secondary summaries
- M. Kurbaitaev, "What Judges Actually Score", DEV Community, Jul 2026: https://dev.to/kurbaitaev/what-judges-actually-score-notes-from-a-year-of-hackathon-judging-3p4l
- DevCon Hack Coach pitch template: https://tessl.io/registry/paker-it/devcon-hack-coach/files/references/pitch-template.md
- W3C, Understanding SC 2.3.1 "Three Flashes or Below Threshold" (updated 17 Sep 2025): https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html
