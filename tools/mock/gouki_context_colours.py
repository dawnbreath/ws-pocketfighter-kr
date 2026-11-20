"""Exact Gouki drawings whose shared source tiles need a character context.

The exporter protects all retained Gouki tile sources before adding variants.
These source-bound polygons are proposals; projected final labels are checked
against runtime buffers and actual screenshots, with art approval separate.
"""

from __future__ import annotations
import hashlib
import numpy as np
from wrist_fixes import selection

REGIONS = {
    "425340f5f536b56de4c8475fd17cc2cf": [
        (
            1,
            [
                (13, 18),
                (19, 18),
                (23, 20),
                (29, 20),
                (29, 26),
                (27, 29),
                (29, 35),
                (21, 36),
                (18, 33),
                (14, 34),
                (9, 36),
                (7, 34),
                (10, 29),
                (13, 26),
            ],
        ),
        (3, [(15, 16), (27, 16), (27, 18), (15, 18)]),
        (4, [(12, 27), (26, 27), (26, 29), (12, 29)]),
        (
            2,
            [
                (14, 1),
                (20, 0),
                (24, 3),
                (25, 10),
                (23, 15),
                (19, 14),
                (16, 12),
                (14, 7),
            ],
        ),
    ],
    "bcaec94640d559535fac694b9b05a251": [
        (
            1,
            [
                (11, 22),
                (19, 21),
                (23, 24),
                (23, 29),
                (26, 33),
                (27, 38),
                (21, 38),
                (17, 33),
                (11, 33),
                (10, 38),
                (5, 38),
                (5, 34),
                (10, 28),
            ],
        ),
        (
            2,
            [
                (6, 0),
                (12, 0),
                (14, 3),
                (21, 4),
                (22, 9),
                (20, 12),
                (15, 10),
                (12, 13),
                (7, 11),
                (5, 7),
            ],
        ),
        (
            3,
            [
                (8, 19),
                (12, 20),
                (18, 20),
                (22, 18),
                (22, 21),
                (19, 24),
                (14, 25),
                (9, 23),
            ],
        ),
        (4, [(10, 29), (21, 29), (21, 31), (11, 31)]),
    ],
    "fa9d47018a9a8e90382640c315fb0ae5": [
        (
            1,
            [
                (11, 22),
                (19, 21),
                (23, 24),
                (23, 29),
                (26, 33),
                (27, 38),
                (21, 38),
                (17, 33),
                (11, 33),
                (10, 38),
                (5, 38),
                (5, 34),
                (10, 28),
            ],
        ),
        (
            2,
            [
                (6, 0),
                (12, 0),
                (14, 3),
                (21, 4),
                (22, 9),
                (20, 12),
                (15, 10),
                (12, 13),
                (7, 11),
                (5, 7),
            ],
        ),
        (
            3,
            [
                (8, 19),
                (12, 20),
                (18, 20),
                (22, 18),
                (22, 21),
                (19, 24),
                (14, 25),
                (9, 23),
            ],
        ),
        (4, [(10, 29), (21, 29), (21, 31), (11, 31)]),
    ],
}

RECIPES = {"GOUKI": {"poses": tuple(REGIONS)}}


def author(character: str, source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if character != "GOUKI" or key not in REGIONS:
        raise ValueError("unsupported Gouki context drawing")
    out = source.astype(np.int8).copy()
    for material, points in REGIONS[key]:
        chosen = selection(source.shape, points) & (source > 0)
        out[chosen] = material if material in (4, 12) else material * 4 + source[chosen]
    return out
