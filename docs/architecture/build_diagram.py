#!/usr/bin/env python3
"""Build docs/architecture/thingtracker-architecture.svg (and .png with Chrome), in European Portuguese.

Every position comes from the grid below, so boxes line up and every line is straight.
Body text is measured with the font Chrome renders (Helvetica Neue) and wrapped to each box's padded width.
    python3 docs/architecture/build_diagram.py
"""
import base64
import re
import struct
import subprocess
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ICONS = HERE / "icons"                                  # cropped from the Altice app (Add device list)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"

# ---------------------------------------------------------------- grid
W = 1700
BAND_TOP = 64
R1, R2, R3 = (150, 390), (430, 580), (620, 792)        # home rows, 40 px apart
BAND_BOTTOM = R3[1] + 20
LEGEND_Y = BAND_BOTTOM + 16
H = LEGEND_Y + 50 + 16
HOME = (24, 946)
PLAT = (966, 1372)
CLOUD = (1392, 1676)
BOUNDARY_X = 956
PAD = 18                                               # inner padding of every box
APP, SVC, MCP = (R1[0], 340), (380, 550), (590, R3[1])   # app, ThingTracker service (the MCP host), MCP server
PX0, PX1 = 988, 1250                                   # platform box x-range
LX0, LX1 = 1414, 1654                                  # language model panel x-range
LLM_OUT_1, LLM_BACK_1 = ["frase, pergunta,", "caso duvidoso"], ["regra, resposta,", "veredicto"]
INK, MUTED, BLUE, DEEP, LINE, FAINT = "#111", "#555", "#0084D6", "#003399", "#D0D0D0", "#777"

# energy per model: time measured on our laptop GPU x the edge box's power x the Portuguese price
WATTS, EUR_KWH, SECONDS_A_MONTH = 15, 0.2367, 730 * 3600      # business case B15 (base), A24 (Eurostat)
ACTIVE_HOURS = 2      # the models run only while something moves or makes sound; 2 h a day is an EXAMPLE


def eur_month(seconds_per_frame):
    return seconds_per_frame * WATTS * SECONDS_A_MONTH * ACTIVE_HOURS / 24 / 3.6e6 * EUR_KWH


E_OWL, E_DINO, E_DEPTH = eur_month(0.57), eur_month(0.022), eur_month(0.055)


def eur_pt(v):
    """Electricity a month in Portuguese format; below a cent it says so instead of showing 0,00."""
    return "< 0,01 €/mês*" if v < 0.01 else f"≈ {v:.2f} €/mês*".replace(".", ",")

out = []
_fonts = {}


def font(size, weight):
    key = (size, weight)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, size, index=1 if weight >= 700 else 0)
    return _fonts[key]


def width(s, size=13.5, weight=400):
    return font(size, weight).getlength(s.replace("_", ""))


def wrap(s, max_w, size=13.5, weight=400):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and width(trial, size, weight) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13.5, weight=400, fill="#333", anchor="start", family=None):
    fam = f' font-family="{family}"' if family else ""
    body = re.sub(r"(?<![\w])_([^_]+)_(?![\w])", lambda m: f'<tspan font-style="italic">{m.group(1)}</tspan>', esc(s))
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{fam}>{body}</text>')


def rect(x, y, w, h, fill="#FFF", stroke=LINE, rx=14, sw=1):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>')


def paragraphs(x, y, max_w, paras, size=13.5, lead=19, fill="#333", weight=400):
    """Draw wrapped paragraphs; returns the baseline after the last line."""
    for p in paras:
        for ln in wrap(p, max_w, size, weight):
            text(x, y, ln, size, weight, fill)
            y += lead
    return y


def box(x0, x1, row, title, paras):
    y0, y1 = row
    rect(x0, y0, x1 - x0, y1 - y0)
    text(x0 + PAD, y0 + 30, title, 16, 700, INK)
    end = paragraphs(x0 + PAD, y0 + 54, x1 - x0 - 2 * PAD, paras)
    assert end - 19 <= y1 - 12, f"text overflows the box '{title}'"


