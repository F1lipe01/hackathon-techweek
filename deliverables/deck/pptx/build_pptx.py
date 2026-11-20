"""The pitch as PowerPoint, on the organisers' template (Aveiro Tech City Hackathon).

    python build_pptx.py guide TEMPLATE.pptx OUT.pptx     # the frame, with every zone outlined, for approval

TEMPLATE.pptx is the organisers' file (kept out of the repo). This file holds the frame every slide follows:
the template's marks made smaller and fixed in place, and one grid. The slides themselves come next, from the
asset library in ../assets/, once the frame is approved.

The frame (inches, slide 10 x 5.625):
- header mark on content slides: 60 % of the template's size, top left at (0.45, 0.28); the cover keeps its big one;
- partner logos: 60 % of the template's size, the visible logos centred, their bottom 0.30 above the slide's bottom;
- title: box (0.45, 0.80, 9.10, 0.55), one line, Arial Bold 26 pt, left; white on black, 1E1D1A on white;
  the green pixel square is the marker, at a fixed offset inside the box;
- content zone: x 0.45 to 9.55, y 1.50 to 4.85; with no title, y 0.80 to 4.85;
- captions: Arial 11 to 12 pt, muted, 0.08 under what they caption; 0.25 between content blocks.
The template's layouts stay: 0 = cover, 1 = black frame, 9 = white frame. Its own six slides are removed.
"""
import html
import io
import re
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = HERE.parent / "source" / "slides"
ASSETS = HERE.parent / "assets"

# ---------- the frame ----------

SLIDE_W, SLIDE_H = 10.0, 5.625
MARK_SCALE = 0.60                      # header mark and logos: 40 % smaller than the template's
MARK_X, MARK_Y = 0.45, 0.28
LOGOS_BOTTOM_GAP = 0.30                # the visible logos end 0.30" above the slide's bottom
TITLE = (0.45, 0.80, 9.10, 0.55)       # x, y, w, h
TITLE_INSET = 0.25                     # the text starts after the pixel marker
MARKER = 0.13                          # the pixel square, left of the title text
CONTENT_X0, CONTENT_X1 = 0.45, 9.55
CONTENT_Y0, CONTENT_Y0_NO_TITLE, CONTENT_Y1 = 1.50, 0.80, 4.85
CAPTION_GAP = 0.08
GAP = 0.25

L_COVER, L_BLACK, L_WHITE = 0, 1, 9

NEON = RGBColor(0x00, 0xFC, 0x75)      # the template's HACKATHON green
GREEN_D = RGBColor(0x00, 0x78, 0x00)   # the template's dark pixel green, for marks on white
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1E, 0x1D, 0x1A)       # titles on white
MUTED_D = RGBColor(0x9A, 0xA0, 0xA6)   # captions on black
MUTED_W = RGBColor(0x5F, 0x63, 0x68)   # captions on white
FONT = "Arial"

# the template's pictures, recognised by their original box (EMU); the visible part of the logos picture
TPL_MARK = (299287, 342667, 2330789)                   # left, top, width of the small header mark
TPL_LOGOS_TOPS = (4335975, 4344975)
LOGOS_INK = (38 / 1536, 46 / 149, 1316 / 1536, 109 / 149)  # visible logos inside the picture: x0, y0, x1, y1
LOGOS_W = int(8226374 * MARK_SCALE)                    # one size on every layout


def _near(a, b, tol=6000):
    return abs(int(a) - int(b)) <= tol


def logos_box():
    """Where the logos picture goes (inches): the visible logos centred, their bottom LOGOS_BOTTOM_GAP above the edge."""
    w = LOGOS_W / 914400
    h = w * 798000 / 8226374
    ink_cx = (LOGOS_INK[0] + LOGOS_INK[2]) / 2
    x = SLIDE_W / 2 - ink_cx * w
    y = SLIDE_H - LOGOS_BOTTOM_GAP - LOGOS_INK[3] * h
    return x, y, w, h


def mark_box():
    w = TPL_MARK[2] * MARK_SCALE / 914400
    return MARK_X, MARK_Y, w, w * 491820 / 2330789


def apply_frame(prs):
    """Resize and place the template's header mark and logos on every layout, keeping each picture's aspect."""
    lx, ly, lw, _ = logos_box()
    for layout in prs.slide_layouts:
        for sh in layout.shapes:
            if sh.shape_type != MSO_SHAPE_TYPE.PICTURE:
                continue
            ratio = sh.height / sh.width
            if _near(sh.left, TPL_MARK[0]) and _near(sh.top, TPL_MARK[1]) and _near(sh.width, TPL_MARK[2]):
                w = int(sh.width * MARK_SCALE)
                sh.left, sh.top, sh.width, sh.height = Inches(MARK_X), Inches(MARK_Y), w, int(w * ratio)
            elif any(_near(sh.top, t) for t in TPL_LOGOS_TOPS) and sh.width > Inches(7):
                sh.width, sh.height = LOGOS_W, int(LOGOS_W * ratio)
                sh.left, sh.top = Inches(lx), Inches(ly)


def drop_template_slides(prs):
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        prs.part.drop_rel(sid.get(qn("r:id")))
        lst.remove(sid)


def open_template(path):
    prs = Presentation(path)
    drop_template_slides(prs)
    apply_frame(prs)
    return prs


# ---------- helpers ----------

def runs_of(t):
    """'a _kit_ b' -> [('a ', False), ('kit', True), (' b', False)]: underscores mark English terms, set in italics."""
    out = []
    for p in re.split(r"(_[^_]+_)", t):
        if p:
            out.append((p[1:-1], True) if p.startswith("_") and p.endswith("_") else (p, False))
    return out


