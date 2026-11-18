#!/usr/bin/env python3
"""Build the Track Things logo files with the text converted to outlines.

    python build_logos.py SWITZER_SEMIBOLD.ttf SWITZER_MEDIUM.ttf

Needs fonttools and uharfbuzz (pip install fonttools uharfbuzz). Switzer is by the Indian Type Foundry
(Fontshare, ITF Free Font License); the fonts themselves are not stored in this repo.
Writes SVG files next to this script. render_png.sh turns them into PNGs.
"""
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent

# Altice Labs palette (assets/brand/README.md)
THEMES = {
    "light": {"frame": "#0084D6", "dot": "#000000", "text": "#000000", "endorse": "#555555"},
    "dark": {"frame": "#FFFFFF", "dot": "#02A1EA", "text": "#FFFFFF", "endorse": "#FFFFFF"},  # for #003399 or black grounds
}

# The mark, on its 64-unit grid (same paths as the animation).
CORNERS = ["M7 21 V12 Q7 7 12 7 H21", "M43 7 H52 Q57 7 57 12 V21", "M57 43 V52 Q57 57 52 57 H43", "M7 43 V52 Q7 57 12 57 H21"]


def mark_svg(theme, x, y, size):
    s = size / 64
    c = THEMES[theme]
    corners = "".join(f'<path d="{d}"/>' for d in CORNERS)
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">'
            f'<g fill="none" stroke="{c["frame"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{corners}</g>'
            f'<circle cx="19" cy="45" r="2.4" fill="{c["frame"]}" fill-opacity="0.35"/>'
            f'<circle cx="25.5" cy="38.5" r="3" fill="{c["frame"]}" fill-opacity="0.6"/>'
            f'<circle cx="35" cy="29" r="8" fill="{c["dot"]}"/></g>')


class Face:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        blob = hb.Blob.from_file_path(str(path))
        self.hbfont = hb.Font(hb.Face(blob))
        self.upm = self.tt["head"].unitsPerEm
        self.cap = self.tt["OS/2"].sCapHeight

    def path(self, text, size, x0, baseline, tracking_em=0.0):
        """SVG path data for text at font size `size`, starting at x0 on `baseline`. Returns (d, advance)."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": True})
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs)
        x = 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            # font units, y up -> SVG user units, y down
            t = TransformPen(pen, (scale, 0, 0, -scale, x0 + (x + pos.x_offset) * scale, baseline - pos.y_offset * scale))
            self.glyphs[name].draw(t)
            x += pos.x_advance + tracking_em * self.upm
        return pen.getCommands(), (x - tracking_em * self.upm) * scale


def lockup(bold, medium, theme, endorsed):
    F = 100.0                      # font size of "Track Things"
    mark = 1.15 * F
    gap = 0.30 * F
    cap = bold.cap / bold.upm * F
    baseline = mark / 2 + cap / 2  # the mark is centred on the capitals
    tx = mark + gap
    d, w = bold.path("Track Things", F, tx, baseline, tracking_em=-0.04)
    c = THEMES[theme]
    parts = [mark_svg(theme, 0, 0, mark), f'<path fill="{c["text"]}" d="{d}"/>']
    width, height = tx + w, mark
    if endorsed:
        E = 0.30 * F
        eb = baseline + 0.56 * F   # below the descender of the g
        d2, w2 = medium.path("by Altice Labs", E, tx + 0.02 * F, eb, tracking_em=0.0)
        parts.append(f'<path fill="{c["endorse"]}" d="{d2}"/>')
        height = max(height, eb + 0.08 * F)
        width = max(width, tx + w2)
    pad = 0.06 * F
    vb = f"{-pad:.1f} {-pad:.1f} {width + 2 * pad:.1f} {height + 2 * pad:.1f}"
    label = "Track Things by Altice Labs" if endorsed else "Track Things"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">'
            f'<title>{label}</title>{"".join(parts)}</svg>\n')


def main():
    bold, medium = Face(Path(sys.argv[1])), Face(Path(sys.argv[2]))
    for theme in THEMES:
        (HERE / f"track-things-{theme}.svg").write_text(lockup(bold, medium, theme, False))
        (HERE / f"track-things-by-altice-labs-{theme}.svg").write_text(lockup(bold, medium, theme, True))
        (HERE / f"track-things-mark-{theme}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Track Things"><title>Track Things</title>'
            f'{mark_svg(theme, 0, 0, 64)}</svg>\n')
    print("written:", *sorted(p.name for p in HERE.glob("*.svg")))


if __name__ == "__main__":
    main()
