"""Exact Tabasa familiar form, identified against actual Saturn low-punch footage.

The dark violet body, golden eyes and white teeth are material proposals. Only
this completely observed WS source is registered; two partly hidden related
sources and an unidentified appendage remain outside this recipe.
"""

from __future__ import annotations

import hashlib
import numpy as np
from wrist_fixes import selection

POSE = "9447fa3e4bd0ae5a2d65c897ebcc14be"
RECIPES = {"TABASA": {"poses": (POSE,)}}
REGIONS = [
    # Entire lower familiar silhouette is non-skin, including its small appendages.
    (2, [(0, 33), (59, 33), (59, 52), (0, 52)]),
    # Familiar body, long tail and lower extensions.
    (
        2,
        [
            (0, 37),
            (11, 37),
            (18, 35),
            (26, 32),
            (38, 31),
            (50, 32),
            (57, 35),
            (59, 40),
            (57, 45),
            (49, 49),
            (45, 52),
            (35, 52),
            (27, 49),
            (20, 48),
            (13, 46),
            (8, 43),
            (11, 40),
            (0, 39),
        ],
    ),
    # Character's pointed hat and robe, independently from the familiar face.
    (
        2,
        [
            (35, 0),
            (37, 8),
            (39, 17),
            (41, 21),
            (49, 23),
            (54, 24),
            (44, 25),
            (35, 24),
            (27, 24),
            (17, 23),
            (23, 21),
            (31, 20),
            (34, 17),
        ],
    ),
    (
        2,
        [
            (26, 29),
            (31, 29),
            (35, 31),
            (39, 30),
            (41, 34),
            (36, 37),
            (30, 36),
            (25, 33),
        ],
    ),
    # Gold braids and skin face under the brim.
    (3, [(29, 25), (32, 24), (34, 26), (33, 30), (30, 31), (28, 28)]),
    (3, [(36, 25), (39, 25), (40, 28), (38, 31), (36, 29)]),
    (0, [(33, 25), (37, 25), (39, 27), (38, 30), (34, 30), (31, 28)]),
    # White robe cuffs.
    (1, [(23, 28), (27, 28), (29, 31), (27, 33), (23, 32), (21, 30)]),
    (1, [(38, 28), (42, 28), (43, 31), (40, 33), (37, 31)]),
    # Visible grey robe fold below the familiar.
    (1, [(21, 47), (31, 47), (34, 50), (31, 52), (24, 52), (20, 50)]),
    # Slanted golden eyes preserve the original shade pattern.
    (3, [(40, 34), (42, 33), (45, 34), (49, 37), (49, 39), (46, 39), (42, 37)]),
    (3, [(47, 33), (49, 33), (52, 35), (55, 38), (53, 39), (50, 37), (48, 35)]),
    # Solid black mouth behind the teeth; index 4 is opaque black.
    (4, [(28, 41), (54, 41), (54, 45), (29, 45)]),
    (1, [(31, 42), (52, 42), (53, 44), (30, 44)]),
]


def author(character: str, source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if character != "TABASA" or key != POSE:
        raise ValueError("unsupported Tabasa familiar drawing")
    out = source.astype(np.int8).copy()
    for material, points in REGIONS:
        chosen = selection(source.shape, points) & (source > 0)
        out[chosen] = material if material in (4, 12) else material * 4 + source[chosen]
    return out
