#!/usr/bin/env python3
"""Draw the five business-case charts in Portuguese as SVG, then render each to PNG at 3x with headless Chrome.

    graficos/1-mercado.svg/.png      Figura 1, the market funnel for MEO
    graficos/2-uma-casa.svg/.png     Figura 2, one home and one month, as a waterfall
    graficos/3-equipamento.svg/.png  Figura 3, margin by where the local vision models run
    graficos/4-precos.svg/.png       Figura 4, monthly price against camera plans
    graficos/5-receita.svg/.png      Figura 5, MEO revenue by adoption

Every number is read by row id from the model (docs/16-business-case-model.csv), as the committed English
script (build_charts.py) does, and is then looked up in the Portuguese text (docs/pt/16-viabilidade-negocio.md).
If a chart value is not written in the text, the build stops: the text is the reference.

Text is measured with the team's Lato (deliverables/executive-summary/.fonts) and wrapped inside its padding.
Colours, checked with the dataviz palette validator (light mode, white surface, all checks pass): blue #0084D6 =
money in or a profit, orange #E8710A = a cost or a loss, grey = competitors' published prices.
    python3 docs/business-case/build_graficos.py
"""
import csv
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "graficos"
MODEL = ROOT / "docs" / "16-business-case-model.csv"
DOC = ROOT / "docs" / "pt" / "16-viabilidade-negocio.md"
FONTS = ROOT / "deliverables" / "executive-summary" / ".fonts"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SCALE = 3                       # PNG pixels per SVG unit

W, PAD = 680, 20                # printed 170 mm wide in the PDF, so 1 unit is about 0.94 px
INK, MUTED, FAINT = "#1F2328", "#56606C", "#6B7480"
GRID, AXIS, LINK = "#E6E9ED", "#A3ACB7", "#C9CFD6"
BLUE, ORANGE, GREY = "#0084D6", "#E8710A", "#B4BCC6"
FAMILY = "Lato, 'Helvetica Neue', Arial, sans-serif"
NB = " "                   # thousands separator and the space before % and €

rows = {r[0]: r for r in csv.reader(MODEL.open(encoding="utf8")) if r and r[0] != "id"}


def v(row_id, case="base"):
    return float(rows[row_id][{"low": 3, "base": 4, "high": 5}[case]])


# ---------------------------------------------------------------- the text is the reference
DOC_TEXT = DOC.read_text(encoding="utf8").replace(NB, " ")
missing = []


def in_doc(*strings):
    """Every value a chart prints must also be written in the Portuguese text."""
    for s in strings:
        if s.replace(NB, " ") not in DOC_TEXT:
            missing.append(s)


# ---------------------------------------------------------------- Portuguese numbers
def num(x, d=0):
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", NB)
    return ("−" if round(x, d) < 0 else "") + s


def eur(x, d=2, sign=False):
    return ("+" if sign and round(x, d) > 0 else "") + num(x, d) + NB + "€"


def pct(x, d=0):
    return num(x * 100, d) + NB + "%"


# ---------------------------------------------------------------- text: measure, wrap, draw
_fonts = {}


def font(size, bold=False, italic=False):
    name = {(False, False): "regular", (True, False): "bold", (False, True): "italic", (True, True): "boldItalic"}[(bold, italic)]
    if (size, name) not in _fonts:
        _fonts[(size, name)] = ImageFont.truetype(str(FONTS / f"Lato-{name}.ttf"), size)
    return _fonts[(size, name)]


def words(s):
    """'a _b c_ d' -> [[('a', False)], [('b', True)], [('c', True)], [('d', False)]]; _x_ marks italics."""
    segs, pos = [], 0
    for m in re.finditer(r"(?<![\w])_([^_]+)_(?![\w])", s):
        segs += [(s[pos:m.start()], False), (m.group(1), True)]
        pos = m.end()
    segs.append((s[pos:], False))
    out = [[]]
    for text, it in segs:
        for i, piece in enumerate(text.split(" ")):
            if i:
                out.append([])
            if piece:
                out[-1].append((piece, it))
    return [w for w in out if w]


