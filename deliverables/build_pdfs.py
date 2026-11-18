#!/usr/bin/env python3
"""Rebuild the PDFs for the team's Drive: the English editions and the Portuguese architecture and integration spec.

    python3 deliverables/build_pdfs.py

  deliverables/english/ThingTracker - Report (EN).pdf            executive summary, English edition (official template)
  deliverables/english/ThingTracker - Architecture (EN).pdf      docs/14-architecture.md
  deliverables/english/ThingTracker - Integration spec (EN).pdf  docs/15-integration-spec.md
  deliverables/english/ThingTracker - Business case (EN).pdf     docs/16-business-case.md
  deliverables/pt/ThingTracker · Arquitetura.pdf                 docs/pt/14-arquitetura.md
  deliverables/pt/ThingTracker · Especificação de integração.pdf docs/pt/15-especificacao-integracao.md

The English figures are drawn first (each script's --lang en writes *.en.* files or charts-en/). Nothing Portuguese
is redrawn here: the Portuguese PDFs use the committed figures, and the Portuguese report keeps its own build.py.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    ["docs/architecture/build_diagram.py", "--lang", "en"],
    ["docs/architecture/build_sequence.py", "--lang", "en"],
    ["deliverables/executive-summary/figuras.py", "--lang", "en"],
    ["deliverables/executive-summary/build.py", "--lang", "en"],
    ["docs/business-case/build_graficos.py", "--lang", "en"],
    ["docs/business-case/build_pdf.py", "--lang", "en"],
    ["docs/business-case/build_pdf.py", "--doc", "architecture", "--lang", "en"],
    ["docs/business-case/build_pdf.py", "--doc", "integration", "--lang", "en"],
    ["docs/business-case/build_pdf.py", "--doc", "architecture"],
    ["docs/business-case/build_pdf.py", "--doc", "integration"],
]

for script, *args in STEPS:
    print(f"$ python3 {script} {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, str(ROOT / script), *args], check=True, cwd=ROOT / Path(script).parent)

for pdf in sorted((ROOT / "deliverables" / "english").glob("*.pdf")) + sorted((ROOT / "deliverables" / "pt").glob("*.pdf")):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = next((line.split()[1] for line in info.splitlines() if line.startswith("Pages")), "?")
    print(f"{pages:>3} pages  {pdf.relative_to(ROOT)}")
