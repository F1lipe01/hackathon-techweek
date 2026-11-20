"""Build the pitch as a PowerPoint on the organisers' template (Aveiro Tech City Hackathon).

    python build_pptx.py TEMPLATE.pptx BUILD_DIR OUT_5MIN.pptx OUT_3MIN.pptx

TEMPLATE.pptx is the organisers' file (kept out of the repo). BUILD_DIR receives the film stills and the pixel icons.
Slide texts are short on purpose; what is said goes in the speaker notes, read from the deck's own source
(../source/slides/<id>.html, the <aside> of each slide), so the PowerPoint and the Slides deck say the same.
The template's slides are removed; its layouts stay: 0 = cover, 1 = black frame, 9 = white frame.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
IMG = HERE / "img"
SRC = HERE.parent / "source" / "slides"
FILMS = REPO / "video" / "out" / "pitch"
DIAG = REPO / "docs" / "architecture"
LOGO = REPO / "assets" / "brand" / "logo" / "thingtracker-dark.png"

NEON = RGBColor(0x00, 0xFC, 0x75)      # the template's HACKATHON green
GREEN_D = RGBColor(0x00, 0x78, 0x00)   # the template's dark pixel green, for text on white
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY_L = RGBColor(0xD0, 0xD4, 0xD8)
GREY_M = RGBColor(0x9A, 0xA0, 0xA6)
INK = RGBColor(0x11, 0x11, 0x11)
BODY = RGBColor(0x40, 0x40, 0x40)
TILE_W = RGBColor(0xF0, 0xF2, 0xF0)
TILE_D = RGBColor(0x1A, 0x1C, 0x1E)
RED = RGBColor(0xFF, 0x1F, 0x20)
ORANGE = RGBColor(0xEF, 0x78, 0x0B)
FONT = "Arial"


# ---------- helpers ----------

def runs_of(text):
    """'a _kit_ b' -> [('a ', False), ('kit', True), (' b', False)]: underscores mark English terms, set in italics."""
    out, parts = [], re.split(r"(_[^_]+_)", text)
    for p in parts:
        if not p:
            continue
        if p.startswith("_") and p.endswith("_"):
            out.append((p[1:-1], True))
        else:
            out.append((p, False))
    return out


def text(slide, x, y, w, h, paras, size=14, color=WHITE, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         font=FONT, spacing=None, name=None):
    """paras: a string, or a list of strings / (string, {size, color, bold, italic}) tuples, one per paragraph."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        opts = {}
        if isinstance(para, tuple):
            para, opts = para
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
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


def box(slide, x, y, w, h, fill=None, line=None, line_w=1.5, shape=MSO_SHAPE.RECTANGLE, dash=False, name=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
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
            s.line.dash_style = 4  # dash
    style = s._element.find(qn("p:style"))  # no theme effects: LibreOffice and PowerPoint would add a shadow
    if style is not None:
        s._element.remove(style)
    return s


def picture(slide, path, x, y, w=None, h=None, fit=None, name=None, alt=None):
    """fit=(w, h): scale the image to fit inside the box, centred (object-fit: contain)."""
    if fit:
        bw, bh = fit
        with Image.open(path) as im:
            iw, ih = im.size
        s = min(bw / iw, bh / ih)
        w, h = iw * s, ih * s
        x, y = x + (bw - w) / 2, y + (bh - h) / 2
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if name:
        pic.name = name
    if alt:
        pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic


def pixel(slide, x, y, s=0.13, color=NEON):
    """The template's motif: one square pixel."""
    return box(slide, x, y, s, s, fill=color)


def title(slide, words, dark=True, y=1.02):
    pixel(slide, 0.5, y + 0.1, color=NEON if dark else GREEN_D)
    text(slide, 0.75, y, 8.75, 0.5, words, size=26, bold=True, color=WHITE if dark else INK, name="Title")


def eyebrow(slide, x, y, words, dark=True, w=4.0):
    text(slide, x, y, w, 0.25, words.upper(), size=10, bold=True, color=NEON if dark else GREEN_D)


def notes_from_source(sid):
    f = SRC / f"{sid}.html"
    if not f.exists():
        return ""
    m = re.search(r"<aside>(.*?)</aside>", f.read_text(encoding="utf-8"), re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def set_notes(slide, notes):
    slide.notes_slide.notes_text_frame.text = notes


def new_slide(prs, layout):
    s = prs.slides.add_slide(prs.slide_layouts[layout])
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


# ---------- assets made at build time ----------

def film_still(build, name, video, t):
    out = build / f"still-{name}.jpg"
    if not out.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(FILMS / video), "-frames:v", "1", "-q:v", "3", str(out)],
                       check=True)
    return out


