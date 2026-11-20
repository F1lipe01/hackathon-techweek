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


def v_afirmacao():
    y0 = CONTENT_Y0_NO_TITLE
    third = (CONTENT_Y1 - y0) / 3
    tw = (CW - GAP) * 2 / 3
    return {"frase": (CONTENT_X0, y0, tw, third), "subfrase": (CONTENT_X0, y0 + third + GAP, tw, 0.5),
            "imagem": (CONTENT_X0 + tw + GAP, y0, CW - tw - GAP, CONTENT_Y1 - y0)}


def v_imagem(has_title=False):
    y0 = content_top(has_title)
    return {"imagem": (CONTENT_X0, y0, CW, CONTENT_Y1 - y0), "faixa": (CONTENT_X0, CONTENT_Y1 - STRIP_H, 4.2, STRIP_H)}


def v_duas_colunas(has_title=True):
    y0 = content_top(has_title)
    cw = (CW - GAP) / 2
    lab_h, cap_h = 0.22, 0.25
    z = {}
    for i, k in enumerate(["esq", "dir"]):
        x = CONTENT_X0 + i * (cw + GAP)
        img_y = y0 + lab_h + CAPTION_GAP
        img_h = CONTENT_Y1 - img_y - CAPTION_GAP - cap_h
        z[f"{k}-rotulo"] = (x, y0, cw, lab_h)
        z[f"{k}-imagem"] = (x, img_y, cw, img_h)
        z[f"{k}-legenda"] = (x, img_y + img_h + CAPTION_GAP, cw, cap_h)
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


def v_grelha(n=3, rows=1, ratio=16 / 9, has_title=True):
    y0 = content_top(has_title)
    cw = (CW - (n - 1) * GAP) / n
    ih = cw / ratio
    cap_h = 0.25
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


def gv_afirmacao(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("afirmacao", False)
    z = v_afirmacao()
    g.words(z["frase"], "frase · Arial Bold 40 pt · terço de cima", "Uma frase grande, no terço de cima", 40, bold=True)
    g.words(z["subfrase"], "subfrase (opcional) · 16 pt", "Uma linha pequena, se for precisa", 16, color=g.muted)
    g.image(z["imagem"], "imagem ou recorte (opcional)", "imagem ou recorte")
    return s, "Afirmação: sem título. Uma frase grande (Arial Bold 40 pt) no terço de cima da zona de conteúdo, uma " \
              "subfrase opcional e, à direita, uma imagem ou um recorte opcional. Sem imagem, a frase pode ocupar toda a largura."


def gv_imagem(prs):
    s = new_slide(prs, L_BLACK)
    g = Guide(s, True)
    g.frame("imagem", False)
    z = v_imagem(False)
    g.image(z["imagem"], "imagem ou fotograma · preenche a zona (cover) · com título, começa em y 1,50",
            "imagem ou fotograma do filme")
    fx, fy, fw, fh = z["faixa"]
    band = box(s, fx, fy, fw, fh, fill=RGBColor(0, 0, 0))
    _alpha(band, 60)
    text(s, fx + 0.14, fy, fw - 0.2, fh, "Legenda opcional, faixa escura, 12 pt", size=12, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    g.outline(z["faixa"], "faixa de legenda", inside=False, align=PP_ALIGN.LEFT)
    return s, "Imagem: uma imagem ou um fotograma enche a zona de conteúdo (cover); título opcional (com título, a " \
              "imagem começa em y 1,50). Legenda opcional numa faixa escura translúcida, em baixo à esquerda, 12 pt. Para os filmes."


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


VARIANT_GUIDES = [gv_capa, gv_afirmacao, gv_imagem, gv_duas_colunas, gv_fluxo, gv_numero, gv_grelha, gv_fecho]


def build_guide(template, out):
    prs = open_template(template)
    for dark, has_title in [(True, True), (True, False), (False, True), (False, False)]:
        guide_slide(prs, dark, has_title)
    for make in VARIANT_GUIDES:
        s, note = make(prs)
        set_notes(s, note + " As linhas a laranja não entram nos diapositivos.")
    prs.save(out)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "guide" and len(sys.argv) == 4:
        print("wrote", build_guide(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
