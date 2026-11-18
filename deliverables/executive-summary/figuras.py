#!/usr/bin/env python3
"""Draw the report's two figures as SVG, in Portuguese (build.py renders and embeds them).

  figura-exemplo.svg      one use case, from the sentence to the house acting
  figura-arquitetura.svg  how it works: home, Altice platform, language model

Text is measured with the template's Lato (extracted to .fonts/) and wrapped to each box. Every arrow is
straight, and a two-way flow is two arrows, each with its own label.
    python3 figuras.py
"""
import base64
import re
import struct
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FLUENT = ROOT / "prototype" / "web" / "icons" / "fluent"
DEVICES = ROOT / "docs" / "architecture" / "icons"
TABLER = ROOT / "prototype" / "web" / "icons" / "tabler"
W = 1000
INK, MUTED, LINE, BLUE, DEEP, ARROW = "#1F2328", "#56606C", "#CFD5DC", "#0084D6", "#0A3FA3", "#6B7480"
_f = {}


def font(size, bold=False):
    k = (size, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(str(HERE / ".fonts" / f"Lato-{'bold' if bold else 'regular'}.ttf"), size)
    return _f[k]


def width(s, size, bold=False):
    return font(size, bold).getlength(s.replace("_", ""))


def wrap(s, max_w, size, bold=False):
    lines, cur = [], ""
    for w in s.split():
        t = f"{cur} {w}".strip()
        if cur and width(t, size, bold) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Fig:
    def __init__(self, h):
        self.h, self.o = h, []

    def text(self, x, y, s, size=15, bold=False, fill=INK, anchor="start"):
        body = re.sub(r"(?<![\w])_([^_]+)_(?![\w])", lambda m: f'<tspan font-style="italic">{m.group(1)}</tspan>', esc(s))
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{700 if bold else 400}" '
                      f'fill="{fill}" text-anchor="{anchor}">{body}</text>')

    def para(self, x, y, s, max_w, size=14, lead=18, fill=MUTED, bold=False, anchor="start"):
        lines = wrap(s, max_w, size, bold)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lead, ln, size, bold, fill, anchor)
        return y + (len(lines) - 1) * lead

    def rect(self, x, y, w, h, fill="#FFF", stroke=LINE, rx=10, sw=1.2, dash=None):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}{d}/>')

    def arrow(self, x1, y1, x2, y2, color=ARROW):
        # stop the line at the base of the head (9 units long), so its end never shows beside the tip
        ln = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1
        ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
        x2, y2 = x2 - ux * 9, y2 - uy * 9
        if ln < 10:                       # shorter than the head: a 1-unit stub keeps the head pointing the right way
            x1, y1 = x2 - ux, y2 - uy
        self.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                      f'stroke-width="1.6" marker-end="url(#ah)"/>')

    def svg_icon(self, path, x, y, size):
        s = path.read_text()
        vb = re.search(r'viewBox="([^"]+)"', s).group(1)
        inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", s, flags=re.S)
        self.o.append(f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="{vb}">{inner}</svg>')

    def png_icon(self, path, x, y, h):
        data = path.read_bytes()
        w0, h0 = struct.unpack(">II", data[16:24])
        w = w0 * h / h0
        self.o.append(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" '
                      f'href="data:image/png;base64,{base64.b64encode(data).decode()}"/>')
        return w

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {self.h}" width="{W}" height="{self.h}" '
               'font-family="Lato, Arial, sans-serif"><defs><marker id="ah" viewBox="0 0 10 10" refX="0" refY="5" '
               f'markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0 1.6 L10 5 L0 8.4 Z" fill="{ARROW}"/>'
               f'</marker></defs><rect width="{W}" height="{self.h}" fill="#FFF"/>' + "".join(self.o) + "</svg>")
        (HERE / name).write_text(svg, encoding="utf8")
        print("wrote", name, f"{W}x{self.h}")


