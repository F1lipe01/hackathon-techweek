#!/usr/bin/env python3
"""Lay out docs/pt/16-viabilidade-negocio.md as an A4 PDF: HTML in Lato, printed by headless Chrome.

    docs/business-case/viabilidade-negocio.pdf

Run build_graficos.py first; the PDF embeds the PNGs that the Markdown references (graficos/*.png).
The Markdown is read as it is: headings, paragraphs, lists, pipe tables, links, _italics_ and figures
(an image followed by its "Figura N – …" line). The document's own title is replaced by the header block
below. The four summary tiles restate figures from "Em resumo"; the build stops if a tile's value is not in
the text. Standard library only, plus Google Chrome.
    python3 docs/business-case/build_pdf.py
"""
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOC = ROOT / "docs" / "pt" / "16-viabilidade-negocio.md"
FONTS = ROOT / "deliverables" / "executive-summary" / ".fonts"
OUT = HERE / "viabilidade-negocio.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NB = " "

TITLE = "<em>ThingTracker</em> – Viabilidade do negócio"
META = "Equipa IT-Porto · novembro de 2026"
FOOTER = "Viabilidade do negócio · Equipa IT-Porto"
# value, label; each value must appear in the text (checked below)
KPIS = [(f"≈{NB}19{NB}000", "19 000 casas", f"casas MEO no cenário esperado, 1,2{NB}% da base"),
        (f"3,99{NB}€", "3,99 €", "mensalidade proposta para o serviço adicional, com IVA"),
        (f"1,74{NB}€", "1,74 €", "restam por casa e por mês, depois do IVA e dos custos"),
        (f"34,99{NB}€", "34,99 €", "preço de entrada de um plano de alarme com câmara em Portugal")]


# ---------------------------------------------------------------- Markdown subset
def parse(md):
    lines, blocks, i = md.splitlines(), [], 0
    starts = re.compile(r"(#{1,4} |!\[|\||- |\d+\. )")
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif m := re.match(r"(#{1,4}) (.*)", ln):
            blocks.append(("h", len(m.group(1)), m.group(2)))
            i += 1
        elif m := re.match(r"!\[([^\]]*)\]\(([^)]+)\)\s*$", ln):
            blocks.append(("img", m.group(1), m.group(2)))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append(("table", rows[0], rows[2:]))
        elif ln.startswith("- ") or re.match(r"\d+\. ", ln):
            kind, items = ("ul" if ln.startswith("- ") else "ol"), []
            while i < len(lines) and (lines[i].startswith("- ") if kind == "ul" else re.match(r"\d+\. ", lines[i])):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            blocks.append((kind, items))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not starts.match(lines[i]):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


def emphasis(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![\w])_(.+?)_(?![\w])", r"<em>\1</em>", s)


def keep_together(s):
    """No line break inside 19 000, 1,2 %, 3,99 €, 2 700 mil, n = 1 or [linhas R]."""
    s = re.sub(r"(?<=\d) (?=\d{3}(?!\d))", NB, s)
    s = re.sub(r"(?<=\d) (?=(?:%|€|mil\b|milhões\b|USD\b|W\b))", NB, s)
    s = re.sub(r"(?<=\S) = (?=\S)", f"{NB}={NB}", s)
    return s.replace("[linhas R]", f"[linhas{NB}R]")


