# Deliverables

Per the rules (Article 14) and FAQ Q18, there are **two submission moments**:

| # | Deliverable | Deadline | Folder | Submit |
|---|---|---|---|---|
| 1 | Succinct 2-page report (PDF) — use the exec-summary template | **Wed 18 Nov, 19:00** | `executive-summary/` | [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSepZIiXKm-tQaNF-1UmPIh4Z3IapeybneKr7N5W47Qs1Vf7dQ/viewform) |
| 2 | Executive summary (PDF, max 2 pages) | **Fri 20 Nov, 17:30** | `executive-summary/` | TBA |
| 3 | Presentation (PPT) | **Fri 20 Nov, 17:30** | `final-presentation/` | TBA |
| 4 | Code / app repository link, optional | **Fri 20 Nov, 17:30** | the repo | TBA |

The 18 Nov "report" and 20 Nov "executive summary" are, in practice, the same 2-page PDF refined — the only 2-page template is the exec summary. See [docs/01-event.md](../docs/01-event.md#deliverables) for the naming inconsistency. **Late = possible disqualification.** Submit early.

## Files

| File | What |
|---|---|
| `executive-summary/sumario-executivo-template.docx` | Official template. Original name `Sumário Executivo Template ATC Hackathon 2026.docx` |
| `executive-summary/sumario-executivo-IT-Porto.pdf` | **Today's submission (18 Nov), ThingTracker.** 2 pages, PT-PT, on the official template. Built from the source below |
| `executive-summary/sumario-executivo.md` | The text of the Sumário. Edit this, then run `python3 build.py` |
| `executive-summary/build.py` | Fills the official .docx and prints a matching PDF with Chrome (no Word or LibreOffice needed). Checks nothing else; check the page count with `pdfinfo` |
| `executive-summary/sumario-executivo-IT-Porto.docx` | The same text in the official template, for edits in Word or Google Docs. Its line breaks may differ slightly from the PDF |
| `executive-summary/fluxo.svg`, `fluxo.png` | The flow figure on page 2 (source and render) |
| `executive-summary/draft.md` | The first skeleton with the template rules. Superseded by `sumario-executivo.md` |
| `checkpoint/checkpoint-brief.pdf` | **Mentor checkpoint, 18 Nov.** One page in English: the 30-second pitch, status, Friday demo, 8 ranked questions, known risks. Source `checkpoint-brief.md`, build `build.sh` |
| `final-presentation/apresentacao-final-template.pptx` | Official slide template, 5 layout slides with no text. Original name `Template - ATC Hackathon 2026.pptx` |
| `use-case-report/top5-use-cases.pdf` | **Top 5 use cases** (v3, 17 Nov): evidence, kit fit, scores, pitch scripts in PT-PT, Q&A, and a draft Sumário Executivo in PT-PT for Wednesday. Source: `top5-use-cases.md`; rebuild with `use-case-report/build.sh` (pandoc + Chrome) |
| `use-case-report/top5-summary.pdf` | **Current recommendation, v4** (5 pages): **Casa Atenta**, one assistant that uses every device (camera vision, mic and speaker, phone presence, door, plug, bulb, sensors, alarm). Evidence, scores, privacy design, demo plan, pitch in PT-PT, to-dos. Supersedes the recommendation in `top5-use-cases.pdf` (v3), which still holds the damp, cold and fire evidence |

The templates were downloaded on 16 Nov. The live versions are in the [templates folder on Drive](https://drive.google.com/drive/folders/1rYi1o8HWRieewvc4dZwyyiTYM_o9bOyT); the slide template was still being edited that afternoon, so re-download before building the final deck.

## Pitch formats

| Round | When | Pitch | Q&A |
|---|---|---|---|
| Intermediate, mentors | Fri 20 Nov, 16:00 | 3 min | 2 min |
| Final, jury, top 3 only | Time not announced | 5 min | 3 min |