# ---------------------------------------------------------------- figure 1: one use case, end to end
def exemplo():
    f = Fig(270)
    gap, top, h = 34, 6, 258
    cw = (W - 3 * gap) / 4
    steps = [("Uma frase", "O modelo de linguagem converte a frase numa regra, uma única vez."),
             ("A câmara vê", "Modelos de visão _open-source_, a funcionar em casa, encontram as chaves."),
             ("A casa lembra", "A memória local guarda o que viu, onde e quando, sem vídeo."),
             ("A casa age", "A regra é avaliada em casa e os comandos seguem pelo MCP.")]
    for i, (title, caption) in enumerate(steps):
        x = i * (cw + gap)
        f.rect(x, top, cw, h)
        f.o.append(f'<circle cx="{x + 24}" cy="{top + 26}" r="12" fill="{BLUE}"/>')
        f.text(x + 24, top + 31, str(i + 1), 14, True, "#FFF", "middle")
        f.text(x + 44, top + 31, title, 17, True)
        f.para(x + 16, top + 200, caption, cw - 32, 14.5, 18.5)
        vx, vy = x + 14, top + 50            # visual area: cw - 28 wide, 122 tall
        if i == 0:
            f.rect(vx, vy + 8, cw - 28, 100, fill="#EEF3FB", stroke=None, rx=16)
            lines = wrap("“Avisa-me se sair de casa sem as chaves”", cw - 60, 16.5)
            y0 = vy + 58 - (len(lines) - 1) * 11
            for k, ln in enumerate(lines):
                f.text(vx + (cw - 28) / 2, y0 + k * 22, ln, 16.5, False, INK, "middle")
        elif i == 1:
            cx = x + cw / 2
            f.rect(cx - 46, vy + 22, 92, 82, fill="none", stroke=BLUE, rx=4, sw=2, dash="6 4")
            f.svg_icon(FLUENT / "key.svg", cx - 28, vy + 35, 56)
            tw = width("chaves", 13, True) + 14
            f.rect(cx - 46, vy + 4, tw, 20, fill=BLUE, stroke=None, rx=4)
            f.text(cx - 46 + 7, vy + 18.5, "chaves", 13, True, "#FFF")
            f.text(cx, vy + 124, "mesa da entrada", 14, False, MUTED, "middle")
        elif i == 2:
            for k, (ic, what, where) in enumerate([("key", "Chaves", "mesa da entrada · 08h42"),
                                                    ("glasses", "Óculos", "secretária · 07h15")]):
                ry = vy + 12 + k * 54
                f.rect(vx, ry, cw - 28, 46, fill="#F4F5F7", stroke=None, rx=8)
                f.svg_icon(FLUENT / f"{ic}.svg", vx + 10, ry + 9, 28)
                f.text(vx + 48, ry + 20, what, 15, True)
                f.text(vx + 48, ry + 38, where, 13.5, False, MUTED)
        else:
            half = (cw - 28) / 2
            for k, (ic, lab) in enumerate([("contact-sensor", "porta abre"), ("light", "lâmpada pisca")]):
                cx = vx + half * (k + 0.5)
                data = (DEVICES / f"{ic}.png").read_bytes()
                w0, h0 = struct.unpack(">II", data[16:24])
                f.png_icon(DEVICES / f"{ic}.png", cx - w0 * 34 / h0 / 2, vy + 10, 34)
                f.text(cx, vy + 62, lab, 13.5, False, MUTED, "middle")
            pill = "Saiu sem as chaves"
            pw = 22 + 8 + width(pill, 15, True) + 28
            px0 = vx + (cw - 28 - pw) / 2
            f.rect(px0, vy + 76, pw, 40, fill="#EEF3FB", stroke=None, rx=20)
            f.svg_icon(TABLER / "bell.svg", px0 + 14, vy + 85, 22)
            f.text(px0 + 14 + 22 + 8, vy + 101, pill, 15, True, INK)
        if i < 3:
            f.arrow(x + cw + 5, top + h / 2, x + cw + gap - 5, top + h / 2)
    f.save("figura-exemplo.svg")


# ---------------------------------------------------------------- figure 1, with real photos from the kit camera
FOTOS = HERE / "fotos"   # fotos.json: {"obj_en", "obj_pt", "art", "place", "time", "score", "views": [...], "scene": file,
                         #              "box": [x1, y1, x2, y2] in the scene's pixels}


def photo(f, path, x, y, w, h, rx=8):
    """A JPEG, cropped to fill the box (like object-fit: cover), with rounded corners."""
    cid = f"c{len(f.o)}"
    data = base64.b64encode(path.read_bytes()).decode()
    f.o.append(f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}"/></clipPath>'
               f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="xMidYMid slice" '
               f'clip-path="url(#{cid})" href="data:image/jpeg;base64,{data}"/>')


