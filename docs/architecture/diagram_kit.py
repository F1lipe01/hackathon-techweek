"""Shared drawing kit for the architecture views built by build_views.py.

Every diagram is plain SVG written by hand from a grid, rendered to a 2x PNG with headless Chrome, as in
build_diagram.py. The rules the kit enforces:
- text is measured with the font Chrome renders (Helvetica Neue; code in Menlo) and wrapped to its box; a box whose
  text does not fit stops the build;
- every arrow is one straight horizontal or vertical segment that stops at the base of its head, so the line never
  shows beside the tip; a two-way flow is drawn as two arrows.

Markup inside a string: _italic_ (English terms in the Portuguese figures), **bold**, `code` (Menlo).
"""
import re
import subprocess
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"

INK, BODY, MUTED, FAINT = "#111111", "#333333", "#555555", "#777777"
BLUE, DEEP, LINE = "#0084D6", "#003399", "#D0D0D0"
HOME_BG, ALTICE_BG, PHONE_BG, EXT_BG = "#F4F4F4", "#EEF3FB", "#FFF6EA", "#F3EFFA"
NOTE_BG, NOTE_LINE = "#E6F2FB", "#B9D7EE"
WARN = "#C2410C"
HEAD = 10            # arrowhead length, in user units

_fonts = {}


def fnt(size, style):
    key = (size, style)
    if key not in _fonts:
        if style == "c":
            _fonts[key] = ImageFont.truetype(MONO, size * 0.9)
        else:
            _fonts[key] = ImageFont.truetype(FONT, size, index={"n": 0, "b": 1, "i": 2, "bi": 3}[style])
    return _fonts[key]


NB = "\u00a0"
_UNITS = re.compile(r"(\d) (?=%|€|M€|s\b|ms\b|min\b|h\b|GB|fps|Mbps|Gbps|kWh|W\b|\d{3}\b)")


def nb(s):
    """Keep a number with its unit (25 %, 0,49 €, 30 s) and thousands (500 000) on one line."""
    return _UNITS.sub(lambda m: m.group(1) + NB, s)


def parse(s, bold=False):
    """A string with markup -> [(text, style)], style in n, b, i, bi, c."""
    s = nb(s)
    runs, buf, ital, bld = [], "", False, bold
    i = 0

    def style():
        return "bi" if (ital and bld) else "i" if ital else "b" if bld else "n"

    def flush():
        nonlocal buf
        if buf:
            runs.append((buf, style()))
        buf = ""

    while i < len(s):
        c = s[i]
        if c == "`":
            j = s.index("`", i + 1)
            flush()
            runs.append((s[i + 1:j], "c"))
            i = j + 1
            continue
        if s.startswith("**", i):
            flush()
            bld = not bld if not bold else True
            i += 2
            continue
        if c == "_":
            prev = s[i - 1] if i else " "
            nxt = s[i + 1] if i + 1 < len(s) else " "
            if not ital and not prev.isalnum() and nxt != " ":
                flush()
                ital = True
                i += 1
                continue
            if ital and not nxt.isalnum():
                flush()
                ital = False
                i += 1
                continue
        buf += c
        i += 1
    flush()
    return runs


def _words(runs):
    words, cur = [], []
    for text, st in runs:
        parts = text.split(" ")
        for k, p in enumerate(parts):
            if k > 0:
                if cur:
                    words.append(cur)
                cur = []
            if p:
                cur.append((p, st))
    if cur:
        words.append(cur)
    return words


def _ww(word, size):
    return sum(fnt(size, st).getlength(p) for p, st in word)


def line_width(line, size):
    return _ww(line, size)


def wrap(s, max_w, size, bold=False):
    """Wrap a marked-up string to max_w; returns lines, each a list of (text, style)."""
    sp = fnt(size, "n").getlength(" ")
    lines, cur, cw = [], [], 0.0
    for w in _words(parse(s, bold)):
        ww = _ww(w, size)
        if cur and cw + sp + ww > max_w:
            lines.append(cur)
            cur, cw = [], 0.0
        if cur:
            cur = cur + [(" ", w[0][1] if w[0][1] != "c" else "n")] + w
            cw += sp + ww
        else:
            cur, cw = list(w), ww
        assert ww <= max_w + 0.5, f"one word is wider than its box: {''.join(p for p, _ in w)!r} ({ww:.0f} > {max_w:.0f})"
    if cur:
        lines.append(cur)
    return lines