def width(s, size, bold=False):
    ws = words(s) if isinstance(s, str) else s
    space = font(size, bold).getlength(" ")
    return sum(font(size, bold, it).getlength(p) for w in ws for p, it in w) + space * max(len(ws) - 1, 0)


def wrap(s, max_w, size, bold=False):
    lines, cur = [], []
    for w in words(s):
        if cur and width(cur + [w], size, bold) > max_w * 0.97:     # 3 % slack for kerning
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    return lines + ([cur] if cur else [])


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tspans(ws):
    out = []
    for i, w in enumerate(ws):
        for p, it in w:
            out.append(f'<tspan font-style="italic">{esc(p)}</tspan>' if it else esc(p))
        if i < len(ws) - 1:
            out.append(" ")
    return "".join(out)


class Chart:
    def __init__(self, name, title, subtitle):
        self.name, self.o = name, []
        y = PAD + 18
        y = self.text(PAD, y, title, 19, INK, bold=True, max_w=W - 2 * PAD, lead=24) + 22
        y = self.text(PAD, y, subtitle, 12.5, MUTED, max_w=W - 2 * PAD, lead=17)
        self.top = y + 14                       # first free y below the heading

    def text(self, x, y, s, size, fill, bold=False, anchor="start", max_w=None, lead=None):
        """Draw s (wrapped to max_w when given) with its first baseline at y; return the last baseline."""
        lines = wrap(s, max_w, size, bold) if max_w else [words(s)]
        for i, ln in enumerate(lines):
            self.o.append(f'<text x="{x:.1f}" y="{y + i * (lead or size * 1.3):.1f}" font-size="{size}" '
                          f'font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{tspans(ln)}</text>')
        return y + (len(lines) - 1) * (lead or size * 1.3)

    def line(self, x1, y1, x2, y2, color=GRID, w=1):
        self.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                      f'stroke-width="{w}" shape-rendering="crispEdges"/>')

    def rect(self, x, y, w, h, color, rx=0):
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{color}"/>')

    def hbar(self, x_from, x_to, y, h, color, rounded="right"):
        """Horizontal bar, 4 px round at the data end and square at the baseline; rounded=None floats square."""
        x1, x2 = min(x_from, x_to), max(x_from, x_to)
        r = min(4, (x2 - x1) / 2, h / 2)
        if rounded == "right":
            d = f"M{x1:.1f} {y:.1f}H{x2 - r:.1f}Q{x2:.1f} {y:.1f} {x2:.1f} {y + r:.1f}V{y + h - r:.1f}Q{x2:.1f} {y + h:.1f} {x2 - r:.1f} {y + h:.1f}H{x1:.1f}Z"
        elif rounded == "left":
            d = f"M{x2:.1f} {y:.1f}H{x1 + r:.1f}Q{x1:.1f} {y:.1f} {x1:.1f} {y + r:.1f}V{y + h - r:.1f}Q{x1:.1f} {y + h:.1f} {x1 + r:.1f} {y + h:.1f}H{x2:.1f}Z"
        else:
            d = f"M{x1:.1f} {y:.1f}H{x2:.1f}V{y + h:.1f}H{x1:.1f}Z"
        self.o.append(f'<path d="{d}" fill="{color}"/>')

    def vbar(self, x, w, y_base, y_top, color):
        r = min(4, w / 2, (y_base - y_top) / 2)
        d = (f"M{x:.1f} {y_base:.1f}V{y_top + r:.1f}Q{x:.1f} {y_top:.1f} {x + r:.1f} {y_top:.1f}H{x + w - r:.1f}"
             f"Q{x + w:.1f} {y_top:.1f} {x + w:.1f} {y_top + r:.1f}V{y_base:.1f}Z")
        self.o.append(f'<path d="{d}" fill="{color}"/>')

    def finish(self, bottom, source):
        """bottom = the lowest baseline or mark of the plot; the source line goes 28 units below it."""
        y = self.text(PAD, bottom + 28, source, 10.5, FAINT, max_w=W - 2 * PAD, lead=14)
        h = math.ceil(y + PAD - 4)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
               f'font-family="{FAMILY}" style="white-space:pre"><rect width="{W}" height="{h}" fill="#FFFFFF"/>'
               + "".join(self.o) + "</svg>\n")
        OUT.mkdir(exist_ok=True)
        (OUT / f"{self.name}.svg").write_text(svg, encoding="utf8")
        render(svg, OUT / f"{self.name}.png", W, h)
        print(f"built graficos/{self.name}.png ({W * SCALE} x {h * SCALE})")