def text(slide, x, y, w, h, paras, size=12, color=WHITE, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         font=FONT, wrap=True, inset_left=0.0, name=None):
    """paras: a string, or a list of strings / (string, {size, color, bold, italic, font}) tuples, one per paragraph."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = Inches(inset_left)
    tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate([paras] if isinstance(paras, str) else paras):
        opts = {}
        if isinstance(para, tuple):
            para, opts = para
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, it in runs_of(para):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = opts.get("font", font)
            f.size = Pt(opts.get("size", size))
            f.bold = opts.get("bold", bold)
            f.italic = it or opts.get("italic", False)
            f.color.rgb = opts.get("color", color)
    return tb


def box(slide, x, y, w, h, fill=None, line=None, line_w=1.0, dash=False, shape=MSO_SHAPE.RECTANGLE, name=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
        if dash:
            s.line.dash_style = 4
    style = s._element.find(qn("p:style"))  # no theme effects (they add a shadow)
    if style is not None:
        s._element.remove(style)
    return s


def picture(slide, path, x, y, w=None, h=None, fit=None, alt=None, name=None):
    """fit=(w, h): scale to fit inside the box, centred (contain)."""
    if fit:
        with Image.open(path) as im:
            iw, ih = im.size
        bw, bh = fit
        k = min(bw / iw, bh / ih)
        w, h = iw * k, ih * k
        x, y = x + (bw - w) / 2, y + (bh - h) / 2
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if alt:
        pic._element.nvPicPr.cNvPr.set("descr", alt)
    if name:
        pic.name = name
    return pic


def new_slide(prs, layout):
    s = prs.slides.add_slide(prs.slide_layouts[layout])
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def title(slide, words, dark=True):
    """The one title position: the pixel marker, then one line of Arial Bold 26 pt."""
    x, y, w, h = TITLE
    box(slide, x, y + (h - MARKER) / 2, MARKER, MARKER, fill=NEON if dark else GREEN_D, name="Title marker")
    return text(slide, x, y, w, h, words, size=26, bold=True, color=WHITE if dark else INK, anchor=MSO_ANCHOR.MIDDLE,
                wrap=False, inset_left=TITLE_INSET, name="Title")


def content_top(has_title=True):
    return CONTENT_Y0 if has_title else CONTENT_Y0_NO_TITLE


def caption(slide, x, under_y, w, words, dark=True, size=11):
    """A caption, CAPTION_GAP under the bottom edge (under_y) of what it captions."""
    return text(slide, x, under_y + CAPTION_GAP, w, 0.25, words, size=size, color=MUTED_D if dark else MUTED_W,
                name="Caption")


def notes_from_source(sid):
    f = SRC / f"{sid}.html"
    if not f.exists():
        return ""
    m = re.search(r"<aside>(.*?)</aside>", f.read_text(encoding="utf-8"), re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def set_notes(slide, notes):
    slide.notes_slide.notes_text_frame.text = notes


# ---------- the layout guide ----------

GUIDE_D = RGBColor(0xEF, 0x78, 0x0B)   # the template's orange, for the guide's outlines on black
GUIDE_W = RGBColor(0xB8, 0x55, 0x00)   # a darker orange that holds on white


def _fmt(v):
    return f"{v:.2f}".replace(".", ",")


def guide_slide(prs, dark, has_title):
    s = new_slide(prs, L_BLACK if dark else L_WHITE)
    g = GUIDE_D if dark else GUIDE_W
    block = RGBColor(0x1A, 0x1C, 0x1E) if dark else RGBColor(0xEE, 0xF0, 0xEE)
    lab = dict(size=8, bold=True, color=g)

    # header mark
    mx, my, mw, mh = mark_box()
    box(s, mx, my, mw, mh, line=g, dash=True, name="Guide: header mark")
    text(s, mx + mw + 0.12, my + 0.05, 5.0, 0.2,
         f"MARCA DO CABEÇALHO · 60 % · x {_fmt(mx)} · y {_fmt(my)} · {_fmt(mw)} × {_fmt(mh)}", **lab)

    # title
    if has_title:
        x, y, w, h = TITLE
        title(s, "Título do diapositivo, numa só linha", dark=dark)
        box(s, x, y, w, h, line=g, dash=True, name="Guide: title")
        text(s, x, y - 0.17, w, 0.15, f"TÍTULO · x {_fmt(x)} · y {_fmt(y)} · {_fmt(w)} × {_fmt(h)} · "
             "Arial Bold 26 pt", align=PP_ALIGN.RIGHT, **lab)

    # content zone
    cy0 = content_top(has_title)
    box(s, CONTENT_X0, cy0, CONTENT_X1 - CONTENT_X0, CONTENT_Y1 - cy0, line=g, dash=True, name="Guide: content")
    text(s, CONTENT_X0 + 0.08, cy0 + 0.06, 8.0, 0.18,
         f"CONTEÚDO{'' if has_title else ', SEM TÍTULO'} · x {_fmt(CONTENT_X0)} a {_fmt(CONTENT_X1)} · "
         f"y {_fmt(cy0)} a {_fmt(CONTENT_Y1)}", **lab)

    # two example blocks, GAP apart, each with its caption CAPTION_GAP under it
    bw = (CONTENT_X1 - CONTENT_X0 - GAP) / 2
    by0 = cy0 + 0.35
    bh = CONTENT_Y1 - by0 - CAPTION_GAP - 0.25 - 0.06
    for i in range(2):
        bx = CONTENT_X0 + i * (bw + GAP)
        box(s, bx, by0, bw, bh, fill=block, name=f"Guide: block {i + 1}")
        text(s, bx, by0, bw, bh, "imagem, diagrama ou número", size=11, color=MUTED_D if dark else MUTED_W,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        caption(s, bx, by0 + bh, bw, "Legenda · Arial 11 pt, cinzento, 0,08\" por baixo", dark=dark)
        box(s, bx, by0 + bh + CAPTION_GAP, bw, 0.22, line=g, dash=True, name=f"Guide: caption {i + 1}")
    gx = CONTENT_X0 + bw
    text(s, gx - 0.4, by0 - 0.19, GAP + 0.8, 0.16, "0,25\"", align=PP_ALIGN.CENTER, **lab)
    text(s, CONTENT_X1 - 3.2, by0 + bh + CAPTION_GAP + 0.03, 3.15, 0.16, "LEGENDA", align=PP_ALIGN.RIGHT, **lab)

    # logos row
    lx, ly, lw, lh = logos_box()
    ix0, iy0 = lx + LOGOS_INK[0] * lw, ly + LOGOS_INK[1] * lh
    iw, ih = (LOGOS_INK[2] - LOGOS_INK[0]) * lw, (LOGOS_INK[3] - LOGOS_INK[1]) * lh
    box(s, ix0, iy0, iw, ih, line=g, dash=True, name="Guide: logos")
    text(s, ix0 + iw + 0.1, iy0 - 0.02, 9.55 - (ix0 + iw + 0.1), 0.36,
         ["LOGÓTIPOS · 60 % · centrados", f"0,30\" acima do fundo"], **lab)

    set_notes(s, "Guia da grelha, para aprovação. Fundo " + ("preto" if dark else "branco") + ", "
              + ("com título" if has_title else "sem título") + ". As linhas a laranja não entram nos diapositivos.\n"
              f"Título: caixa x 0,45, y 0,80, 9,10 × 0,55; uma linha, Arial Bold 26 pt, alinhado à esquerda; "
              "branco no preto, 1E1D1A no branco; o quadrado verde é o marcador.\n"
              f"Conteúdo: x 0,45 a 9,55, y {_fmt(cy0)} a 4,85. Legendas: Arial 11 a 12 pt, cinzento, 0,08\" por baixo "
              "do que legendam. Espaço entre blocos: 0,25\".\n"
              "Marca do cabeçalho e logótipos: 60 % do tamanho do modelo; os logótipos centrados, 0,30\" acima do fundo.")
    return s


def guide_cover(prs):
    s = new_slide(prs, L_COVER)
    lx, ly, lw, lh = logos_box()
    ix0, iy0 = lx + LOGOS_INK[0] * lw, ly + LOGOS_INK[1] * lh
    iw, ih = (LOGOS_INK[2] - LOGOS_INK[0]) * lw, (LOGOS_INK[3] - LOGOS_INK[1]) * lh
    box(s, ix0, iy0, iw, ih, line=GUIDE_D, dash=True, name="Guide: logos")
    text(s, ix0 + iw + 0.1, iy0 - 0.02, 9.55 - (ix0 + iw + 0.1), 0.36,
         ["LOGÓTIPOS · 60 % · centrados", "0,30\" acima do fundo"], size=8, bold=True, color=GUIDE_D)
    text(s, 0.36, 2.2, 3.9, 0.6, ["CAPA", "a marca grande do modelo fica; o texto da capa entra aqui"], size=8, bold=True,
         color=GUIDE_D)
    set_notes(s, "Guia da capa: a marca grande e os desenhos do modelo ficam como estão; os logótipos passam a 60 %, "
                 "centrados, 0,30\" acima do fundo, como nos outros diapositivos.")
    return s


# ---------- slide variants: one geometry each, shared by the guide and the slides ----------
# Each returns {zone: (x, y, w, h)} in inches, inside the frame. The slides will place their assets in these zones.

CW = CONTENT_X1 - CONTENT_X0
COVER_TEXT = (0.36, 2.15, 3.8, 1.75)   # on the cover, left of the drawings and above the red bar
FLOW_GAP = 0.50                        # steps of a flow: room for the arrow, 0.10" clear on each side
ARROW_LEN = 0.30
STRIP_H = 0.36                         # caption strip inside a full image


def v_capa():
    x, y, w, _ = COVER_TEXT
    return {"nome": (x, y, 2.9, 0.5), "linha": (x, y + 0.62, w, 0.3), "equipa": (x, y + 1.04, w, 0.25),
            "nomes": (x, y + 1.33, w, 0.25)}


INTRO_LOGO_H = 0.75


def v_intro():
    """No title. Logo, line, challenge and team, names: one block, left-aligned, centred in the content zone."""
    y0 = CONTENT_Y0_NO_TITLE
    logo_w = INTRO_LOGO_H * 2400 / 414
    rows = [("logo", INTRO_LOGO_H, 0.0), ("linha", 0.36, 0.20), ("equipa", 0.26, 0.35), ("nomes", 0.26, 0.06)]
    total = sum(h + gap for _, h, gap in rows)
    y = y0 + (CONTENT_Y1 - y0 - total) / 2
    z = {}
    for k, h, gap in rows:
        y += gap
        z[k] = (CONTENT_X0, y, logo_w if k == "logo" else CW, h)
        y += h
    return z


def v_afirmacao(has_title=True):
    """The one-line title, then the statement at the top of the content zone, then the sub-line."""
    y0 = content_top(has_title)
    tw = (CW - GAP) * 2 / 3
    fh = 1.3
    return {"frase": (CONTENT_X0, y0, tw, fh), "subfrase": (CONTENT_X0, y0 + fh + GAP, tw, 0.6),
            "imagem": (CONTENT_X0 + tw + GAP, y0, CW - tw - GAP, CONTENT_Y1 - y0)}


def v_imagem(has_title=True, strip_w=4.2):
    y0 = content_top(has_title)
    return {"imagem": (CONTENT_X0, y0, CW, CONTENT_Y1 - y0),
            "faixa": (CONTENT_X0, CONTENT_Y1 - STRIP_H, strip_w, STRIP_H)}


def v_duas_colunas(has_title=True, cap_h=0.25, band_h=0.0):
    """Two equal columns; with band_h, a band across both at the bottom of the content zone, GAP under the captions."""
    y0 = content_top(has_title)
    y1 = CONTENT_Y1 - (band_h + GAP if band_h else 0)
    cw = (CW - GAP) / 2
    lab_h = 0.22
    z = {}
    for i, k in enumerate(["esq", "dir"]):
        x = CONTENT_X0 + i * (cw + GAP)
        img_y = y0 + lab_h + CAPTION_GAP
        img_h = y1 - img_y - CAPTION_GAP - cap_h
        z[f"{k}-rotulo"] = (x, y0, cw, lab_h)
        z[f"{k}-imagem"] = (x, img_y, cw, img_h)
        z[f"{k}-legenda"] = (x, img_y + img_h + CAPTION_GAP, cw, cap_h)
    if band_h:
        z["faixa"] = (CONTENT_X0, CONTENT_Y1 - band_h, CW, band_h)
    return z


def v_fluxo(n=4, has_title=True):
    y0 = content_top(has_title)
    sw = (CW - (n - 1) * FLOW_GAP) / n
    img_h = min(sw * 0.8, CONTENT_Y1 - y0 - 0.6)
    block = img_h + CAPTION_GAP + 0.3
    top = y0 + (CONTENT_Y1 - y0 - block) / 2
    z = {}
    for i in range(n):
        x = CONTENT_X0 + i * (sw + FLOW_GAP)
        z[f"passo{i + 1}-imagem"] = (x, top, sw, img_h)
        z[f"passo{i + 1}-rotulo"] = (x, top + img_h + CAPTION_GAP, sw, 0.3)
        if i < n - 1:
            ax = x + sw + (FLOW_GAP - ARROW_LEN) / 2
            z[f"seta{i + 1}"] = (ax, top + img_h / 2, ARROW_LEN, 0)
    return z


def v_numero(has_title=True):
    """The number needs about 5.3" at 96 pt ("≈ 0,49 €"), so it takes 60 % of the width; the image the rest."""
    y0 = content_top(has_title)
    nw = round(CW * 0.6, 2)
    return {"numero": (CONTENT_X0, y0, nw, 1.45), "rotulo": (CONTENT_X0, y0 + 1.45 + CAPTION_GAP, nw, 0.4),
            "fonte": (CONTENT_X0, CONTENT_Y1 - 0.2, nw, 0.2),
            "imagem": (CONTENT_X0 + nw + GAP, y0, CW - nw - GAP, CONTENT_Y1 - y0)}