def width(s, size, bold=False):
    return line_width([r for r in parse(s, bold)], size)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _tspans(line, size):
    merged = []
    for p, st in line:
        if merged and merged[-1][1] == st:
            merged[-1] = (merged[-1][0] + p, st)
        else:
            merged.append((p, st))
    out = []
    for p, st in merged:
        a = []
        if st in ("b", "bi"):
            a.append('font-weight="700"')
        if st in ("i", "bi"):
            a.append('font-style="italic"')
        if st == "c":
            a.append(f'font-family="Menlo, monospace" font-size="{size * 0.9:.1f}"')
        p = esc(p).replace(" ", "&#160;") if p.strip() == "" else esc(p)
        out.append(f'<tspan {" ".join(a)}>{p}</tspan>' if a else p)
    return "".join(out)


class Canvas:
    def __init__(self, w, lang, title):
        self.w, self.lang, self.title, self.o, self.colors = w, lang, title, [], {BODY}

    def L(self, pt, en):
        return pt if self.lang == "pt" else en

    # ------------------------------------------------------------------ text
    def line(self, x, y, line, size, fill, anchor="start", weight=400):
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                      f'text-anchor="{anchor}">{_tspans(line, size)}</text>')

    def text(self, x, y, s, size=13.5, bold=False, fill=BODY, anchor="start", max_w=None):
        """One line; with max_w it must fit."""
        runs = parse(s, bold)
        if max_w is not None:
            assert line_width(runs, size) <= max_w + 0.5, f"{s!r} is {line_width(runs, size):.0f} wide, room {max_w:.0f}"
        self.line(x, y, runs, size, fill, anchor)

    def para(self, x, y, s, max_w, size=13.5, lead=None, bold=False, fill=BODY, anchor="start"):
        """Wrapped text; returns the baseline of the next line."""
        lead = lead or round(size * 1.4, 1)
        for ln in wrap(s, max_w, size, bold):
            self.line(x, y, ln, size, fill, anchor)
            y += lead
        return y

    def para_h(self, s, max_w, size=13.5, lead=None, bold=False):
        lead = lead or round(size * 1.4, 1)
        return len(wrap(s, max_w, size, bold)) * lead

    # ------------------------------------------------------------------ shapes
    def rect(self, x, y, w, h, fill="#FFFFFF", stroke=LINE, rx=12, sw=1.0, dash=None):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}{da}/>')

    def band(self, x, y, w, h, title, sub=None, fill=HOME_BG, color=INK, dash=None, stroke=None, pad=20):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=18, sw=1.5, dash=dash)
        self.text(x + pad, y + 30, title, 17, True, color, max_w=w - 2 * pad)
        if sub:
            self.para(x + pad, y + 50, sub, w - 2 * pad, 12.5, fill=MUTED)

    def box_h(self, w, title, body=(), pad=14, title_size=14.5, body_size=12.5, sub=None, gap=6, sub_bold=True):
        """The height box() needs, computed the way box() lays the text out."""
        ts, bs = title_size, body_size
        nt = len(wrap(title, w - 2 * pad, ts, True))
        last = pad + ts * 0.95 + (nt - 1) * ts * 1.4
        desc = ts * 0.3
        ty = last + bs * 1.4
        if sub or body:
            if sub:
                ty += 4 + self.para_h(sub, w - 2 * pad, bs, bold=sub_bold)
            for p in body:
                ty += gap + self.para_h(p, w - 2 * pad, bs)
            last, desc = ty - bs * 1.4, bs * 0.35
        return last + desc + pad

    def box(self, x, y, w, title, body=(), h=None, pad=14, title_size=14.5, body_size=12.5, fill="#FFFFFF",
            stroke=LINE, sw=1.0, sub=None, sub_color=BLUE, title_color=INK, body_color=BODY, dash=None, gap=6, rx=12,
            sub_bold=True):
        """A card: a bold title (wrapped), an optional blue subtitle, then paragraphs. Returns its height."""
        need = self.box_h(w, title, body, pad, title_size, body_size, sub, gap, sub_bold)
        h = h or need
        assert need <= h + 0.5, f"text overflows the box {title!r}: needs {need:.0f}, has {h:.0f}"
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash, rx=rx)
        ty = y + pad + title_size * 0.95
        ty = self.para(x + pad, ty, title, w - 2 * pad, title_size, bold=True, fill=title_color)
        ty += -title_size * 1.4 + body_size * 1.4
        if sub:
            ty += 4
            ty = self.para(x + pad, ty, sub, w - 2 * pad, body_size, bold=sub_bold, fill=sub_color)
        for p in body:
            ty += gap
            ty = self.para(x + pad, ty, p, w - 2 * pad, body_size, fill=body_color)
        return h

    # ------------------------------------------------------------------ arrows
    def arrow(self, x0, y0, x1, y1, color=BODY, sw=1.6, dash=None):
        """One straight arrow, horizontal or vertical, from (x0, y0) to the tip at (x1, y1)."""
        assert x0 == x1 or y0 == y1, f"arrow not straight: {(x0, y0, x1, y1)}"
        self.colors.add(color)
        if y0 == y1:
            s = 1 if x1 > x0 else -1
            d = f"M{x0:.1f} {y0:.1f} H{x1 - s * HEAD:.1f}"
        else:
            s = 1 if y1 > y0 else -1
            d = f"M{x0:.1f} {y0:.1f} V{y1 - s * HEAD:.1f}"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mid = "m" + color.strip("#")
        self.o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da} marker-end="url(#{mid})"/>')

    def label(self, x, y, s, max_w, size=11.5, fill=BLUE, anchor="start", bg=None, bold=False, lead=None, below=False):
        """A wrapped arrow label. y is the baseline of the LAST line (above an arrow) or of the first (below=True)."""
        lead = lead or round(size * 1.3, 1)
        lines = wrap(s, max_w, size, bold)
        y0 = y if below else y - lead * (len(lines) - 1)
        for i, ln in enumerate(lines):
            if bg:
                lw = line_width(ln, size) + 8
                lx = x - 4 if anchor == "start" else x - lw / 2 if anchor == "middle" else x - lw + 4
                self.rect(lx, y0 + i * lead - size * 0.95, lw, size * 1.3, fill=bg, stroke=None, rx=3)
            self.line(x, y0 + i * lead, ln, size, fill, anchor, 700 if bold else 400)
        return len(lines)

    def boundary_v(self, x, y0, y1, color=BLUE):
        self.o.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{color}" stroke-width="2.2" stroke-dasharray="8 7"/>')

    # ------------------------------------------------------------------ output
    def save(self, name, h):
        suffix = ".en" if self.lang == "en" else ""
        markers = "".join(
            f'<marker id="m{c.strip("#")}" viewBox="0 0 10 10" refX="0" refY="5" markerUnits="userSpaceOnUse" '
            f'markerWidth="{HEAD}" markerHeight="{HEAD}" orient="auto"><path d="M0 1.5 L10 5 L0 8.5 Z" fill="{c}"/></marker>'
            for c in sorted(self.colors))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {h}" width="{self.w}" height="{h}" '
               f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif" role="img" aria-label="{esc(self.title)}">'
               f'<title>{esc(self.title)}</title><defs>{markers}</defs><rect width="{self.w}" height="{h}" fill="#FFFFFF"/>'
               + "\n".join(self.o) + "</svg>\n")
        path = HERE / f"{name}{suffix}.svg"
        path.write_text(svg, encoding="utf8")
        png = HERE / f"{name}{suffix}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={self.w},{h}", f"--screenshot={png}", path.as_uri()], check=True, capture_output=True)
        print(f"built {path.name} and {png.name} ({self.w}x{h})")


