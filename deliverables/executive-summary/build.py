#!/usr/bin/env python3
"""Build the Sumário Executivo from sumario-executivo.md.

Outputs, next to this script:
  <figure>.png                     each [[figura: name]] in the source, rendered from <name>.svg
  sumario-executivo-IT-Porto.docx  the official template, filled in (for edits in Word / Google Docs)
  sumario-executivo-IT-Porto.pdf   the file to submit (HTML replica of the template, printed by Chrome)

Standard library only, plus Google Chrome. Run:  python3 build.py
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "sumario-executivo-template.docx"
SOURCE = HERE / "sumario-executivo.md"
OUT = "sumario-executivo-IT-Porto"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

GREEN, GREY = "4bd26c", "666666"
FIG_W_CM = 15.9  # text width of the template is 15.93 cm
FIG_ALT = {"figura-exemplo": "Exemplo do ThingTracker: uma frase, a câmara vê, a casa lembra, a casa age",
           "figura-arquitetura": "Como funciona o ThingTracker: em casa, na plataforma Altice e no modelo de linguagem",
           "arquitetura": "Arquitetura do ThingTracker: em casa, na plataforma Altice e no modelo de linguagem",
           "fluxo": "Fluxo do ThingTracker: ver, filtrar, perceber, lembrar, agir"}


# ---------- source parsing ----------

def parse(md):
    meta, blocks = {}, []
    lines = md.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
        k, v = lines[i].split(":", 1)
        meta[k.strip()] = v.strip()
        i += 1
    para = []

    def flush():
        if para:
            text = " ".join(para)
            kind = "sources" if text.startswith("Fontes:") else "p"
            blocks.append((kind, text))
            para.clear()

    for line in lines[i:]:
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("## "):
            flush()
            blocks.append(("h", s[3:]))
        elif s.startswith("- "):
            flush()
            blocks.append(("li", s[2:]))
        elif s.startswith("[[figura:"):
            flush()
            name, _, caption = s[len("[[figura:"):-2].partition("|")
            blocks.append(("fig", name.strip().removesuffix(".png").removesuffix(".svg")))
            if caption.strip():
                blocks.append(("caption", caption.strip()))
        else:
            para.append(s)
    flush()
    return meta, blocks


def runs(text):
    """Split **bold**, `code` and _italic_ (loanwords) into (text, bold, code, italic) runs.
    Italic may sit inside bold: **Modelos _open-source_, em casa.**"""
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("`"):
            out.append((part[1:-1], False, True, False))
            continue
        bold = part.startswith("**")
        inner = part[2:-2] if bold else part
        for piece in re.split(r"(?<![\w])(_[^_]+_)(?![\w])", inner):
            if piece:
                italic = piece.startswith("_") and piece.endswith("_") and len(piece) > 2
                out.append((piece[1:-1] if italic else piece, bold, False, italic))
    return out


# ---------- figure ----------

def font_faces(fontdir):
    faces = []
    for style, weight, name in [("normal", 400, "regular"), ("normal", 700, "bold"),
                                ("italic", 400, "italic"), ("italic", 700, "boldItalic")]:
        faces.append(f"@font-face{{font-family:Lato;font-style:{style};font-weight:{weight};"
                     f"src:url('file://{fontdir}/Lato-{name}.ttf')}}")
    return "\n".join(faces)


def fig_size(name):
    svg = (HERE / f"{name}.svg").read_text(encoding="utf8")
    w, h = (int(float(v)) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
    return w, h


def render_figure(tmp, fontdir, name):
    """Render <name>.svg to <name>.png at 3x, with the template's Lato."""
    svg = (HERE / f"{name}.svg").read_text(encoding="utf8")
    w, h = fig_size(name)
    page = tmp / f"{name}.html"
    page.write_text(f"<!doctype html><meta charset=utf-8><style>{font_faces(fontdir)}"
                    "html,body{margin:0;background:#fff}svg{display:block}</style>" + svg,
                    encoding="utf8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=3", f"--window-size={w},{h}",
                    "--virtual-time-budget=2000", f"--screenshot={HERE / (name + '.png')}",
                    page.as_uri()], check=True, capture_output=True)


# ---------- docx ----------

def x(s):
    return html.escape(s, quote=False)


def w_run(text, bold=False, code=False, size=21, color=None, font=None, italic=False):
    rpr = ""
    face = "Courier New" if code else font
    if face:
        rpr += f'<w:rFonts w:ascii="{face}" w:cs="{face}" w:eastAsia="{face}" w:hAnsi="{face}"/>'
    if bold:
        rpr += '<w:b w:val="1"/><w:bCs w:val="1"/>'
    if italic:
        rpr += '<w:i w:val="1"/><w:iCs w:val="1"/>'
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    sz = size - 2 if code else size
    rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:lang w:val="pt-PT"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{x(text)}</w:t></w:r>'


def w_par(text, ppr="", all_bold=False, **kw):
    return f"<w:p><w:pPr>{ppr}</w:pPr>" + "".join(
        w_run(t, b or all_bold, c, italic=i, **kw) for t, b, c, i in runs(text)) + "</w:p>"


