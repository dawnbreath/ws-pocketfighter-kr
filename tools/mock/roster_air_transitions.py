"""Material masks for source-verified drawings following airborne inputs."""

from __future__ import annotations

import hashlib
from types import SimpleNamespace

import numpy as np

from fighter_contexts import ACTOR_CONTEXTS
from roster_dash_colours import paint_materials
from roster_followthrough_colours import author as followthrough

FELICIA_ROLL = "bc392617e5e7891baa40529de68332bf"

REGIONS = {
    "GOUKI": {
        "7968f698e3fb8db4a725da02ff7e2b03": [
            # Gi, including the trouser cuff above the extended bare foot.
            (1, [(0, 30), (5, 26), (6, 25), (8, 30), (8, 37), (1, 36)]),
            (1, [
                (7, 21), (10, 22), (13, 24), (18, 23), (21, 19),
                (24, 18), (28, 19), (26, 23), (24, 25), (24, 28),
                (28, 30), (32, 31), (39, 32), (44, 34), (47, 37),
                (44, 38), (39, 36), (35, 38), (33, 40), (30, 38),
                (27, 37), (22, 35), (17, 34), (14, 34), (13, 31),
                (12, 29), (9, 29), (8, 27),
            ]),
            (2, [
                (8, 10), (10, 5), (12, 3), (15, 0), (19, 2), (22, 4),
                (25, 6), (25, 10), (23, 12), (20, 10), (17, 10),
                (14, 11), (12, 14), (9, 13),
            ]),
            (3, [(6, 18), (9, 15), (12, 18), (11, 21), (14, 23),
                 (18, 24), (16, 27), (12, 26), (8, 23), (5, 22)]),
            (3, [(26, 20), (32, 21), (38, 24), (37, 26), (31, 26), (27, 24)]),
            (4, [(12, 30), (17, 29), (22, 26), (23, 28), (18, 32), (12, 33)]),
        ],
    },
    "TABASA": {
        "e11a7463eaa61741622f33a132c81d66": [
            # Hat and raised cape. The hand and sleeve interrupt their contour.
            (2, [(0, 4), (12, 5), (13, 0), (17, 5), (23, 4), (27, 6),
                 (27, 15), (34, 9), (35, 10), (35, 15), (30, 19),
                 (27, 22), (21, 22), (17, 19), (14, 18), (13, 23),
                 (12, 30), (9, 34), (6, 30), (6, 24), (3, 17)]),
            (0, [(17, 8), (20, 7), (23, 9), (25, 13), (23, 15),
                 (21, 17), (18, 18), (16, 16), (16, 11)]),
            (1, [(11, 18), (14, 17), (17, 19), (19, 22), (17, 26),
                 (15, 25), (14, 29), (13, 35), (11, 34), (10, 29),
                 (9, 25), (10, 20)]),
            (3, [(22, 18), (26, 16), (31, 15), (29, 19), (26, 22), (22, 23)]),
            (1, [(9, 35), (12, 33), (16, 34), (20, 36), (25, 34),
                 (28, 36), (31, 38), (32, 42), (28, 46), (21, 50),
                 (16, 51), (12, 49), (7, 45), (6, 41), (7, 38)]),
            (3, [(30, 17), (32, 16), (32, 27), (30, 32), (28, 35),
                 (25, 38), (23, 38), (26, 35), (28, 30), (29, 25)]),
            (3, [(13, 51), (22, 50), (21, 55), (20, 58),
                 (21, 62), (19, 60), (18, 56), (16, 59), (16, 62),
                 (14, 61), (14, 57)]),
        ],
    },
    "KEN": {
        "0cc71830356e8989db25f350b907dcef": [
            (1, [
                (6, 18), (9, 18), (10, 22), (12, 24), (15, 23),
                (18, 18), (20, 19), (18, 25), (17, 29), (19, 32),
                (19, 36), (17, 38), (14, 38), (12, 37), (11, 40),
                (10, 44), (8, 45), (4, 44), (4, 37), (3, 33),
                (3, 27), (6, 25), (7, 22),
            ]),
            (3, [
                (3, 5), (5, 0), (19, 0), (22, 2), (22, 8), (19, 10),
                (17, 14), (15, 16), (14, 13), (12, 16), (10, 14),
                (9, 11), (6, 10), (4, 9),
            ]),
            (2, [(3, 10), (5, 8), (8, 10), (9, 13), (8, 15),
                 (5, 17), (3, 16)]),
            (2, [(18, 10), (21, 9), (24, 12), (24, 17), (22, 19),
                 (19, 18), (18, 16)]),
            (4, [(5, 29), (10, 30), (14, 28), (17, 28), (16, 30),
                 (12, 32), (8, 32), (5, 31)]),
        ],
    },
}


def author(character: str, source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if character == "FELICIA" and key == FELICIA_ROLL:
        # All 1,024 source pixels match the reviewed roll after a quarter-turn.
        return np.rot90(followthrough(character, np.rot90(source)), -1)
    regions = REGIONS.get(character, {}).get(key)
    if regions is None:
        raise ValueError("unregistered airborne drawing")
    return paint_materials(source, regions)


def for_context(context: int) -> SimpleNamespace:
    poses = {name: tuple(drawings) for name, drawings in REGIONS.items()}
    poses["FELICIA"] = (FELICIA_ROLL,)
    return SimpleNamespace(
        __file__=__file__,
        author=author,
        RECIPES={
            name: {"poses": keys}
            for name, keys in poses.items()
            if ACTOR_CONTEXTS.get(name, 0) == context
        },
    )