def v_grelha(n=3, rows=1, ratio=16 / 9, has_title=True, cap_h=0.25):
    y0 = content_top(has_title)
    cw = (CW - (n - 1) * GAP) / n
    ih = cw / ratio
    cell = ih + CAPTION_GAP + cap_h
    total = rows * cell + (rows - 1) * GAP
    if total > CONTENT_Y1 - y0:  # too tall: shrink the images, keep the ratio
        ih = ((CONTENT_Y1 - y0) - rows * (CAPTION_GAP + cap_h) - (rows - 1) * GAP) / rows
        cell = ih + CAPTION_GAP + cap_h
        total = rows * cell + (rows - 1) * GAP
    top = y0 + (CONTENT_Y1 - y0 - total) / 2
    z = {}
    for r in range(rows):
        for c in range(n):
            k = r * n + c + 1
            x, y = CONTENT_X0 + c * (cw + GAP), top + r * (cell + GAP)
            z[f"imagem{k}"] = (x, y, cw, ih)
            z[f"legenda{k}"] = (x, y + ih + CAPTION_GAP, cw, cap_h)
    return z


def v_fecho(has_title=True):
    y0 = content_top(has_title)
    pts = 3 * 0.42
    return {"pontos": (CONTENT_X0, y0, CW, pts), "pedido": (CONTENT_X0, y0 + pts + GAP, 6.6, 0.5),
            "assinatura": (CONTENT_X0, CONTENT_Y1 - 0.38, CW, 0.38)}


# ---------- the variants in the guide ----------

LOGO = REPO / "assets" / "brand" / "logo" / "thingtracker-dark.png"


def _alpha(shape, pct):
    clr = shape._element.spPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    clr.append(clr.makeelement(qn("a:alpha"), {"val": str(int(pct * 1000))}))


def _arrow(slide, x, y, length, color, width=1.5):
    c = slide.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + length), Inches(y))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))
    c.name = "Arrow"
    return c