def font_faces():
    faces = [("normal", 400, "regular"), ("normal", 700, "bold"), ("italic", 400, "italic"), ("italic", 700, "boldItalic")]
    return "".join(f"@font-face{{font-family:Lato;font-style:{s};font-weight:{wt};src:url('{(FONTS / f'Lato-{n}.ttf').as_uri()}')}}"
                   for s, wt, n in faces)


def render(svg, png, w, h):
    """Screenshot the SVG, inside a page that loads Lato, at SCALE device pixels per unit."""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "grafico.html"
        page.write_text(f"<!doctype html><meta charset=utf-8><style>{font_faces()}"
                        f"html,body{{margin:0;background:#fff}}svg{{display:block}}</style>{svg}", encoding="utf8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        f"--force-device-scale-factor={SCALE}", f"--window-size={w},{h}", "--virtual-time-budget=3000",
                        f"--screenshot={png}", page.as_uri()], check=True, capture_output=True)


# ---------------------------------------------------------------- Figura 1: the market
def mercado():
    base, ready, take = v("D01"), v("D02"), v("D04")
    addr, subs, share = v("D03"), v("D05"), v("D06")
    subs_txt = num(round(subs) * 1000)
    lo, hi = num(round(v("D05", "low") * 10) * 100), num(round(v("D05", "high")) * 1000)
    in_doc(f"{num(base / 1000, 2)} milhões", pct(ready, 2), pct(take), f"{subs_txt} casas", pct(share, 1), f"{lo} a {hi} casas")

    c = Chart("1-mercado", f"Cerca de {subs_txt} casas MEO no cenário esperado",
              "Das casas com banda larga fixa da MEO às casas que aderem ao serviço")
    steps = [("Casas com banda larga fixa da MEO", base, f"{num(base / 1000, 2)} milhões", None),
             (f"Já usam um sistema de casa conectada ({pct(ready, 2)})", addr, f"{num(addr)} mil", None),
             (f"Aderem ao serviço ({pct(take)} destas casas)", subs, f"cerca de {subs_txt} casas · {pct(share, 1)} da MEO",
              f"Intervalo considerado no modelo: de {lo} a {hi} casas")]
    room = W - 2 * PAD - 10
    full = min((room - width(val, 13, True)) / (x / base) for _, x, val, _ in steps)   # longest bar that leaves room for its label
    y = c.top + 4
    for label, x, val, note in steps:
        c.text(PAD, y + 13, label, 13, INK)
        bw = full * x / base
        c.hbar(PAD, PAD + max(bw, 2), y + 22, 20, BLUE)
        last = c.text(PAD + max(bw, 2) + 10, y + 36.5, val, 13, INK, bold=True)
        if note:
            last = c.text(PAD, y + 60, note, 11.5, MUTED)
        y = last + 22
    c.finish(last, "Fontes: ANACOM, 4.º trimestre de 2025 [D01]; Eurostat 2024, pessoas que utilizam um sistema de casa "
                     "conectada em Portugal, usado como aproximação para as casas [D02]; taxa de adesão: pressuposto da equipa, "
                     "de 2 a 10 % [B22]. Resultado: [D05].")


