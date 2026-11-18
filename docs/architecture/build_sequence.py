#!/usr/bin/env python3
"""Draw the integration spec's Figure 1: the messages from a sentence to an action, as a sequence diagram (PT).

    python3 docs/architecture/build_sequence.py     # writes sequencia-regra.svg and .png (with Chrome)

Text is measured with Lato (deliverables/executive-summary/.fonts) and wrapped to its box; every arrow is straight
and one-way, labelled above its line.
"""
import subprocess
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parents[1] / "deliverables" / "executive-summary" / ".fonts"
INK, MUTED, LINE, BLUE, SOFT = "#1F2328", "#56606C", "#CFD5DC", "#0084D6", "#EEF3FB"
W = 1200
_f = {}


def width(s, size, bold=False):
    k = (size, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(str(FONTS / f"Lato-{'bold' if bold else 'regular'}.ttf"), size)
    return _f[k].getlength(s)


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


o = []


def text(x, y, s, size=14, bold=False, fill=INK, anchor="middle", italic=False):
    st = ' font-style="italic"' if italic else ""
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" '
             f'text-anchor="{anchor}"{st}>{esc(s)}</text>')


COLS = [("Aplicação", "no telemóvel"), ("Serviço ThingTracker", "plataforma Altice"),
        ("Modelo de linguagem", "fornecedor sob contrato"), ("Servidor MCP e cenários", "plataforma Altice"),
        ("Serviço local", "em casa, junto da câmara"), ("Dispositivos", "sensor da porta, lâmpada")]
X = [100 + i * 200 for i in range(len(COLS))]
TOP = 20

# column headers
for x, (name, sub) in zip(X, COLS):
    o.append(f'<rect x="{x - 88}" y="{TOP}" width="176" height="56" rx="10" fill="#FFF" stroke="{LINE}" stroke-width="1.2"/>')
    if "ThingTracker" in name:                    # product names in italics, as in the report
        o.append(f'<text x="{x}" y="{TOP + 25}" font-size="15" font-weight="700" fill="{INK}" text-anchor="middle">'
                 f'{esc(name.replace("ThingTracker", ""))}<tspan font-style="italic">ThingTracker</tspan></text>')
    else:
        text(x, TOP + 25, name, 15, True)
    text(x, TOP + 44, sub, 12.5, False, MUTED)

# messages: (step, from, to, label); a "gap" row is a time break; a "note" row sits on one lifeline
ROWS = [
    (1, 0, 1, "“Avisa-me se sair de casa sem a carteira”"),
    (2, 1, 2, "frase, objetos, dispositivos e ferramentas MCP"),
    (3, 2, 1, "regra estruturada"),
    (4, 1, 3, "post_new_scenario"),
    (5, 3, 4, "condição: carteira na secretária há 2 min"),
    ("gap", "Mais tarde, a porta da entrada abre"),
    (6, 5, 3, "porta aberta (sensorState: alarm)"),
    (6, 3, 4, "evento da porta"),
    ("note", 4, "Motor de regras: a carteira continua na secretária"),
    (6, 4, 3, "sensor.fired"),
    (7, 3, 5, "update_device_capabilities: lâmpada vermelha"),
    (7, 3, 0, "aviso, com a miniatura da carteira"),
]

y = TOP + 56 + 56
marks = []
for row in ROWS:
    if row[0] == "gap":
        o.append(f'<rect x="10" y="{y - 14}" width="{W - 20}" height="30" rx="6" fill="{SOFT}"/>')
        text(W / 2, y + 6, row[1], 13.5, False, INK, italic=True)
        y += 44
        continue
    if row[0] == "note":
        x = X[row[1]]
        lines = wrap(row[2], 230, 13)
        h = 14 + 17 * len(lines)
        o.append(f'<rect x="{x - 125}" y="{y - 12}" width="250" height="{h}" rx="8" fill="#FFF7EC" stroke="#E8710A" stroke-width="1"/>')
        for i, ln in enumerate(lines):
            text(x, y + 6 + i * 17, ln, 13, False, INK)
        y += h + 22
        continue
    step, a, b, label = row
    xa, xb = X[a], X[b]
    d = 1 if xb > xa else -1
    x1, x2 = xa + d * 6, xb - d * 6
    span = abs(xb - xa) - 40
    lines = wrap(label, span, 13)
    ly = y - 8 - 16 * (len(lines) - 1)
    for i, ln in enumerate(lines):
        lw = width(ln, 13) + 10                 # a white backing, so the dashed lifelines never cross the words
        o.append(f'<rect x="{(xa + xb) / 2 - lw / 2:.1f}" y="{ly + i * 16 - 12:.1f}" width="{lw:.1f}" height="16" fill="#FFF"/>')
        text((xa + xb) / 2, ly + i * 16, ln, 13, False, INK)
    o.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{INK}" stroke-width="1.4" marker-end="url(#ah)"/>')
    o.append(f'<circle cx="{xa}" cy="{y}" r="11" fill="{BLUE}"/>')
    text(xa, y + 4.5, str(step), 12, True, "#FFF")
    marks.append(y)
    y += 46 + 16 * (len(lines) - 1)

H = y + 6
lifelines = "".join(f'<line x1="{x}" y1="{TOP + 56}" x2="{x}" y2="{H - 10}" stroke="{LINE}" stroke-width="1.2" stroke-dasharray="4 4"/>'
                    for x in X)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       'font-family="Lato, Arial, sans-serif"><defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
       'markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 1.8 L10 5 L0 8.2 Z" '
       f'fill="{INK}"/></marker></defs><rect width="{W}" height="{H}" fill="#FFF"/>{lifelines}' + "".join(o) + "</svg>")
# the lifelines go under the boxes and labels: draw them first, then put the header boxes back on top
(HERE / "sequencia-regra.svg").write_text(svg, encoding="utf8")
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
html = HERE / ".seq.html"
html.write_text(f'<html><head><style>@font-face{{font-family:Lato;src:url("file://{FONTS}/Lato-regular.ttf")}}'
                f'@font-face{{font-family:Lato;font-weight:700;src:url("file://{FONTS}/Lato-bold.ttf")}}'
                f'body{{margin:0}}</style></head><body>{svg}</body></html>')
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={HERE / 'sequencia-regra.png'}", f"file://{html}"],
               check=True, capture_output=True)
html.unlink()
print(f"wrote sequencia-regra.svg and .png ({W}x{H})")
