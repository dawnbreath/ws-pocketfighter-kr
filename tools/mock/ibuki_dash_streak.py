"""Ibuki's isolated dash smear. Materials follow the Saturn dash reference."""

from __future__ import annotations

import hashlib
import numpy as np
from wrist_fixes import selection

VISIBLE_SOURCE = False
POSE = "d26b0bdba5c7d5ae4234078b94d35844"
RECIPES = {"IBUKI": {"poses": (POSE,)}}

# Cream gi, dark hair, exposed skin and the brown face covering.
REGIONS = [
    (1, [(0, 13), (60, 13), (63, 21), (0, 21)]),
    (1, [(37, 25), (83, 25), (83, 32), (37, 32)]),
    (
        2,
        [
            (20, 0),
            (43, 0),
            (59, 5),
            (63, 5),
            (63, 11),
            (57, 11),
            (53, 7),
            (40, 4),
            (20, 4),
        ],
    ),
    (
        2,
        [
            (59, 1),
            (68, 0),
            (76, 2),
            (81, 5),
            (83, 9),
            (79, 13),
            (75, 12),
            (72, 8),
            (66, 8),
            (62, 10),
            (58, 7),
        ],
    ),
    (0, [(64, 6), (69, 5), (75, 6), (78, 8), (76, 10), (70, 11), (65, 10), (62, 8)]),
    (
        3,
        [
            (66, 10),
            (72, 11),
            (78, 10),
            (82, 10),
            (81, 15),
            (77, 18),
            (73, 18),
            (68, 16),
            (65, 13),
        ],
    ),
    (
        1,
        [
            (58, 13),
            (62, 14),
            (67, 18),
            (70, 20),
            (66, 25),
            (60, 27),
            (50, 26),
            (46, 23),
            (52, 21),
            (59, 20),
        ],
    ),
    (0, [(43, 9), (49, 9), (52, 11), (51, 14), (46, 14), (43, 12)]),
    (3, [(53, 10), (57, 10), (60, 13), (59, 17), (56, 17), (53, 14)]),
]


def author(character: str, source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if character != "IBUKI" or key != POSE:
        raise ValueError("unsupported Ibuki dash drawing")
    out = source.copy()
    for material, points in REGIONS:
        mask = selection(source.shape, points) & (source > 0)
        out[mask] = material * 4 + source[mask]
    return out