# ---------------------------------------------------------------- Figura 2: one home, one month
def uma_casa():
    price, left = v("N02"), v("M02")
    costs = [("Modelo de linguagem", "custo medido por pedido × utilização estimada", v("C02")),
             ("Servidores na nuvem", "pressuposto da equipa", v("B07")),
             ("Apoio ao cliente", "pressuposto da equipa", v("C03")),
             ("Angariação", "pressuposto da equipa, repartida por 36 meses", v("C04"))]
    assert abs(price - sum(x for *_, x in costs) - left) < 1e-3
    in_doc(eur(price), eur(left), "3,99 €", *(num(x, 2) for *_, x in costs))

    c = Chart("2-uma-casa", f"Cada assinante deixa cerca de {eur(left)} por mês",
              "Serviço adicional a 3,99 € por mês, com a IA em equipamento já instalado (E1); valores sem IVA")
    steps = [("Mensalidade sem IVA", "3,99 € com IVA de 23 %", 0, price, BLUE, eur(price))]
    run = price
    for label, sub, x in costs:
        steps.append((label, sub, run - x, run, ORANGE, eur(-x)))
        run -= x
    steps.append(("Resta por casa", "margem com os custos esperados", 0, left, BLUE, eur(left)))

    LW = 270
    P0, P1 = PAD + LW, W - PAD - max(width(s[5], 13, True) for s in steps) - 12
    sx = lambda m: P0 + (P1 - P0) * m / price
    y, top, prev = c.top + 2, c.top + 2, None
    for i, (label, sub, a, b, color, val) in enumerate(steps):
        total = color == BLUE
        c.text(PAD, y + 13, label, 13, INK, bold=total)
        last = c.text(PAD, y + 28, sub, 11.5, MUTED, max_w=LW - 16, lead=14)
        c.hbar(sx(a), sx(b), y + 3, 18, color, "right" if a == 0 else None)
        c.text(sx(b) + 10, y + 16.5, val, 13, INK, bold=True)
        if prev is not None:                     # thin connector from the previous step's end
            c.line(sx(b), prev, sx(b), y + 3, LINK)
        prev = y + 21
        bottom = max(last, prev)
        y = max(y + 42, last + 14)
    c.line(P0, top - 4, P0, prev + 4, AXIS)
    c.finish(bottom, "Fontes, por linha: [B20], [C02], [B07], [C03], [C04] e [M02]. Valores arredondados ao cêntimo.")


