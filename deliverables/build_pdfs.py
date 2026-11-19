#!/usr/bin/env python3
"""Rebuild the PDFs for the team's Drive: the English editions and the Portuguese technical documents.

    python3 deliverables/build_pdfs.py

  deliverables/english/ThingTracker - Report (EN).pdf            executive summary, English edition (official template)
  deliverables/english/ThingTracker - Architecture (EN).pdf      docs/14-architecture.md
  deliverables/english/ThingTracker - Integration spec (EN).pdf  docs/15-integration-spec.md
  deliverables/english/ThingTracker - Business case (EN).pdf     docs/16-business-case.md
  deliverables/english/ThingTracker - Operator costs (EN).pdf    docs/17-operator-costs.md
  deliverables/english/ThingTracker - Use cases (EN).pdf         docs/18-use-cases.md
  deliverables/english/ThingTracker - Product (EN).pdf           docs/20-product.md (figures from docs/product/build_flows.py)
  deliverables/pt/ThingTracker · Arquitetura.pdf                 docs/pt/14-arquitetura.md
  deliverables/pt/ThingTracker · Especificação de integração.pdf docs/pt/15-especificacao-integracao.md
  deliverables/pt/ThingTracker · Custos para o operador.pdf      docs/pt/17-custos-operador.md
  deliverables/pt/ThingTracker · Casos de uso.pdf                docs/pt/18-casos-de-uso.md
  deliverables/pt/ThingTracker · Produto.pdf                     docs/pt/20-produto.md

The English figures are drawn first (each script's --lang en writes *.en.* files or charts-en/). Nothing Portuguese
is redrawn here: the Portuguese PDFs use the committed figures, and the Portuguese report keeps its own build.py.
Each step runs through video/tools/heavy.sh, one heavy job at a time, so run this script directly, not through heavy.sh
(its lock would wait for itself).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAVY = ROOT / "video" / "tools" / "heavy.sh"
PDF = "docs/business-case/build_pdf.py"
STEPS = [
    ["docs/architecture/build_diagram.py", "--lang", "en"],      # still copied by the submitted report's figuras.py
    ["docs/architecture/build_views.py", "--lang", "en"],        # the architecture views of docs/14 and docs/15
    ["deliverables/executive-summary/figuras.py", "--lang", "en"],
    ["deliverables/executive-summary/build.py", "--lang", "en"],
    ["docs/business-case/build_graficos.py", "--lang", "en"],
    [PDF, "--lang", "en"],
    *([PDF, "--doc", doc, *lang] for doc in ["architecture", "integration", "operator-costs", "use-cases", "product"]
      for lang in (["--lang", "en"], [])),
]

for script, *args in STEPS:
    print(f"$ python3 {script} {' '.join(args)}", flush=True)
    subprocess.run([str(HEAVY), sys.executable, str(ROOT / script), *args], check=True, cwd=ROOT / Path(script).parent)

for pdf in sorted((ROOT / "deliverables" / "english").glob("*.pdf")) + sorted((ROOT / "deliverables" / "pt").glob("*.pdf")):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = next((line.split()[1] for line in info.splitlines() if line.startswith("Pages")), "?")
    print(f"{pages:>3} pages  {pdf.relative_to(ROOT)}")