def icon(name, x, y, h):
    data = (ICONS / f"{name}.png").read_bytes()
    w0, h0 = struct.unpack(">II", data[16:24])
    w = round(w0 * h / h0, 1)
    out.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(data).decode()}"/>')
    return w


def arrow(d, color="#333", both=False, width=2):
    m = "b" if color == BLUE else "a"
    start = f' marker-start="url(#{m})"' if both else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{start} marker-end="url(#{m})"/>')


def label(x, y, lines, anchor="start", bold_first=True):
    """Line labels in the accent blue: by default the first line bold, the rest regular."""
    for i, s in enumerate(lines):
        text(x, y + i * 15, s, 12, 700 if (i == 0 and bold_first) else 400, BLUE, anchor)


def logo_tile(x, y, name, caption):
    rect(x, y, 42, 42, fill="#FFF", stroke=None, rx=10)
    svg = HERE / "logos" / f"{name}.svg"
    if svg.exists():
        m = re.search(r'<path fill="([^"]+)" d="([^"]+)"', svg.read_text())
        out.append(f'<svg x="{x + 8}" y="{y + 8}" width="26" height="26" viewBox="0 0 24 24"><path fill="{m.group(1)}" d="{m.group(2)}"/></svg>')
    else:
        data = base64.b64encode((HERE / "logos" / f"{name}.png").read_bytes()).decode()
        out.append(f'<image x="{x + 6}" y="{y + 6}" width="30" height="30" href="data:image/png;base64,{data}"/>')
    text(x + 21, y + 57, caption, 10.5, 400, "#DCE5F7", "middle")


# ---------------------------------------------------------------- canvas and bands
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" role="img" '
           'aria-label="Arquitetura do ThingTracker: perceção local em casa, um canal seguro para a plataforma Altice '
           'e um modelo de linguagem sob contrato">')
out.append('<title>Arquitetura do ThingTracker</title>')
out.append('<defs>'
           '<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0 1.8 L10 5 L0 8.2 Z" fill="#333"/></marker>'
           f'<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0 1.8 L10 5 L0 8.2 Z" fill="{BLUE}"/></marker>'
           '</defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#FFF"/>')

rect(HOME[0], BAND_TOP, HOME[1] - HOME[0], BAND_BOTTOM - BAND_TOP, fill="#F6F6F6", stroke=None, rx=20)
text(48, 100, "Em casa · serviço local do _ThingTracker_", 20, 700, "#000")
text(48, 122, "Corre no _gateway_ da casa ou numa pequena caixa (um portátil, na demonstração). A análise fica em casa.", 13.5, 400, MUTED)
rect(PLAT[0], BAND_TOP, PLAT[1] - PLAT[0], BAND_BOTTOM - BAND_TOP, fill="#EEF3FB", stroke=None, rx=20)
text(PX0, 100, "Plataforma Altice", 20, 700, "#1A2233")
text(PX0, 122, "_Cognitive Home_", 13.5, 400, MUTED)
rect(CLOUD[0], BAND_TOP, CLOUD[1] - CLOUD[0], BAND_BOTTOM - BAND_TOP, fill=DEEP, stroke=None, rx=20)
text(LX0, 100, "Modelo de linguagem", 20, 700, "#FFF")
text(LX0, 122, "Chamado só quando é preciso", 13.5, 400, "#C9D6F0")

out.append(f'<line x1="{BOUNDARY_X}" y1="{BAND_TOP + 6}" x2="{BOUNDARY_X}" y2="{BAND_BOTTOM - 6}" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="8 7"/>')
out.append(f'<text font-size="12" font-weight="700" fill="{BLUE}" letter-spacing="1" transform="translate({BOUNDARY_X - 6} {R1[1] - 60}) rotate(-90)">FRONTEIRA DA CASA</text>')