# ---------------------------------------------------------------- Figura 3: where the AI runs
def equipamento():
    groups = [("Equipamento já instalado", "_router_, _gateway_ ou câmara (E1)",
               [("3,99 €", v("M02")), ("4,99 €", v("M03"))]),
              ("Caixa pequena com NPU", f"cerca de {num(v('B12'))} € por casa (E2)",
               [("3,99 €", v("M04")), ("4,99 €", v("M05"))]),
              ("Caixa com GPU", f"cerca de {num(v('B13'))} € por casa (E3)",
               [("3,99 €", None), ("4,99 €", v("M06"))])]       # E3 at 3,99 €: "Não calculada" in table D4
    in_doc("60 / 100 / 150 €", "200 / 300 / 400 €", "Não calculada",
           *(num(x, 2) for _, _, bars in groups for _, x in bars if x is not None))

    c = Chart("3-equipamento", "Onde corre a IA decide o caso",
              "Margem mensal por casa do serviço adicional, sem IVA, consoante onde funcionam os modelos de visão")
    vals = [x for _, _, bars in groups for _, x in bars if x is not None]
    lo_v, hi_v = min(vals), max(vals)
    A, B = PAD + 262, W - PAD
    l_neg, l_pos = width(eur(lo_v), 13, True), width(eur(hi_v, sign=True), 13, True)
    k = (B - A - 20 - l_neg - l_pos) / (hi_v - lo_v)
    z = A + 10 + l_neg - lo_v * k
    sx = lambda m: z + m * k
    top = c.top + 14
    c.text(z - 8, c.top + 4, "prejuízo", 11.5, MUTED, anchor="end")
    c.text(z + 8, c.top + 4, "lucro", 11.5, MUTED)
    y = top + 8
    rows_y = []
    for label, sub, bars in groups:
        c.text(PAD, y + 13, label, 13, INK, bold=True)
        last = c.text(PAD, y + 29, sub, 11.5, MUTED, max_w=A - PAD - 64, lead=14)
        for j, (price, x) in enumerate(bars):
            by = y + j * 22
            rows_y.append((by, price, x))
        y = max(y + 58, last + 18)
    bottom = max(max(by for by, _, _ in rows_y) + 17, last) + 6     # below the last bar and the last label
    ticks = range(math.ceil((A - z) / k), math.floor((B - z) / k) + 1)
    step = 1 if k >= 34 else 2
    for t in ticks:
        c.line(sx(t), top, sx(t), bottom, AXIS if t == 0 else GRID)
        if t % step == 0:
            c.text(sx(t), bottom + 14, f"{num(t)}{NB}€", 11, FAINT, anchor="middle")
    for by, price, x in rows_y:
        c.text(A - 8, by + 13, f"a {price}", 11.5, MUTED, anchor="end")
        if x is None:
            c.text(z + 8, by + 13, "não calculada", 11.5, FAINT)
            continue
        color = BLUE if x >= 0 else ORANGE
        c.hbar(z, sx(x), by + 1, 16, color, "right" if x >= 0 else "left")
        c.text(sx(x) + (8 if x >= 0 else -8), by + 13.5, eur(x, sign=True), 13, INK, bold=True,
               anchor="start" if x >= 0 else "end")
    c.finish(bottom + 12, "Fontes: margens com os custos esperados [M02–M06]; caixas: preços estimados pela equipa de forma "
                         "aproximada, amortizados em 36 meses [C07, C08]. Exclui a eletricidade, paga pela família. A caixa "
                         "com GPU não foi calculada a 3,99 €.")


# ---------------------------------------------------------------- Figura 4: price against camera plans
def precos():
    sfr_box = v("A15") - 5                       # model A15: SFR Box customers get 5 € a month off
    plans = [("Vodafone + Prosegur Alarmes", "a partir deste valor; câmara de 360° incluída", v("A11"), GREY),
             ("NOS Securitas, apartamento", f"preço de campanha, com fidelização de 36 meses; cada câmara interior "
              f"adicional custa mais {eur(v('A13'))}", v("A12"), GREY),
             ("SFR _Maison Sécurisée_, França", f"{eur(sfr_box)} para clientes _SFR Box_; câmara incluída", v("A15"), GREY),
             ("_ThingTracker_ com câmara", "pacote proposto", v("B21"), BLUE),
             ("_ThingTracker_, serviço adicional", "proposto, para casas que já têm câmara", v("B20"), BLUE)]
    in_doc("“desde €45,5/mês”", eur(v("A12")), eur(v("A13")), eur(v("A15")), eur(sfr_box), eur(v("B21")), eur(v("B20")))

    c = Chart("4-precos", "Uma fração do preço de um plano com câmara", "Preço mensal com IVA")
    lx = PAD
    for color, label in [(GREY, "Ofertas atuais, preços publicados"), (BLUE, "_ThingTracker_, preços propostos")]:
        c.rect(lx, c.top - 9, 10, 10, color, rx=2)
        c.text(lx + 16, c.top, label, 11.5, MUTED)
        lx += 16 + width(label, 11.5) + 22
    LW = 300
    P0 = PAD + LW
    P1 = W - PAD - max(width(eur(p), 13, True) for *_, p, _ in plans) - 12
    top = max(p for *_, p, _ in plans)
    y = c.top + 22
    for label, sub, p, color in plans:
        ours = color == BLUE
        c.text(PAD, y + 14, label, 13, INK, bold=ours)
        last = c.text(PAD, y + 30, sub, 11.5, MUTED, max_w=LW - 20, lead=14)
        bw = (P1 - P0) * p / top
        c.hbar(P0, P0 + bw, y + 3, 18, color)
        c.text(P0 + bw + 10, y + 16.5, eur(p), 13, INK, bold=True)
        bar_end = y + 21
        y = max(y + 44, last + 16)
    c.line(P0, c.top + 18, P0, bar_end + 6, AXIS)
    c.finish(max(last, bar_end), "Fontes: vodafone.pt, nos.pt e sfr.fr/maison, consultados a 18/11/2026. Preços do _ThingTracker_: "
                     "pressupostos da equipa [B20, B21].")