def inline(s):
    s = keep_together(s)
    links = []

    def keep(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00{len(links) - 1}\x00"

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", keep, s)          # links first: URLs hold underscores
    s = emphasis(html.escape(s, quote=False))
    return re.sub("\x00(\\d+)\x00", lambda m: '<a href="{}">{}</a>'.format(
        html.escape(links[int(m.group(1))][1]), emphasis(html.escape(links[int(m.group(1))][0], quote=False))), s)


NUMERIC = re.compile(r"^[−+\-]?\d")


def table(head, body):
    n = len(head)
    num_cols = set()
    for j in range(1, n):                      # a column of figures is right-aligned
        cells = [r[j] for r in body if j < len(r) and r[j]]
        figures = [c for c in cells if NUMERIC.match(c) and len(c) <= 40]
        if cells and len(figures) >= 0.5 * len(cells):
            num_cols.add(j)

    def cls(j, c=None):
        out = []
        if j in num_cols:
            out.append("num")
        if c is not None and len(c.replace("_", "")) <= (24 if j in num_cols else 12):
            out.append("nowrap")                         # short cells stay on one line; headers may wrap
        return f' class="{" ".join(out)}"' if out else ""

    th = "".join(f"<th{cls(j)}>{inline(c)}</th>" for j, c in enumerate(head))
    trs = []
    for r in body:
        total = r[0].startswith("= ") or r[0].startswith("Custo de funcionamento")
        tds = "".join(f"<td{cls(j, c)}>{inline(c)}</td>" for j, c in enumerate(r))
        trs.append(f'<tr{" class=total" if total else ""}>{tds}</tr>')
    keep = ' class="keep"' if len(body) <= 10 else ""    # tables of up to 10 rows never split across pages
    return f"<table{keep}><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>"


def kpis(text):
    flat = text.replace(NB, " ")
    for _, needle, _ in KPIS:
        if needle.replace(NB, " ") not in flat:
            sys.exit(f"summary tile value not in the text: {needle}")
    tiles = "".join(f'<div class="kpi"><div class="kpi-value">{html.escape(vv)}</div>'
                    f'<div class="kpi-label">{html.escape(lab)}</div></div>' for vv, _, lab in KPIS)
    return f'<div class="kpis">{tiles}</div>'


def body_html(md):
    blocks, parts, i = parse(md), [], 0
    while i < len(blocks):
        b = blocks[i]
        if b[0] == "h":
            level, text = b[1], b[2]
            if level == 1:                              # replaced by the header block
                i += 1
                continue
            cls = ' class="appendix"' if text.startswith("Detalhes e fontes") else ""
            parts.append(f"<h{level}{cls}>{inline(text)}</h{level}>")
            if text == "Em resumo":
                parts.append(kpis(md))
        elif b[0] == "img":
            src = (DOC.parent / b[2]).resolve()
            if not src.exists():
                sys.exit(f"missing figure {src}; run build_graficos.py first")
            cap = ""
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if nxt and nxt[0] == "p" and (m := re.match(r"Figura (\d+) – (.*)", nxt[1])):
                cap = f"<figcaption><b>Figura {m.group(1)}</b> – {inline(m.group(2))}</figcaption>"
                i += 1
            parts.append(f'<figure><div class="frame"><img src="{src.as_uri()}" alt="{html.escape(b[1])}"></div>{cap}</figure>')
        elif b[0] == "table":
            parts.append(table(b[1], b[2]))
        elif b[0] in ("ul", "ol"):
            parts.append(f"<{b[0]}>" + "".join(f"<li>{inline(t)}</li>" for t in b[1]) + f"</{b[0]}>")
        else:
            lead = ' class="lead"' if not parts else ""     # the paragraph right under the title
            parts.append(f"<p{lead}>{inline(b[1])}</p>")
        i += 1
    return "\n".join(parts)


def font_faces():
    faces = [("normal", 400, "regular"), ("normal", 700, "bold"), ("italic", 400, "italic"), ("italic", 700, "boldItalic")]
    return "\n".join(f"@font-face{{font-family:Lato;font-style:{s};font-weight:{wt};src:url('{(FONTS / f'Lato-{n}.ttf').as_uri()}')}}"
                     for s, wt, n in faces)


CSS = """
@page { size: A4; margin: 16mm 20mm 19mm 20mm;
  @bottom-left { content: "%(footer)s"; font: 7.5pt Lato, sans-serif; color: #6B7480; vertical-align: top; padding-top: 7mm; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt Lato, sans-serif; color: #6B7480;
                  vertical-align: top; padding-top: 7mm; } }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 9.6pt/1.47 Lato, "Helvetica Neue", Arial, sans-serif; color: #1F2328; }
header.doc { border-bottom: 0.75pt solid #D5DBE0; padding-bottom: 9pt; margin-bottom: 12pt; }
header.doc h1 { font-size: 22pt; line-height: 1.15; margin: 0 0 4pt; letter-spacing: -0.01em; }
header.doc .meta { font-size: 10.5pt; color: #56606C; }
h2 { font-size: 13.5pt; line-height: 1.25; margin: 16pt 0 6pt; break-after: avoid; }
h3 { font-size: 11pt; line-height: 1.3; margin: 14pt 0 5pt; break-after: avoid; }
h4 { font-size: 9.8pt; line-height: 1.3; margin: 10pt 0 4pt; color: #56606C; break-after: avoid; }
h2.appendix { break-before: page; margin-top: 0; }
p { margin: 0 0 6pt; orphans: 3; widows: 3; }
p.lead { color: #56606C; }
ul, ol { margin: 0 0 7pt; padding-left: 15pt; }
li { margin: 0 0 3pt; padding-left: 2pt; }
a { color: #0067A8; text-decoration: none; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 2pt 0 10pt; break-inside: avoid; }
.kpi { background: #F3F5F7; border-radius: 4pt; padding: 8pt 9pt 8pt; }
.kpi-value { font-size: 17pt; font-weight: 700; line-height: 1.15; margin-bottom: 3pt; }
.kpi-label { font-size: 8pt; line-height: 1.3; color: #56606C; }
figure { margin: 6pt 0 10pt; break-inside: avoid; }
figure .frame { border: 0.6pt solid #D5DBE0; border-radius: 4pt; overflow: hidden; }
figure img { width: 100%%; display: block; }
figcaption { font-size: 8.5pt; line-height: 1.35; color: #56606C; margin-top: 5pt; }
figcaption b { color: #1F2328; }
table { border-collapse: collapse; width: 100%%; margin: 4pt 0 10pt; font-size: 8.3pt; line-height: 1.33; }
table.keep { break-inside: avoid; }
p:has(+ table.keep) { break-after: avoid; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #EEF1F4; font-weight: 700; text-align: left; vertical-align: bottom;
     border-top: 0.75pt solid #AEB6C0; border-bottom: 0.75pt solid #AEB6C0; }
th, td { padding: 3pt 5pt; }
td { vertical-align: top; border-bottom: 0.5pt solid #DDE2E7; }
.num { text-align: right; }
.nowrap { white-space: nowrap; }
tr.total td { border-top: 0.75pt solid #8B95A1; }
tbody tr:last-child td { border-bottom: 0.75pt solid #AEB6C0; }
"""


def main():
    md = DOC.read_text(encoding="utf8")
    page = (f'<!doctype html><html lang="pt-PT"><meta charset="utf-8"><title>ThingTracker – Viabilidade do negócio</title>'
            f"<style>{font_faces()}{CSS % {'footer': FOOTER}}</style><body>"
            f'<header class="doc"><h1>{TITLE}</h1><div class="meta">{META}</div></header>'
            + body_html(md) + "</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "viabilidade-negocio.html"
        src.write_text(page, encoding="utf8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        "--virtual-time-budget=5000", f"--print-to-pdf={OUT}", src.as_uri()], check=True, capture_output=True)
    print(f"built {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
