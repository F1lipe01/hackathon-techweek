#!/usr/bin/env python3
"""Build the business-case charts (16:9 SVG + PNG) from docs/16-business-case-model.csv.

Every number is read from the model by its row id, so each chart traces back to a sourced figure or a
labelled assumption. Colours: blue = money in or a good result, orange = money out or a loss,
grey = competitors (validated with the dataviz palette checker: #0084D6 / #E8710A pass every check).
    python3 docs/business-case/build_charts.py
"""
import csv
import subprocess
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"
MODEL = HERE.parent / "16-business-case-model.csv"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"

W, H = 1200, 675
BLUE, ORANGE, GREY = "#0084D6", "#E8710A", "#B9C1CC"
INK, SOFT, FAINT, GRID = "#111", "#4A4A4A", "#767676", "#E4E7EC"
X0 = 64

rows = {r[0]: r for r in csv.reader(MODEL.open()) if r and r[0][:1].isalpha() and r[0] != "id"}


def v(row_id, col=4):          # columns: id, section, item, low, base, high, ...; base by default
    return float(rows[row_id][col])


_fonts = {}


def width(s, size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, size, index=1 if bold else 0)
    return _fonts[key].getlength(s)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Chart:
    def __init__(self, name, title, subtitle, source):
        self.name, self.out = name, []
        self.text(X0, 74, title, 32, INK, bold=True)
        self.text(X0, 108, subtitle, 17, SOFT)
        self.text(X0, H - 34, source, 12.5, FAINT)

    def text(self, x, y, s, size, fill, bold=False, anchor="start"):
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{700 if bold else 400}" '
                        f'fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, w=1):
        self.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"/>')

    def hbar(self, x_from, x_to, y, h, color, round_end="right"):
        """Horizontal bar: 4 px rounded data end, square at the baseline end."""
        x1, x2 = min(x_from, x_to), max(x_from, x_to)
        w, r = max(x2 - x1, 1), min(4, (x2 - x1) / 2, h / 2)
        if round_end == "right":
            d = f"M{x1} {y} H{x2 - r} Q{x2} {y} {x2} {y + r} V{y + h - r} Q{x2} {y + h} {x2 - r} {y + h} H{x1} Z"
        elif round_end == "left":
            d = f"M{x2} {y} H{x1 + r} Q{x1} {y} {x1} {y + r} V{y + h - r} Q{x1} {y + h} {x1 + r} {y + h} H{x2} Z"
        else:
            d = f"M{x1} {y} H{x1 + w} V{y + h} H{x1} Z"
        self.out.append(f'<path d="{d}" fill="{color}"/>')

    def vbar(self, x, w, y_base, y_top, color):
        r = min(4, w / 2, (y_base - y_top) / 2)
        d = f"M{x} {y_base} V{y_top + r} Q{x} {y_top} {x + r} {y_top} H{x + w - r} Q{x + w} {y_top} {x + w} {y_top + r} V{y_base} Z"
        self.out.append(f'<path d="{d}" fill="{color}"/>')

    def save(self):
        OUT.mkdir(exist_ok=True)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
               f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif"><rect width="{W}" height="{H}" fill="#FFF"/>'
               + "".join(self.out) + "</svg>")
        p = OUT / f"{self.name}.svg"
        p.write_text(svg)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={W},{H}", f"--screenshot={OUT / (self.name + '.png')}", p.as_uri()],
                       check=True, capture_output=True)
        print("built", self.name)


def eur(x, digits=2):
    s = f"€{abs(x):,.{digits}f}"
    return ("−" if x < 0 else "") + s