# ---------------------------------------------------------------- Figura 5: revenue for MEO
def receita():
    cases = [("0,5 %", "R1"), ("1 %", "R2"), ("2 %", "R3"), ("5 %", "R4")]
    data = [(lab, round(v(r + "b") * 1000), round(v(r + "c") * 1000), v(r + "a")) for lab, r in cases]
    for lab, rev, mar, homes in data:
        in_doc(f"| {lab} | {num(homes, 1)} mil |", f" {num(rev)} / ", f"{num(mar)} mil €")

    c = Chart("5-receita", "A receita cresce com cada casa que adere",
              "Receita anual da MEO, sem IVA, com o serviço a 3,99 € por mês, por percentagem de casas MEO que aderem")
    X0, X1 = PAD + 46, W - PAD
    PT, PH, top_v = c.top + 22, 180, 3500
    base = PT + PH
    sy = lambda m: base - PH * m / top_v
    for t in (0, 1000, 2000, 3000):
        c.line(X0, sy(t), X1, sy(t), AXIS if t == 0 else GRID)
        c.text(X0 - 8, sy(t) + 4, num(t), 11, FAINT, anchor="end")
    c.text(X0 - 8, PT - 6, "mil €", 11, FAINT, anchor="end")
    slot = (X1 - X0) / len(data)
    cx = [X0 + slot * (i + 0.5) for i in range(len(data))]
    for x, (lab, rev, mar, homes) in zip(cx, data):
        c.vbar(x - 12, 24, base, sy(rev), BLUE)
        c.text(x, sy(rev) - 22, f"{num(rev)} mil €", 13, INK, bold=True, anchor="middle")
        c.text(x, sy(rev) - 8, f"margem: {num(mar)} mil €", 11, MUTED, anchor="middle")
        c.text(x, base + 20, f"{lab} das casas", 12.5, INK, bold=True, anchor="middle")
        c.text(x, base + 36, f"{num(homes, 1)} mil casas", 11.5, MUTED, anchor="middle")
    yb = base + 52                                # the expected case (1,2 %) lies between the 1 % and 2 % columns
    c.line(cx[1], yb, cx[2], yb, AXIS)
    c.line(cx[1], yb - 5, cx[1], yb, AXIS)
    c.line(cx[2], yb - 5, cx[2], yb, AXIS)
    in_doc("(1,2 %) situa-se entre as colunas de 1 % e de 2 %")
    c.text((cx[1] + cx[2]) / 2, yb + 16, "cenário esperado: 1,2 %", 11.5, MUTED, anchor="middle")
    c.finish(yb + 16, "As percentagens de adesão são cenários e não previsões (pressuposto da equipa). Margem de "
                      "contribuição com a IA em equipamento já instalado (E1) e com os custos esperados [linhas R].")


if __name__ == "__main__":
    mercado()
    uma_casa()
    equipamento()
    precos()
    receita()
    if missing:
        print("These chart values are not written in docs/pt/16-viabilidade-negocio.md:", *missing, sep="\n  ")
        sys.exit(1)
    print("every chart value is in the Portuguese text")