BODY_SPACING = '<w:spacing w:before="0" w:after="100" w:line="264" w:lineRule="auto"/>'


def w_blocks(blocks, fig_rids):
    out, fig_no = [], [0]
    for kind, text in blocks:
        if kind == "h":
            out.append(w_par(text, '<w:keepNext/><w:spacing w:before="200" w:after="80" w:line="276" w:lineRule="auto"/>',
                             all_bold=True, size=28, color=GREEN, font="Lato"))
        elif kind == "p":
            out.append(w_par(text, BODY_SPACING))
        elif kind == "li":
            ppr = ('<w:tabs><w:tab w:val="left" w:pos="284"/></w:tabs>'
                   '<w:spacing w:before="0" w:after="60" w:line="264" w:lineRule="auto"/>'
                   '<w:ind w:left="284" w:hanging="284"/>')
            out.append(w_par("•\t" + text, ppr).replace(
                f'<w:t xml:space="preserve">•\t', '<w:t xml:space="preserve">•</w:t><w:tab/><w:t xml:space="preserve">', 1))
        elif kind == "sources":
            out.append(w_par(text, '<w:spacing w:before="120" w:after="0" w:line="240" w:lineRule="auto"/>',
                             size=15, color=GREY))
        elif kind == "caption":
            fig_no[0] += 1
            out.append(w_par(f"**Figura {fig_no[0]}** – {text}",
                             '<w:spacing w:before="0" w:after="140" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>',
                             size=17, color=GREY))
        elif kind == "fig":
            n = list(fig_rids).index(text)
            fig_rid, (fw, fh) = fig_rids[text], fig_size(text)
            cx = int(FIG_W_CM * 360000)
            cy = int(cx * fh / fw)
            out.append(
                '<w:p><w:pPr><w:keepNext/><w:spacing w:before="60" w:after="120"/><w:jc w:val="center"/></w:pPr>'
                '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
                f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
                f'<wp:docPr id="{101 + n}" name="{text}" descr="{x(FIG_ALT.get(text, text))}"/>'
                '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
                '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{101 + n}" name="{text}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
                f'<pic:blipFill><a:blip r:embed="{fig_rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
                '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
    return "".join(out)


def build_docx(tmp, meta, blocks):
    src = tmp / "docx"
    doc_path = src / "word" / "document.xml"
    doc = doc_path.read_text(encoding="utf8")

    head, body_start = doc.split("<w:body>", 1)
    sect = re.search(r"<w:sectPr>.*?</w:sectPr>", body_start, re.S).group(0)
    paras = re.findall(r"<w:p[ >].*?</w:p>", body_start.split("<w:tbl>", 1)[0], re.S)
    t1 = next(p for p in paras if "NOME DA EQUIPA" in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
    t2 = next(p for p in paras if "Sumário Executivo" in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))

    def retitle(p, text):
        first = re.search(r"<w:r [^>]*>\s*<w:rPr>.*?</w:rPr>", p, re.S).group(0)
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S).group(0)
        return f"<w:p>{ppr}{first}<w:t xml:space=\"preserve\">{x(text)}</w:t></w:r></w:p>"

    rels_path = src / "word" / "_rels" / "document.xml.rels"
    rels = rels_path.read_text(encoding="utf8")
    rids = {}
    for n, name in enumerate(t for k, t in blocks if k == "fig"):
        rids[name] = f"rIdFig{n + 1}"
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="{rids[name]}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}.png"/></Relationships>')
        shutil.copy(HERE / f"{name}.png", src / "word" / "media" / f"{name}.png")
    rels_path.write_text(rels, encoding="utf8")

    body = (retitle(t1, f"Equipa {meta['equipa']}")
            + retitle(t2, f"Desafio {meta['desafio']} - Sumário Executivo")
            + '<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:p>'
            + w_blocks(blocks, rids) + sect)
    doc_path.write_text(f"{head}<w:body>{body}</w:body></w:document>", encoding="utf8")

    # well-formedness check before zipping
    import xml.dom.minidom
    xml.dom.minidom.parseString(doc_path.read_bytes())

    out = HERE / f"{OUT}.docx"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(src / "[Content_Types].xml", "[Content_Types].xml")
        for f in sorted(src.rglob("*")):
            rel = f.relative_to(src).as_posix()
            if f.is_file() and rel != "[Content_Types].xml":
                z.write(f, rel)
    return out


# ---------- pdf (HTML replica of the template) ----------

def inline_html(text):
    out = []
    for t, b, c, i in runs(text):
        t = x(t)
        if c:
            t = f"<code>{t}</code>"
        if i:
            t = f"<i>{t}</i>"
        out.append(f"<b>{t}</b>" if b else t)
    return "".join(out)