# ---------------------------------------------------------------- 1. the market, from MEO's base to subscribers
def market():
    base, ready, take = v("D01"), v("D02"), v("D04")
    steps = [("Homes with MEO fixed broadband", base, "1.58 million"),
             (f"Already use a connected-home system ({ready:.0%})", base * ready, f"{base * ready:,.0f} thousand"),
             (f"Would subscribe ({take:.0%} of those)", v("D05"), f"≈ {round(v('D05')):,} thousand homes · {v('D06'):.1%} of MEO")]
    c = Chart("1-market", f"About {round(v('D05'))},000 MEO homes in the expected case",
              "From MEO’s fixed-broadband homes to subscribers", "MEO base: ANACOM, Q4 2025 · connected-home use: "
              "Eurostat 2024, Portugal · take rate: our assumption (2% to 10%)")
    plot_w = W - 2 * X0 - 230
    for i, (lab, val, note) in enumerate(steps):
        y = 178 + i * 148
        c.text(X0, y, lab, 18, SOFT)
        bw = plot_w * val / base
        c.hbar(X0, X0 + bw, y + 16, 28, BLUE)
        c.text(X0 + bw + 12, y + 37, note, 18, INK, bold=True)
    c.save()


# ---------------------------------------------------------------- 2. one subscriber's month, as a waterfall
def unit():
    price = v("N02")
    costs = [("Language model (AI)", v("C02")), ("Cloud servers", v("B07")), ("Customer support", v("C03")),
             ("Winning the customer", v("C04"))]
    left = price - sum(x for _, x in costs)
    c = Chart("2-one-home", f"Each subscriber leaves about {eur(left)} a month",
              "One home, one month: the €3.99 add-on, with the AI running on hardware already in the home",
              "AI: cost measured per call × expected use. Other costs: our assumptions. Prices without VAT (23%).")
    LBL, P0, P1 = 300, X0 + 300, W - X0 - 110
    scale = (P1 - P0) / price
    rows_ = [("Price without VAT", 0, price, BLUE, eur(price))]
    run = price
    for lab, x in costs:
        rows_.append((lab, run - x, run, ORANGE, "−" + eur(x)))
        run -= x
    rows_.append(("Left per home", 0, left, BLUE, eur(left)))
    for i, (lab, a, b, col, val) in enumerate(rows_):
        y = 150 + i * 78
        c.text(X0, y + 22, lab, 18, SOFT if col == ORANGE else INK, bold=col == BLUE)
        c.hbar(P0 + a * scale, P0 + b * scale, y, 30, col, "right" if a == 0 else "none")
        c.text(P0 + b * scale + 12, y + 22, val, 18, INK, bold=True)
        if 0 < i < len(rows_) - 1:     # thin connector from the previous step
            c.line(P0 + b * scale, y - 48, P0 + b * scale, y, GRID, 1)
    c.line(P0, 140, P0, 150 + len(rows_) * 78 - 40, "#C9CED6", 1)
    c.save()


# ---------------------------------------------------------------- 3. where the AI runs decides the case
def hardware():
    e1 = v("M02")
    e2 = v("M04")
    e3 = v("N02") - v("C05") - v("C08")          # our arithmetic: same formula as M04 with the GPU box
    opts = [("On hardware already in the home", e1, "router, gateway or camera"),
            ("On a small box per home", e2, "≈ €100, over 3 years"),
            ("On a GPU box per home", e3, "≈ €300, over 3 years")]
    c = Chart("3-hardware", "Where the AI runs decides the case",
              "Money left per home per month for the €3.99 add-on, by where the local vision models run",
              "Box prices are rough assumptions, spread over 36 months. Small and GPU boxes: our arithmetic from the model.")
    LBL, lo, hi = 330, -7.0, 2.5
    P0, P1 = X0 + LBL, W - X0 - 40
    sx = lambda x: P0 + (x - lo) / (hi - lo) * (P1 - P0)
    for t in range(-7, 3):
        c.line(sx(t), 150, sx(t), 520, GRID if t else "#9AA3AF", 1)
        c.text(sx(t), 548, eur(t, 0) if t else "€0", 14, FAINT, anchor="middle")
    for i, (lab, val, sub) in enumerate(opts):
        y = 180 + i * 115
        c.text(X0, y + 10, lab, 18, INK, bold=True)
        c.text(X0, y + 34, sub, 15, FAINT)
        col = BLUE if val >= 0 else ORANGE
        c.hbar(sx(0), sx(val), y - 6, 30, col, "right" if val >= 0 else "left")
        anchor = "start" if val >= 0 else "end"
        c.text(sx(val) + (12 if val >= 0 else -12), y + 16, ("+" if val > 0 else "") + eur(val), 18, INK, True, anchor)
    c.text(sx(0), 140, "loses money  ←", 14, FAINT, anchor="end")
    c.text(sx(0) + 6, 140, "→  makes money", 14, FAINT)
    c.save()


