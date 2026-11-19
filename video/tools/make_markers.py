"""Marker screens for the phone held on camera, so its screen can be tracked and replaced (video 1, filming plan).
    python3 video/tools/make_markers.py
Writes video/shoot/markers/<variant>-<model>.png and layout-<model>.json for each phone size:
  - green: a dark-green screen with five ArUco markers drawn in two greens; it keys out with the markers, so a thumb
    that crosses the screen can be cut out and kept over the inserted app. For takes where a finger touches the screen.
  - grey: a dark-grey screen with black and white markers. For takes where nothing touches the screen.
Markers: DICT_4X4_50, IDs 0 top-left, 1 top-right, 2 bottom-right, 3 bottom-left, 4 centre. Each is 6 x 6 modules
(4 x 4 bits and a 1-module border) of side about 0,20 of the screen width, inside a 1-module light quiet zone; the tiles
sit 0,06 of the width in from the edges, clear of the rounded corners and the Dynamic Island.
The layout JSON gives every marker corner in screen pixels; the tracker uses it when no on-set screenshot is given."""
import json
from pathlib import Path

import cv2
import numpy as np

MODELS = {"pro-402": (1206, 2622), "pro-393": (1179, 2556)}  # iPhone 16/17 Pro, iPhone 15/16 (393 x 852 pt) at 3x
VARIANTS = {
    # background, dark module, light module (RGB)
    "green": ((0x0C, 0x40, 0x1C), (0x0C, 0x40, 0x1C), (0x46, 0xBE, 0x64)),
    "grey": ((0x33, 0x33, 0x33), (0x00, 0x00, 0x00), (0xFF, 0xFF, 0xFF)),
}
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
OUT = Path(__file__).resolve().parents[1] / "shoot" / "markers"


def layout(w: int, h: int):
    """Each marker: id, the tile's top-left (px) and the module size (px). Tiles are 8 modules: quiet zone + 6 + quiet zone."""
    mod = round(0.20 * w / 6)
    tile = 8 * mod
    inset = round(0.06 * w)
    pos = {
        0: (inset, inset),
        1: (w - inset - tile, inset),
        2: (w - inset - tile, h - inset - tile),
        3: (inset, h - inset - tile),
        4: ((w - tile) // 2, (h - tile) // 2),
    }
    return mod, tile, pos


def draw(w: int, h: int, colours):
    bg, dark, light = colours
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = bg
    mod, tile, pos = layout(w, h)
    corners = {}
    for mid, (x, y) in pos.items():
        bits = cv2.aruco.generateImageMarker(DICT, mid, 6, borderBits=1)  # 6 x 6, 0 or 255
        img[y:y + tile, x:x + tile] = light  # the quiet zone
        for r in range(6):
            for c in range(6):
                col = light if bits[r, c] else dark
                y0, x0 = y + (r + 1) * mod, x + (c + 1) * mod
                img[y0:y0 + mod, x0:x0 + mod] = col
        # the marker's outer corners (its black border), clockwise from top-left, as ArUco reports them
        a, b = x + mod, x + 7 * mod
        t, u = y + mod, y + 7 * mod
        corners[mid] = [[a, t], [b, t], [b, u], [a, u]]
    return img, corners


def check(img_rgb, corners):
    """The PNG must detect with every marker found exactly where the layout says."""
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    found, ids, _ = det.detectMarkers(gray)
    got = {int(i): f.reshape(4, 2) for i, f in zip(ids.ravel(), found)} if ids is not None else {}
    assert set(got) == set(corners), f"found {sorted(got)}, expected {sorted(corners)}"
    err = max(float(np.abs(got[k] - np.array(corners[k]) + 0.5).max()) for k in got)  # ArUco corners sit on pixel edges
    return err


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for model, (w, h) in MODELS.items():
        lay = None
        for name, colours in VARIANTS.items():
            img, corners = draw(w, h, colours)
            err = check(img, corners)
            cv2.imwrite(str(OUT / f"{name}-{model}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            lay = corners
            print(f"{name}-{model}.png  {w}x{h}  5 markers found, max corner offset {err:.2f} px")
        (OUT / f"layout-{model}.json").write_text(json.dumps({"screen": {"w": w, "h": h}, "dict": "DICT_4X4_50",
                                                               "markers": {str(k): v for k, v in lay.items()}}, indent=1))


if __name__ == "__main__":
    main()
