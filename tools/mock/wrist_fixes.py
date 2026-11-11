"""Owner-scoped corrections to the middle-column (#41) basic poses only."""

from __future__ import annotations

import hashlib
import numpy as np
from PIL import Image, ImageDraw

POSES = {
    "chunli": "91f38eefec7d270fbdad21bd9208a7da",
    "zangief": "d6c38a439bca04684b9f7124e41d052e",
}
# Coordinates refer to the displayed crop: Chun-Li's hand on the image right.
# Preserve the central hand; recolour only the outer cuff and its two spikes.
REGIONS = {
    "chunli": [
        ("cuff", [(23, 22), (24, 22), (24, 28), (23, 27)]),
        ("trousers", [(18, 29), (21, 29), (23, 31), (23, 34), (17, 34), (17, 31)]),
    ],
    "zangief": [
        ("red", [(6, 20), (8, 21), (8, 24), (7, 27), (5, 27), (4, 25), (5, 22)]),
        ("red", [(29, 19), (31, 20), (32, 22), (32, 25), (30, 27), (28, 26), (29, 24)]),
    ],
}


def selection(shape: tuple[int, int], points: list) -> np.ndarray:
    h, w = shape
    image = Image.new("1", (w, h))
    draw = ImageDraw.Draw(image)
    draw.polygon(points, fill=1)
    return np.asarray(image, dtype=bool)


def adjust(crop: np.ndarray, who: str, groups: np.ndarray) -> np.ndarray:
    if hashlib.md5(crop.tobytes() + bytes(crop.shape)).hexdigest() != POSES[who]:
        raise ValueError("wrist correction requires the exact selected pose")
    result = groups.copy()
    for material, points in REGIONS[who]:
        selected = selection(crop.shape, points) & (crop > 0)
        result[selected] = 1 if material == "red" else 2
    if who == "chunli":
        for x, y in [(24, 22), (24, 28)]:
            if crop[y, x] == 1:
                result[y, x] = 3
    return result
