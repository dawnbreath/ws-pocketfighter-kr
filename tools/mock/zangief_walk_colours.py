"""Exact-source Zangief forward/backward walking drawings.

Keep hands/legs skin, wristbands/boots red1, trunks red2 and hair/beard dark
skin. The fifth drawing also repeats in far forward walking (T47 controls).
Source hashes bind these polygons; they are not an arbitrary pose transfer.
"""

from __future__ import annotations
import hashlib
import numpy as np
from wrist_fixes import selection

BACK = ("edf5d1e6518c1d82e730660e36da1b83", "0ce1c596239944b85ecf69468ba56ab2")
FORWARD = ("17ece493fd2fc86f91c2a224d7f08b0e", "bc0c17f07da6642035c689f7fade1f41")
FORWARD_STEP = "5f7e6f558f359512ba60ee52a941d42b"
POSES = (*BACK, *FORWARD, FORWARD_STEP)
REGIONS = {
    BACK[0]: {
        1: [
            [(3, 19), (5, 19), (6, 21), (6, 24), (4, 24), (3, 22)],
            [(18, 19), (20, 19), (21, 21), (21, 26), (18, 26)],
            [(8, 35), (13, 35), (13, 38), (15, 39), (15, 42), (6, 42), (6, 38)],
            [(14, 35), (18, 35), (18, 38), (22, 40), (22, 42), (13, 42)],
        ],
        2: [[(12, 26), (24, 26), (25, 28), (21, 31), (17, 30), (14, 29)]],
    },
    BACK[1]: {
        1: [
            [(6, 17), (8, 17), (9, 20), (8, 23), (6, 23)],
            [(25, 22), (28, 22), (30, 25), (28, 28), (25, 28), (24, 26)],
            [(4, 34), (9, 32), (11, 33), (8, 36), (7, 40), (2, 40), (2, 36)],
            [(14, 35), (20, 35), (20, 38), (26, 40), (26, 42), (13, 42)],
        ],
        2: [[(10, 27), (14, 27), (16, 30), (21, 31), (20, 34), (14, 35), (12, 32)]],
    },
    FORWARD[0]: {
        1: [
            [(7, 14), (10, 15), (10, 17), (7, 19), (5, 18), (5, 16)],
            [(37, 19), (40, 20), (41, 22), (41, 25), (37, 25)],
            [(9, 34), (15, 34), (15, 37), (20, 38), (20, 40), (9, 40), (8, 37)],
            [(25, 32), (32, 32), (32, 35), (36, 37), (36, 40), (24, 40)],
        ],
        2: [
            [
                (15, 22),
                (21, 22),
                (24, 24),
                (26, 25),
                (31, 25),
                (32, 27),
                (29, 30),
                (24, 28),
                (21, 27),
                (15, 27),
            ]
        ],
    },
    FORWARD[1]: {
        1: [
            [(3, 18), (5, 18), (6, 21), (6, 23), (3, 24)],
            [(17, 19), (19, 19), (20, 21), (20, 26), (17, 26)],
            [(2, 34), (7, 32), (8, 34), (5, 37), (4, 40), (0, 42), (0, 38)],
            [(12, 34), (18, 34), (18, 36), (23, 38), (23, 41), (10, 41), (10, 37)],
        ],
        2: [
            [(9, 26), (21, 26), (22, 28), (18, 31), (14, 30), (11, 29)],
            # This two-pixel toe shares a retained tile. Its existing index11
            # is also dark red in Zangief's palette; preserve that output.
            [(24, 40), (24, 41)],
        ],
    },
    FORWARD_STEP: {
        1: [
            [(7, 17), (9, 17), (10, 20), (10, 23), (7, 23)],
            [(28, 22), (30, 21), (32, 23), (31, 26), (28, 27), (27, 25)],
            [(11, 36), (15, 36), (15, 42), (9, 42), (9, 39)],
            [(16, 35), (21, 35), (21, 38), (27, 40), (27, 42), (14, 42), (14, 38)],
        ],
        2: [[(13, 29), (18, 29), (21, 31), (24, 31), (22, 34), (18, 35), (15, 33)]],
    },
}


def author(source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if key not in POSES:
        raise ValueError("unsupported Zangief walking drawing")
    result = source.astype(np.int8).copy()
    for group, polygons in REGIONS[key].items():
        for points in polygons:
            selected = selection(source.shape, points) & (source > 0)
            result[selected] = group * 4 + source[selected]
    return result