# ---------------------------------------------------------------- home, row 1
# Cameras above the privacy guard, in one column as wide as Enrolment below, so lines stay long and even
COL = (48, 362)
CAM_ROW = (R1[0], R1[0] + 110)
GUARD_ROW = (R1[1] - 110, R1[1])
PERC = (386, 866)
box(*COL, CAM_ROW, "Câmaras RTSP", ["Em repouso até haver movimento ou som; só então lê 1 a 2 imagens por segundo."])
text(COL[0] + PAD, CAM_ROW[1] - PAD, "Câmara do kit: H.265 · 2304 × 1296 · 20 fps, via _relay_", 11, 400, FAINT)
box(*COL, GUARD_ROW, "Filtro de privacidade", ["Máscaras nunca analisadas; imagens apagadas após a análise. "
                                               "Pessoas contadas, não reconhecidas, salvo com consentimento."])
rect(PERC[0], R1[0], PERC[1] - PERC[0], R1[1] - R1[0], stroke=BLUE, sw=2)
text(PERC[0] + PAD, R1[0] + 30, "Perceção · modelos _open-source_ locais", 16, 700, INK)
chips = [
    ("Deteção por nome", "_OWLv2_ base", f"0,62 GB · {eur_pt(E_OWL)}", "LVIS (raras): 40,5 AP"),
    ("Seguimento", "_ByteTrack_", "sem pesos · CPU", "MOT17: 80,3 MOTA"),
    ("Assinatura visual", "_DINOv2 small_", f"0,09 GB · {eur_pt(E_DINO)}", "ImageNet: 81,1 %"),
    ("Lugares", "_OWLv2_ (o mesmo)", "+0 GB · +0 €", "secretária, sofá, porta…"),
    ("Profundidade", "_Depth Anything V2_", f"0,10 GB · {eur_pt(E_DEPTH)}", "DA-2K: 95,3 %"),
    ("Pessoas", "_OWLv2_ (o mesmo)", "+0 GB · +0 €", "conhecidas: opcional"),
]
CW, CH, CG = (PERC[1] - PERC[0] - 2 * PAD - 16) // 3, 70, 8
for i, (t, model, stats, bench) in enumerate(chips):
    cx = PERC[0] + PAD + (i % 3) * (CW + CG)
    cy = R1[0] + 46 + (i // 3) * (CH + 6)
    rect(cx, cy, CW, CH, fill="#E6F2FB", stroke=None, rx=8)
    text(cx + 10, cy + 17, t, 12.5, 700, DEEP)
    text(cx + 10, cy + 33, model, 12.5)
    text(cx + 10, cy + 49, stats, 10.5, 400, MUTED)
    text(cx + 10, cy + 62, bench, 10.5, 400, MUTED)
    assert max(width(model, 12.5), width(stats, 10.5), width(bench, 10.5)) <= CW - 20, t
foot_y = R1[0] + 46 + 2 * CH + 6 + 18
text(PERC[0] + PAD, foot_y, "Por modelo: espaço em disco · eletricidade por mês* · resultado publicado", 11, 400, MUTED)
text(PERC[0] + PAD, foot_y + 14, f"* tempo medido × {WATTS} W × {str(EUR_KWH).replace('.', ',')} €/kWh (PT), com {ACTIVE_HOURS} h de movimento por dia (exemplo)", 11, 400, MUTED)

# ---------------------------------------------------------------- home, row 2
ENROL, MEM, ENG = (48, 362), (418, 626), (650, 866)
box(*ENROL, R2, "Registo de objetos", ["Reúne o nome, a assinatura visual e o lugar habitual de cada objeto, para encontrar "
                                      "as suas chaves e não quaisquer chaves. Basta mostrar o objeto à câmara durante 3 s ou tirar 3 fotografias."])
box(*MEM, R2, "Memória da casa", ["O quê, onde e quando", "Última vez e cronologia", "Quem está em casa", "Guardada 30 dias, sem vídeo"])
box(*ENG, R2, "Motor de regras", ["Avalia as regras sobre a memória, a cada segundo.", "Resposta: nada, lembrar, avisar, agir ou escalar."])

# ---------------------------------------------------------------- home, row 3: the Altice kit
DEV = (48, 866)
rect(DEV[0], R3[0], DEV[1] - DEV[0], R3[1] - R3[0])
title = "Dispositivos da casa (kit Altice)"
text(DEV[0] + PAD, R3[0] + 30, title, 16, 700, INK)
text(DEV[0] + PAD + width(title, 16, 700) + 12, R3[0] + 30,
     "Os comandos passam pela plataforma, como hoje: nenhum caminho novo.", 13.5, 400, MUTED)
devices = [("camera", "Câmara", "vídeo, sirene, visão noturna", "Tuya SC034-WNV3"),
           ("light", "Lâmpada", "cor, branco e cenas", "E27 · Wi-Fi"),
           ("plug", "Tomada", "liga e desliga aparelhos", "Wi-Fi · mede kWh"),
           ("security-hub", "Central", "sirene, armar, _gateway_ LTE", "MS-WES1AS"),
           ("contact-sensor", "Contacto", "abertura de porta ou janela", "MS-D3D"),
           ("smoke-sensor", "Fumo", "alarme, sirene de 85 dB", "EN 14604, ótico"),
           ("temperature-sensor", "Clima", "temperatura e humidade", "Nedis ZBSC10WT")]
TG, TP = 8, 8                                           # gap between tiles, padding inside a tile
TW = (DEV[1] - DEV[0] - 2 * PAD - (len(devices) - 1) * TG) / len(devices)
TH = R3[1] - R3[0] - 46 - 14
for i, (ic, name, role, model) in enumerate(devices):
    x, y = DEV[0] + PAD + i * (TW + TG), R3[0] + 46
    rect(round(x, 1), y, round(TW, 1), TH, fill="#F6F6F6", stroke=None, rx=10)
    tx, inner = round(x + TP, 1), TW - 2 * TP
    icon(ic, tx, y + 12, 24)
    text(tx, y + 54, name, 12, 700, INK)
    role_lines = wrap(role, inner, 11.5)
    assert len(role_lines) <= 2 and width(name, 12, 700) <= inner and width(model, 10, 700) <= inner, name
    for j, ln in enumerate(role_lines):
        text(tx, y + 71 + j * 15, ln, 11.5, 400, MUTED)
    text(tx, y + TH - 9, model, 10, 700, FAINT)

# ---------------------------------------------------------------- platform and language model
def stack(top, bottom, blocks):
    """Place blocks so the first starts at `top` and the last ends at `bottom`, with equal gaps between them.
    Each block is (span, draw): span is the distance from its first baseline to its last."""
    gap = (bottom - top - sum(sp for sp, _ in blocks)) / (len(blocks) - 1)
    assert gap >= 22, f"blocks do not fit: gap {gap:.1f}"
    ys, y = [], top
    for sp, draw in blocks:
        draw(round(y, 1))
        ys.append(round(y, 1))
        y += sp + gap
    return ys


def para_block(x, max_w, s, size=13.5, lead=19, fill="#333", weight=400):
    n = len(wrap(s, max_w, size, weight))
    return (n - 1) * lead, lambda y: paragraphs(x, y, max_w, [s], size, lead, fill, weight)


PW = PX1 - PX0 - 2 * PAD
rect(PX0, APP[0], PX1 - PX0, APP[1] - APP[0], stroke="#C9D2E3")
stack(APP[0] + 30, APP[1] - PAD - 4, [
    (24, lambda y: (text(PX0 + PAD, y, "Aplicação Altice", 16, 700, "#1A2233"),
                    text(PX0 + PAD, y + 24, "Novo separador “Things”", 13.5, 700, BLUE))),
    *[para_block(PX0 + PAD, PW, t) for t in ["Adicionar um objeto: sugerido, mostrado à câmara ou 3 fotografias",
                                             "Sensores a partir de uma frase", "Perguntar: “Onde estão as chaves?”",
                                             "Avisos; vídeo em direto, como hoje"]],
])

# the host: the only component that talks to the language model, and the client of the MCP server
rect(PX0, SVC[0], PX1 - PX0, SVC[1] - SVC[0], stroke=BLUE, sw=2)
stack(SVC[0] + 30, SVC[1] - PAD - 4, [
    (24, lambda y: (text(PX0 + PAD, y, "Serviço _ThingTracker_", 16, 700, "#1A2233"),
                    text(PX0 + PAD, y + 24, "O único que chama o modelo", 13.5, 700, BLUE))),
    *[para_block(PX0 + PAD, PW, t) for t in ["Ciclo: modelo ↔ ferramentas MCP", "Escolhe o modelo e a região",
                                             "Limita o gasto por casa", "Recebe os eventos das casas"]],
])

rect(PX0, MCP[0], PX1 - PX0, MCP[1] - MCP[0], stroke="#C9D2E3")
desc_span, desc_draw = para_block(PX0 + PAD, PW, "18 ferramentas da Altice: dispositivos, cenários e segurança")
trig_span, trig_draw = para_block(PX0 + PAD, PW, "objetos e pessoas iniciam cenários")


def tools(y):
    text(PX0 + PAD, y, "+ Ferramentas _Things_ (novas)", 13.5, 700, BLUE)
    for i, t in enumerate(["list_things", "create_thing", "get_thing_last_seen", "get_thing_timeline"]):
        text(PX0 + PAD + (i // 2) * 92, y + 20 + (i % 2) * 16, t, 11, 400, DEEP, family="Menlo, monospace")


stack(MCP[0] + 30, MCP[1] - PAD - 4, [
    (24 + desc_span, lambda y: (text(PX0 + PAD, y, "Servidor MCP", 16, 700, "#1A2233"), desc_draw(y + 24))),
    (20 + 16, tools),
    (22 + trig_span, lambda y: (text(PX0 + PAD, y, "+ Acionador _thingTracker_ (novo)", 13.5, 700, BLUE), trig_draw(y + 22))),
])

L0, L1 = R1[0], R3[1]
rect(LX0, L0, LX1 - LX0, L1 - L0, fill="#0A3FA3", stroke=None)
X, LW = LX0 + PAD, LX1 - LX0 - 2 * PAD


def logos(heading, items):
    def draw(y):
        text(X, y, heading, 12.5, 700, "#C9D6F0")
        for i, (n, cap) in enumerate(items):
            logo_tile(X + i * 54, y + 10, n, cap)
    return 10 + 57, draw


def jobs(y):
    for k, (t, s) in enumerate([("Frase → regra", "uma vez, ao criar um sensor"), ("Responder a perguntas", "a partir da memória, em texto"),
                                ("Avaliar casos duvidosos", "a partir de um recorte, raramente")]):
        text(X, y + k * 46, t, 13.5, 700, "#FFF")
        text(X, y + k * 46 + 18, s, 13.5, 400, "#C9D6F0")


def measured(y):
    text(X, y, "Custo do modelo de linguagem", 12.5, 700, "#C9D6F0")
    text(X, y + 20, "≈ 0,43 € por casa e por mês", 13.5, 700, "#FFF")
    text(X, y + 38, "cenário base (0,10 a 1,78 €)", 13.5, 400, "#C9D6F0")


ys = stack(L0 + 30, L1 - PAD - 4, [
    (20, lambda y: (text(X, y, "Qualquer modelo capaz,", 16, 700, "#FFF"), text(X, y + 20, "sob contrato", 16, 700, "#FFF"))),
    logos("Alojados, processamento na UE", [("claude", "Claude"), ("openai", "OpenAI"), ("gemini", "Gemini"), ("mistral", "Mistral")]),
    logos("_Open-weight_, alojados pela Altice", [("qwen", "Qwen"), ("deepseek", "DeepSeek"), ("kimi", "Kimi")]),
    para_block(X, LW, "Só com: sem treino com os nossos dados, acordo de tratamento de dados, processamento na UE", 13, 18, "#FFF", 700),
    (2 * 46 + 18, jobs),
    (38, measured),
])
JOBS_Y = ys[4]

# ---------------------------------------------------------------- lines (all straight)
mid1, mid2, mid3 = (R1[0] + R1[1]) // 2, (R2[0] + R2[1]) // 2, (R3[0] + R3[1]) // 2
arrow(f"M{(COL[0] + COL[1]) // 2} {CAM_ROW[1]} V{GUARD_ROW[0] - 4}")
arrow(f"M{COL[1]} {(GUARD_ROW[0] + GUARD_ROW[1]) // 2} H{PERC[0] - 4}")
# one arrow per direction, each with its own label, so the direction of every flow is unambiguous
def pair_h(x_left, x_right, y, right_label, left_label):
    """Two arrows; each label may be several lines: above the upper arrow, below the lower one."""
    right_label = [right_label] if isinstance(right_label, str) else right_label
    left_label = [left_label] if isinstance(left_label, str) else left_label
    arrow(f"M{x_left} {y - 7} H{x_right - 4}")
    label(x_left + 12, y - 17 - 15 * (len(right_label) - 1), right_label, bold_first=False)
    arrow(f"M{x_right} {y + 7} H{x_left + 4}")
    label(x_left + 12, y + 26, left_label, bold_first=False)


def pair_v(x, y_top, y_bottom, up_label, down_label):
    arrow(f"M{x - 7} {y_bottom} V{y_top + 4}")
    label(x - 17, (y_top + y_bottom) // 2 + 4, [up_label], "end", bold_first=False)
    arrow(f"M{x + 7} {y_top} V{y_bottom - 4}")
    label(x + 17, (y_top + y_bottom) // 2 + 4, [down_label], bold_first=False)


# perception reads the fingerprints from the memory and writes sightings to it
pair_v(MEM[0] + 104, R1[1], R2[0], "assinaturas", "observações")
arrow(f"M{ENROL[1]} {mid2} H{MEM[0] - 4}")
label((ENROL[1] + MEM[0]) // 2, mid2 - 10, ["objetos"], "middle")
arrow(f"M{MEM[1]} {mid2} H{ENG[0] - 4}")
# the two lines that cross the house boundary, labelled inside the corridor
arrow(f"M{ENG[1]} {mid2} H{PX0 - 4}", color=BLUE, both=True, width=2.5)
label(878, mid2 - 26, ["canal", "seguro"])
arrow(f"M{PX0} {mid3} H{DEV[1] + 4}")
label(878, mid3 - 11, ["comandos"])
PXM = (PX0 + PX1) // 2
pair_v(PXM, APP[1], SVC[0], "respostas, avisos", "pedidos")
pair_v(PXM, SVC[1], MCP[0], "resultados", "chamadas")
# the service is the only box that talks to the language model
pair_h(PX1, LX0, (SVC[0] + SVC[1]) // 2, LLM_OUT_1, LLM_BACK_1)

# ---------------------------------------------------------------- legend
rect(24, LEGEND_Y, W - 48, 50, fill="#F6F6F6", stroke=None, rx=12)
out.append(f'<text x="48" y="{LEGEND_Y + 31}" font-size="14" fill="#333">'
           f'<tspan font-weight="700" fill="{BLUE}">Atravessa a fronteira da casa</tspan>'
           '<tspan>   ·   Sai: eventos, objetos, um recorte se um caso for duvidoso   ·   Entra: regras e comandos   ·   </tspan>'
           '<tspan font-weight="700">Só por escolha do utilizador:</tspan>'
           '<tspan> vídeo em direto, como hoje; reconhecer pessoas registadas pela família</tspan></text>')
out.append("</svg>")

svg_path = HERE / "thingtracker-architecture.svg"
svg_path.write_text("\n".join(out) + "\n")
png = HERE / "thingtracker-architecture.png"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={png}", svg_path.as_uri()], check=True, capture_output=True)
print("built", svg_path.name, "and", png.name, f"({W}x{H}); energy €/month at {ACTIVE_HOURS} h of movement a day:",
      f"OWLv2 {E_OWL:.3f}, DINOv2 {E_DINO:.3f}, depth {E_DEPTH:.3f}, total {E_OWL + E_DINO + E_DEPTH:.2f}")
