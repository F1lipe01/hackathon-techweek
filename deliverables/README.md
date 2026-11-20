# Deliverables

The files the team hands in, and the material behind them. Deadlines, and what was submitted when, are in [DELIVERABLES.md](../DELIVERABLES.md). Each folder has a README that lists its files.

| Folder | Contents |
|---|---|
| [executive-summary/](executive-summary/) | The 2-page report in European Portuguese, on the official template, with its source, figures and build |
| [deck/](deck/) | The pitch: PowerPoint files on the organisers' template (3 and 5 minutes, and an appendix for questions), their PDFs, and the sources |
| [pt/](pt/) | The supporting documents in European Portuguese, as PDFs |
| [english/](english/) | The English editions, as PDFs |
| [final-presentation/](final-presentation/) | The organisers' slide template |
| [checkpoint/](checkpoint/) | The one-page brief for the mentors' checkpoint on 18 Nov |
| [use-case-report/](use-case-report/) | The use-case research of 17 and 18 Nov, from before ThingTracker was chosen |
| [opcost/](opcost/) | The model behind the operator-cost tables |

The PDFs in `english/` and `pt/` are printed from the documents in [docs/](../docs/) by `docs/business-case/build_pdf.py --doc <name> [--lang en]`. `build_pdfs.py` redraws the English figures and rebuilds the main set in one go, one heavy job at a time: `python3 deliverables/build_pdfs.py`.
