"""Exact Zangief breathing drawings; keep the existing basic pose untouched.

Red boots, trunks and wristbands follow the accepted middle-version palette.
Hair/beard keep the dark skin ramp; group 2 is red trunks, never brown hair.
Coordinates belong only to these two source hashes. No pose propagation.
"""

from __future__ import annotations
import hashlib
import numpy as np
from PIL import Image, ImageDraw

POSES = ("d31dac2508219dad2b407c584af9ae7d", "d1539bf006207f456e951bd13ea41084")
REGIONS = {
    POSES[0]: {
        1: [
            [(8, 18), (10, 19), (8, 22), (8, 26), (6, 27), (4, 25), (5, 22)],
            [(32, 18), (34, 19), (35, 22), (34, 25), (32, 26), (31, 24), (31, 21)],
            [(3, 36), (10, 36), (10, 42), (0, 42), (0, 38)],
            [(22, 36), (27, 36), (27, 38), (31, 40), (31, 42), (20, 42), (20, 38)],
        ],
        2: [[(15, 26), (21, 26), (23, 29), (22, 33), (19, 34), (15, 32)]],
    },
    POSES[1]: {
        1: [
            [(8, 18), (11, 19), (9, 22), (8, 26), (6, 27), (4, 25), (5, 22)],
            [(31, 18), (33, 18), (35, 21), (34, 24), (32, 25), (30, 23), (30, 20)],
            [(5, 35), (12, 35), (12, 41), (2, 41), (2, 37)],
            [(25, 35), (30, 35), (30, 37), (34, 39), (34, 41), (23, 41), (23, 37)],
        ],
        2: [[(17, 26), (23, 26), (25, 29), (24, 33), (21, 34), (17, 32)]],
    },
}


def author(source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if key not in POSES:
        raise ValueError("unsupported Zangief breathing drawing")
    result = source.astype(np.int8).copy()
    for group, polygons in REGIONS[key].items():
        for points in polygons:
            mask = Image.new("1", (source.shape[1], source.shape[0]))
            ImageDraw.Draw(mask).polygon(points, fill=1)
            selected = np.asarray(mask, dtype=bool) & (source > 0)
            result[selected] = group * 4 + source[selected]
    return result
