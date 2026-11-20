# Pitch deck

The pitch in European Portuguese, as PowerPoint on the Aveiro Tech City Hackathon template, for the presentation deliverable of 20 Nov. The run of show for the 3- and 5-minute versions is in [docs/pt/21-pitch.md](../../docs/pt/21-pitch.md).

## Files

| File | What |
|---|---|
| `ThingTracker - Pitch 3 min.pptx` | The 3-minute pitch: the template's cover, an introduction, then the pitch. Spoken lines and timings are in the speaker notes |
| `ThingTracker - Pitch 5 min.pptx` | The 5-minute pitch, on the same frame |
| `ThingTracker - Anexo (perguntas).pptx` | Seven architecture diagrams, for the jury's questions |
| `ThingTracker - Narrativa A-E.pptx` | The opening sequence alone (five slides), for rehearsal |
| `ThingTracker - Pitch layout.pptx` | The layout guide: every zone of the frame outlined, then the eight slide variants |
| `*.pdf` | PDF exports. The 3- and 5-minute PDFs (7 and 9 pages) predate the new opening of 20 Nov and have fewer slides than the PPTX files (9 and 12) |
| `assets/` | The kit camera, the child scene from the report's Figure 1, frames from the kit camera in the lab with and without the system's boxes, and the app's alerts |
| `pptx/build_pptx.py` | Builds every PPTX above from the template, the images and the notes |
| `pptx/img/` | The other photos on the slides |
| `source/` | The sources of the HTML version of the deck (below) |

`assets/frame-filipe-ia.png`, used by the 5-minute pitch, is not in the repository: a person in the background is not fully blurred.

## Building the PowerPoint files

`pptx/build_pptx.py` holds the frame every slide follows: the template's header mark and partner logos at 60 %, fixed in place, one title position (x 0,45", y 0,80", 9,10" × 0,55", Arial Bold 26 pt, one line) and one content zone (x 0,45"–9,55", y 1,50"–4,85", or from 0,80" without a title), captions 0,08" under what they caption, 0,25" between blocks. Each slide variant is one geometry function (`v_<name>`), used by the layout guide and by the slides.

```
python pptx/build_pptx.py decks <template.pptx> <out-dir>    # the pitches, the opening sequence and the appendix
python pptx/build_pptx.py guide <template.pptx> "ThingTracker - Pitch layout.pptx"
```

The template is the organisers' slide template; the copy downloaded on 16 Nov is in [../final-presentation/](../final-presentation/).

## HTML version

The deck was first built as a claude.ai Slides artifact, [ThingTracker · Pitch](https://claude.ai/artifact/HrCc8JBAhjvCy1fcKEkyXp), which keeps the motion that the exports lose; it is private unless shared from its page. `source/` is a copy of its files:
- `deck.json`: the slide order and fonts;
- `deck.css`: the shared styles;
- `slides/<id>.html`: one file per slide, with its speaker notes in `<aside>`.

Images appear as `/_blob/<id>` links, which resolve only inside the artifact.

| Version | Date | What changed |
|---|---|---|
| 1 | 18 Nov | First deck |
| 2 | 18 Nov | Rebuilt as 17 slides with motion |
| 19 | 18 Nov | 18 slides; official logos; team slide; one typeface; PT-PT review; use cases with stock photos and detection boxes |
| 21 | 18 Nov | Smoother motion (one easing, 0,8–0,9 s); space balanced on every slide |
| 22 | 18 Nov | The real example moved up to slide 9; notes with speaker, timing and word count; a close with a recap and a request |
| 23 | 19 Nov | Measured numbers on the example (0,93 in 68 of 68 frames); presence and faces on the architecture; privacy wording; a seven-slide appendix with the architecture diagrams |
| 24 | 20 Nov | The new run of show: three films, open models, prototype versus proposal, repository; the earlier use-case slides kept in reserve for questions |
