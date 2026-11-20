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


def build_guide(template, out):
    prs = open_template(template)
    for dark, has_title in [(True, True), (True, False), (False, True), (False, False)]:
        guide_slide(prs, dark, has_title)
    guide_cover(prs)
    prs.save(out)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "guide" and len(sys.argv) == 4:
        print("wrote", build_guide(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
