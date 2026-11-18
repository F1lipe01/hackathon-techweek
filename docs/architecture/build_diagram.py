#!/usr/bin/env python3
"""Build docs/architecture/thingtracker-architecture.svg (and .png with Chrome).

Every position comes from the grid below, so boxes line up and lines stay straight.
    python3 docs/architecture/build_diagram.py
"""
import base64
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W, H = 1600, 790
BAND_TOP, BAND_BOTTOM = 64, 700
ROWS = [(150, 300), (340, 490), (530, 680)]          # three rows, 40 px apart
HOME = (24, 946)                                    # band x-range
PLAT = (966, 1272)
CLOUD = (1292, 1576)
BOUNDARY_X = 956
INK, MUTED, BLUE, DEEP, LINE = "#111", "#555", "#0084D6", "#003399", "#D0D0D0"

out = []


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13.5, weight=400, fill="#333", anchor="start", family=None):
    fam = f' font-family="{family}"' if family else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{fam}>{esc(s)}</text>')


def rect(x, y, w, h, fill="#FFF", stroke=LINE, rx=14, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{d}/>')


def box(x0, x1, row, title, lines, title_fill=INK, stroke=LINE, sw=1, sub=None):
    y0, y1 = row
    rect(x0, y0, x1 - x0, y1 - y0, stroke=stroke, sw=sw)
    text(x0 + 18, y0 + 30, title, 16, 700, title_fill)
    y = y0 + 54
    if sub:
        text(x0 + 18, y, sub, 13.5, 700, BLUE)
        y += 22
    for ln in lines:
        text(x0 + 18, y, ln)
        y += 19


def arrow(d, color="#333", both=False, width=2):
    m = "b" if color == BLUE else "a"
    start = f' marker-start="url(#{m})"' if both else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{start} marker-end="url(#{m})"/>')


def pill(cx, cy, label):  # kept for later use
    w = 7.2 * len(label) + 20
    rect(cx - w / 2, cy - 11, w, 22, fill="#FFF", stroke=BLUE, rx=11)
    text(cx, cy + 4.5, label, 12, 700, BLUE, "middle")


def logo_tile(x, y, name, label):
    rect(x, y, 42, 42, fill="#FFF", stroke=None, rx=10)
    svg = HERE / "logos" / f"{name}.svg"
    if svg.exists():
        m = re.search(r'<path fill="([^"]+)" d="([^"]+)"', svg.read_text())
        out.append(f'<svg x="{x + 8}" y="{y + 8}" width="26" height="26" viewBox="0 0 24 24"><path fill="{m.group(1)}" d="{m.group(2)}"/></svg>')
    else:
        data = base64.b64encode((HERE / "logos" / f"{name}.png").read_bytes()).decode()
        out.append(f'<image x="{x + 6}" y="{y + 6}" width="30" height="30" href="data:image/png;base64,{data}"/>')
    text(x + 21, y + 57, label, 10.5, 400, "#DCE5F7", "middle")


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
text(48, 122, "Runs on the home gateway or a small edge box (a laptop in the demo). Video never leaves the home.", 13.5, 400, MUTED)
rect(PLAT[0], BAND_TOP, PLAT[1] - PLAT[0], BAND_BOTTOM - BAND_TOP, fill="#EEF3FB", stroke=None, rx=20)
text(988, 100, "Altice platform", 20, 700, "#1A2233")
text(988, 122, "Cognitive Home", 13.5, 400, MUTED)
rect(CLOUD[0], BAND_TOP, CLOUD[1] - CLOUD[0], BAND_BOTTOM - BAND_TOP, fill=DEEP, stroke=None, rx=20)
text(1314, 100, "Language model", 20, 700, "#FFF")
text(1314, 122, "Called by the platform, only when needed", 13.5, 400, "#C9D6F0")

out.append(f'<line x1="{BOUNDARY_X}" y1="{BAND_TOP + 6}" x2="{BOUNDARY_X}" y2="{BAND_BOTTOM - 6}" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="8 7"/>')
out.append(f'<text font-size="12" font-weight="700" fill="{BLUE}" letter-spacing="1" transform="translate({BOUNDARY_X - 6} 290) rotate(-90)">HOUSE BOUNDARY</text>')

# ---------------------------------------------------------------- home, row 1
R1, R2, R3 = ROWS
box(48, 188, R1, "Cameras", ["RTSP on the", "home network,", "1–2 frames/s"])
box(212, 382, R1, "Privacy guard", ["Masks: never analysed", "Frames dropped after", "use; no video stored"])
rect(406, R1[0], 460, R1[1] - R1[0], stroke=BLUE, sw=2)
text(424, R1[0] + 30, "Perception · local open-source models", 16, 700, INK)
chips = [("Detect by name", "OWLv2"), ("Track", "ByteTrack"), ("Fingerprint", "DINOv2: your thing"),
         ("Places", "desk, sofa, door…"), ("Depth", "Depth Anything V2"), ("People", "presence, no identity")]
for i, (t, s) in enumerate(chips):
    cx = 424 + (i % 3) * 144
    cy = R1[0] + 46 + (i // 3) * 50
    rect(cx, cy, 136, 44, fill="#E6F2FB", stroke=None, rx=8)
    text(cx + 10, cy + 18, t, 12.5, 700, DEEP)
    text(cx + 10, cy + 35, s, 12.5)

# ---------------------------------------------------------------- home, row 2
box(48, 382, R2, "Enrolment", ["A thing is shown to a camera for", "about 3 s: ~8 crops become its", "fingerprint, so it finds your keys,", "not any keys"])
box(406, 626, R2, "Scene memory", ["What, where and when", "Last seen, timelines", "Who is home (known phones)", "Kept 30 days, no video"])
box(650, 866, R2, "Sensor engine", ["Runs the compiled rules on", "the memory, every second", "Answer: nothing, remember,", "tell, act or escalate"])

# ---------------------------------------------------------------- home, row 3: devices
rect(48, R3[0], 818, R3[1] - R3[0])
text(66, R3[0] + 30, "Home devices (the Altice kit)", 16, 700, INK)
text(66, R3[0] + 52, "Commands reach them through the platform, exactly as today. ThingTracker adds no new path.", 13.5, 400, MUTED)
devices = [("Light", "colour bulb"), ("Plug", "energy meter"), ("Alarm hub", "siren, modes"),
           ("Door sensor", "open / closed"), ("Smoke sensor", "alarm"), ("Climate sensor", "°C, humidity")]
cw, gap = 121, 10
for i, (t, s) in enumerate(devices):
    x = 66 + i * (cw + gap)
    rect(x, R3[0] + 72, cw, 54, fill="#F6F6F6", stroke=None, rx=10)
    text(x + 12, R3[0] + 94, t, 13, 700, INK)
    text(x + 12, R3[0] + 113, s, 12.5, 400, MUTED)

# ---------------------------------------------------------------- platform
APP = (150, 380)
MCP = (420, 680)
rect(988, APP[0], 262, APP[1] - APP[0], stroke="#C9D2E3")
text(1006, APP[0] + 30, "Altice app", 16, 700, "#1A2233")
text(1006, APP[0] + 54, "New Things tab", 13.5, 700, BLUE)
for i, ln in enumerate(["Add a thing: suggested, or", "shown to a camera", "Places and masks", "Sensors from one sentence",
                        "Ask: “Where are my keys?”", "Alerts and notifications"]):
    text(1006, APP[0] + 82 + i * 22 - (6 if i == 1 else 0), ln)

rect(988, MCP[0], 262, MCP[1] - MCP[0], stroke="#C9D2E3")
text(1006, MCP[0] + 30, "MCP server", 16, 700, "#1A2233")
text(1006, MCP[0] + 54, "Devices, scenarios, security:")
text(1006, MCP[0] + 73, "18 tools today")
text(1006, MCP[0] + 101, "+ Things tools (new)", 13.5, 700, BLUE)
for i, t in enumerate(["list_things", "create_thing", "get_thing_last_seen", "get_thing_timeline"]):
    text(1006, MCP[0] + 123 + i * 18, t, 12, 400, DEEP, family="Menlo, monospace")
text(1006, MCP[0] + 214, "One secure channel per home:", 13.5, 400, MUTED)
text(1006, MCP[0] + 233, "events and rules in, actions out", 13.5, 400, MUTED)

# ---------------------------------------------------------------- language model
L0, L1 = 150, 680
rect(1314, L0, 240, L1 - L0, fill="#0A3FA3", stroke=None)
text(1332, L0 + 30, "Any capable model,", 16, 700, "#FFF")
text(1332, L0 + 50, "under contract", 16, 700, "#FFF")
text(1332, L0 + 82, "Hosted, EU processing", 12.5, 700, "#C9D6F0")
for i, (n, lab) in enumerate([("claude", "Claude"), ("openai", "OpenAI"), ("gemini", "Gemini"), ("mistral", "Mistral")]):
    logo_tile(1332 + i * 54, L0 + 92, n, lab)
text(1332, L0 + 184, "Open weights, run by Altice", 12.5, 700, "#C9D6F0")
for i, (n, lab) in enumerate([("qwen", "Qwen"), ("deepseek", "DeepSeek"), ("kimi", "Kimi")]):
    logo_tile(1332 + i * 54, L0 + 194, n, lab)
text(1332, L0 + 290, "Only with: no training on our", 13, 700, "#FFF")
text(1332, L0 + 308, "data, a DPA, EU processing", 13, 700, "#FFF")
y = L0 + 346
for t, s in [("Sentence → rule", "once, when a sensor is made"), ("Answer questions", "from the memory, as text"),
             ("Judge unclear cases", "from one crop, rarely")]:
    text(1332, y, t, 13.5, 700, "#FFF")
    text(1332, y + 18, s, 13.5, 400, "#C9D6F0")
    y += 46
text(1332, y + 6, "Never sees video or full frames", 12.5, 400, "#C9D6F0")

# ---------------------------------------------------------------- lines
arrow("M188 225 H208")
arrow("M382 225 H402")
arrow("M516 300 V336")
text(526, 326, "sightings", 12, 700, BLUE)
arrow("M626 415 H646")
arrow("M382 415 H394 V282 H402")
text(404, 326, "fingerprints", 12, 700, BLUE)
# the two lines that cross the boundary, labelled inside the 90 px corridor
arrow("M866 460 H984", color=BLUE, both=True, width=2.5)
text(878, 434, "secure", 12, 700, BLUE)
text(878, 449, "channel", 12, 700, BLUE)
arrow("M988 625 H870")
text(878, 599, "device", 12, 700, BLUE)
text(878, 614, "commands", 12, 700, BLUE)
arrow(f"M1119 {APP[1]} V{MCP[0] - 4}", both=True)
arrow("M1250 265 H1310", both=True)
arrow("M1250 600 H1310", both=True)

# ---------------------------------------------------------------- legend
rect(24, 716, 1552, 50, fill="#F6F6F6", stroke=None, rx=12)
out.append('<text x="48" y="747" font-size="14" fill="#333">'
           f'<tspan font-weight="700" fill="{BLUE}">Crosses the house boundary</tspan>'
           '<tspan>   ·   Out: events, things, one crop when a case is unclear   ·   In: rules, device commands   ·   </tspan>'
           '<tspan font-weight="700">Never: video, full frames, faces, identities</tspan></text>')
out.append("</svg>")

svg_path = HERE / "thingtracker-architecture.svg"
svg_path.write_text("\n".join(out) + "\n")
png = HERE / "thingtracker-architecture.png"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={W},{H}", f"--screenshot={png}", svg_path.as_uri()], check=True, capture_output=True)
print("built", svg_path.name, "and", png.name)