PIX = {
    "laptop": [
        "..GGGGGGGGGG..",
        "..G........G..",
        "..G.WWWWWW.G..",
        "..G.WWWWWW.G..",
        "..G.WWWWWW.G..",
        "..G........G..",
        "..GGGGGGGGGG..",
        "GGGGGGGGGGGGGG",
        ".GGGGGGGGGGGG.",
    ],
    "house": [
        "......RR......",
        ".....RRRR.....",
        "....RRRRRR....",
        "...RRRRRRRR...",
        "..RRRRRRRRRR..",
        "...WWWWWWWW...",
        "...WGGWWGGW...",
        "...WGGWWGGW...",
        "...WWWOOWWW...",
        "...WWWOOWWW...",
        "OOOOOOOOOOOOOO",
    ],
    "server": [
        "GGGGGGGGGGGG",
        "G.YY.......G",
        "GGGGGGGGGGGG",
        "G.YY.......G",
        "GGGGGGGGGGGG",
        "G.YY.......G",
        "GGGGGGGGGGGG",
        ".....GG.....",
        "..OOOOOOOO..",
    ],
}
PIX.update({
    "camera": [
        "...GGG......",
        "GGGGGGGGGGGG",
        "GGGGWWWWGGGG",
        "GGGW....WGGG",
        "GGGW.YY.WGGG",
        "GGGW....WGGG",
        "GGGGWWWWGGGG",
        "GGGGGGGGGGGG",
    ],
    "frames": [
        "GGGGGGGG...",
        "G......G...",
        "G..WWWWWWWW",
        "G..W......W",
        "GGGW..YY..W",
        "...W......W",
        "...WWWWWWWW",
    ],
    "chip": [
        "..Y..Y..Y..",
        ".GGGGGGGGG.",
        "YG.......GY",
        ".G..WWW..G.",
        "YG..WWW..GY",
        ".G.......G.",
        ".GGGGGGGGG.",
        "..Y..Y..Y..",
    ],
    "phone": [
        "GGGGGGGG",
        "G......G",
        "G.RRRR.G",
        "G......G",
        "G.WWWW.G",
        "G.WWWW.G",
        "G......G",
        "GGGGGGGG",
        "...GG...",
    ],
})
PIX_COL = {"G": (0, 207, 117), "W": (255, 255, 255), "R": (255, 31, 32), "O": (239, 120, 11), "Y": (239, 207, 0)}


def crop_to(build, src, name, ratio, cx=0.5, cy=0.5):
    """Crop an image to width/height = ratio around the focus point (cx, cy), as fractions."""
    out = build / f"crop-{name}.jpg"
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w / h > ratio:
            nw, nh = int(h * ratio), h
        else:
            nw, nh = w, int(w / ratio)
        x = min(max(int(cx * w - nw / 2), 0), w - nw)
        y = min(max(int(cy * h - nh / 2), 0), h - nh)
        im.crop((x, y, x + nw, y + nh)).save(out, quality=92)
    return out


def arrow_line(slide, x1, y1, x2, y2, color, width=2.0):
    c = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    c.name = "Arrow"
    return c


def pixel_icon(build, name, white_bg):
    out = build / f"pix-{name}-{'w' if white_bg else 'd'}.png"
    rows = PIX[name]
    cell = 40
    im = Image.new("RGBA", (len(rows[0]) * cell, len(rows) * cell), (0, 0, 0, 0))
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            c = PIX_COL[ch]
            if ch == "W" and white_bg:
                c = (60, 60, 60)
            for yy in range(j * cell, (j + 1) * cell):
                for xx in range(i * cell, (i + 1) * cell):
                    im.putpixel((xx, yy), c + (255,))
    im.save(out)
    return out


# ---------- slides ----------

def s_cover(prs, b):
    s = new_slide(prs, 0)
    picture(s, LOGO, 0.36, 2.2, w=2.9, name="ThingTracker", alt="ThingTracker")
    text(s, 0.36, 2.82, 3.9, 0.3, "A câmara da casa, atenta ao que importa.", size=14, color=WHITE)
    text(s, 0.36, 3.22, 3.9, 0.25, "Desafio #3 · Altice Labs · Equipa IT-Porto", size=11, bold=True, color=NEON)
    text(s, 0.36, 3.5, 3.9, 0.25, "Filipe Peixoto · Simon Ranjith · Mushahid Hussain", size=11, color=GREY_L)
    return s


