#!/usr/bin/env python3
"""Build docs/architecture/thingtracker-architecture.svg (and .png with Chrome).

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
APP, MCP = (R1[0], R1[1]), (R2[0], R3[1])              # platform boxes sit on the same grid
PX0, PX1 = 988, 1250                                   # platform box x-range
LX0, LX1 = 1414, 1654                                  # language model panel x-range
INK, MUTED, BLUE, DEEP, LINE, FAINT = "#111", "#555", "#0084D6", "#003399", "#D0D0D0", "#777"

# energy per model: time measured on our laptop GPU x the edge box's power x the Portuguese price
WATTS, EUR_KWH, SECONDS_A_MONTH = 15, 0.2367, 730 * 3600      # business case B15 (base), A24 (Eurostat)


def eur_month(seconds_per_frame):
    return seconds_per_frame * WATTS * SECONDS_A_MONTH / 3.6e6 * EUR_KWH


E_OWL, E_DINO, E_DEPTH = eur_month(0.57), eur_month(0.022), eur_month(0.055)

out = []
_fonts = {}


def font(size, weight):
    key = (size, weight)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, size, index=1 if weight >= 700 else 0)
    return _fonts[key]


def width(s, size=13.5, weight=400):
    return font(size, weight).getlength(s)


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
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{fam}>{esc(s)}</text>')


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
           'aria-label="ThingTracker architecture: local perception in the home, one secure channel to the Altice platform, '
           'and a language model under contract">')
out.append('<title>ThingTracker architecture</title>')
out.append('<defs>'
           '<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#333"/></marker>'
           f'<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{BLUE}"/></marker>'
           '</defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#FFF"/>')

rect(HOME[0], BAND_TOP, HOME[1] - HOME[0], BAND_BOTTOM - BAND_TOP, fill="#F6F6F6", stroke=None, rx=20)
text(48, 100, "In the home · ThingTracker edge service", 20, 700, "#000")
text(48, 122, "Runs on the home gateway or a small edge box (a laptop in the demo). The analysis stays in the home.", 13.5, 400, MUTED)
rect(PLAT[0], BAND_TOP, PLAT[1] - PLAT[0], BAND_BOTTOM - BAND_TOP, fill="#EEF3FB", stroke=None, rx=20)
text(PX0, 100, "Altice platform", 20, 700, "#1A2233")
text(PX0, 122, "Cognitive Home", 13.5, 400, MUTED)
rect(CLOUD[0], BAND_TOP, CLOUD[1] - CLOUD[0], BAND_BOTTOM - BAND_TOP, fill=DEEP, stroke=None, rx=20)
text(LX0, 100, "Language model", 20, 700, "#FFF")
text(LX0, 122, "Called by the platform, only when needed", 13.5, 400, "#C9D6F0")

out.append(f'<line x1="{BOUNDARY_X}" y1="{BAND_TOP + 6}" x2="{BOUNDARY_X}" y2="{BAND_BOTTOM - 6}" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="8 7"/>')
out.append(f'<text font-size="12" font-weight="700" fill="{BLUE}" letter-spacing="1" transform="translate({BOUNDARY_X - 6} {R1[1] - 60}) rotate(-90)">HOUSE BOUNDARY</text>')

# ---------------------------------------------------------------- home, row 1
CAM, GUARD, PERC = (48, 198), (222, 382), (406, 866)
box(*CAM, R1, "Cameras", ["RTSP on the home network.", "Read at 1–2 frames/s through one open connection."])
y = R1[1] - PAD - 50                                   # the kit camera, anchored to the bottom of the box
icon("camera", CAM[0] + PAD, y - 4, 22)
for i, s in enumerate(["Tuya SC034-WNV3", "H.265 · 2304 × 1296", "20 fps, via a relay"]):
    text(CAM[0] + PAD, y + 32 + i * 14, s, 10.5, 700 if i == 0 else 400, FAINT)
box(*GUARD, R1, "Privacy guard", ["Masked areas: never analysed.", "Frames dropped after use; no video stored.",
                                  "People counted, not recognised, unless the household enrols them, with consent."])

rect(PERC[0], R1[0], PERC[1] - PERC[0], R1[1] - R1[0], stroke=BLUE, sw=2)
text(PERC[0] + PAD, R1[0] + 30, "Perception · local open-source models", 16, 700, INK)
chips = [
    ("Detect by name", "OWLv2 base", f"0.62 GB · ≈ €{E_OWL:.2f}/mo", "LVIS rare: 40.5 AP"),
    ("Track", "ByteTrack", "no weights · CPU", "MOT17: 80.3 MOTA"),
    ("Fingerprint", "DINOv2 small", f"0.09 GB · ≈ €{E_DINO:.2f}/mo", "ImageNet: 81.1 %"),
    ("Places", "OWLv2, same pass", "+0 GB · +€0", "desk, sofa, door…"),
    ("Depth", "Depth Anything V2", f"0.10 GB · ≈ €{E_DEPTH:.2f}/mo", "DA-2K: 95.3 %"),
    ("People", "OWLv2, same pass", "+0 GB · +€0", "known people: opt-in"),
]
CW, CH, CG = 136, 70, 8
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
text(PERC[0] + PAD, foot_y, "Under each model: disk size · electricity a month · published benchmark", 11, 400, MUTED)
text(PERC[0] + PAD, foot_y + 14, f"Electricity: measured s/frame × {WATTS} W × €{EUR_KWH}/kWh (PT), at 1 frame/s", 11, 400, MUTED)

# ---------------------------------------------------------------- home, row 2
ENROL, MEM, ENG = (48, 362), (418, 626), (650, 866)
box(*ENROL, R2, "Enrolment", ["Show a thing to a camera for about 3 s, or take 3 photos with the phone. About 8 crops "
                              "become its fingerprint, so it finds your keys, not any keys."])
box(*MEM, R2, "Scene memory", ["What, where and when", "Last seen, timelines", "Who is home (known phones)", "Kept 30 days, no video"])
box(*ENG, R2, "Sensor engine", ["Runs the compiled rules on the memory, every second.", "Answer: nothing, remember, tell, act or escalate."])

# ---------------------------------------------------------------- home, row 3: the Altice kit
DEV = (48, 866)
rect(DEV[0], R3[0], DEV[1] - DEV[0], R3[1] - R3[0])
title = "Home devices (the Altice kit)"
text(DEV[0] + PAD, R3[0] + 30, title, 16, 700, INK)
text(DEV[0] + PAD + width(title, 16, 700) + 12, R3[0] + 30,
     "Commands go through the platform, as today: ThingTracker adds no new path.", 13.5, 400, MUTED)
devices = [("light", "Smart light", "colour, white, scenes", "E27 bulb · Wi-Fi"),
           ("plug", "Smart plug", "any appliance on/off by event", "Wi-Fi · energy meter"),
           ("security-hub", "Security hub", "siren, arming, LTE gateway", "MS-WES1AS"),
           ("contact-sensor", "Contact sensor", "door or window, open / closed", "MS-D3D"),
           ("smoke-sensor", "Smoke sensor", "smoke alarm, 85 dB siren", "EN 14604, optical"),
           ("temperature-sensor", "Climate sensor", "temperature and humidity", "Nedis ZBSC10WT")]
TW = (DEV[1] - DEV[0] - 2 * PAD - 5 * 10) / 6
TH = R3[1] - R3[0] - 46 - 14
for i, (ic, name, role, model) in enumerate(devices):
    x, y = DEV[0] + PAD + i * (TW + 10), R3[0] + 46
    rect(round(x, 1), y, round(TW, 1), TH, fill="#F6F6F6", stroke=None, rx=10)
    tx = round(x + 10, 1)
    icon(ic, tx, y + 12, 26)
    text(tx, y + 56, name, 13, 700, INK)
    role_lines = wrap(role, TW - 20, 12)
    assert len(role_lines) <= 2 and width(name, 13, 700) <= TW - 20 and width(model, 10.5, 700) <= TW - 20, name
    for j, ln in enumerate(role_lines):
        text(tx, y + 73 + j * 15, ln, 12, 400, MUTED)
    text(tx, y + TH - 9, model, 10.5, 700, FAINT)

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
    (24, lambda y: (text(PX0 + PAD, y, "Altice app", 16, 700, "#1A2233"),
                    text(PX0 + PAD, y + 24, "New Things tab", 13.5, 700, BLUE))),
    *[para_block(PX0 + PAD, PW, t) for t in ["Add a thing: suggested, shown to a camera, or 3 photos", "Places and masks",
                                             "Sensors from one sentence", "Ask: “Where are my keys?”",
                                             "Alerts; live view and clips as today"]],
])

rect(PX0, MCP[0], PX1 - PX0, MCP[1] - MCP[0], stroke="#C9D2E3")
desc_span, desc_draw = para_block(PX0 + PAD, PW, "Devices, scenarios, security: 18 tools today")
trig_span, trig_draw = para_block(PX0 + PAD, PW, "thingTracker: a thing or person condition starts any scenario, "
                                                 "e.g. the smart plug switches the kettle on")


def tools(y):
    text(PX0 + PAD, y, "+ Things tools (new)", 13.5, 700, BLUE)
    for i, t in enumerate(["list_things", "create_thing", "get_thing_last_seen", "get_thing_timeline"]):
        text(PX0 + PAD, y + 22 + i * 18, t, 12, 400, DEEP, family="Menlo, monospace")


foot_span, foot_draw = para_block(PX0 + PAD, PW, "One secure channel per home: events and rules in, actions out", fill=MUTED)
stack(MCP[0] + 30, MCP[1] - PAD - 4, [
    (24 + desc_span, lambda y: (text(PX0 + PAD, y, "MCP server", 16, 700, "#1A2233"), desc_draw(y + 24))),
    (22 + 3 * 18, tools),
    (22 + trig_span, lambda y: (text(PX0 + PAD, y, "+ Scenario trigger (new)", 13.5, 700, BLUE), trig_draw(y + 22))),
    (foot_span, foot_draw),
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
    for k, (t, s) in enumerate([("Sentence → rule", "once, when a sensor is made"), ("Answer questions", "from the memory, as text"),
                                ("Judge unclear cases", "from one crop, rarely")]):
        text(X, y + k * 46, t, 13.5, 700, "#FFF")
        text(X, y + k * 46 + 18, s, 13.5, 400, "#C9D6F0")


def measured(y):
    text(X, y, "Cost: measured calls × usage", 12.5, 700, "#C9D6F0")
    text(X, y + 20, "≈ €0.43 per home a month", 13.5, 700, "#FFF")
    text(X, y + 38, "base case (€0.10–1.78)", 13.5, 400, "#C9D6F0")


ys = stack(L0 + 30, L1 - PAD - 4, [
    (20, lambda y: (text(X, y, "Any capable model,", 16, 700, "#FFF"), text(X, y + 20, "under contract", 16, 700, "#FFF"))),
    logos("Hosted, EU processing", [("claude", "Claude"), ("openai", "OpenAI"), ("gemini", "Gemini"), ("mistral", "Mistral")]),
    logos("Open weights, run by Altice", [("qwen", "Qwen"), ("deepseek", "DeepSeek"), ("kimi", "Kimi")]),
    para_block(X, LW, "Only with: no training on our data, a DPA, EU processing", 13, 18, "#FFF", 700),
    (2 * 46 + 18, jobs),
    (38, measured),
    para_block(X, LW, "Sees text, and a crop only when a case is unclear", 12.5, 17, "#C9D6F0"),
])
JOBS_Y = ys[4]

# ---------------------------------------------------------------- lines (all straight)
mid1, mid2, mid3 = (R1[0] + R1[1]) // 2, (R2[0] + R2[1]) // 2, (R3[0] + R3[1]) // 2
arrow(f"M{CAM[1]} {mid1} H{GUARD[0] - 4}")
arrow(f"M{GUARD[1]} {mid1} H{PERC[0] - 4}")
# perception reads the fingerprints from the memory and writes sightings to it
vx = MEM[0] + 104
arrow(f"M{vx} {R1[1]} V{R2[0] - 4}", both=True)
label(vx - 10, R1[1] + 24, ["fingerprints"], "end")
label(vx + 10, R1[1] + 24, ["sightings"])
arrow(f"M{ENROL[1]} {mid2} H{MEM[0] - 4}")
label((ENROL[1] + MEM[0]) // 2, mid2 - 10, ["things"], "middle")
arrow(f"M{MEM[1]} {mid2} H{ENG[0] - 4}")
# the two lines that cross the house boundary, labelled inside the corridor
arrow(f"M{ENG[1]} {mid2} H{PX0 - 4}", color=BLUE, both=True, width=2.5)
label(878, mid2 - 26, ["secure", "channel"])
arrow(f"M{PX0} {mid3} H{DEV[1] + 4}")
label(878, mid3 - 26, ["device", "commands"])
arrow(f"M{(PX0 + PX1) // 2} {APP[1]} V{MCP[0] - 4}", both=True)
# platform <-> language model, labelled inside the platform band's corridor
arrow(f"M{PX1} {mid1} H{LX0 - 4}", both=True)
label(PX1 + 12, mid1 - 26, ["text only", "sentence, question"])
label(PX1 + 12, mid1 + 22, ["rule, answer"], bold_first=False)
y_judge = JOBS_Y + 2 * 46 + 5
arrow(f"M{PX1} {y_judge} H{LX0 - 4}", both=True)
label(PX1 + 12, y_judge - 26, ["one crop", "when unclear"])
label(PX1 + 12, y_judge + 22, ["a verdict"], bold_first=False)

# ---------------------------------------------------------------- legend
rect(24, LEGEND_Y, W - 48, 50, fill="#F6F6F6", stroke=None, rx=12)
out.append(f'<text x="48" y="{LEGEND_Y + 31}" font-size="14" fill="#333">'
           f'<tspan font-weight="700" fill="{BLUE}">Crosses the house boundary</tspan>'
           '<tspan>   ·   Out: events, things, one crop when a case is unclear   ·   In: rules, device commands   ·   </tspan>'
           '<tspan font-weight="700">Only by the user’s choice:</tspan>'
           '<tspan> live view and clips, as in the app today; recognising people the household enrolled</tspan></text>')
out.append("</svg>")

svg_path = HERE / "thingtracker-architecture.svg"
svg_path.write_text("\n".join(out) + "\n")
png = HERE / "thingtracker-architecture.png"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={png}", svg_path.as_uri()], check=True, capture_output=True)
print("built", svg_path.name, "and", png.name, f"({W}x{H}); energy €/month at 1 frame/s:",
      f"OWLv2 {E_OWL:.3f}, DINOv2 {E_DINO:.3f}, depth {E_DEPTH:.3f}, total {E_OWL + E_DINO + E_DEPTH:.2f}")
