"""Render the team's documents as page images for the web app's document pages (web/docs.html).

    python3 prototype/build_doc_pages.py

Reads the PDFs and diagrams that the deliverables' build scripts produce, writes JPEG pages, a copy of each PDF and
web/docs/manifest.json into prototype/web/docs/ (generated, not committed). Needs pdftoppm (poppler).
"""
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "web" / "docs"

# document → language → (PDF, diagram shown first or None)
DOCS = {
    "architecture": {
        "title": {"pt": "Arquitetura", "en": "Architecture"},
        "pt": (ROOT / "deliverables/pt/ThingTracker · Arquitetura.pdf", ROOT / "docs/architecture/thingtracker-architecture.png"),
        "en": (ROOT / "deliverables/english/ThingTracker - Architecture (EN).pdf", ROOT / "docs/architecture/thingtracker-architecture.en.png"),
    },
    "business-case": {
        "title": {"pt": "Viabilidade do negócio", "en": "Business case"},
        "pt": (ROOT / "docs/business-case/viabilidade-negocio.pdf", None),
        "en": (ROOT / "deliverables/english/ThingTracker - Business case (EN).pdf", None),
    },
    "report": {
        "title": {"pt": "Relatório intermédio", "en": "Interim report"},
        "pt": (ROOT / "deliverables/executive-summary/sumario-executivo-IT-Porto.pdf", None),
        "en": (ROOT / "deliverables/english/ThingTracker - Report (EN).pdf", None),
    },
}


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    manifest = {}
    for key, doc in DOCS.items():
        manifest[key] = {"title": doc["title"]}
        for lang in ("pt", "en"):
            pdf, lead = doc[lang]
            if not pdf.exists():
                print(f"missing, skipped: {pdf}")
                continue
            stem = f"{key}-{lang}"
            shutil.copyfile(pdf, OUT / f"{stem}.pdf")
            subprocess.run(["pdftoppm", "-r", "150", "-jpeg", "-jpegopt", "quality=86", str(pdf), str(OUT / stem)], check=True)
            pages = sorted(p.name for p in OUT.glob(f"{stem}-*.jpg"))
            entry = {"pdf": f"{stem}.pdf", "pages": pages}
            if lead and lead.exists():
                shutil.copyfile(lead, OUT / f"{stem}-diagram.png")
                entry["lead"] = f"{stem}-diagram.png"
            manifest[key][lang] = entry
            print(f"{stem}: {len(pages)} pages")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