def exemplo_real():
    import json
    from PIL import Image
    spec = json.loads((FOTOS / "fotos.json").read_text())
    en, pt, art = spec["obj_en"], spec["obj_pt"], spec["art"]
    f = Fig(312)
    gap, top, h = 30, 6, 300
    cw = (W - 3 * gap) / 4
    titles = ["Registo visual", "Deteção", "Pergunta", "Regra e ação"]
    for i, title in enumerate(titles):
        x = i * (cw + gap)
        f.rect(x, top, cw, h)
        f.o.append(f'<circle cx="{x + 24}" cy="{top + 26}" r="12" fill="{BLUE}"/>')
        f.text(x + 24, top + 31, str(i + 1), 14, True, "#FFF", "middle")
        f.text(x + 44, top + 31, title, 17, True)
        if i < 3:
            f.arrow(x + cw + 5, top + h / 2, x + cw + gap - 5, top + h / 2)
    ix, iw = 14, cw - 28

    # 1. registration: six of the real views, then what they become
    x, vy = ix, top + 50
    cols = 2 if len(spec["views"]) <= 4 else 3
    tw = (iw - (cols - 1) * 6) / cols
    th = tw * 2 / 3
    for k, v in enumerate(spec["views"][:2 * cols]):
        photo(f, FOTOS / v, x + (k % cols) * (tw + 6), vy + (k // cols) * (th + 6), tw, th, rx=6)
    f.para(x, vy + 2 * th + 6 + 26, f"O nome “_{en}_” pesquisa o objeto; as imagens geram uma assinatura digital e visual da _thing_, "
           "guardada em casa e na base de dados da Altice.", iw, 13.5, 17.5)

    # 2. detection: the scene, with the box the edge drew
    x = cw + gap + ix
    sc = Image.open(FOTOS / spec["scene"])
    sh = 128
    photo(f, FOTOS / spec["scene"], x, vy, iw, sh, rx=6)
    # the photo fills the box with 'slice': map the scene's pixels onto it
    s = max(iw / sc.width, sh / sc.height)
    ox, oy = x + (iw - sc.width * s) / 2, vy + (sh - sc.height * s) / 2
    b = spec["box"]
    bx, by, bw, bh = ox + b[0] * s, oy + b[1] * s, (b[2] - b[0]) * s, (b[3] - b[1]) * s
    f.rect(bx, by, bw, bh, fill="none", stroke=BLUE, rx=3, sw=2.2)
    lab = f"{pt.capitalize()} · sua {spec['score']}"
    lw = width(lab, 12.5, True) + 12
    ly = by - 20 if by - 20 > vy + 2 else by + bh + 2
    lx = min(bx, x + iw - lw - 2)
    f.rect(lx, ly, lw, 18, fill=BLUE, stroke=None, rx=4)
    f.text(lx + 6, ly + 13, lab, 12.5, True, "#FFF")
    f.para(x, vy + sh + 26, "Só quando há movimento: o _OWLv2_ encontra candidatos e o _DINOv2_ confirma que é "
           f"{art} {pt} registad{art}.", iw, 13.5, 17.5)

    # 3. the question, the answer with the photo, and the disambiguation
    x = 2 * (cw + gap) + ix
    q = f"Onde está {art} {pt}?"
    qw = width(q, 14.5) + 24
    f.rect(x + iw - qw, vy, qw, 32, fill=BLUE, stroke=None, rx=16)
    f.text(x + iw - qw / 2, vy + 21, q, 14.5, False, "#FFF", "middle")
    f.rect(x, vy + 42, iw, 62, fill="#EEF3FB", stroke=None, rx=14)
    photo(f, FOTOS / spec["answer"], x + 8, vy + 50, 46, 46, rx=8)
    ans = wrap(f"Na {spec['place']}, às {spec['time']}.", iw - 72, 14)
    for j, ln in enumerate(ans[:3]):
        f.text(x + 64, vy + 73 - (len(ans) - 1) * 8.5 + j * 17, ln, 14, False, INK)
    f.rect(x, vy + 112, iw, 46, fill="#F4F5F7", stroke=None, rx=12)
    f.text(x + iw / 2, vy + 131, f"Se houver duas, pergunta:", 13.5, False, INK, "middle")
    f.text(x + iw / 2, vy + 149, "“Qual delas?”", 13.5, False, INK, "middle")
    f.para(x, vy + 184, "A memória da casa responde com o último local e a hora.", iw, 13.5, 17.5)

    # 4. sentence → service → language model with MCP tools → scenario via MCP → evaluated at home → action via MCP
    x = 3 * (cw + gap) + ix
    chain = [(f"“Avisa-me se sair sem {art} {pt}”", "#EEF3FB", INK),
             ("Serviço _ThingTracker_", "#FFF", INK),
             ("Modelo de linguagem, com as ferramentas MCP", "#FFF", INK),
             ("Regra gravada como cenário (MCP)", "#FFF", INK),
             ("Avaliada em casa; ação pelo MCP", "#FFF", INK)]
    y = vy
    for k, (t, fill, col) in enumerate(chain):
        lines = wrap(t, iw - 16, 13.5)
        ph = 12 + 16 * len(lines)
        f.rect(x, y, iw, ph, fill=fill, stroke=None if fill != "#FFF" else LINE, rx=8)
        for j, ln in enumerate(lines):
            f.text(x + iw / 2, y + ph / 2 + 5 - (len(lines) - 1) * 8 + j * 16, ln, 13.5, False, col, "middle")
        if k < len(chain) - 1:
            f.arrow(x + iw / 2, y + ph + 1, x + iw / 2, y + ph + 9)
        y += ph + 10
    assert y - 10 <= top + h - 6, f"panel 4 overflows by {y - 10 - (top + h - 6):.0f}"
    f.save("figura-exemplo.svg")


# ---------------------------------------------------------------- figure 2: how it works
def arquitetura():
    H = 352
    f = Fig(H)
    HOME, PLAT, LLM = (0, 552), (572, 798), (812, 1000)
    R1, R2, R3 = (46, 122), (150, 226), (254, 336)
    f.rect(HOME[0], 0, HOME[1] - HOME[0], H, fill="#F4F5F7", stroke=None, rx=14)
    f.rect(PLAT[0], 0, PLAT[1] - PLAT[0], H, fill="#EEF3FB", stroke=None, rx=14)
    f.rect(LLM[0], 0, LLM[1] - LLM[0], H, fill=DEEP, stroke=None, rx=14)
    f.text(16, 29, "Em casa", 17, True)
    f.text(16 + width("Em casa", 17, True) + 10, 29, "serviço local; a análise fica em casa", 14.5, False, MUTED)
    f.text(PLAT[0] + 16, 29, "Plataforma Altice", 17, True)
    lx, lw = LLM[0] + 16, LLM[1] - LLM[0] - 32
    f.text(lx, 29, "Modelo de linguagem", 16 if width("Modelo de linguagem", 16, True) <= lw else 15, True, "#FFF")

    def box(x0, x1, row, title, sub, stroke=LINE, sw=1.2, size=15.5, dash=None):
        f.rect(x0, row[0], x1 - x0, row[1] - row[0], stroke=stroke, sw=sw, dash=dash)
        assert width(title, size, True) <= x1 - x0 - 24, title
        f.text(x0 + 12, row[0] + 25, title, size, True)
        end = f.para(x0 + 12, row[0] + 46, sub, x1 - x0 - 24, 13.5, 17)
        assert end <= row[1] - 10, f"overflow: {title}"

    CAM, VIS, MEM = (16, 140), (170, 380), (410, 536)
    box(*CAM, R1, "Câmara", "1 a 2 imagens por segundo")
    box(*VIS, R1, "Modelos de visão", "_open-source_: encontram objetos e lugares pelo nome")
    box(*MEM, R1, "Memória local", "o quê, onde e quando")
    box(16, 380, R2, "Privacidade", "máscaras definidas pelo utilizador; imagens descartadas; sem vídeo guardado", dash="5 4")
    box(*MEM, R2, "Regras", "avaliadas a cada segundo")
    f.rect(16, R3[0], 536 - 16, R3[1] - R3[0])
    f.text(28, R3[0] + 24, "Dispositivos do kit", 15.5, True)
    kit = [("camera", "câmara"), ("light", "lâmpada"), ("plug", "tomada"), ("security-hub", "central"),
           ("contact-sensor", "porta"), ("smoke-sensor", "fumo"), ("temperature-sensor", "clima")]
    slot = (536 - 16 - 24) / len(kit)
    for k, (ic, lab) in enumerate(kit):
        cx = 28 + slot * (k + 0.5)
        data = (DEVICES / f"{ic}.png").read_bytes()
        w0, h0 = struct.unpack(">II", data[16:24])
        f.png_icon(DEVICES / f"{ic}.png", cx - w0 * 24 / h0 / 2, R3[0] + 34, 24)
        f.text(cx, R3[0] + 73, lab, 13, False, MUTED, "middle")

    P = (PLAT[0] + 16, 760)
    box(*P, R1, "Aplicação Altice", "separador «Coisas»", size=15)
    box(*P, R2, "Serviço ThingTracker", "o único que chama o modelo", stroke=BLUE, sw=2, size=15)
    box(*P, R3, "Servidor MCP", "comandos e 4 novas ferramentas", size=15)

    y = R1[0] + 22
    f.text(lx, y, "Claude ou equivalente,", 14.5, True, "#FFF")
    f.text(lx, y + 19, "sob contrato", 14.5, True, "#FFF")
    y += 52
    for s_ in ["Converte frases em regras", "Responde a perguntas", "Avalia casos duvidosos"]:
        y = f.para(lx, y, s_, lw, 14, 17.5, "#FFF") + 27
    f.para(lx, y + 4, "Sem treino com os nossos dados; acordo de tratamento de dados", lw, 13, 16.5, "#C9D6F0")
    # cost, anchored to the bottom of the panel
    f.text(lx, R3[1] - 24, "Custo estimado", 13, True, "#C9D6F0")
    f.text(lx, R3[1] - 4, "0,43 € por casa e por mês", 14, True, "#FFF")

    def pair_h(x1, x2, y, top_label, bottom_label, anchor="middle"):
        f.arrow(x1, y - 6, x2 - 3, y - 6)
        f.arrow(x2, y + 6, x1 + 3, y + 6)
        tx = (x1 + x2) / 2 if anchor == "middle" else x1 + 5
        f.text(tx, y - 13, top_label, 11.5, False, BLUE, anchor)
        f.text(tx, y + 23, bottom_label, 11.5, False, BLUE, anchor)

    def pair_v(x, y1, y2, left_label, right_label):
        f.arrow(x - 6, y2, x - 6, y1 + 3)
        f.text(x - 14, (y1 + y2) / 2 + 4, left_label, 11.5, False, BLUE, "end")
        f.arrow(x + 6, y1, x + 6, y2 - 3)
        f.text(x + 14, (y1 + y2) / 2 + 4, right_label, 11.5, False, BLUE)

    m1, m2, m3 = (R1[0] + R1[1]) / 2, (R2[0] + R2[1]) / 2, (R3[0] + R3[1]) / 2
    f.arrow(CAM[1] + 3, m1, VIS[0] - 3, m1)
    f.arrow(VIS[1] + 3, m1, MEM[0] - 3, m1)
    f.arrow((MEM[0] + MEM[1]) / 2, R1[1] + 2, (MEM[0] + MEM[1]) / 2, R2[0] - 2)
    pair_h(MEM[1], P[0], m2, "eventos", "regras")
    assert P[1] + 5 + width("resposta", 11.5) < LLM[0], "model labels would enter the dark band"
    pair_h(P[1], LLM[0], m2, "pedido", "resposta", anchor="start")
    px = (P[0] + P[1]) / 2
    pair_v(px, R1[1], R2[0], "respostas", "pedidos")
    pair_v(px, R2[1], R3[0], "resultados", "ações")
    f.arrow(P[0] - 3, m3, 536 + 3, m3)
    f.text((536 + P[0]) / 2, m3 - 9, "ações", 11.5, False, BLUE, "middle")
    f.save("figura-arquitetura.svg")


if __name__ == "__main__":
    exemplo_real() if (FOTOS / "fotos.json").exists() else exemplo()
    arquitetura()
    import shutil
    shutil.copy(ROOT / "docs" / "architecture" / "thingtracker-architecture.svg", HERE / "arquitetura.svg")
    print("copied arquitetura.svg from docs/architecture")