# ---------------------------------------------------------------------- sequence diagrams
ZONE_FILL = {"home": HOME_BG, "altice": ALTICE_BG, "phone": PHONE_BG, "ext": EXT_BG}


def sequence(lang, name, title, cols, rows, legend, colw=215):
    """cols: (title, subtitle, zone); rows: ("m", from, to, label) | ("n", first_col, last_col, text) | ("g", text).
    Messages are numbered in order; a note spans the columns first..last; a gap is a full-width band (a time break
    or an alternative)."""
    n = len(cols)
    ws = colw if isinstance(colw, (list, tuple)) else [colw] * n
    W = round(sum(ws) + 40)
    cv = Canvas(W, lang, title)
    X = [20 + sum(ws[:i]) + ws[i] / 2 for i in range(n)]
    HW = [w - 24 for w in ws]
    top = 20
    head_h = max(cv.box_h(hw, t, [], 12, 14, 12.5, s, sub_bold=False) for hw, (t, s, z) in zip(HW, cols))
    y = top + head_h + 44
    step = 0
    body = []                                   # drawn after the lifelines
    for row in rows:
        kind = row[0]
        if kind == "g":
            h = cv.para_h(row[1], W - 80, 13) + 14
            body.append(("g", y, h, row[1]))
            y += h + 26
        elif kind == "n":
            a, b, s = row[1], row[2], row[3]
            x0 = X[a] - ws[a] / 2 + 10
            x1 = X[b] + ws[b] / 2 - 10
            if a == b:
                x0, x1 = X[a] - 150, X[a] + 150
                x0, x1 = max(x0, 14), min(x1, W - 14)
            h = cv.para_h(s, x1 - x0 - 24, 12.5, 17) + 16
            body.append(("n", y, h, (x0, x1, s)))
            y += h + 24
        else:
            a, b, s = row[1], row[2], row[3]
            step += 1
            span = abs(X[b] - X[a]) - 36
            nl = len(wrap(s, span, 12.5))
            y += 17 * (nl - 1)
            body.append(("m", y, 0, (a, b, s, step)))
            y += 48
    H = y - 6
    leg_y = H
    H += 40
    for x in X:
        cv.o.append(f'<line x1="{x:.1f}" y1="{top + head_h}" x2="{x:.1f}" y2="{leg_y - 14}" stroke="{LINE}" '
                    f'stroke-width="1.2" stroke-dasharray="4 4"/>')
    for x, hw, (t, s, z) in zip(X, HW, cols):
        cv.box(x - hw / 2, top, hw, t, [], h=head_h, pad=12, title_size=14, body_size=12.5, sub=s, sub_color=MUTED,
               fill=ZONE_FILL[z], stroke="#C9CED6", sub_bold=False)
    for kind, yy, h, data in body:
        if kind == "g":
            cv.rect(12, yy - 4, W - 24, h, fill="#EEF1F6", stroke=None, rx=8)
            cv.para(W / 2, yy + 15, data, W - 80, 13, fill=DEEP, anchor="middle")
        elif kind == "n":
            x0, x1, s = data
            cv.rect(x0, yy - 4, x1 - x0, h, fill=NOTE_BG, stroke=NOTE_LINE, rx=8)
            cv.para((x0 + x1) / 2, yy + 15, s, x1 - x0 - 24, 12.5, 17, anchor="middle")
        else:
            a, b, s, k = data
            xa, xb = X[a], X[b]
            d = 1 if xb > xa else -1
            span = abs(xb - xa) - 36
            lines = wrap(s, span, 12.5)
            ly = yy - 9 - 17 * (len(lines) - 1)
            for i, ln in enumerate(lines):
                lw = line_width(ln, 12.5) + 10
                cv.rect((xa + xb) / 2 - lw / 2, ly + i * 17 - 12.5, lw, 17, fill="#FFFFFF", stroke=None, rx=2)
                cv.line((xa + xb) / 2, ly + i * 17, ln, 12.5, BODY, "middle")
            cv.arrow(xa + d * 12, yy, xb - d * 4, yy, INK, 1.4)
            cv.o.append(f'<circle cx="{xa:.1f}" cy="{yy}" r="11" fill="{BLUE}"/>')
            cv.text(xa, yy + 4.3, str(k), 11.5, True, "#FFFFFF", "middle")
    cv.para(20, leg_y + 12, legend, W - 40, 12, fill=MUTED)
    cv.save(name, round(H))
    return cv