def build_pdf(tmp, meta, blocks, fontdir):
    import base64
    logo = base64.b64encode((tmp / "docx/word/media/image1.png").read_bytes()).decode()
    # header image at the template's size (5.31 x 1.31 cm), as SVG so it stays sharp
    (tmp / "header.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="5.31cm" height="1.31cm" viewBox="0 0 312 77">'
        f'<image width="312" height="77" xlink:href="data:image/png;base64,{logo}"/></svg>', encoding="utf8")
    # the template's header text, right-aligned beside the logo (GalanoGrotesque is not embedded; Arial, as Google Docs shows)
    (tmp / "header-right.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="8cm" height="1.0cm" viewBox="0 0 302 38" '
        'font-family="Arial, Helvetica, sans-serif" text-anchor="end">'
        '<text x="302" y="16" font-size="14.67" font-weight="700" fill="#000">AVEIRO TECH CITY - HACKATHON</text>'
        '<text x="302" y="33" font-size="13.33" fill="#7f7f7f">Sumário Executivo – 2026</text></svg>', encoding="utf8")
    (tmp / "footer.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="9cm" height="0.9cm" viewBox="0 0 340 34" font-family="Arial, Helvetica, sans-serif" font-size="10.7" fill="#7f7f7f">'
        '<text x="0" y="12" font-weight="700">AVEIRO TECH CITY</text>'
        '<text x="0" y="28"><tspan font-weight="700">Aveiro Tech City Hackathon </tspan>– 4ª Edição</text></svg>',
        encoding="utf8")

    parts, items, n_fig = [], [], 0

    def close_list():
        if items:
            parts.append("<ul>" + "".join(items) + "</ul>")
            items.clear()

    for kind, text in blocks:
        if kind != "li":
            close_list()
        if kind == "h":
            parts.append(f"<h2>{x(text)}</h2>")
        elif kind == "p":
            parts.append(f"<p>{inline_html(text)}</p>")
        elif kind == "li":
            items.append(f"<li>{inline_html(text)}</li>")
        elif kind == "sources":
            parts.append(f'<p class="sources">{inline_html(text)}</p>')
        elif kind == "caption":
            n_fig += 1
            parts.append(f'<p class="caption"><b>Figura {n_fig}</b> – {inline_html(text)}</p>')
        elif kind == "fig":
            parts.append(f'<figure><img src="{(HERE / (text + ".png")).as_uri()}" alt="{x(FIG_ALT.get(text, text))}"></figure>')
    close_list()

    css = font_faces(fontdir) + """
@page { size: A4; margin: 2.54cm;
  @top-left { content: url(header.svg); vertical-align: bottom; padding-bottom: 0.05cm; }
  @top-right { content: url(header-right.svg); vertical-align: bottom; padding-bottom: 0.05cm; }
  @bottom-left { content: url(footer.svg); vertical-align: top; padding-top: 0.45cm; }
  @bottom-right { content: counter(page); vertical-align: top; padding-top: 1.0cm;
                  font: 8pt Calibri, Carlito, Arial, sans-serif; color: #7f7f7f; } }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.5pt/1.265 Arial, Helvetica, sans-serif; color: #000; }
.t1 { font: 700 18pt/1.3 Lato, sans-serif; color: #4bd26c; text-align: center; }
.t2 { font: 700 15pt/1.3 Lato, sans-serif; color: #666; text-align: center; margin: 2pt 0 8pt; }
h2 { font: 700 14pt/1.3 Lato, sans-serif; color: #4bd26c; margin: 10pt 0 4pt; break-after: avoid; }
p { margin: 0 0 5pt; }
ul { margin: 0 0 5pt; padding-left: 0.5cm; }
li { margin: 0 0 3pt; padding-left: 0; }
li::marker { content: "•  "; }
code { font: 9.5pt 'Courier New', monospace; }
figure { margin: 3pt 0 6pt; break-inside: avoid; }
figure img { width: 100%; display: block; }
.sources { font-size: 7.5pt; line-height: 1.25; color: #666; margin-top: 6pt; }
.caption { font-size: 8.5pt; line-height: 1.25; color: #555; text-align: center; margin: -3pt 0 7pt; }
"""
    page = (f'<!doctype html><html lang="pt-PT"><meta charset="utf-8"><title>{OUT}</title><style>{css}</style><body>'
            f'<div class="t1">Equipa {x(meta["equipa"])}</div>'
            f'<div class="t2">Desafio {x(meta["desafio"])} - Sumário Executivo</div>'
            + "".join(parts) + "</body></html>")
    src = tmp / "page.html"
    src.write_text(page, encoding="utf8")
    out = HERE / f"{OUT}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=3000", f"--print-to-pdf={out}", src.as_uri()],
                   check=True, capture_output=True)
    return out


def main():
    meta, blocks = parse(SOURCE.read_text(encoding="utf8"))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        with zipfile.ZipFile(TEMPLATE) as z:
            z.extractall(tmp / "docx")
        fontdir = tmp / "docx" / "word" / "fonts"
        for name in dict.fromkeys(t for k, t in blocks if k == "fig"):
            render_figure(tmp, fontdir, name)
        docx = build_docx(tmp, meta, blocks)
        pdf = build_pdf(tmp, meta, blocks, fontdir)
    words = sum(len(re.sub(r"[*`_]", "", t).split()) for k, t in blocks if k not in ("fig", "caption"))
    print(f"built {docx}\nbuilt {pdf}\nwords: {words}")


if __name__ == "__main__":
    sys.exit(main())