def s_hoje(prs, b):
    s = new_slide(prs, 1)
    title(s, "Hoje, a câmara de casa só grava")
    x, y, w, h = 2.25, 2.2, 5.5, 1.25
    box(s, x, y, w, h, fill=RGBColor(0x26, 0x28, 0x2C), shape=MSO_SHAPE.ROUNDED_RECTANGLE, name="Notification")
    box(s, x + 0.25, y + 0.27, 0.7, 0.7, fill=RGBColor(0x3A, 0x3D, 0x42), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    picture(s, pixel_icon(b, "camera", False), x + 0.33, y + 0.42, w=0.54, alt="Câmara")
    text(s, x + 1.15, y + 0.25, 3.0, 0.25, "Câmara · Sala", size=11, color=GREY_M)
    text(s, x + w - 1.0, y + 0.25, 0.75, 0.25, "agora", size=11, color=GREY_M, align=PP_ALIGN.RIGHT)
    text(s, x + 1.15, y + 0.55, 4.1, 0.45, "Movimento detetado", size=22, bold=True, color=WHITE)
    return s


def s_possivel(prs, b):
    s = new_slide(prs, 1)
    title(s, "Câmara + IA: a casa percebe o que vê")
    cases = [("As chaves esquecidas", IMG / "problema-chaves.jpg", 0.5, 0.5, "Chaves em cima da mesa da entrada"),
             ("A criança em perigo", IMG / "conceito-crianca.jpg", 0.42, 0.32, "Uma criança com uma cápsula de detergente"),
             ("Os comprimidos do pai", IMG / "conceito-pai.jpg", 0.5, 0.42, "Um homem idoso ao pequeno-almoço"),
             ("O gato na bancada", IMG / "possivel-gato.jpg", 0.66, 0.44, "Um gato em cima da bancada da cozinha"),
             ("A luz que ficou acesa", film_still(b, "luz", "ThingTracker - pitch - ninguém em casa (20 s).mp4", 9.0), 0.5, 0.45,
              "Imagem do filme: a sala com as luzes acesas"),
             ("Um desconhecido em casa", film_still(b, "desconhecido", "ThingTracker - pitch - pessoa desconhecida (20 s).mp4", 13.0),
              0.47, 0.45, "Imagem do filme: um desconhecido na sala")]
    w, ih = 2.88, 0.95
    for i, (cap, src, cx, cy, alt) in enumerate(cases):
        x, y = 0.5 + (i % 3) * (w + 0.18), 1.62 + (i // 3) * 1.36
        picture(s, crop_to(b, src, f"possivel-{i}", w / ih, cx, cy), x, y, w=w, h=ih, alt=alt)
        text(s, x, y + ih + 0.06, w, 0.25, cap, size=12, bold=True, color=WHITE)
    text(s, 0.5, 4.36, 9.0, 0.28, "Cada família cria os seus, com uma frase.", size=14, bold=True, color=NEON)
    return s


def s_thingtracker(prs, b):
    s = new_slide(prs, 9)
    title(s, "Por isso criámos o _ThingTracker_", dark=False)
    steps = [("Câmara", "a câmara da Altice", "camera"), ("Imagens", "só quando há movimento", "frames"),
             ("IA", "reconhece o livro, a família, a casa vazia", "chip"), ("Aviso", "na app da Altice", "phone")]
    w, gap, x = 1.8, 0.6, 0.5
    for i, (h, lab, icon) in enumerate(steps):
        last = i == 3
        box(s, x, 1.85, w, 1.35, fill=NEON if last else TILE_W, name=f"Step {h}")
        picture(s, pixel_icon(b, icon, True), x + (w - 0.55) / 2, 2.0, h=0.5, alt=h)
        text(s, x, 2.65, w, 0.4, h, size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
        text(s, x, 3.32, w, 0.6, lab, size=11, color=BODY, align=PP_ALIGN.CENTER)
        if i < 3:
            arrow_line(s, x + w + 0.1, 2.52, x + w + gap - 0.1, 2.52, GREEN_D)
        x += w + gap
    return s


def s_comecar(prs, b):
    s = new_slide(prs, 9)
    title(s, "Como começamos", dark=False)
    box(s, 0.5, 1.68, 9.0, 0.62, fill=NEON)
    text(s, 0.7, 1.68, 8.6, 0.62, "Um piloto em casas de colaboradores da MEO", size=20, bold=True, color=INK,
         anchor=MSO_ANCHOR.MIDDLE)
    eyebrow(s, 0.5, 2.55, "O que precisa, e já existe", dark=False, w=6)
    needs = [("A câmara do _kit_", "camera"), ("A app da Altice", "phone"), ("O servidor MCP", "server")]
    x, w = 0.5, 2.88
    for n, icon in needs:
        box(s, x, 2.85, w, 1.25, fill=TILE_W)
        picture(s, pixel_icon(b, icon, True), x + 0.25, 3.12, h=0.6, alt=n)
        text(s, x + 1.25, 3.12, w - 1.4, 0.6, n, size=15, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
        x += w + 0.18
    text(s, 0.5, 4.28, 9.0, 0.28, "GPU alugadas, sem custo fixo", size=13, color=BODY)
    return s


def s_problema(prs, b):
    s = new_slide(prs, 1)
    title(s, "Pequenas preocupações de todos os dias")
    items = [("problema-chaves.jpg", "Comodidade", "“Onde deixei as chaves?”", "Chaves em cima da mesa da entrada"),
             ("problema-crianca.jpg", "Segurança", "“A criança está em segurança?”", "Brinquedos de criança no chão da sala"),
             ("problema-mae.jpg", "Bem-estar", "“A minha mãe está bem?”", "Uma senhora idosa a beber chá junto à janela"),
             ("problema-cao.jpg", "Animais", "“O cão já comeu?”", "Um cão a comer da taça")]
    w, gap, x = 2.1, 0.2, 0.5
    for f, k, q, alt in items:
        picture(s, IMG / f, x, 1.72, w=w, h=w * 600 / 784, alt=alt)
        eyebrow(s, x, 3.42, k, w=w)
        text(s, x, 3.66, w, 0.6, q, size=13, bold=True, color=WHITE)
        x += w + gap
    return s


def s_ideia(prs, b):
    s = new_slide(prs, 1)
    title(s, "A câmara passa a perceber o que vê")
    verbs = [("1", "Ver", "só quando há movimento"), ("2", "Perceber", "a criança e o detergente"),
             ("3", "Lembrar", "o quê, onde e quando"), ("4", "Agir", "avisa os pais, com a fotografia")]
    y = 1.75
    for n, v, d in verbs:
        sq = box(s, 0.75, y, 0.42, 0.42, fill=NEON)
        text(s, 0.75, y, 0.42, 0.42, n, size=16, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 1.35, y - 0.04, 4.0, 0.3, v, size=18, bold=True, color=WHITE)
        text(s, 1.35, y + 0.27, 4.0, 0.25, d, size=11, color=GREY_L)
        y += 0.7
    # the photo, cropped to the kitchen scene
    crop = b / "ideia-crop.jpg"
    with Image.open(IMG / "ideia-cozinha.jpg") as im:
        w, h = im.size  # portrait; keep the band with the child and the capsule
        ch = int(w * 2.95 / 3.2)
        top = min(330, h - ch)
        im.convert("RGB").crop((0, top, w, top + ch)).save(crop, quality=92)
    picture(s, crop, 6.0, 1.62, w=3.2, h=2.95, alt="Imagem gerada com IA: uma criança na cozinha, junto a um armário aberto, com uma cápsula de detergente")
    text(s, 6.0, 4.6, 3.2, 0.15, "Imagem gerada com IA · Gemini", size=7, color=GREY_M, align=PP_ALIGN.RIGHT)
    return s


def s_conceitos(prs, b):
    s = new_slide(prs, 1)
    title(s, "Uma frase basta")
    badge = box(s, 3.85, 1.1, 1.0, 0.32, fill=NEON, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, 3.85, 1.1, 1.0, 0.32, "Conceito", size=11, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cols = [(0.5, "“Avisa-me se a criança estiver em perigo.”", "conceito-crianca.jpg",
             "A criança pôs um detergente na boca.", "Cozinha · 16h30 · com fotografia",
             "Uma criança na cozinha com uma cápsula de detergente na boca; rosto e logótipos desfocados"),
            (5.1, "“Avisa-me se o pai não tomar os comprimidos até ao meio-dia.”", "conceito-pai.jpg",
             "O pai ainda não tomou os comprimidos.", "12h00 · para a filha",
             "Um homem idoso, de barba branca, à mesa do pequeno-almoço")]
    pw, ph = 4.4, 4.4 * 720 / 1616
    for x, rule, img, nt, nb, alt in cols:
        text(s, x, 1.6, pw, 0.5, rule, size=13, bold=True, color=WHITE)
        picture(s, IMG / img, x, 2.13, w=pw, h=ph, alt=alt)
        if "crianca" in img:
            k = pw / 808
            box(s, x + 191 * k, 2.13 + 9 * k, 332 * k, 340 * k, line=RED, line_w=2)
            box(s, x + 364 * k, 2.13 + 177 * k, 60 * k, 47 * k, line=RED, line_w=2)
            for tx, ty, tw, label in [(533, 16, 0.72, "criança"), (436, 172, 0.92, "detergente")]:
                box(s, x + tx * k, 2.13 + ty * k, tw, 0.2, fill=RED)
                text(s, x + tx * k, 2.13 + ty * k, tw, 0.2, label, size=9, bold=True, color=WHITE, font="Courier New",
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        box(s, x, 2.13 + ph + 0.1, pw, 0.52, fill=TILE_D)
        text(s, x + 0.15, 2.13 + ph + 0.15, pw - 0.3, 0.22, nt, size=12, bold=True, color=WHITE)
        text(s, x + 0.15, 2.13 + ph + 0.39, pw - 0.3, 0.2, nb, size=10, color=GREY_L)
    return s


def s_film(prs, b, kind):
    s = new_slide(prs, 1)
    spec = {
        "livro": ("As coisas: o livro esquecido",
                  "Filmado no nosso laboratório, com a câmara do _kit_ e o nosso protótipo; alguns momentos foram encenados.",
                  ("ThingTracker - pitch - o livro (20 s).mp4", 6.5),
                  "Imagem do filme: a porta fechou e o livro ficou na mesa, reconhecido a 0,96"),
        "desconhecido": ("A segurança: uma pessoa desconhecida",
                         "Com a família fora, o sistema distingue quem é da família de um desconhecido.",
                         ("ThingTracker - pitch - pessoa desconhecida (20 s).mp4", 13.0),
                         "Imagem do filme: com a família fora, um desconhecido pega no livro e o alarme toca"),
        "casa": ("A energia: ninguém em casa",
                 "Quando sai a última pessoa, a app propõe desligar o que ficou ligado.",
                 ("ThingTracker - pitch - ninguém em casa (20 s).mp4", 12.5),
                 "Imagem do filme: a sala às escuras; no telemóvel, a app propõe desligar a luz e o ar condicionado"),
    }[kind]
    head, line, (video, t), alt = spec
    eyebrow(s, 0.5, 1.12, "Filme")
    text(s, 0.5, 1.4, 3.2, 1.0, head, size=24, bold=True, color=WHITE)
    text(s, 0.5, 2.75, 3.1, 0.5, "Filmado no laboratório, com a câmara do _kit_", size=11, color=GREY_L)
    if kind == "livro":
        text(s, 0.5, 3.45, 3.2, 0.6, "68 de 68", size=36, bold=True, color=NEON)
        text(s, 0.5, 4.08, 3.2, 0.4, "fotogramas com o livro reconhecido, a 0,93", size=10, color=GREY_L)
    still = film_still(b, kind, video, t)
    picture(s, still, 3.9, 1.45, w=5.6, h=5.6 * 9 / 16, alt=alt)
    return s


def s_modelos(prs, b):
    s = new_slide(prs, 9)
    title(s, "Modelos e ferramentas", dark=False)
    eyebrow(s, 0.5, 1.68, "Modelos _open-source_, com uso comercial", dark=False, w=6)
    models = [("_OWLv2_", "Apache-2.0"), ("_DINOv2_", "Apache-2.0"), ("_YuNet_ e _SFace_", "MIT e Apache-2.0"),
              ("_Qwen3_", "Apache-2.0"), ("_Qwen2-VL_", "Apache-2.0 · opcional")]
    w, gap, x = 1.66, 0.175, 0.5
    for n, lic in models:
        box(s, x, 1.95, w, 0.78, fill=TILE_W)
        text(s, x + 0.14, 2.05, w - 0.2, 0.32, n, size=14, bold=True, color=INK)
        text(s, x + 0.14, 2.42, w - 0.2, 0.22, lic, size=10, color=BODY)
        x += w + gap
    eyebrow(s, 0.5, 2.95, "Ferramentas", dark=False)
    tools = [("Servidor MCP", "_Connected Home_ da Altice"), ("_Claude Code_", "_Claude Opus 5.5_ · desenvolvimento"),
             ("Em produção", "modelo de linguagem de pesos abertos, ou sob contrato")]
    w, gap, x = 2.88, 0.18, 0.5
    for n, d in tools:
        box(s, x, 3.22, w, 0.78, fill=TILE_W)
        text(s, x + 0.14, 3.32, w - 0.25, 0.3, n, size=14, bold=True, color=INK)
        text(s, x + 0.14, 3.66, w - 0.25, 0.3, d, size=10, color=BODY)
        x += w + gap
    text(s, 0.5, 4.18, 9.0, 0.3, "Os modelos veem · o código decide", size=14, bold=True, color=GREEN_D)
    return s


def s_proposta(prs, b):
    s = new_slide(prs, 9)
    title(s, "Como funciona", dark=False)
    box(s, 0.5, 1.72, 3.3, 2.3, fill=TILE_W)
    eyebrow(s, 0.7, 1.88, "Hoje, no protótipo", dark=False)
    picture(s, pixel_icon(b, "laptop", True), 0.7, 2.2, h=0.8, alt="Um portátil")
    text(s, 0.7, 3.12, 2.9, 0.7, "Um portátil faz de casa e de Altice", size=15, bold=True, color=INK)
    arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(3.98), Inches(2.67), Inches(0.5), Inches(0.36))
    arrow.fill.solid(); arrow.fill.fore_color.rgb = GREY_M; arrow.line.fill.background(); arrow.name = "Arrow"
    box(s, 4.65, 1.72, 4.85, 2.3, fill=None, line=GREEN_D, line_w=2.25)
    eyebrow(s, 4.85, 1.88, "Proposta", dark=False)
    picture(s, pixel_icon(b, "house", True), 4.85, 2.2, h=0.8, alt="Casa com o router")
    text(s, 4.85, 3.12, 2.1, 0.3, "_Router_", size=15, bold=True, color=INK)
    text(s, 4.85, 3.45, 2.1, 0.45, "em casa, sem _hardware_ novo", size=11, color=BODY)
    picture(s, pixel_icon(b, "server", True), 7.15, 2.2, h=0.8, alt="Servidores da Altice")
    text(s, 7.15, 3.12, 2.2, 0.3, "Servidores da Altice", size=15, bold=True, color=INK)
    text(s, 7.15, 3.45, 2.2, 0.45, "visão e regras", size=11, color=BODY)
    text(s, 0.5, 4.18, 9.0, 0.3, "Os modelos veem · o código decide", size=14, bold=True, color=GREEN_D)
    return s


def s_custos(prs, b):
    s = new_slide(prs, 1)
    title(s, "Quanto custa à Altice")
    text(s, 0.5, 1.75, 9.0, 1.5, "≈ 0,49 €", size=96, bold=True, color=NEON)
    text(s, 0.55, 3.3, 9.0, 0.45, "por casa e por mês", size=24, color=WHITE)
    text(s, 0.55, 4.3, 9.0, 0.25, "Estimativa da equipa para 500 000 casas, com preços públicos (documento 17, novembro de 2026)",
         size=9, color=GREY_M)
    return s


def s_custos_barras(prs, b):
    s = new_slide(prs, 1)
    title(s, "Quanto custa à Altice, por casa e por mês")
    text(s, 0.5, 1.75, 3.0, 0.9, "0,49 €", size=54, bold=True, color=NEON)
    text(s, 0.5, 2.7, 2.9, 0.6, "por casa e por mês, na opção híbrida", size=14, color=WHITE)
    bars = [("Uma caixa em cada casa", 6.55, 8.64, "6,55 a 8,64 €"), ("GPU alugadas na nuvem", 3.93, 4.26, "3,93 a 4,26 €"),
            ("Servidores da Altice, imagens completas", 2.41, 2.41, "2,41 €"), ("Opção híbrida", 0.49, 0.49, "0,49 €")]
    x0, wmax, vmax, y = 3.9, 4.2, 8.64, 1.72
    for i, (lab, lo, hi, val) in enumerate(bars):
        win = i == 3
        text(s, x0, y, 5.5, 0.22, lab, size=11, bold=win, color=NEON if win else WHITE)
        box(s, x0, y + 0.26, wmax * lo / vmax, 0.26, fill=NEON if win else GREY_M)
        if hi > lo:
            box(s, x0 + wmax * lo / vmax, y + 0.26, wmax * (hi - lo) / vmax, 0.26, fill=RGBColor(0x5A, 0x60, 0x66))
        text(s, x0 + wmax * hi / vmax + 0.1, y + 0.25, 1.3, 0.28, val, size=11, bold=True, color=NEON if win else WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
        y += 0.66
    text(s, x0, 4.4, 5.5, 0.22, "1,73 €: o máximo que a visão pode custar sem dar prejuízo", size=10, bold=True,
         color=RGBColor(0xFF, 0x6B, 0x6B))
    return s


def s_replicacao(prs, b):
    s = new_slide(prs, 1)
    title(s, "Replica-se noutros operadores e países")
    blocks = [("Uma câmara", "a que o operador já vende"), ("A app", "com o separador _Things_"),
              ("Uma interface", "como o MCP"), ("_ThingTracker_", "em qualquer operador")]
    x, w = 0.5, 1.85
    for i, (h, d) in enumerate(blocks):
        last = i == 3
        box(s, x, 1.78, w, 1.2, fill=NEON if last else TILE_D)
        text(s, x + 0.15, 1.95, w - 0.3, 0.35, h, size=15, bold=True, color=INK if last else WHITE)
        text(s, x + 0.15, 2.36, w - 0.3, 0.5, d, size=11, color=INK if last else GREY_L)
        if i < 3:
            text(s, x + w, 1.78, 0.55, 1.2, "=" if i == 2 else "+", size=26, bold=True, color=GREY_M,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += w + 0.55
    eyebrow(s, 0.5, 3.3, "Outros contextos")
    x = 0.5
    for p, w in [("Outros operadores", 1.95), ("Lares de idosos", 1.75), ("Pequenos negócios", 1.95), ("Alojamento local", 1.85)]:
        box(s, x, 3.62, w, 0.42, line=NEON, line_w=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(s, x, 3.62, w, 0.42, p, size=12, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += w + 0.2
    return s


def s_lancamento(prs, b):
    s = new_slide(prs, 9)
    title(s, "Como se começa", dark=False)
    steps = [("Passo 1", "O piloto", "Casas de colaboradores da MEO · GPU alugadas, sem custo fixo", "01"),
             ("Passo 2", "Os clientes", "3,99 € por mês", "02"),
             ("Passo 3", "Os _routers_ com IA", "A visão passa para casa · 0,36 € por casa", "03")]
    x, w = 0.5, 2.88
    for i, (k, h, d, n) in enumerate(steps):
        first = i == 0
        box(s, x, 1.72, w, 2.45, fill=NEON if first else TILE_W)
        text(s, x + 0.2, 1.88, w - 0.4, 0.22, k.upper(), size=10, bold=True, color=INK if first else GREEN_D)
        text(s, x + 0.2, 2.14, w - 0.4, 0.35, h, size=17, bold=True, color=INK)
        text(s, x + 0.2, 2.55, w - 0.4, 0.7, d, size=12, color=INK if first else BODY)
        text(s, x + 0.2, 3.35, w - 0.4, 0.7, n, size=40, bold=True, color=INK if first else GREEN_D)
        x += w + 0.18
    return s


def s_repositorio(prs, b):
    s = new_slide(prs, 9)
    title(s, "Está tudo no repositório", dark=False)
    tiles = [("Código", "o protótipo"), ("Arquitetura", "12 diagramas, PT e EN"), ("Custos", "modelos de cálculo"),
             ("107 testes", "todos a passar"), ("Filmes", "o que é real em cada um"), ("Execuções", "sem montagem")]
    for i, (h, d) in enumerate(tiles):
        x, y = 0.5 + (i % 3) * 3.06, 1.72 + (i // 3) * 1.0
        box(s, x, y, 2.88, 0.85, fill=TILE_W)
        pixel(s, x + 0.18, y + 0.2, color=GREEN_D)
        text(s, x + 0.42, y + 0.12, 2.3, 0.32, h, size=16, bold=True, color=INK)
        text(s, x + 0.42, y + 0.48, 2.3, 0.25, d, size=11, color=BODY)
    text(s, 0.5, 3.88, 9.0, 0.35, "github.com/F1lipe01/hackathon-techweek", size=18, bold=True, color=GREEN_D,
         font="Courier New")
    return s


def s_equipa(prs, b):
    s = new_slide(prs, 1)
    title(s, "Equipa IT-Porto")
    x = 0.5
    for n in ["Filipe Peixoto", "Simon Ranjith", "Mushahid Hussain"]:
        pixel(s, x, 2.35, s=0.18)
        text(s, x, 2.65, 2.9, 0.5, n, size=22, bold=True, color=WHITE)
        x += 3.0
    text(s, 0.5, 3.55, 9.0, 0.3, "Instituto de Telecomunicações", size=13, color=GREY_L)
    return s


def s_fecho(prs, b):
    s = new_slide(prs, 1)
    title(s, "Em resumo")
    y = 1.68
    for t in ["O reconhecimento já funciona na câmara do _kit_.", "Cerca de 0,49 € por casa e por mês.",
              "Usa a app e o MCP que a Altice já tem."]:
        pixel(s, 0.75, y + 0.08, s=0.16)
        text(s, 1.05, y, 8.2, 0.34, t, size=18, bold=True, color=WHITE)
        y += 0.42
    box(s, 0.75, 3.0, 6.6, 0.48, fill=NEON)
    text(s, 0.95, 3.0, 6.3, 0.48, "Propomos um piloto em casas de colaboradores da MEO.", size=15, bold=True, color=INK,
         anchor=MSO_ANCHOR.MIDDLE)
    picture(s, LOGO, 0.75, 3.62, h=0.3, alt="ThingTracker")
    text(s, 2.75, 3.6, 5.5, 0.34, "A câmara da casa, atenta ao que importa.", size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.75, 4.02, 8.5, 0.6, [
        "Imagens: arquivo da Pexels; as da criança, geradas com _Gemini_ e fornecidas pela equipa. Filmes: laboratório da equipa, "
        "com momentos encenados. Ferramentas: _OWLv2_, _DINOv2_, _YuNet_, _SFace_, _Qwen3_ e _Qwen2-VL_; o servidor MCP da Altice; "
        "_Claude Code_. Fontes: Eurostat, isoc_iiot_use, 2024; ANACOM, 2.º trimestre de 2026; estimativa de custos da equipa, "
        "novembro de 2026. github.com/F1lipe01/hackathon-techweek"], size=8, color=GREY_M)
    return s


def s_divider(prs, b):
    s = new_slide(prs, 1)
    pixel(s, 0.5, 2.3, s=0.22)
    text(s, 0.85, 2.17, 8.5, 0.5, "Anexo e reserva", size=30, bold=True, color=WHITE)
    text(s, 0.85, 2.75, 8.5, 0.3, "Para as perguntas do júri: a arquitetura em pormenor", size=14, color=GREY_L)
    return s


ANNEX = [("anexo-implantacao", "Anexo · Onde corre cada parte", "implantacao.png"),
         ("anexo-presenca", "Anexo · Quem está em casa", "presenca-estados.png"),
         ("anexo-contentores", "Anexo · Os contentores", "c4-2-contentores.png"),
         ("anexo-fronteiras", "Anexo · O que sai de casa", "dfd-fronteiras.png"),
         ("anexo-livro", "Anexo · O livro esquecido", "seq-livro-esquecido.png"),
         ("anexo-pessoa", "Anexo · A pessoa desconhecida", "seq-pessoa-desconhecida.png"),
         ("anexo-casa-vazia", "Anexo · A casa vazia", "seq-casa-vazia.png")]


def s_annex(prs, b, head, png):
    s = new_slide(prs, 9)
    title(s, head, dark=False)
    picture(s, DIAG / png, 0.5, 1.6, fit=(9.0, 2.98), alt=head)
    return s


def s_privacidade(prs, b):
    s = new_slide(prs, 1)
    title(s, "A privacidade decide-se em casa")
    rules = ["Escolhes onde ficam as câmaras; nunca em quartos nem em casas de banho.",
             "Uma pessoa é só “uma pessoa”; reconhecer a família exige consentimento.",
             "Os padrões faciais nunca saem de casa.",
             "Só sai de casa a zona que mudou; não se grava vídeo.",
             "O modelo de linguagem nunca vê vídeo nem a imagem completa."]
    y = 1.7
    for i, r in enumerate(rules):
        text(s, 0.5, y, 0.3, 0.3, str(i + 1), size=13, bold=True, color=NEON)
        text(s, 0.8, y, 4.6, 0.5, r, size=12, color=WHITE)
        y += 0.56
    picture(s, IMG / "privacidade-zona.jpg", 5.75, 1.62, w=3.75, h=3.75 * 685 / 840,
            alt="Só a zona que mudou: o gato na bancada")
    box(s, 5.9, 1.77, 1.85, 0.26, fill=RGBColor(0x00, 0x6F, 0xB8))
    text(s, 5.9, 1.77, 1.85, 0.26, "só isto sai de casa", size=9, bold=True, color=WHITE, font="Courier New",
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


RESERVE_NOTE = "Reserva: não entra no pitch. 3 min: não · 5 min: não."

# Notes for the slides that exist only here; the others come from the deck's source (NOTES_FROM maps ids).
NOTES = {
    "cover": "CAPA. 3 min: sim · 5 min: sim.\n"
             "Tempos: 0:00–0:05 com a abertura A, ou 0:00–0:12 com a abertura B.\n"
             "Abertura A, a pergunta: “Onde deixaram as chaves esta manhã?” (clique)\n"
             "Abertura B, a cena: “Imaginem uma criança a pegar numa cápsula de detergente. A câmara da cozinha vê-a e os "
             "pais recebem logo um aviso, com a fotografia.” (clique)\n"
             "O Filipe escolhe uma das duas no primeiro ensaio. Um colega controla o portátil e os filmes; outro cronometra.",
    "hoje": "HOJE. 3 min: sim · 5 min: sim.\n"
            "Tempos: até aos 0:12 (abertura A) ou 0:18 (abertura B), cerca de 12 palavras.\n"
            "Dizer: “Hoje, a câmara de casa só grava e avisa ‘movimento detetado’… e depois?”\n"
            "Pausa curta depois de “e depois?”.",
    "possivel": "CÂMARA + IA. 3 min: sim · 5 min: sim.\n"
                "Tempos: até aos 0:23, cerca de 20 palavras.\n"
                "Abertura A: “E as crianças, estão em segurança? A câmara que já têm em casa pode responder. Cada família cria "
                "os seus avisos, com uma frase.”\n"
                "Abertura B: “Com IA, a câmara percebe o que vê, e cada família cria os seus avisos, com uma frase.”\n"
                "Mostrar a grelha sem ler os seis casos.",
    "thingtracker": "O THINGTRACKER. 3 min: sim · 5 min: sim.\n"
                    "Tempos: 0:23–0:35, cerca de 27 palavras.\n"
                    "Dizer: “Por isso criámos o ThingTracker. A câmara só analisa a imagem quando há movimento: reconhece o "
                    "que importa e avisa a família, na app da Altice.”",
    "custos-barras": "CUSTOS EM PORMENOR. " + RESERVE_NOTE + "\n"
                     "Analisar imagens completas, numa caixa em casa ou na nuvem, custaria 2,41 a 8,64 € por casa e por mês; "
                     "a opção híbrida fica em cerca de 0,49 €, e o máximo que a visão pode custar sem dar prejuízo é 1,73 €.\n"
                     "Fonte: estimativa da equipa para 500 000 casas, 1 câmara e 2 h de movimento por dia, com preços públicos "
                     "da AWS, da Azure e da NVIDIA (18 nov 2026; documento 17).",
}
NOTES_FROM = {"como-funciona": "prototipo-proposta", "comecar": "lancamento"}


def build(template, build_dir, order):
    prs = Presentation(template)
    original = list(prs.slides._sldIdLst)
    b = Path(build_dir)
    b.mkdir(parents=True, exist_ok=True)
    makers = {
        "cover": s_cover, "hoje": s_hoje, "possivel": s_possivel, "thingtracker": s_thingtracker,
        "problema": s_problema, "ideia": s_ideia, "conceitos": s_conceitos,
        "filme-livro": lambda p, b: s_film(p, b, "livro"), "filme-desconhecido": lambda p, b: s_film(p, b, "desconhecido"),
        "filme-casa-vazia": lambda p, b: s_film(p, b, "casa"), "modelos": s_modelos, "como-funciona": s_proposta,
        "custos": s_custos, "custos-barras": s_custos_barras, "replicacao": s_replicacao, "comecar": s_comecar,
        "lancamento": s_lancamento, "repositorio": s_repositorio,
        "equipa": s_equipa, "fecho": s_fecho, "divisor": s_divider, "privacidade": s_privacidade,
    }
    for item in order:
        if item.startswith("anexo-"):
            sid, head, png = next(a for a in ANNEX if a[0] == item)
            s = s_annex(prs, b, head, png)
            set_notes(s, notes_from_source(sid))
            continue
        sid = item.split(":")[0]
        s = makers[sid](prs, b)
        if item == "divisor":
            set_notes(s, "ANEXO E RESERVA. Só para perguntas; não entra no pitch. 3 min: não · 5 min: não.")
        elif sid in NOTES:
            set_notes(s, NOTES[sid])
        elif item.endswith(":reserva"):
            n = notes_from_source(sid)
            set_notes(s, n if "Reserva" in n else "Neste ficheiro, reserva para perguntas.\n" + n)
        else:
            set_notes(s, notes_from_source(NOTES_FROM.get(sid, sid)))
    # drop the template's own (empty) slides; their parts are not written once unreferenced
    lst = prs.slides._sldIdLst
    for sid in original:
        prs.part.drop_rel(sid.get(qn("r:id")))
        lst.remove(sid)
    return prs


FIVE = ["cover", "hoje", "possivel", "thingtracker", "filme-livro", "filme-desconhecido", "filme-casa-vazia",
        "como-funciona", "modelos", "custos", "replicacao", "comecar", "repositorio", "fecho", "divisor",
        *[a[0] for a in ANNEX], "conceitos:reserva", "privacidade:reserva", "custos-barras:reserva"]
THREE = ["cover", "hoje", "possivel", "thingtracker", "conceitos", "filme-livro", "como-funciona", "custos", "comecar",
         "fecho"]

if __name__ == "__main__":
    template, build_dir, out5, out3 = sys.argv[1:5]
    build(template, build_dir, FIVE).save(out5)
    build(template, build_dir, THREE).save(out3)
    print("wrote", out5, "and", out3)
