#!/usr/bin/env python3
"""Lay out docs/pt/16-viabilidade-negocio.md as an A4 PDF: HTML in Lato, printed by headless Chrome.

    docs/business-case/viabilidade-negocio.pdf

Run build_graficos.py first; the PDF embeds the PNGs that the Markdown references (graficos/*.png).
The Markdown is read as it is: headings, paragraphs, lists, pipe tables, links, _italics_ and figures
(an image followed by its "Figura N – …" line). The document's own title is replaced by the header block
below. The four summary tiles restate figures from "Em resumo"; the build stops if a tile's value is not in
the text. Standard library only, plus Google Chrome.
    python3 docs/business-case/build_pdf.py

The same layout serves the other documents, in both languages (see DOCS below):
    python3 docs/business-case/build_pdf.py --lang en                       # docs/16-business-case.md
    python3 docs/business-case/build_pdf.py --doc architecture [--lang en]  # docs/pt/14-arquitetura.md, docs/14-architecture.md
    python3 docs/business-case/build_pdf.py --doc integration [--lang en]   # docs/pt/15-..., docs/15-integration-spec.md
    python3 docs/business-case/build_pdf.py --doc operator-costs [--lang en]  # docs/pt/17-custos-operador.md, docs/17-...
    python3 docs/business-case/build_pdf.py --doc use-cases [--lang en]     # docs/pt/18-casos-de-uso.md, docs/18-use-cases.md
    python3 docs/business-case/build_pdf.py --doc product [--lang en]       # docs/pt/20-produto.md, docs/20-product.md
English documents use English numbers (€1.74, 19,000, 1.2 %). For these documents the reader also takes fenced code
blocks, `code`, *italics*, nested bullets and "{width=…}" after an image; a link to a file in the repo is printed as
its text. --out writes the PDF elsewhere.
"""
import argparse
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
KPIS_EN = [(f"≈{NB}19,000", "19,000", f"MEO homes in the expected case, 1.2{NB}% of the base"),
           ("€3.99", "€3.99", "proposed monthly fee for the add-on, including VAT"),
           ("€1.74", "€1.74", "left per home a month, after VAT and costs"),
           ("€34.99", "€34.99", "entry price of a camera alarm plan in Portugal")]