class Guide:
    """Draws one variant's zones: dashed outline, a short label, and a stand-in in the real style."""

    def __init__(self, slide, dark):
        self.s, self.dark = slide, dark
        self.g = GUIDE_D if dark else GUIDE_W
        self.block = RGBColor(0x1A, 0x1C, 0x1E) if dark else RGBColor(0xEE, 0xF0, 0xEE)
        self.muted = MUTED_D if dark else MUTED_W
        self.fg = WHITE if dark else INK

    def outline(self, z, label, inside=True, align=PP_ALIGN.RIGHT):
        x, y, w, h = z
        box(self.s, x, y, w, h, line=self.g, dash=True, line_w=0.75, name=f"Guide: {label}")
        ly = y + 0.03 if inside else y - 0.16
        text(self.s, x + 0.05, ly, w - 0.1, 0.14, label.upper(), size=7, bold=True, color=self.g, align=align)

    def image(self, z, label, note="imagem"):
        x, y, w, h = z
        box(self.s, x, y, w, h, fill=self.block)
        text(self.s, x, y, w, h, note, size=11, color=self.muted, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        self.outline(z, label)

    def words(self, z, label, sample, size, bold=False, color=None, anchor=MSO_ANCHOR.TOP, wrap=True, inside=True):
        x, y, w, h = z
        text(self.s, x, y, w, h, sample, size=size, bold=bold, color=color or self.fg, anchor=anchor, wrap=wrap)
        self.outline(z, label, inside=inside)

    def frame(self, variant, has_title, title_words=None):
        mx, my, mw, mh = mark_box()
        text(self.s, 4.0, my + 0.04, CONTENT_X1 - 4.0, 0.2, f"VARIANTE · {variant}", size=10, bold=True, color=self.g,
             align=PP_ALIGN.RIGHT)
        if has_title:
            title(self.s, title_words or "Título, numa só linha", dark=self.dark)
            self.outline(TITLE, "título", inside=False)
        y0 = content_top(has_title)
        box(self.s, CONTENT_X0, y0, CW, CONTENT_Y1 - y0, line=self.g, dash=True, line_w=0.5, name="Guide: content")


def gv_capa(prs):
    s = new_slide(prs, L_COVER)
    g = Guide(s, True)
    text(s, 4.0, 0.12, 5.55, 0.2, "VARIANTE · capa", size=10, bold=True, color=g.g, align=PP_ALIGN.RIGHT)
    z = v_capa()
    picture(s, LOGO, *z["nome"][:2], w=z["nome"][2], alt="ThingTracker")
    g.outline(z["nome"], "nome do produto", inside=False)
    g.words(z["linha"], "linha", "A câmara da casa, atenta ao que importa.", 14, inside=False)
    g.words(z["equipa"], "desafio e equipa", "Desafio #3 · Altice Labs · Equipa IT-Porto", 11, bold=True, color=NEON,
            inside=False)
    g.words(z["nomes"], "nomes", "Filipe Peixoto · Simon Ranjith · Mushahid Hussain", 11, color=RGBColor(0xD0, 0xD4, 0xD8),
            inside=False)
    return s, "Capa: a marca grande e os desenhos do modelo; à esquerda, o nome do produto, a linha, o desafio e a equipa, e os nomes."


def gv_intro(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("intro", False)
    z = v_intro()
    picture(s, LOGO, *z["logo"][:2], h=INTRO_LOGO_H, alt="ThingTracker")
    g.outline(z["logo"], "logótipo · 0,75\"")
    g.words(z["linha"], "linha · 22 pt", "A câmara da casa, atenta ao que importa.", 22)
    g.words(z["equipa"], "desafio e equipa · 14 pt", "Desafio #3 · Altice Labs · Equipa IT-Porto", 14, bold=True, color=NEON)
    g.words(z["nomes"], "nomes · 14 pt", "Filipe Peixoto · Simon Ranjith · Mushahid Hussain", 14,
            color=RGBColor(0xD0, 0xD4, 0xD8))
    return s, "Introdução: sem título. O logótipo (0,75\" de altura), a linha (22 pt), o desafio e a equipa (14 pt, verde) e " \
              "os nomes (14 pt), num só bloco alinhado à esquerda e centrado na zona de conteúdo. Sem imagem nem ícones."


def gv_afirmacao(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("afirmacao", True, "Como começamos")
    z = v_afirmacao(True)
    g.words(z["frase"], "frase · Arial Bold 38 pt", "Uma frase grande, no topo da zona", 38, bold=True)
    g.words(z["subfrase"], "subfrase (opcional) · 16 pt", "Uma linha pequena, se for precisa", 16, color=g.muted)
    g.image(z["imagem"], "imagem ou recorte (opcional)", "imagem ou recorte")
    return s, "Afirmação: o título numa linha e, por baixo, uma frase grande (Arial Bold 36 a 40 pt) no topo da zona de " \
              "conteúdo, uma subfrase opcional e, à direita, uma imagem ou um recorte opcional."


def gv_imagem(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("imagem", True, "O livro esquecido")
    z = v_imagem(True)
    g.image(z["imagem"], "imagem ou fotograma · preenche a zona por baixo do título (cover)",
            "imagem ou fotograma do filme")
    fx, fy, fw, fh = z["faixa"]
    band = box(s, fx, fy, fw, fh, fill=RGBColor(0, 0, 0))
    _alpha(band, 60)
    text(s, fx + 0.14, fy, fw - 0.2, fh, "Legenda opcional, faixa escura, 12 pt", size=12, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    g.outline(z["faixa"], "faixa de legenda", inside=False, align=PP_ALIGN.LEFT)
    return s, "Imagem: o título numa linha e, por baixo, uma imagem ou um fotograma que enche a zona de conteúdo (cover). " \
              "Legenda opcional numa faixa escura translúcida, em baixo à esquerda, 12 pt. Para os filmes."


def gv_duas_colunas(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("duas-colunas", True, "Hoje e com IA, lado a lado")
    z = v_duas_colunas(True)
    for k, lab in [("esq", "Hoje"), ("dir", "Com IA")]:
        g.words(z[f"{k}-rotulo"], "rótulo (opcional)", lab.upper(), 11, bold=True, color=NEON)
        g.image(z[f"{k}-imagem"], "imagem")
        g.words(z[f"{k}-legenda"], "legenda", "Legenda, 11 a 12 pt", 11, color=g.muted)
    return s, "Duas colunas: iguais, 0,25\" entre elas; cada uma com um rótulo opcional, a imagem e a legenda 0,08\" por baixo. " \
              "Fundo preto ou branco."


def gv_fluxo(prs):
    s = new_slide(prs, L_WHITE)
    g = Guide(s, False)
    g.frame("fluxo", True, "Da câmara ao aviso, em quatro passos")
    z = v_fluxo(4, True)
    for i in range(1, 5):
        g.image(z[f"passo{i}-imagem"], f"passo {i}")
        x, y, w, h = z[f"passo{i}-rotulo"]
        text(s, x, y, w, h, ["Câmara", "Imagens", "IA", "Aviso"][i - 1], size=12, bold=True, color=INK, align=PP_ALIGN.CENTER)
        g.outline(z[f"passo{i}-rotulo"], "rótulo")
        if i < 4:
            ax, ay, al, _ = z[f"seta{i}"]
            _arrow(s, ax, ay, al, RGBColor(0x5F, 0x63, 0x68))
    text(s, CONTENT_X0, CONTENT_Y1 - 0.18, CW, 0.15, "PASSOS IGUAIS · 0,50\" ENTRE PASSOS, COM A SETA AO CENTRO · TRÊS OU QUATRO",
         size=7, bold=True, color=g.g, align=PP_ALIGN.CENTER)
    return s, "Fluxo: três ou quatro passos iguais, numa linha; cada um com uma área de imagem e um rótulo de duas ou três " \
              "palavras por baixo; setas finas e retas no centro dos intervalos (0,50\" entre passos, para caber a seta). Branco ou preto."


def gv_numero(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("numero", True, "Quanto custa à Altice")
    z = v_numero(True)
    g.words(z["numero"], "número · 96 pt · 60 % da largura", "≈ 0,49 €", 96, bold=True, color=NEON, wrap=False)
    g.words(z["rotulo"], "rótulo · 18 pt", "por casa e por mês", 18)
    g.words(z["fonte"], "fonte · 10 pt", "Fonte: estimativa da equipa (documento 17)", 10, color=g.muted)
    g.image(z["imagem"], "imagem de apoio (opcional)", "imagem de apoio")
    return s, "Número: um número a verde, cerca de 96 pt, à esquerda, em 60 % da largura (a 96 pt, “≈ 0,49 €” ocupa " \
              "cerca de 5,3\"); o rótulo por baixo, 18 pt; a fonte no fundo da zona de conteúdo, 10 a 11 pt; uma imagem de " \
              "apoio opcional nos 40 % da direita."


def gv_grelha(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("grelha", True, "Três exemplos, lado a lado")
    z = v_grelha(3, 1, 16 / 9, True)
    for i in range(1, 4):
        g.image(z[f"imagem{i}"], f"imagem {i} · mesma proporção")
        g.words(z[f"legenda{i}"], "legenda", "Legenda, 11 a 12 pt", 11, color=g.muted)
    text(s, CONTENT_X0, CONTENT_Y1 - 0.18, CW, 0.15, "TRÊS OU QUATRO NUMA LINHA, OU 2 × 3 · 0,25\" ENTRE IMAGENS",
         size=7, bold=True, color=g.g, align=PP_ALIGN.CENTER)
    return s, "Grelha: três ou quatro imagens numa linha, ou 2 × 3, todas com a mesma proporção, 0,25\" entre elas, " \
              "cada uma com a legenda 0,08\" por baixo. Preto ou branco."


def gv_fecho(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("fecho", True, "Em resumo")
    z = v_fecho(True)
    x, y, w, h = z["pontos"]
    for i, t in enumerate(["Um ponto curto, numa linha", "Outro ponto curto", "O terceiro ponto"]):
        box(s, x + 0.3, y + i * 0.42 + 0.1, 0.16, 0.16, fill=NEON)
        text(s, x + 0.6, y + i * 0.42, w - 0.6, 0.34, t, size=18, bold=True, color=WHITE)
    g.outline(z["pontos"], "três pontos · marcador verde · 18 pt")
    px, py, pw, ph = z["pedido"]
    box(s, px, py, pw, ph, fill=NEON)
    text(s, px + 0.2, py, pw - 0.3, ph, "O pedido, numa linha", size=15, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    g.outline(z["pedido"], "pedido em destaque", inside=False, align=PP_ALIGN.LEFT)
    ax, ay, aw, ah = z["assinatura"]
    picture(s, LOGO, ax, ay + 0.04, h=0.3, alt="ThingTracker")
    text(s, ax + 2.0, ay, aw - 2.0, ah, "A câmara da casa, atenta ao que importa.", size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    g.outline(z["assinatura"], "nome do produto e frase final")
    return s, "Fecho: três pontos curtos com o marcador verde, o pedido numa faixa verde e, no fundo da zona de conteúdo, " \
              "o nome do produto e a frase final."


VARIANT_GUIDES = [gv_capa, gv_intro, gv_afirmacao, gv_imagem, gv_duas_colunas, gv_fluxo, gv_numero, gv_grelha, gv_fecho]


def build_guide(template, out):
    prs = open_template(template)
    for dark, has_title in [(True, True), (True, False), (False, True), (False, False)]:
        guide_slide(prs, dark, has_title)
    for make in VARIANT_GUIDES:
        s, note = make(prs)
        set_notes(s, note + " As linhas a laranja não entram nos diapositivos.")
    prs.save(out)
    return out


# ---------- the pitch slides, on the variants ----------

DIAG = REPO / "docs" / "architecture"
TILE_D = RGBColor(0x17, 0x19, 0x1C)
TILE_L = RGBColor(0xF0, 0xF2, 0xF0)


def pic_cover(slide, path, z, cx=0.5, cy=0.5, alt=None):
    """Fill the zone with the image, cropped around (cx, cy) (object-fit: cover)."""
    x, y, w, h = z
    with Image.open(path) as im:
        iw, ih = im.size
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    r, t = iw / ih, w / h
    if r > t:
        keep = t / r
        left = min(max(cx - keep / 2, 0), 1 - keep)
        pic.crop_left, pic.crop_right = left, 1 - keep - left
    else:
        keep = r / t
        top = min(max(cy - keep / 2, 0), 1 - keep)
        pic.crop_top, pic.crop_bottom = top, 1 - keep - top
    if alt:
        pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic


def phone(slide, path, z, margin=0.12, alt=None):
    """A phone screenshot: fitted, rounded corners, soft shadow, no drawn frame."""
    x, y, w, h = z
    pic = picture(slide, path, x + margin, y + margin, fit=(w - 2 * margin, h - 2 * margin), alt=alt)
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    geom = pic._element.spPr.find(qn("a:prstGeom"))
    av = geom.find(qn("a:avLst"))
    if av is None:
        av = geom.makeelement(qn("a:avLst"), {})
        geom.append(av)
    av.append(av.makeelement(qn("a:gd"), {"name": "adj", "fmla": "val 12000"}))
    spPr = pic._element.spPr
    eff = spPr.makeelement(qn("a:effectLst"), {})
    sh = eff.makeelement(qn("a:outerShdw"), {"blurRad": str(Inches(0.14)), "dist": str(Inches(0.04)),
                                             "dir": "5400000", "algn": "t", "rotWithShape": "0"})
    clr = sh.makeelement(qn("a:srgbClr"), {"val": "000000"})
    clr.append(clr.makeelement(qn("a:alpha"), {"val": "45000"}))
    sh.append(clr)
    eff.append(sh)
    spPr.append(eff)
    return pic


def tile(slide, z, dark=True):
    return box(slide, *z, fill=TILE_D if dark else TILE_L)


def notification(slide, x, y, w, h=0.95):
    """The kit camera's notification today, as words on a card (no icon)."""
    box(slide, x, y, w, h, fill=RGBColor(0x2A, 0x2C, 0x31), shape=MSO_SHAPE.ROUNDED_RECTANGLE, name="Notification")
    text(slide, x + 0.2, y + 0.16, w - 1.0, 0.2, "Câmara · Sala", size=10, color=MUTED_D)
    text(slide, x + w - 0.8, y + 0.16, 0.6, 0.2, "agora", size=10, color=MUTED_D, align=PP_ALIGN.RIGHT)
    text(slide, x + 0.2, y + 0.42, w - 0.3, 0.35, "Movimento detetado", size=15, bold=True, color=WHITE, wrap=False)


def label(slide, z, words, dark=True):
    x, y, w, h = z
    text(slide, x, y, w, h, words, size=12, bold=True, color=NEON if dark else GREEN_D, anchor=MSO_ANCHOR.BOTTOM)


def cap(slide, z, words, dark=True, size=11):
    x, y, w, h = z
    text(slide, x, y, w, h, words, size=size, color=MUTED_D if dark else MUTED_W, name="Caption")


JPEG_DIR = None  # set by build_decks: photos are embedded as JPEG (quality 88, at most 1920 px wide)


def jpg(path):
    """A photo or screenshot as JPEG; a picture with real transparency (the camera cutout) stays PNG."""
    path = Path(path)
    if JPEG_DIR is None:
        return path
    with Image.open(path) as im:
        if "A" in im.getbands() and im.getchannel("A").getextrema()[0] < 255:
            return path
        out = JPEG_DIR / f"{path.stem}.jpg"
        if not out.exists():
            im = im.convert("RGB")
            if im.width > 1920:
                im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
            im.save(out, quality=88)
    return out


def sl_capa(prs):
    """The template's cover exactly as delivered: none of our text on it."""
    return new_slide(prs, L_COVER)


def sl_intro(prs):
    s = new_slide(prs, L_BLACK)
    z = v_intro()
    picture(s, LOGO, *z["logo"][:2], h=INTRO_LOGO_H, alt="ThingTracker")
    text(s, *z["linha"], "A câmara da casa, atenta ao que importa.", size=22, color=WHITE)
    text(s, *z["equipa"], "Desafio #3 · Altice Labs · Equipa IT-Porto", size=14, bold=True, color=NEON)
    text(s, *z["nomes"], "Filipe Peixoto · Simon Ranjith · Mushahid Hussain", size=14, color=RGBColor(0xD0, 0xD4, 0xD8))
    return s


def sl_hoje(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Hoje só grava. Com IA, percebe o que vê")
    z = v_duas_colunas(True)
    label(s, z["esq-rotulo"], "Hoje")
    ex, ey, ew, eh = z["esq-imagem"]
    tile(s, z["esq-imagem"])
    picture(s, ASSETS / "kit-camera.png", ex + 0.12, ey + 0.15, fit=(1.45, eh - 0.3), alt="A câmara do kit")
    notification(s, ex + 1.7, ey + (eh - 0.95) / 2, ew - 1.85)
    cap(s, z["esq-legenda"], "A câmara do _kit_ só avisa que houve movimento")
    label(s, z["dir-rotulo"], "Com o _ThingTracker_")
    pic_cover(s, jpg(ASSETS / "frame-livro-ia.png"), z["dir-imagem"], cx=0.6, cy=0.45,
              alt="Imagem do laboratório com as caixas do sistema: o livro reconhecido a 0,94, a pessoa, a porta e o alarme")
    cap(s, z["dir-legenda"], "Reconhece o livro, a família, a casa vazia")
    return s


def sl_thingtracker(prs):
    s = new_slide(prs, L_WHITE)
    title(s, "Por isso criámos o _ThingTracker_", dark=False)
    z = v_fluxo(4, True)
    steps = [("kit-camera.png", "Câmara", "cut", "A câmara do kit"),
             ("frame-livro-camera.png", "Imagem", "cover", "Uma imagem da câmara, sem caixas"),
             ("frame-livro-ia.png", "IA reconhece", "cover", "A mesma imagem com as caixas do sistema"),
             ("alert-last.png", "Aviso na app", "phone", "O aviso na app: o livro ficou em casa")]
    for i, (f, lab, kind, alt) in enumerate(steps, 1):
        zi = z[f"passo{i}-imagem"]
        if kind == "cover":
            pic_cover(s, jpg(ASSETS / f), zi, cx=0.62, cy=0.42, alt=alt)
        else:
            tile(s, zi, dark=False)
            if kind == "cut":
                picture(s, ASSETS / f, zi[0] + 0.12, zi[1] + 0.12, fit=(zi[2] - 0.24, zi[3] - 0.24), alt=alt)
            else:
                phone(s, jpg(ASSETS / f), zi, margin=0.1, alt=alt)
        x, y, w, h = z[f"passo{i}-rotulo"]
        text(s, x, y, w, h, lab, size=12, bold=True, color=INK, align=PP_ALIGN.CENTER)
        if i < 4:
            ax, ay, al, _ = z[f"seta{i}"]
            _arrow(s, ax, ay, al, RGBColor(0x5F, 0x63, 0x68))
    return s


def sl_livro(prs):
    s = new_slide(prs, L_BLACK)
    words = "O livro esquecido · reconhecido em 68 de 68 imagens, a 0,93"
    z = v_imagem(False, strip_w=5.3)
    pic_cover(s, jpg(ASSETS / "frame-livro-ia.png"), z["imagem"], cx=0.6, cy=0.42,
              alt="Imagem do filme: o livro reconhecido na mesa, a 0,94, depois de a porta fechar")
    fx, fy, fw, fh = z["faixa"]
    band = box(s, fx, fy, fw, fh, fill=RGBColor(0, 0, 0))
    _alpha(band, 62)
    text(s, fx + 0.14, fy, fw - 0.2, fh, words, size=12, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    return s


def sl_altice(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Porque a Altice")
    z = v_grelha(3, 1, 4 / 3, True, cap_h=0.42)
    tile(s, z["imagem1"])
    x, y, w, h = z["imagem1"]
    picture(s, ASSETS / "kit-camera.png", x + 0.2, y + 0.2, fit=(w - 0.4, h - 0.4), alt="A câmara do kit")
    cap(s, z["legenda1"], "A câmara, a app e o MCP que já existem")
    tile(s, z["imagem2"])
    text(s, *z["imagem2"], "≈ 0,49 €", size=44, bold=True, color=NEON, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cap(s, z["legenda2"], "por casa e por mês")
    tile(s, z["imagem3"])
    phone(s, jpg(ASSETS / "alert-nobody.png"), z["imagem3"], margin=0.15,
          alt="O aviso na app: ninguém em casa, com dois cartões para desligar")
    cap(s, z["legenda3"], "Começa com um piloto em casas de colaboradores da MEO")
    return s


def sl_fecho(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Em resumo")
    z = v_fecho(True)
    x, y, w, h = z["pontos"]
    for i, t in enumerate(["Reconhece o que importa em cada casa", "Cerca de 0,49 € por casa e por mês",
                           "Usa a câmara, a app e o MCP da Altice"]):
        box(s, x + 0.05, y + i * 0.42 + 0.1, 0.16, 0.16, fill=NEON)
        text(s, x + 0.35, y + i * 0.42, w - 0.35, 0.34, t, size=18, bold=True, color=WHITE)
    px, py, pw, ph = z["pedido"]
    box(s, px, py, pw, ph, fill=NEON)
    text(s, px + 0.2, py, pw - 0.3, ph, "Propomos um piloto já", size=16, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    ax, ay, aw, ah = z["assinatura"]
    picture(s, LOGO, ax, ay + 0.04, h=0.3, alt="ThingTracker")
    text(s, ax + 2.0, ay, aw - 2.0, ah, "A câmara da casa, atenta ao que importa.", size=14, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
    return s


def sl_exemplos(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Três exemplos, filmados no laboratório")
    z = v_grelha(3, 1, 16 / 9, True, cap_h=0.42)
    items = [("frame-livro-ia.png", "O livro esquecido", "O livro reconhecido na mesa, a 0,94"),
             ("frame-filipe-ia.png", "A família reconhecida, o desconhecido avisado", "O Filipe reconhecido pelo sistema"),
             ("frame-casa-vazia-ia.png", "Ninguém em casa: desligar e fechar", "Ninguém em casa, com as luzes e o ar condicionado ligados")]
    for i, (f, c, alt) in enumerate(items, 1):
        pic_cover(s, jpg(ASSETS / f), z[f"imagem{i}"], alt=alt)
        cap(s, z[f"legenda{i}"], c)
    return s


# At 11 pt the list does not fit on one line across 9.1", so it breaks where the models end and the tools begin.
MODELS_LINE = ["Modelos e ferramentas: _OWLv2_ e _DINOv2_ (Apache-2.0) · _YuNet_ (MIT) · _SFace_ (Apache-2.0) ·",
               "_Qwen3-1.7B_ (Apache-2.0) · MCP da Altice · _Claude Code_"]


def sl_como(prs):
    s = new_slide(prs, L_WHITE)
    title(s, "Como funciona", dark=False)
    z = v_duas_colunas(True, cap_h=0.42, band_h=0.42)
    label(s, z["esq-rotulo"], "Hoje, no protótipo", dark=False)
    pic_cover(s, jpg(ASSETS / "frame-livro-ia.png"), z["esq-imagem"], cx=0.6, cy=0.45,
              alt="Imagem do laboratório com as caixas do sistema")
    cap(s, z["esq-legenda"], "Um portátil faz de casa e de servidores da Altice", dark=False)
    label(s, z["dir-rotulo"], "Proposta", dark=False)
    box(s, *z["dir-imagem"], fill=WHITE, line=RGBColor(0xD3, 0xD7, 0xDC), line_w=0.75)
    x, y, w, h = z["dir-imagem"]
    picture(s, DIAG / "implantacao.png", x + 0.06, y + 0.06, fit=(w - 0.12, h - 0.12),
            alt="Implantação: o agente da casa no router, o ThingTracker nos servidores da Altice")
    cap(s, z["dir-legenda"], "_Router_ em casa + servidores da Altice · os modelos veem, o código decide", dark=False)
    fx, fy, fw, fh = z["faixa"]
    box(s, fx, fy, fw, fh, fill=TILE_L)
    text(s, fx + 0.12, fy, fw - 0.24, fh, MODELS_LINE, size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    return s


def sl_viabilidade(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Quanto custa à Altice")
    z = v_numero(True)
    text(s, *z["numero"], "≈ 0,49 €", size=96, bold=True, color=NEON, wrap=False)
    text(s, *z["rotulo"], "por casa e por mês, com uma câmara", size=18, color=WHITE)
    cap(s, z["fonte"], "Estimativa da equipa para 500 000 casas, com preços públicos (documento 17)", size=10)
    x, y, w, h = z["imagem"]
    picture(s, ASSETS / "kit-camera.png", x + w * 0.2, y + h * 0.15, fit=(w * 0.6, h * 0.7), alt="A câmara do kit")
    return s


def sl_comecar(prs):
    s = new_slide(prs, L_BLACK)
    title(s, "Como começamos")
    z = v_afirmacao(True)
    text(s, *z["frase"], "Um piloto em casas de colaboradores da MEO", size=36, bold=True, color=WHITE)
    text(s, *z["subfrase"], "A câmara, a app e o MCP já existem · github.com/F1lipe01/hackathon-techweek", size=16,
         color=MUTED_D)
    tile(s, z["imagem"])
    phone(s, jpg(ASSETS / "alert-nobody.png"), z["imagem"], margin=0.25, alt="A app da Altice com o aviso do ThingTracker")
    return s


def sl_annex(prs, head, png):
    s = new_slide(prs, L_WHITE)
    title(s, head, dark=False)
    picture(s, DIAG / png, CONTENT_X0, CONTENT_Y0, fit=(CW, CONTENT_Y1 - CONTENT_Y0), alt=head)
    return s


PITCH_NOTES = {
    "capa": "Capa. Clicar logo para a apresentação.",
    "intro": "INTRODUÇÃO. 3 min: sim · 5 min: sim.\nTempos: 0:00–0:05, 10 palavras.\n"
             "Dizer: “Boa tarde. Somos a equipa IT-Porto, do Instituto de Telecomunicações.”",
    "hoje": "HOJE E COM IA. 3 min: sim · 5 min: sim.\nTempos: 0:05–0:31, 52 palavras.\n"
            "Dizer (a cena, por omissão): “Hoje, a câmara de casa só grava. Uma criança pega numa cápsula de detergente, e o "
            "telemóvel diz apenas ‘movimento detetado’. E depois? Com IA, a câmara percebe o que vê: onde ficaram as chaves, "
            "quem entrou em casa, o que ficou ligado. Cada família cria os seus avisos, com uma frase.”\n"
            "Em alternativa (a pergunta): “Onde deixaram as chaves esta manhã? A câmara de casa até as viu, mas só sabe gravar, "
            "e o telemóvel diz apenas ‘movimento detetado’. E depois?” e, na segunda metade, “a criança em perigo” em vez de "
            "“onde ficaram as chaves”.",
    "thingtracker": "O THINGTRACKER. 3 min: sim · 5 min: sim.\nTempos: 0:31–0:43, 24 palavras.\n"
                    "Dizer: “Por isso criámos o ThingTracker: a câmara que a Altice já vende capta as imagens, a IA percebe-as "
                    "e a família recebe o aviso.”",
    "livro": "O LIVRO ESQUECIDO. 3 min: sim · 5 min: não.\nTempos: 0:43–0:52, 17 palavras; o filme passa de 0:53 a 1:18.\n"
             "Dizer: “Filmámos no nosso laboratório, com a câmara do kit e o nosso protótipo; alguns momentos foram encenados.”\n"
             "O filme passa daqui, em ecrã inteiro, a partir do ficheiro local: ThingTracker - pitch - o livro (25 s).mp4. "
             "Ponto de controlo: o filme começa até aos 0:55.\n"
             "Se o filme não arrancar em 3 s: “No filme, saio sem o livro; a porta fecha-se, a câmara confirma que o livro "
             "ficou na secretária e o telemóvel avisa-me.”",
    "altice": "PORQUE A ALTICE. 3 min: sim · 5 min: não.\nTempos: 1:19–2:00, 84 palavras.\n"
              "Dizer: “Encaixa no que a Altice já tem: a câmara, a app e o MCP. A adoção não exige hardware novo: o router deteta "
              "o movimento e os servidores da Altice tratam da visão. Os modelos veem, o código decide. Viabilidade: uns 49 "
              "cêntimos por casa e por mês; num serviço de 3,99 €, ficam uns 1,25 € de margem. E começa com um piloto em casas "
              "de colaboradores da MEO, em GPU alugadas, sem custo fixo.”\nPonto de controlo: o fecho começa até aos 2:05.",
    "fecho": "FECHO. 3 min: sim · 5 min: sim.\nTempos. 3 min: 2:00–2:27. 5 min: 3:33–4:00. 50 palavras.\n"
             "Dizer: “O ThingTracker já reconhece objetos nas imagens da câmara do kit, custa à Altice cerca de 49 cêntimos por "
             "casa e por mês, e usa a app e o MCP que a Altice já tem. Propomos começar já pelo piloto.”\n"
             "Pausa. Última frase, palavra por palavra: “A câmara da casa, atenta ao que importa.” Depois, silêncio; nunca "
             "“alguma pergunta?”.",
    "exemplos": "TRÊS EXEMPLOS. 3 min: não · 5 min: sim.\nTempos: 0:43–0:56, 26 palavras; os filmes passam de 0:57 a 2:00.\n"
                "Dizer: “Filmámos no nosso laboratório, com a câmara do kit e o nosso protótipo; alguns momentos foram "
                "encenados. Três exemplos: as coisas, a segurança e a energia.”\n"
                "Os três filmes passam daqui, seguidos, sem nada dito entre eles: o livro (20 s), pessoa desconhecida (20 s), "
                "ninguém em casa (20 s). Ponto de controlo: os filmes começam até aos 1:00.",
    "como": "COMO FUNCIONA. 3 min: não · 5 min: sim.\nTempos: 2:00–2:38, 77 palavras.\n"
            "Dizer: “No protótipo, este portátil faz de casa e de servidores da Altice. A adoção não exige hardware novo: o "
            "router deteta o movimento e os servidores da Altice tratam da visão, com modelos open-source que permitem uso "
            "comercial. O OWLv2 encontra pessoas e coisas, o DINOv2 reconhece as coisas de cada família, o YuNet e o SFace "
            "tratam dos rostos e o Qwen3 escreve regras e mensagens. Os modelos veem, o código decide.”\n"
            "A faixa de baixo cumpre a menção obrigatória das ferramentas utilizadas. Ponto de controlo: este diapositivo "
            "começa até aos 2:05.",
    "viabilidade": "QUANTO CUSTA À ALTICE. 3 min: não · 5 min: sim.\nTempos: 2:38–3:05, 53 palavras.\n"
                   "Dizer: “Viabilidade: uns 49 cêntimos por casa e por mês; num serviço de 3,99 €, ficam uns 1,25 € de margem. "
                   "Para a replicação, basta uma câmara, uma app e uma interface como o MCP: serve outros operadores, outros "
                   "países, lares de idosos e alojamento local.”",
    "comecar": "COMO COMEÇAMOS. 3 min: não · 5 min: sim.\nTempos: 3:05–3:33, 57 palavras.\n"
               "Dizer: “Para começar: um piloto em casas de colaboradores da MEO, com a câmara, a app e o MCP que já existem, e "
               "GPU alugadas, sem custo fixo. Depois, os clientes, a 3,99 € por mês. E está tudo no repositório: o código, 12 "
               "diagramas de arquitetura e 107 testes, todos a passar.”\nPonto de controlo: o fecho começa até aos 3:40.",
}

# ---------- the narrative (20 Nov): the motivation first, ThingTracker revealed in the middle ----------
# A: the home is already connected; B: until now the camera only watched; C: ThingTracker; D: one image is enough;
# E (5 min only): the eyes can be fooled. The photos are placeholders: the team picks each one. Each placeholder says
# what its image is for and what to search for.

from PIL import ImageFont

_FONTS = {}
FIT_PROBLEMS = []
PH_FILL_D, PH_FILL_W = RGBColor(0x1E, 0x1E, 0x1E), RGBColor(0xED, 0xED, 0xED)
PH_LINE_D, PH_LINE_W = RGBColor(0x6B, 0x6F, 0x75), RGBColor(0x9A, 0xA0, 0xA6)
CHIP = RGBColor(0x2A, 0x2C, 0x31)
LIGHT = RGBColor(0xD0, 0xD4, 0xD8)
LOGO_LIGHT = REPO / "assets" / "brand" / "logo" / "thingtracker-light.png"
DEV = REPO / "assets" / "devices"


def _font(size, bold=False):
    k = (size, bold)
    if k not in _FONTS:
        f = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
        _FONTS[k] = ImageFont.truetype(f, size * 10)  # measured at 10x
    return _FONTS[k]


def text_width(words, size, bold=False):
    return _font(size, bold).getlength(words) / 720


def text_height(words, size, width, bold=False, leading=1.2):
    """Height in inches of words wrapped at width (inches) in Arial; Google Slides never shrinks text to fit."""
    f, maxw, lines = _font(size, bold), width * 720, 0
    for para in words.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if f.getlength(t) <= maxw:
                cur = t
            else:
                lines, cur = lines + 1, w
        lines += 1
    return lines * size * leading / 72


def placeholder(s, z, nome, purpose, search, dark=True, pad=0.12, reserve_bottom=0.0, purpose_size=11, search_size=9):
    """Where a photo goes: the image's name, what it is for, what to search for. All of it must fit inside."""
    x, y, w, h = z
    box(s, x, y, w, h, fill=PH_FILL_D if dark else PH_FILL_W, line=PH_LINE_D if dark else PH_LINE_W, line_w=1.0,
        dash=True, name=f"Placeholder · {nome}")
    iw, head_h = w - 2 * pad, 0.17
    text(s, x + pad, y + pad, iw, head_h, f"IMAGEM · {nome.upper()}", size=8, bold=True, color=NEON if dark else GREEN_D,
         name="Placeholder label")
    search = "Procurar: " + search
    p_h, s_h = text_height(purpose, purpose_size, iw), text_height(search, search_size, iw)
    py = y + pad + head_h + 0.06
    text(s, x + pad, py, iw, p_h, purpose, size=purpose_size, color=WHITE if dark else INK, name="Placeholder purpose")
    sy = py + p_h + 0.06
    text(s, x + pad, sy, iw, s_h, search, size=search_size, color=MUTED_D if dark else MUTED_W, name="Placeholder search")
    need = sy + s_h - y + pad + reserve_bottom
    if need > h + 0.005:
        FIT_PROBLEMS.append(f"{nome}: needs {need:.2f}\" of {h:.2f}\"")


def chip(s, x, y, words, size=11, h=0.28, fill=CHIP, color=WHITE):
    w = text_width(words, size, True) + 0.24
    box(s, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name=f"Chip · {words}")
    text(s, x, y, w, h, words, size=size, bold=True, color=color, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         wrap=False)
    return w


def line_between(s, x1, y1, x2, y2, color, width=1.0):
    c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    c.name = "Line"
    return c


def sl_casa(prs):
    """A. Six connected things; the sixth, the camera, is the punchline (green outline)."""
    s = new_slide(prs, L_BLACK)
    title(s, "A casa já está toda ligada")
    y0 = content_top(True)
    cw, ih = (CW - 2 * GAP) / 3, (CONTENT_Y1 - y0 - GAP) / 2
    tiles = [("Porta", "Uma fechadura inteligente na porta: a casa já obedece a aparelhos ligados.",
              "smart lock door"),
             ("Frigorífico", "Um frigorífico com ecrã: até a cozinha está ligada à internet.", "smart fridge touchscreen"),
             ("Taça do cão", "Comedouro automático com um cão: o exemplo inesperado, que faz sorrir.",
              "automatic pet feeder dog"),
             ("Luz", "Uma lâmpada inteligente acesa, controlada pelo telemóvel.", "smart bulb phone app"),
             ("Ar condicionado", "Um ar condicionado de parede, com o comando na mão.", "air conditioner remote home"),
             ("Câmara", "Uma câmara de interior numa estante: a peça que falta.",
              "indoor home security camera shelf")]
    for i, (lab, purpose, search) in enumerate(tiles):
        r, c = divmod(i, 3)
        x, y = CONTENT_X0 + c * (cw + GAP), y0 + r * (ih + GAP)
        placeholder(s, (x, y, cw, ih), lab, purpose, search, reserve_bottom=0.36)
        chip(s, x + 0.12, y + ih - 0.12 - 0.28, lab)
        if i == 5:
            box(s, x, y, cw, ih, line=NEON, line_w=2.25, name="A peça que falta")
    return s


def sl_vigiar(prs):
    """B. What the camera has been (watching) against what vision is (understanding)."""
    s = new_slide(prs, L_BLACK)
    title(s, "Até hoje, a câmara serviu para vigiar")
    y0 = content_top(True)
    lw = round((CW - GAP) * 0.6, 3)
    rx, rw = CONTENT_X0 + lw + GAP, CW - lw - GAP
    placeholder(s, (CONTENT_X0, y0, lw, CONTENT_Y1 - y0), "vigilância",
                "Uma vista de videovigilância a preto e branco, uma grelha de câmaras num monitor ou num telemóvel: "
                "o que a câmara é hoje.", "cctv monitor grid, security camera app phone", reserve_bottom=0.36)
    cx = CONTENT_X0 + 0.12
    for t in ["Movimento", "Intrusão", "Ver em direto"]:
        cx += chip(s, cx, CONTENT_Y1 - 0.12 - 0.28, t) + 0.10
    words = "A visão é o sentido com que percebemos o mundo."
    ch = text_height(words, 12, rw)
    ih = CONTENT_Y1 - y0 - CAPTION_GAP - ch
    placeholder(s, (rx, y0, rw, ih), "olho", "Um olho humano em grande plano, a cores: a visão é como percebemos o mundo.",
                "human eye macro")
    text(s, rx, y0 + ih + CAPTION_GAP, rw, ch, words, size=12, color=WHITE, name="Caption")
    return s


def sl_reveal(prs):
    """C. The reveal, on white: the logo and its line; the camera in the middle of the kit's real devices."""
    s = new_slide(prs, L_WHITE)
    grey = RGBColor(0x9A, 0xA0, 0xA6)
    # left: the logo and one line, centred in the area above the "A seguir" row
    area0, area1 = CONTENT_Y0_NO_TITLE, 4.05
    lw, logo_w = 4.15, 3.9
    logo_h = logo_w * 414 / 2400
    line = "Uma câmara que percebe o que vê, ligada a toda a casa pelo MCP da Altice."
    lh = text_height(line, 18, lw)
    y = area0 + (area1 - area0 - (logo_h + 0.25 + lh)) / 2
    picture(s, LOGO_LIGHT, CONTENT_X0, y, w=logo_w, alt="ThingTracker")
    text(s, CONTENT_X0, y + logo_h + 0.25, lw, lh, line, size=18, color=INK)
    # right: the hub
    cx, cy, rx, ry, d, cd = 7.225, 2.40, 1.95, 0.95, 0.62, 1.05
    head = "Hoje · kit Altice"
    text(s, cx - 1.0, area0, 2.0, 0.18, head, size=10, bold=True, color=GREEN_D, align=PP_ALIGN.CENTER)
    import math
    devices = [(0, "climate-sensor.png", "Temperatura"), (60, "smart-plug.png", "Tomada"),
               (120, "smart-bulb.png", "Lâmpada"), (180, "contact-sensor.png", "Sensor da porta"),
               (240, "gateway.jpg", "Central"), (300, "smoke-alarm.png", "Fumo")]
    pos = [(a, f, lab, cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a, f, lab in devices]
    for _, _, _, px, py in pos:
        line_between(s, cx, cy, px, py, grey)
    for a, f, lab, px, py in pos:
        z = (px - d / 2, py - d / 2, d, d)
        box(s, *z, fill=TILE_L, shape=MSO_SHAPE.OVAL, name=f"Device · {lab}")
        if f.endswith(".jpg"):
            pic = pic_cover(s, jpg(DEV / f), z, alt=lab)
            pic.auto_shape_type = MSO_SHAPE.OVAL
        else:
            picture(s, DEV / f, z[0] + 0.09, z[1] + 0.09, fit=(d - 0.18, d - 0.18), alt=lab)
        ly = py - d / 2 - 0.03 - 0.16 if 180 < a < 360 else py + d / 2 + 0.03
        text(s, px - 0.6, ly, 1.2, 0.16, lab, size=9, color=MUTED_W, align=PP_ALIGN.CENTER)
    box(s, cx - cd / 2, cy - cd / 2, cd, cd, fill=WHITE, line=GREEN_D, line_w=2.0, shape=MSO_SHAPE.OVAL, name="Camera")
    picture(s, ASSETS / "kit-camera.png", cx - cd / 2 + 0.14, cy - cd / 2 + 0.14, fit=(cd - 0.28, cd - 0.28),
            alt="A câmara do kit")
    pw = text_width("MCP da Altice", 9, True) + 0.2
    py0 = cy + cd / 2 + 0.07
    box(s, cx - pw / 2, py0, pw, 0.22, fill=GREEN_D, shape=MSO_SHAPE.ROUNDED_RECTANGLE, name="MCP")
    text(s, cx - pw / 2, py0, pw, 0.22, "MCP da Altice", size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, wrap=False)
    # bottom: what comes next
    ry0, rh = 4.30, 0.42
    text(s, CONTENT_X0, ry0, 0.95, rh, "A seguir", size=11, bold=True, color=GREEN_D, anchor=MSO_ANCHOR.MIDDLE)
    nxt = ["Ar condicionado", "Monitor de saúde", "Frigorífico", "Máquina de lavar", "Computador"]
    bx0 = CONTENT_X0 + 0.95
    bw = (CONTENT_X1 - bx0 - 4 * 0.12) / 5
    for i, n in enumerate(nxt):
        bx = bx0 + i * (bw + 0.12)
        box(s, bx, ry0, bw, rh, fill=PH_FILL_W, line=grey, dash=True, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
            name=f"Next · {n}")
        text(s, bx, ry0, bw, rh, n, size=10, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


def sl_basta(prs):
    """D. Four images a person reads in one second; the child is our real photo, the rest are placeholders."""
    s = new_slide(prs, L_BLACK)
    title(s, "Basta uma imagem para perceber")
    y0 = content_top(True)
    n, cap_h = 4, 0.3
    cw = (CW - (n - 1) * GAP) / n
    ih = cw * 5 / 4
    top = y0 + (CONTENT_Y1 - y0 - (ih + CAPTION_GAP + cap_h)) / 2
    items = [("Criança em perigo", None, None, None),
             ("Faca à porta, às 4h", "faca à porta",
              "Uma pessoa encapuzada à porta de casa, de noite, vista de cima como por uma câmara; junta-se um carimbo "
              "“04:12”.", "hooded person door night"),
             ("Comprimidos por tomar", "comprimidos",
              "Mãos de uma pessoa idosa e uma caixa semanal de comprimidos com o dia de hoje ainda cheio.",
              "weekly pill organizer elderly hands"),
             ("Carteira esquecida", "carteira",
              "Uma carteira e chaves na mesa da entrada, com a porta a fechar-se ao fundo.", "wallet keys entryway table")]
    for i, (capt, nome, purpose, search) in enumerate(items):
        x = CONTENT_X0 + i * (cw + GAP)
        z = (x, top, cw, ih)
        if nome is None:
            pic_cover(s, jpg(ASSETS / "crianca2-cena-deck.jpg"), z, cx=0.5, cy=0.5,
                      alt="Uma criança na cozinha com uma cápsula de detergente na boca; rosto desfocado")
        else:
            placeholder(s, z, nome, purpose, search)
        text(s, x, top + ih + CAPTION_GAP, cw, cap_h, capt, size=13, bold=True, color=WHITE, wrap=False, name="Caption")
        if text_width(capt, 13, True) > cw:
            FIT_PROBLEMS.append(f"caption {capt!r} wider than {cw:.2f}\"")
    return s


def sl_ilusao(prs):
    """E (5 min only). A still image the eyes see moving; the camera's honest advantage."""
    s = new_slide(prs, L_BLACK)
    title(s, "Os olhos também se enganam")
    y0 = content_top(True)
    lw = round((CW - GAP) * 0.6, 3)
    placeholder(s, (CONTENT_X0, y0, lw, CONTENT_Y1 - y0), "ilusão",
                "Uma imagem parada que os olhos veem a mexer (ilusão de movimento periférico). Usar uma de domínio "
                "público da Wikimedia Commons; as “Rotating Snakes” de Kitaoka precisam de autorização.",
                "peripheral drift illusion wikimedia commons")
    words = "A câmara não se cansa, não se distrai e está atenta às 4 da manhã."
    rx, rw = CONTENT_X0 + lw + GAP, CW - lw - GAP
    sh = text_height(words, 26, rw, bold=True)
    text(s, rx, y0 + (CONTENT_Y1 - y0 - sh) / 2, rw, sh, words, size=26, bold=True, color=WHITE)
    return s


PITCH_NOTES.update({
    "casa": "A CASA JÁ ESTÁ TODA LIGADA. 3 min: sim · 5 min: sim. Cerca de 20 s.\n"
            "Dizer: “Hoje, quase tudo em casa está ligado à internet: a fechadura da porta, o frigorífico, até a taça do "
            "cão. E isso já permite coisas muito úteis. Mas ainda falta uma peça. De todos estes aparelhos, há um que pode "
            "abrir uma realidade nova na casa inteligente. E é tão simples como uma câmara.”",
    "vigiar": "ATÉ HOJE, A CÂMARA SERVIU PARA VIGIAR. 3 min: sim · 5 min: sim. Cerca de 20 s.\n"
              "Dizer: “Há anos que a câmara serve sobretudo para segurança. Deteta movimento, as mais avançadas avisam de "
              "uma intrusão, e deixa-nos ver a casa à distância. Mas a visão vale muito mais. É o principal sentido do "
              "corpo humano: é com ela que percebemos o mundo. E foi por isso que criámos…”\n"
              "Cuidado: o júri inclui a Altice. Dizer “até hoje a câmara serviu sobretudo para segurança”, nunca “a "
              "câmara da Altice só deteta movimento”.",
    "reveal": "THINGTRACKER. 3 min: sim · 5 min: sim. Cerca de 17 s.\n"
              "Dizer: “…o ThingTracker. Uma câmara, ligada a todos os aparelhos da casa através do MCP da Altice. Funciona "
              "com os aparelhos do kit que recebemos, e com todos os que vierem: o ar condicionado, os monitores de saúde, "
              "o frigorífico, qualquer máquina, o computador.”",
    "basta": "BASTA UMA IMAGEM PARA PERCEBER. 3 min: sim · 5 min: sim. Cerca de 20 s.\n"
             "Dizer: “Com uma única imagem, o nosso cérebro percebe logo o que se passa: uma criança com uma cápsula de "
             "detergente na boca; alguém de faca na mão à porta, às quatro da manhã; o meu avô, que hoje ainda não tomou "
             "os comprimidos; a carteira que ficou em casa. A IA já faz o mesmo. E em certas situações faz melhor: não se "
             "cansa, não se distrai, e está atenta às quatro da manhã. Nós mostramos um destes casos, com modelos abertos, "
             "a correr num portátil.”\n"
             "Não dizer “99 % dos casos”: não há fonte. Dizer “quase todos estes casos já são possíveis hoje”.",
    "ilusao": "OS OLHOS TAMBÉM SE ENGANAM. 3 min: não · 5 min: sim. Cerca de 15 s.\n"
              "Dizer: “Um professor de visão por computador mostrou-nos imagens paradas que os nossos olhos veem a mexer. "
              "Os olhos humanos também se enganam. Uma câmara não se cansa e não se distrai.”\n"
              "Cuidado: há redes neuronais que também “veem” esta ilusão (Watanabe et al., Frontiers in Psychology, 2018). "
              "Não dizer que a máquina nunca se engana.",
})

NARRATIVE = [("casa", sl_casa), ("vigiar", sl_vigiar), ("reveal", sl_reveal), ("basta", sl_basta),
             ("ilusao", sl_ilusao)]
THREE_MIN = [("capa", sl_capa), ("intro", sl_intro), ("casa", sl_casa), ("vigiar", sl_vigiar), ("reveal", sl_reveal),
             ("basta", sl_basta), ("livro", sl_livro), ("altice", sl_altice), ("fecho", sl_fecho)]
FIVE_MIN = [("capa", sl_capa), ("intro", sl_intro), ("casa", sl_casa), ("vigiar", sl_vigiar), ("reveal", sl_reveal),
            ("basta", sl_basta), ("ilusao", sl_ilusao), ("exemplos", sl_exemplos), ("como", sl_como),
            ("viabilidade", sl_viabilidade), ("comecar", sl_comecar), ("fecho", sl_fecho)]
ANNEX = [("anexo-implantacao", "Anexo · Onde corre cada parte", "implantacao.png"),
         ("anexo-presenca", "Anexo · Quem está em casa", "presenca-estados.png"),
         ("anexo-contentores", "Anexo · Os contentores", "c4-2-contentores.png"),
         ("anexo-fronteiras", "Anexo · O que sai de casa", "dfd-fronteiras.png"),
         ("anexo-livro", "Anexo · O livro esquecido", "seq-livro-esquecido.png"),
         ("anexo-pessoa", "Anexo · A pessoa desconhecida", "seq-pessoa-desconhecida.png"),
         ("anexo-casa-vazia", "Anexo · A casa vazia", "seq-casa-vazia.png")]


def build_decks(template, outdir):
    global JPEG_DIR
    out = Path(outdir)
    JPEG_DIR = out / "_jpeg"
    JPEG_DIR.mkdir(parents=True, exist_ok=True)
    for name, slides in [("ThingTracker - Pitch 3 min.pptx", THREE_MIN), ("ThingTracker - Pitch 5 min.pptx", FIVE_MIN),
                         ("ThingTracker - Narrativa A-E.pptx", NARRATIVE)]:
        prs = open_template(template)
        for key, make in slides:
            set_notes(make(prs), PITCH_NOTES[key])
        prs.save(out / name)
    prs = open_template(template)
    for sid, head, png in ANNEX:
        set_notes(sl_annex(prs, head, png), notes_from_source(sid) or "Só para perguntas.")
    prs.save(out / "ThingTracker - Anexo (perguntas).pptx")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "guide" and len(sys.argv) == 4:
        print("wrote", build_guide(sys.argv[2], sys.argv[3]))
    elif cmd == "decks" and len(sys.argv) == 4:
        print("wrote into", build_decks(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