# ---------------------------------------------------------------------- grids of cards with straight arrows
class Grid:
    """Cards on a grid of columns and rows. A row is as tall as its tallest single-row card; a card may span rows.
    Arrows join two cards with one straight segment, in the middle of their overlap, and assert that they can."""

    def __init__(self, cv, xs, ws, y0, row_gap=60):
        self.cv, self.xs, self.ws, self.y0, self.gap = cv, xs, ws, y0, row_gap
        self.r = {}

    def place(self, cells, min_row=0):
        """cells: {key: (col, row, span, box_kwargs)}; col may be a (first, last) tuple to span columns."""
        cv = self.cv
        nrows = max(r + s for c, r, s, k in cells.values())
        hs = [min_row] * nrows

        def cw(c):
            return (self.xs[c[1]] + self.ws[c[1]] - self.xs[c[0]]) if isinstance(c, tuple) else self.ws[c]

        def cx(c):
            return self.xs[c[0]] if isinstance(c, tuple) else self.xs[c]

        for key, (c, r, s, k) in cells.items():
            if s == 1:
                kk = {a: b for a, b in k.items() if a in ("pad", "title_size", "body_size", "sub", "gap", "sub_bold")}
                hs[r] = max(hs[r], cv.box_h(cw(c), k["title"], k.get("body", ()), **kk))
        ys = [self.y0]
        for h in hs[:-1]:
            ys.append(ys[-1] + h + self.gap)
        self.ys, self.hs = ys, hs
        for key, (c, r, s, k) in cells.items():
            h = ys[r + s - 1] + hs[r + s - 1] - ys[r]
            x = cx(c)
            cv.box(x, ys[r], cw(c), h=h, **k)
            self.r[key] = (x, ys[r], x + cw(c), ys[r] + h)
        return ys[-1] + hs[-1]

    def _h(self, a, b, dy, color, sw, at=None):
        A, B = self.r[a], self.r[b]
        lo, hi = max(A[1], B[1]) + 16, min(A[3], B[3]) - 16
        assert hi >= lo, f"{a} and {b} do not overlap vertically"
        y = ((lo + hi) / 2 if at is None else at) + dy
        assert lo - 10 <= y <= hi + 10, f"{a} -> {b}: y {y:.0f} outside the overlap"
        if A[2] <= B[0]:
            self.cv.arrow(A[2], y, B[0], y, color, sw)
            return y, A[2], B[0]
        self.cv.arrow(A[0], y, B[2], y, color, sw)
        return y, B[2], A[0]

    def _v(self, a, b, dx, color, sw):
        A, B = self.r[a], self.r[b]
        lo, hi = max(A[0], B[0]) + 16, min(A[2], B[2]) - 16
        assert hi >= lo, f"{a} and {b} do not overlap horizontally"
        x = (lo + hi) / 2 + dx
        if A[3] <= B[1]:
            self.cv.arrow(x, A[3], x, B[1], color, sw)
            return x, A[3], B[1]
        self.cv.arrow(x, A[1], x, B[3], color, sw)
        return x, B[3], A[1]

    lpad = 8                                   # label inset from the card's edge; larger where a boundary line runs

    def h(self, a, b, label=None, dy=0, color=BODY, sw=1.6, below=False, lcolor=None, size=11.5, at=None):
        """One horizontal arrow from card a to card b; the label above it (or below), wrapped to the gap."""
        y, x0, x1 = self._h(a, b, dy, color, sw, at)
        if label:
            ly = y + 16 if below else y - 7
            self.cv.label(x0 + self.lpad, ly, label, x1 - x0 - 2 * self.lpad, size=size, fill=lcolor or color, below=below)
        return y

    def v(self, a, b, label=None, dx=0, color=BODY, sw=1.6, side="right", lcolor=None, size=11.5, lw=None):
        """One vertical arrow from card a to card b; the label beside it, vertically centred."""
        x, y0, y1 = self._v(a, b, dx, color, sw)
        if label:
            w = lw or 150
            n = len(wrap(label, w, size))
            ly = (y0 + y1) / 2 - (n - 1) * size * 1.3 / 2 + size * 0.35
            if side == "right":
                self.cv.label(x + 9, ly, label, w, size=size, fill=lcolor or color, below=True)
            else:
                self.cv.label(x - 9, ly, label, w, size=size, fill=lcolor or color, below=True, anchor="end")
        return x

    def h2(self, a, b, ab, ba, color=BODY, lcolor=None, size=11.5, gap=7):
        """Two arrows between a (left) and b (right): a->b labelled above, b->a labelled below."""
        self.h(a, b, ab, dy=-gap, color=color, lcolor=lcolor, size=size)
        self.h(b, a, ba, dy=gap, color=color, lcolor=lcolor, size=size, below=True)

    def v2(self, a, b, ab, ba, color=BODY, lcolor=None, size=11.5, gap=8, lw=None, lw2=None):
        """Two arrows between a (above) and b (below): a->b on the right with its label, b->a on the left."""
        self.v(a, b, ab, dx=gap, color=color, lcolor=lcolor, size=size, side="right", lw=lw)
        self.v(b, a, ba, dx=-gap, color=color, lcolor=lcolor, size=size, side="left", lw=lw2 or lw)