PT_TEAM, EN_TEAM = "Equipa IT-Porto · novembro de 2026", "Team IT-Porto · November 2026"
ENGLISH, PORTUGUESE = ROOT / "deliverables" / "english", ROOT / "deliverables" / "pt"
# (document, language): source, PDF, title (HTML), header line, footer, summary tiles
DOCS = {
    ("business-case", "pt"): (DOC, OUT, TITLE, META, FOOTER, KPIS),
    ("business-case", "en"): (ROOT / "docs" / "16-business-case.md", ENGLISH / "ThingTracker - Business case (EN).pdf",
                              "ThingTracker – Business case", EN_TEAM, "Business case · Team IT-Porto", KPIS_EN),
    ("architecture", "pt"): (ROOT / "docs" / "pt" / "14-arquitetura.md", PORTUGUESE / "ThingTracker · Arquitetura.pdf",
                             "<em>ThingTracker</em> – Arquitetura", PT_TEAM, "Arquitetura · Equipa IT-Porto", None),
    ("architecture", "en"): (ROOT / "docs" / "14-architecture.md", ENGLISH / "ThingTracker - Architecture (EN).pdf",
                             "ThingTracker – Architecture", EN_TEAM, "Architecture · Team IT-Porto", None),
    ("integration", "pt"): (ROOT / "docs" / "pt" / "15-especificacao-integracao.md",
                            PORTUGUESE / "ThingTracker · Especificação de integração.pdf",
                            "<em>ThingTracker</em> – Especificação de integração", PT_TEAM,
                            "Especificação de integração · Equipa IT-Porto", None),
    ("integration", "en"): (ROOT / "docs" / "15-integration-spec.md", ENGLISH / "ThingTracker - Integration spec (EN).pdf",
                            "ThingTracker – Integration specification", EN_TEAM, "Integration specification · Team IT-Porto", None),
    # title None: the document's own first heading is the title (it says "at 500,000 homes", for instance)
    ("operator-costs", "pt"): (ROOT / "docs" / "pt" / "17-custos-operador.md", PORTUGUESE / "ThingTracker · Custos para o operador.pdf",
                               None, PT_TEAM, "Custos para o operador · Equipa IT-Porto", None),
    ("operator-costs", "en"): (ROOT / "docs" / "17-operator-costs.md", ENGLISH / "ThingTracker - Operator costs (EN).pdf",
                               None, EN_TEAM, "Operator costs · Team IT-Porto", None),
    ("use-cases", "pt"): (ROOT / "docs" / "pt" / "18-casos-de-uso.md", PORTUGUESE / "ThingTracker · Casos de uso.pdf",
                          None, PT_TEAM, "Casos de uso · Equipa IT-Porto", None),
    ("use-cases", "en"): (ROOT / "docs" / "18-use-cases.md", ENGLISH / "ThingTracker - Use cases (EN).pdf",
                          None, EN_TEAM, "Use cases · Team IT-Porto", None),
    ("product", "pt"): (ROOT / "docs" / "pt" / "20-produto.md", PORTUGUESE / "ThingTracker · Produto.pdf",
                        None, PT_TEAM, "Produto · Equipa IT-Porto", None),
    ("product", "en"): (ROOT / "docs" / "20-product.md", ENGLISH / "ThingTracker - Product (EN).pdf",
                        None, EN_TEAM, "Product · Team IT-Porto", None),
    # the pitch's documents (20 Nov): the run of show, the cheat sheet, the engineering questions, what is real in the films
    ("pitch", "pt"): (ROOT / "docs" / "pt" / "21-pitch.md", PORTUGUESE / "ThingTracker · Pitch.pdf",
                      None, PT_TEAM, "Pitch · Equipa IT-Porto", None),
    ("cheat-sheet", "pt"): (ROOT / "docs" / "pt" / "25-cola-pitch.md", PORTUGUESE / "ThingTracker · Cábula do pitch.pdf",
                            None, PT_TEAM, "Cábula do pitch · Equipa IT-Porto", None),
    ("questions", "pt"): (ROOT / "docs" / "pt" / "23-perguntas-engenharia.md", PORTUGUESE / "ThingTracker · Perguntas de engenharia.pdf",
                          None, PT_TEAM, "Perguntas de engenharia · Equipa IT-Porto", None),
    ("questions", "en"): (ROOT / "docs" / "23-engineering-qa.md", ENGLISH / "ThingTracker - Engineering Q&A (EN).pdf",
                          None, EN_TEAM, "Engineering Q&A · Team IT-Porto", None),
    ("what-is-real", "en"): (ROOT / "docs" / "24-what-is-real.md", ENGLISH / "ThingTracker - What is real (EN).pdf",
                             None, EN_TEAM, "What is real · Team IT-Porto", None),
}
EN = False          # set by --lang en in main()
KEEP_ROWS = 10      # a table of up to this many rows never splits across pages (6 for the documents other than the business case)
KEEP_LISTS = False  # True for the other documents: a list of up to 8 items stays on one page
NARROW_NUM = False  # operator costs, use cases, product: a column of short figures takes only the width it needs


