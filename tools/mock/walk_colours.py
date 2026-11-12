"""Source-bound Chun-Li walk masks; polygons describe materials, not game pixels."""

from __future__ import annotations
import hashlib
import numpy as np
from PIL import Image, ImageDraw

POSES = (
    "a85e370e3e0e5d717a3ae703eba555f4",
    "57081f8f8361794e5b160c44d64bf5cb",
    "9e1a8f58ba00c6a884a9989f0f2e5927",
    "d6c46e228e977c1b0926c66c3a76a5c5",
)


def author(source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if key not in POSES:
        raise ValueError("unsupported walk drawing")
    n = POSES.index(key)
    out = source.astype(np.int8).copy()  # Exposed face, arms and hands.
    # The lower body is clothed. Keep its contour pixels with the trousers;
    # the tunic, boots and cuffs below override their reviewed regions.
    lower = np.indices(source.shape)[0] >= 27
    out[lower & (source > 0)] += 8

    def region(group: int, points: list[tuple[int, int]], exact: bool = False):
        mask = Image.new("1", (source.shape[1], source.shape[0]))
        ImageDraw.Draw(mask).polygon(points, fill=1)
        selected = np.array(mask, dtype=bool) & (source > 0)
        out[selected] = group if exact else group * 4 + source[selected]

    # Shared head geometry, positioned by the bun's top-left contour.
    shift = [5, 0, -1, 1][n]

    def head(group, points):
        region(group, [(x + shift, y) for x, y in points])

    head(3, [(9, 0), (13, 0), (15, 3), (15, 6), (12, 8), (7, 8), (4, 6), (4, 3)])
    head(3, [(6, 8), (8, 8), (8, 12), (9, 13), (5, 13), (5, 11)])
    head(
        2,
        [
            (14, 2),
            (19, 2),
            (24, 3),
            (26, 6),
            (26, 10),
            (24, 10),
            (23, 7),
            (21, 5),
            (18, 4),
            (15, 5),
        ],
    )
    # Shoulder and tunic behind the exposed arms.
    head(1, [(5, 14), (9, 14), (11, 16), (12, 18), (10, 20), (7, 20), (3, 18), (3, 15)])
    bodies = [
        [
            (14, 19),
            (18, 18),
            (19, 20),
            (18, 25),
            (21, 27),
            (17, 28),
            (17, 32),
            (13, 33),
            (12, 25),
        ],
        [(9, 19), (13, 18), (14, 20), (13, 25), (15, 27), (13, 33), (9, 35), (8, 25)],
        [(8, 19), (12, 18), (14, 20), (13, 25), (12, 29), (11, 34), (7, 33), (6, 24)],
        [(10, 19), (14, 18), (16, 20), (15, 26), (16, 29), (13, 33), (9, 33), (9, 25)],
    ]
    region(1, bodies[n])
    pants = [
        [
            [(9, 24), (12, 24), (13, 28), (13, 33), (5, 33), (5, 29)],
            [(18, 27), (21, 27), (23, 30), (23, 35), (18, 35), (17, 32)],
        ],
        [
            [(4, 24), (7, 24), (9, 28), (9, 32), (4, 35), (1, 34), (1, 28)],
            [(12, 27), (14, 27), (15, 29), (14, 35), (10, 36), (9, 33)],
        ],
        [
            [(4, 25), (7, 26), (8, 29), (7, 34), (3, 36), (1, 33), (1, 28)],
            [(9, 29), (11, 29), (11, 34), (8, 36), (6, 35), (6, 33)],
        ],
        [
            [(5, 25), (8, 25), (9, 29), (8, 33), (5, 36), (1, 37), (1, 33)],
            [(13, 28), (15, 28), (16, 30), (15, 36), (11, 36), (11, 33)],
        ],
    ]
    for p in pants[n]:
        region(2, p)
    boots = [
        [
            [(0, 31), (3, 31), (5, 32), (5, 34), (4, 36), (6, 37), (6, 38), (0, 38)],
            [(18, 35), (21, 35), (22, 36), (26, 37), (26, 38), (18, 38)],
        ],
        [
            [(2, 35), (5, 35), (4, 37), (6, 38), (6, 39), (0, 39), (0, 37)],
            [(10, 36), (12, 36), (13, 37), (16, 38), (16, 39), (9, 39)],
        ],
        [
            [(2, 36), (5, 36), (6, 38), (8, 39), (1, 39), (0, 37)],
            [(7, 35), (9, 35), (10, 37), (12, 39), (7, 39), (6, 37)],
        ],
        [
            [(2, 36), (4, 36), (3, 38), (0, 38), (0, 37)],
            [(11, 35), (14, 35), (14, 36), (17, 37), (17, 38), (11, 38)],
        ],
    ]
    for p in boots[n]:
        region(3, p)
    foot_row = [36, 37, 36, 37][n]
    region(
        3,
        [
            (0, foot_row),
            (source.shape[1] - 1, foot_row),
            (source.shape[1] - 1, source.shape[0] - 1),
            (0, source.shape[0] - 1),
        ],
    )
    if n == 0:
        region(3, [(5, 33), (6, 34), (4, 35)])
    cuffs = [
        [
            [(16, 23), (18, 23), (18, 26), (21, 26), (21, 27), (17, 27), (16, 25)],
            [(26, 20), (30, 20), (30, 22), (28, 23), (25, 22)],
        ],
        [
            [(11, 23), (13, 23), (13, 26), (16, 26), (16, 27), (12, 27), (11, 25)],
            [(21, 20), (25, 20), (25, 22), (23, 23), (20, 22)],
        ],
        [
            [(10, 24), (13, 24), (13, 26), (12, 28), (9, 28), (9, 27)],
            [(21, 22), (25, 22), (25, 24), (23, 24), (20, 23)],
        ],
        [
            [(12, 24), (15, 24), (15, 26), (13, 28), (11, 27)],
            [(24, 22), (28, 22), (28, 24), (26, 25), (23, 24)],
        ],
    ]
    for p in cuffs[n]:
        region(4, p, True)
    studs = [
        [(17, 24), (20, 27), (26, 21), (28, 23)],
        [(12, 24), (15, 27), (21, 21), (23, 23)],
        [(10, 25), (12, 28), (21, 23), (24, 24)],
        [(12, 25), (13, 28), (24, 23), (26, 25)],
    ]
    for x, y in studs[n]:
        if source[y, x]:
            out[y, x] = 13
    return out
