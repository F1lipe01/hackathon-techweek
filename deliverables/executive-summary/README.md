# Executive summary

The 2-page report in European Portuguese, on the organisers' template. The PDF and the DOCX were submitted on 18 Nov 2026 at 18:51 as the succinct report (version 2, with a child at risk in the kitchen as Figure 1). They are kept exactly as submitted.

| File | What |
|---|---|
| `sumario-executivo-IT-Porto.pdf` | The submitted report, 2 pages |
| `sumario-executivo-IT-Porto.docx` | The same text in the official template, for editing in Word or Google Docs. Its line breaks may differ slightly from the PDF |
| `sumario-executivo.md` | The report's text: the source of both files |
| `sumario-executivo.en.md` | The English edition of the text, printed to `../english/ThingTracker - Report (EN).pdf` |
| `build.py` | Fills the official template and prints the PDF with Chrome: `python3 build.py`, or `python3 build.py --lang en` for the English edition. Check the page count with `pdfinfo` |
| `sumario-executivo-template.docx` | The organisers' template, downloaded on 16 Nov (original name `Sumário Executivo Template ATC Hackathon 2026.docx`) |
| `figuras.py` | Draws Figure 1 from the photos in `fotos/`, and copies Figure 2 from `docs/architecture/` (`--lang en` for the English figures) |
| `figura-exemplo.svg`, `.png` | Figure 1: from the visual enrolment of a thing to the action. `figura-exemplo.en.*` is the English version |
| `arquitetura.svg`, `.png` | Figure 2: the architecture, copied from `docs/architecture/thingtracker-architecture.svg`. `arquitetura.en.*` is the English version |
| `figura-arquitetura.svg`, `.png` | An earlier, simpler architecture figure that `figuras.py` still draws. Not used in the report |
| `fotos/` | Figure 1's photos, and `fotos.json`, which places them. The child scene was supplied by the team with the face and the brand logos blurred; `crianca2-cena-full.jpg` is the uncropped original |