# ---------------------------------------------------------------- Markdown subset
def parse(md):
    lines, blocks, i = md.splitlines(), [], 0
    starts = re.compile(r"(#{1,4} |!\[|\||- |\d+\. |```)")
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or re.fullmatch(r"-{3,}\s*", ln):     # blank line or a horizontal rule
            i += 1
        elif ln.startswith("```"):                                 # fenced code block, printed as it is
            code, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            blocks.append(("code", "\n".join(code)))
            i += 1
        elif m := re.match(r"(#{1,4}) (.*)", ln):
            blocks.append(("h", len(m.group(1)), m.group(2)))
            i += 1
        elif m := re.match(r"!\[([^\]]*)\]\(([^)]+)\)(?:\{[^}]*\})?\s*$", ln):
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
            first = int(re.match(r"\d+", ln).group()) if kind == "ol" else 1

            def is_item(line):
                return line.startswith("- ") if kind == "ul" else re.match(r"\d+\. ", line)

            while i < len(lines) and is_item(lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
                while i < len(lines) and re.match(r"\s{2,}\S", lines[i]):
                    items[-1] = items[-1] if isinstance(items[-1], tuple) else (items[-1], [])
                    if re.match(r"\s{2,}- ", lines[i]):              # nested bullets belong to the item above
                        items[-1][1].append(lines[i].strip()[2:])
                    else:                                             # an indented line continues the item (an answer
                        items[-1] = (*items[-1][:2], *items[-1][2:], lines[i].strip())   # under its question)
                    i += 1
                j = i                                                 # blank lines between two items: still one list
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j > i and j < len(lines) and is_item(lines[j]) and isinstance(items[-1], tuple) and len(items[-1]) > 2:
                    i = j
            blocks.append((kind, items, first))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not starts.match(lines[i]):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


def emphasis(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", s)      # *italics*
    return re.sub(r"(?<![\w])_(.+?)_(?![\w])", r"<em>\1</em>", s)


def keep_together(s):
    """No line break inside 19 000, 1,2 %, 3,99 €, 2 700 mil, n = 1 or [linhas R]."""
    if EN:                              # 1.2 %, 1,580 k, 0.81 GB, 557 ms, 15 W, n = 1, [R rows]
        s = re.sub(r"(?<=\d) (?=(?:%|k\b|M\b|GB\b|ms\b|s\b|h\b|W\b|fps\b|cm\b|USD\b|EUR\b|dB\b)(?!\w))", NB, s)
        s = re.sub(r"(?<=\S) = (?=\S)", f"{NB}={NB}", s)
        return s.replace("[R rows]", f"[R{NB}rows]")
    s = re.sub(r"(?<=\d) (?=\d{3}(?!\d))", NB, s)
    s = re.sub(r"(?<=\d) (?=(?:%|€|mil\b|milhões\b|USD\b|W\b))", NB, s)
    s = re.sub(r"(?<=\S) = (?=\S)", f"{NB}={NB}", s)
    return s.replace("[linhas R]", f"[linhas{NB}R]")


def inline(s):
    codes = []

    def code(m):                                                 # `code` first: it holds underscores and asterisks
        codes.append(m.group(1))
        return f"\x01{len(codes) - 1}\x01"

    s = re.sub(r"`([^`]+)`", code, s)
    s = keep_together(s)
    links = []

    def keep(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00{len(links) - 1}\x00"

    def link(m):
        text, url = links[int(m.group(1))]
        text = emphasis(html.escape(text, quote=False))
        if not re.match(r"https?://", url):                      # a file in the repo means nothing in a PDF: keep the words
            return text
        return '<a href="{}">{}</a>'.format(html.escape(url), text)

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", keep, s)          # links first: URLs hold underscores
    urls = []

    def bare(m):                                                 # a URL written out, as in a list of sources
        url, tail = m.group(0), ""
        while url and (url[-1] in ".,;:" or (url[-1] == ")" and url.count(")") > url.count("("))):
            url, tail = url[:-1], url[-1] + tail
        urls.append(url)
        return f"\x02{len(urls) - 1}\x02{tail}"

    s = re.sub(r"https?://[^\s<>\"]+", bare, s)
    s = emphasis(html.escape(s, quote=False))
    s = re.sub("\x00(\\d+)\x00", link, s)
    s = re.sub("\x02(\\d+)\x02", lambda m: '<a class="url" href="{0}">{0}</a>'.format(html.escape(urls[int(m.group(1))])), s)
    return re.sub("\x01(\\d+)\x01", lambda m: f"<code>{html.escape(codes[int(m.group(1))], quote=False)}</code>", s)


NUMERIC = re.compile(r"^[−+\-]?\d")
NUMERIC_EN = re.compile(r"^(?:\*\*)?[≈−+\-]?\s?[€$]?\d")      # €7.50, $0.003612, **1.74**, ≈ €0.12


def table(head, body):
    n = len(head)
    num_cols = set()
    for j in range(1, n):                      # a column of figures is right-aligned
        cells = [r[j] for r in body if j < len(r) and r[j]]
        figures = [c for c in cells if (NUMERIC_EN if EN else NUMERIC).match(c) and len(c) <= 40]
        if cells and len(figures) >= 0.5 * len(cells):
            num_cols.add(j)
    narrow = {j for j in num_cols if NARROW_NUM and all(len(r[j].replace("_", "")) <= 24 for r in body if j < len(r))}

    def cls(j, c=None):
        out = []
        if j in num_cols:
            out.append("num")
        if j in narrow:                                  # with a minimum width only when few: wider would overflow the page
            out.append("narrow" if len(narrow) > 4 else "narrow roomy")
        if c is not None and len(c.replace("_", "")) <= (24 if j in num_cols else 12):
            out.append("nowrap")                         # short cells stay on one line; headers may wrap
        return f' class="{" ".join(out)}"' if out else ""

    th = "".join(f"<th{cls(j)}>{inline(c)}</th>" for j, c in enumerate(head))
    trs = []
    for r in body:
        total = r[0].startswith("= ") or r[0].startswith("Custo de funcionamento") or (EN and "Running cost" in r[0])
        tds = "".join(f"<td{cls(j, c)}>{inline(c)}</td>" for j, c in enumerate(r))
        trs.append(f'<tr{" class=total" if total else ""}>{tds}</tr>')
    keep = ' class="keep"' if len(body) <= KEEP_ROWS else ""    # short tables never split across pages
    return f"<table{keep}><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>"


def kpis(text, tiles=KPIS):
    flat = text.replace(NB, " ")
    for _, needle, _ in tiles:
        if needle.replace(NB, " ") not in flat:
            sys.exit(f"summary tile value not in the text: {needle}")
    tiles = "".join(f'<div class="kpi"><div class="kpi-value">{html.escape(vv)}</div>'
                    f'<div class="kpi-label">{html.escape(lab)}</div></div>' for vv, _, lab in tiles)
    return f'<div class="kpis">{tiles}</div>'


def items_html(items):
    out = []
    for t in items:
        if isinstance(t, tuple):                                 # an item with nested bullets or continuation lines
            t, sub, *more = t
            out.append(f"<li>{inline(t)}" + (f'<div class="more">{inline(" ".join(more))}</div>' if more else "")
                       + ("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in sub) + "</ul>" if sub else "") + "</li>")
        else:
            out.append(f"<li>{inline(t)}</li>")
    return "".join(out)


def body_html(md, doc=DOC, tiles=KPIS):
    blocks, parts, i = parse(md), [], 0
    figure = "Figure" if EN else "Figura"
    while i < len(blocks):
        b = blocks[i]
        if b[0] == "h":
            level, text = b[1], b[2]
            if level == 1:                              # replaced by the header block
                i += 1
                continue
            cls = ' class="appendix"' if text.startswith(("Detalhes e fontes", "Details and sources")) else ""
            parts.append(f"<h{level}{cls}>{inline(text)}</h{level}>")
            if text in ("Em resumo", "In one minute") and tiles:
                parts.append(kpis(md, tiles))
        elif b[0] == "img":
            src = (doc.parent / b[2]).resolve()
            if not src.exists():
                sys.exit(f"missing figure {src}; run build_graficos.py (or the figure's own script) first")
            cap = ""
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if nxt and nxt[0] == "p" and (m := re.match(rf"(?:\*\*)?{figure} (\d+)(?:\*\*)? – (.*)", nxt[1])):
                cap = f"<figcaption><b>{figure} {m.group(1)}</b> – {inline(m.group(2))}</figcaption>"
                i += 1
            parts.append(f'<figure><div class="frame"><img src="{src.as_uri()}" alt="{html.escape(b[1])}"></div>{cap}</figure>')
        elif b[0] == "table":
            parts.append(table(b[1], b[2]))
        elif b[0] in ("ul", "ol"):
            keep = ' class="keep"' if KEEP_LISTS and len(b[1]) <= 8 else ""
            start = f' start="{b[2]}"' if b[0] == "ol" and b[2] != 1 else ""
            parts.append(f"<{b[0]}{keep}{start}>" + items_html(b[1]) + f"</{b[0]}>")
        elif b[0] == "code":
            parts.append(f"<pre><code>{html.escape(b[1], quote=False)}</code></pre>")
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
li > ul { margin: 2pt 0 0; }
ul.keep, ol.keep { break-inside: avoid; }
a.url { overflow-wrap: anywhere; }
.narrow { width: 1%%; }
.roomy { min-width: 6.2em; }
li .more { margin-top: 1.5pt; }
li:has(> .more) { break-inside: avoid; }
code { font: 0.86em Menlo, "SF Mono", Consolas, monospace; overflow-wrap: anywhere; }
pre { font-size: 7.6pt; line-height: 1.45; background: #F3F5F7; border-radius: 4pt; padding: 6pt 8pt; margin: 2pt 0 8pt;
      white-space: pre-wrap; break-inside: avoid; }
pre code { font-size: 1em; }
"""


def main():
    global EN, KEEP_ROWS, KEEP_LISTS, NARROW_NUM
    ap = argparse.ArgumentParser(description="Lay out a ThingTracker document as an A4 PDF.")
    ap.add_argument("--doc", choices=sorted({d for d, _ in DOCS}), default="business-case")
    ap.add_argument("--lang", choices=["pt", "en"], default="pt")
    ap.add_argument("--out", type=Path, help="PDF to write instead of the default")
    args = ap.parse_args()
    EN = args.lang == "en"
    if args.doc != "business-case":
        KEEP_ROWS, KEEP_LISTS = 6, True
    NARROW_NUM = args.doc in ("operator-costs", "use-cases", "product")
    doc, out, title, meta, footer, tiles = DOCS[(args.doc, args.lang)]
    out = args.out or out
    out.parent.mkdir(parents=True, exist_ok=True)
    md = doc.read_text(encoding="utf8")
    if title is None:                                            # the document's own first heading
        title = inline(re.search(r"^# (.+)$", md, re.M).group(1))
    plain = re.sub(r"<[^>]+>", "", title)
    page = (f'<!doctype html><html lang="{"en" if EN else "pt-PT"}"><meta charset="utf-8"><title>{plain}</title>'
            f"<style>{font_faces()}{CSS % {'footer': footer}}</style><body>"
            f'<header class="doc"><h1>{title}</h1><div class="meta">{meta}</div></header>'
            + body_html(md, doc, tiles) + "</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "viabilidade-negocio.html"
        src.write_text(page, encoding="utf8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        "--virtual-time-budget=5000", f"--print-to-pdf={out}", src.as_uri()], check=True, capture_output=True)
    print(f"built {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
