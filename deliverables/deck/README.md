# Pitch deck

The deck is a claude.ai Slides artifact: [ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp). It is private until it is shared from its page. Present it from the link, because the PPTX and PDF exports lose some of the motion.

`source/` is a copy of the deck's own files, kept here so its history shows in the repo:
- `deck.json`: the slide order and fonts;
- `deck.css`: the shared styles;
- `slides/<id>.html`: one file per slide, with its speaker notes in `<aside>`.

Images appear as `/_blob/<id>` links, which only resolve inside the artifact.

| Version | Date | What changed |
|---|---|---|
| 1 | 18 Nov | First deck. Team verdict: no motion, no creativity |
| 2 | 18 Nov | Rebuilt as 17 cinematic slides. Team verdict: "way, way better" |
| 19 | 18 Nov | 18 slides; official logos; team slide; one font; PT-PT review (19 fixes); cases with real stock and boxes |
| 21 | 18 Nov | Smoother motion (one ease, 0,8–0,9 s); space balanced on every slide |
| 22 | 18 Nov | From the pitch research: the real example moved up to slide 9; notes with speaker, timing and word budget; the close with a recap and an ask; contrast and 3-second check on every slide |
| 23 | 19 Nov | Real numbers on the example (0,93 in 68 of 68 frames); the code decides, presence and faces on the architecture; privacy wording; a seven-slide appendix with the architecture diagrams for questions |
| 24 | 20 Nov | The new run of show: three films, open models, prototype versus proposal, repository; the old case slides kept as a reserve for questions |

The run of show for the 3- and 5-minute pitches is in [docs/pt/21-pitch.md](../../docs/pt/21-pitch.md).

## PowerPoint on the organisers' template

The files submitted at 17:30 are `ThingTracker - Pitch 5 min.pptx` (and its PDF); `ThingTracker - Pitch 3 min.pptx` keeps only the 3-minute slides. Both are built on the Aveiro Tech City Hackathon template by `pptx/build_pptx.py` (python-pptx): the template's cover, black and white frames, one headline per slide, images, and the spoken lines and timings in the speaker notes, read from `source/slides/<id>.html`. The template itself is not stored here. Rebuild: `python pptx/build_pptx.py template.pptx BUILD_DIR "ThingTracker - Pitch 5 min.pptx" "ThingTracker - Pitch 3 min.pptx"` (needs ffmpeg and the films in `video/out/pitch/`).