# ---------------------------------------------------------------- 4. price against camera plans
def prices():
    nos = v("A12") + v("A13")
    plans = [("Vodafone + Prosegur alarm", "from this price, camera included", v("A11"), GREY),
             ("NOS Securitas alarm + indoor camera", "€34.99 campaign + €7.50 camera, 36 months", nos, GREY),
             ("SFR Maison Sécurisée (France)", "camera included", v("A15"), GREY),
             ("ThingTracker with a camera", "proposed bundle", v("B21"), BLUE),
             ("ThingTracker add-on", "proposed, for a home with a camera", v("B20"), BLUE)]
    c = Chart("4-prices", "A fraction of what a camera plan costs",
              "Monthly price with VAT",
              "Competitor prices read on vodafone.pt, nos.pt and SFR on 18 Nov 2026. ThingTracker prices are proposals.")
    LBL = 380
    P0, P1 = X0 + LBL, W - X0 - 90
    top = max(p for _, _, p, _ in plans)
    for i, (lab, sub, p, col) in enumerate(plans):
        y = 160 + i * 88
        c.text(X0, y + 6, lab, 18, INK, bold=col == BLUE)
        c.text(X0, y + 29, sub, 14.5, FAINT)
        bw = (P1 - P0) * p / top
        c.hbar(P0, P0 + bw, y - 10, 28, col)
        c.text(P0 + bw + 12, y + 12, eur(p), 18, INK, bold=True)
    c.save()


# ---------------------------------------------------------------- 5. revenue for MEO by adoption
def revenue():
    cases = [("0.5%", "R1"), ("1%", "R2"), ("2%", "R3"), ("5%", "R4")]
    c = Chart("5-revenue", "Revenue grows with every home that joins",
              "MEO revenue a year, without VAT, at €3.99 a month, by share of MEO homes that subscribe",
              "Shares are scenarios, not forecasts. “Left after costs” assumes the AI runs on hardware already in the home.")
    base_y, top_y = 540, 175
    top = 3.5
    sy = lambda m: base_y - (base_y - top_y) * m / top
    for t in (0, 1, 2, 3):
        c.line(X0 + 70, sy(t), W - X0, sy(t), GRID if t else "#9AA3AF", 1)
        c.text(X0 + 56, sy(t) + 5, f"€{t} M" if t else "€0", 14, FAINT, anchor="end")
    slot = (W - X0 - (X0 + 70)) / len(cases)
    for i, (lab, r) in enumerate(cases):
        rev, contrib, homes = v(r + "b"), v(r + "c"), v(r + "a")
        cx = X0 + 70 + slot * (i + 0.5)
        bw = 64
        c.vbar(cx - bw / 2, bw, base_y, sy(rev), BLUE)
        c.text(cx, sy(rev) - 34, f"€{rev:.2f} M" if rev < 1 else f"€{rev:.1f} M", 20, INK, True, "middle")
        c.text(cx, sy(rev) - 13, f"€{contrib:.2f} M left after costs", 14, FAINT, anchor="middle")
        c.text(cx, base_y + 28, f"{lab} of MEO homes", 16, INK, True, "middle")
        c.text(cx, base_y + 48, f"{round(homes * 10) * 100:,} homes", 14, FAINT, anchor="middle")
    c.save()


if __name__ == "__main__":
    market(); unit(); hardware(); prices(); revenue()
