"""Fresh, source-bound fighter surface authoring; no historical seed classifications.

Small polygons describe material regions, not portable rules for other poses.
Generated source pixels, masks and previews remain local game-derived artefacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class_table import pack_table, records_from_votes
from fighter_palettes import encode
from segment_frames import compose, merge_votes, project_labels

POSES = {
    "chunli": "91f38eefec7d270fbdad21bd9208a7da",
    "zangief": "d6c38a439bca04684b9f7124e41d052e",
}
# Ordered material polygons, authored against the original monochrome pose.
SURFACES = {
    "chunli": [
        (
            "hair",
            [
                (10, 1),
                (18, 0),
                (21, 3),
                (22, 8),
                (20, 12),
                (18, 11),
                (18, 6),
                (14, 4),
                (10, 6),
            ],
        ),
        ("white", [(5, 1), (9, 1), (11, 3), (11, 6), (9, 8), (4, 7), (3, 5)]),
        ("white", [(3, 6), (6, 7), (7, 11), (7, 15), (5, 16), (3, 14)]),
        ("blue", [(6, 15), (9, 15), (11, 17), (13, 19), (10, 21), (6, 20), (5, 18)]),
        ("brown", [(7, 25), (12, 25), (12, 30), (9, 34), (4, 35), (2, 33), (4, 29)]),
        ("brown", [(17, 26), (21, 27), (24, 31), (22, 35), (17, 34), (16, 30)]),
        ("blue", [(10, 25), (16, 25), (17, 32), (17, 34), (10, 34)]),
        ("white", [(2, 34), (5, 35), (5, 38), (0, 38), (0, 36)]),
        ("white", [(19, 35), (23, 35), (26, 37), (26, 38), (18, 38), (18, 36)]),
        ("white", [(17, 22), (20, 22), (20, 24), (18, 25), (16, 24)]),
    ],
    "zangief": [
        ("hair", [(20, 0), (24, 0), (27, 2), (29, 4), (25, 3), (22, 1), (19, 2)]),
        (
            "beard",
            [
                (17, 9),
                (19, 13),
                (23, 14),
                (23, 17),
                (21, 18),
                (24, 20),
                (26, 20),
                (26, 22),
                (23, 23),
                (20, 22),
                (18, 20),
                (17, 17),
                (14, 16),
                (15, 13),
            ],
        ),
        (
            "red",
            [
                (14, 25),
                (20, 25),
                (23, 26),
                (27, 26),
                (28, 29),
                (25, 31),
                (23, 32),
                (16, 32),
                (14, 29),
                (12, 27),
            ],
        ),
        (
            "red",
            [
                (3, 34),
                (7, 36),
                (10, 35),
                (10, 38),
                (8, 40),
                (9, 42),
                (9, 44),
                (0, 44),
                (0, 40),
            ],
        ),
        (
            "red",
            [
                (24, 36),
                (28, 37),
                (28, 41),
                (32, 42),
                (32, 44),
                (22, 44),
                (21, 41),
                (21, 38),
            ],
        ),
        ("red", [(7, 20), (8, 21), (8, 24), (7, 27), (5, 27), (4, 25), (5, 22)]),
        ("red", [(29, 19), (31, 20), (32, 22), (32, 25), (30, 27), (28, 26), (29, 24)]),
    ],
}
GROUP = {
    "chunli": {
        "skin": 0,
        "blue": 1,
        "brown": 2,
        "hair": 2,
        "white": 3,
        "ink": 2,
        "gold": 3,
    },
    "zangief": {"skin": 0, "red": 1, "hair": 2, "beard": 2, "ink": 2, "gold": 3},
}
# Interior trim paths follow existing dark seams, without changing the silhouette.
TRIM = {
    "chunli": [[(10, 26), (10, 33), (16, 33)], [(7, 17), (10, 18)]],
    "zangief": [
        [(14, 25), (19, 25), (23, 26), (27, 26)],
        [(3, 34), (7, 36), (10, 35)],
        [(23, 36), (27, 37)],
        [(6, 21), (6, 25), (5, 26)],
        [(30, 20), (31, 23), (30, 25)],
    ],
}


def identity(px: np.ndarray) -> tuple[str, np.ndarray, int, int]:
    yy, xx = np.nonzero(px)
    x, y = int(xx.min()), int(yy.min())
    crop = px[y : int(yy.max()) + 1, x : int(xx.max()) + 1]
    return hashlib.md5(crop.tobytes() + bytes(crop.shape)).hexdigest(), crop, x, y


def author(crop: np.ndarray, who: str) -> tuple[np.ndarray, np.ndarray]:
    """Assign independent surfaces, then distinguish material shadow from ink."""
    if hashlib.md5(crop.tobytes() + bytes(crop.shape)).hexdigest() != POSES[who]:
        raise ValueError("material geometry belongs to one exact original pose")
    h, w = crop.shape
    materials = np.full((h, w), "skin", dtype="<U8")
    for name, points in SURFACES[who]:
        mask = Image.new("1", (w, h))
        ImageDraw.Draw(mask).polygon(points, fill=1)
        materials[np.asarray(mask, dtype=bool) & (crop > 0)] = name
    # Dark silhouette pixels stay dark; internal muscle creases keep skin shadow.
    solid = np.pad(crop > 0, 1)
    boundary = ~(
        solid[:-2, 1:-1] & solid[2:, 1:-1] & solid[1:-1, :-2] & solid[1:-1, 2:]
    )
    materials[(materials == "skin") & (crop == 3) & boundary] = "ink"
    # Facial features: original dark eye/brow/nose/mouth pixels, not whole skin.
    face = Image.new("1", (w, h))
    draw = ImageDraw.Draw(face)
    if who == "chunli":
        draw.polygon([(11, 7), (16, 7), (16, 12), (13, 12), (11, 10)], fill=1)
    else:
        draw.polygon([(23, 6), (27, 6), (27, 12), (24, 12), (23, 10)], fill=1)
    materials[np.asarray(face, dtype=bool) & (crop == 3)] = "ink"
    # White material needs a blue shadow, leaving its shade-3 slot for gold trim.
    if who == "chunli":
        materials[(materials == "white") & (crop == 3)] = "blue"
    trim = Image.new("1", (w, h))
    draw = ImageDraw.Draw(trim)
    for points in TRIM[who]:
        draw.line(points, fill=1, width=1)
    tm = np.asarray(trim, dtype=bool) & (crop > 0)
    if who == "chunli":
        tm &= crop == 3
    materials[tm] = "gold"
    groups = np.zeros(crop.shape, dtype=np.int8)
    for name, group in GROUP[who].items():
        groups[(materials == name) & (crop > 0)] = group
    materials[crop == 0] = "clear"
    return groups, materials


def build(captures: dict[str, Path], palettes: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    config = json.loads(palettes.read_text())
    votes = {}
    sources = {}
    report = {
        "visual_approval": False,
        "method": "fresh material polygons; no inherited seed classes",
        "characters": {},
        "palette_sha256": hashlib.sha256(palettes.read_bytes()).hexdigest(),
    }
    for who, path in captures.items():
        cap = json.loads(path.read_text())
        if (
            cap.get("status") != "CAPTURED"
            or cap.get("character") != who
            or cap.get("schema") != 1
        ):
            raise ValueError("wrong capture provenance")
        used = []
        authored = None
        for index, frame in enumerate(cap["frames"]):
            px, owner, sprites = compose(frame, cap["side"])
            if not px.any():
                continue
            key, crop, x, y = identity(px)
            if key != POSES[who]:
                continue
            if authored is None:
                authored = author(crop, who)
                groups, materials = authored
                np.savez_compressed(
                    out / f"{who}.npz", source=crop, groups=groups, materials=materials
                )
                pal = config["fighters"]["CHUN-LI" if who == "chunli" else "ZANGIEF"]
                colors = np.array(
                    [[int(c, 16) * 17 for c in value] for value in pal], dtype=np.uint8
                )
                rgb = colors[groups * 4 + crop]
                rgb[crop == 0] = (55, 48, 64)
                Image.fromarray(rgb).resize(
                    (crop.shape[1] * 10, crop.shape[0] * 10), Image.Resampling.NEAREST
                ).save(out / f"{who}.png")
            plane = np.full(px.shape, -1, dtype=np.int8)
            plane[y : y + crop.shape[0], x : x + crop.shape[1]] = authored[0]
            merge_votes(votes, project_labels(owner, sprites, plane, cap["side"]))
            sources.update(
                {s["hash"]: s["raw"] for s in sprites if s["side"] == cap["side"]}
            )
            used.append(index)
        if not used:
            raise ValueError("exact source pose absent")
        report["characters"][who] = {
            "capture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "pose_md5": POSES[who],
            "frames": used,
        }
    records, omitted = records_from_votes(votes, sources)
    blob = pack_table(
        records,
        encode(config["fighters"]["CHUN-LI"]) + encode(config["fighters"]["ZANGIEF"]),
    )
    (out / "fresh.ctb2").write_bytes(blob)
    report.update(
        records=len(records),
        omitted=omitted,
        table_sha256=hashlib.sha256(blob).hexdigest(),
    )
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chunli", type=Path)
    parser.add_argument("zangief", type=Path)
    parser.add_argument("palettes", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    report = build(
        {"chunli": args.chunli, "zangief": args.zangief}, args.palettes, args.out
    )
    print(json.dumps({"records": report["records"], "omitted": report["omitted"]}))
