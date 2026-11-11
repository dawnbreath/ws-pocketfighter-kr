"""Build a bounded CTB2 trial from source-bound seed recipes and optional idle proposals.

No unknown/conflicting opaque pixel is exported. This is not all-pose approval.
Outputs contain local game-derived data and must not be committed.
"""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Callable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class_table import pack_table, records_from_votes
from fighter_palettes import encode
from segment_frames import compose, merge_votes, project_labels
from seed_recipe import RECIPES, classify, crop_md5
from register_transfer import transfer

GroupAdjust = Callable[[np.ndarray, str, np.ndarray], np.ndarray]

GROUPS = {
    "chunli": {"skin": 0, "blue": 1, "brown": 2, "hair": 2, "white": 3, "silver": 3},
    "zangief": {"skin": 0, "red": 1, "pants": 2},
}
IDLE_CHUNLI = {
    "09b8001e109c1602f4b3d47951121a04",
    "e9120a9dc9c057e94016e0fd43b5d755",
    "177ef0038785e1b4fe9edb46ea362abe",
}


def collect(
    path: Path, who: str, idle: bool, out: Path, adjust: GroupAdjust | None = None
) -> tuple[dict, dict, dict]:
    cap = json.loads(path.read_text())
    if (
        cap.get("status") != "CAPTURED"
        or cap.get("schema") != 1
        or cap.get("character") != who
    ):
        raise ValueError("need completed capture of the named fighter")
    frames = [compose(frame, cap["side"]) for frame in cap["frames"]]
    recipe = RECIPES[who]
    seed = next(
        (
            crop_md5(px)[1]
            for px, _, _ in frames
            if px.any() and crop_md5(px)[0] == recipe["pose_md5"]
        ),
        None,
    )
    if seed is None:
        raise ValueError("source-bound historical seed pose missing")
    labels = {recipe["pose_md5"]: classify(seed, recipe)}
    crops = {recipe["pose_md5"]: seed}
    votes, sources, used = {}, {}, []
    adjusted_groups = {}
    for index, (px, owner, sprites) in enumerate(frames):
        if not px.any():
            continue
        key, crop = crop_md5(px)
        if key not in labels and idle and who == "chunli" and key in IDLE_CHUNLI:
            labels[key] = transfer(seed, labels[recipe["pose_md5"]], crop, 3, 2, 2)
            crops[key] = crop
        if key not in labels:
            continue
        yy, xx = np.nonzero(px)
        ox, oy = int(xx.min()), int(yy.min())
        groups = np.full(px.shape, -1, dtype=np.int8)
        for (y, x), name in labels[key].items():
            # The early Claude mock only painted shade-3 hair dark;
            # lighter pixels in its broad hair rectangle remain skin.
            if name == "hair" and crop[y, x] != 3:
                name = "skin"
            groups[oy + y, ox + x] = GROUPS[who][name]
        if adjust is not None:
            h, w = crop.shape
            adjusted_groups[key] = adjust(crop, who, groups[oy : oy + h, ox : ox + w])
            groups[oy : oy + h, ox : ox + w] = adjusted_groups[key]
        merge_votes(votes, project_labels(owner, sprites, groups, cap["side"]))
        for sprite in sprites:
            if sprite["side"] == cap["side"]:
                sources[sprite["hash"]] = sprite["raw"]
        used.append(index)
    label_name = f"{who}-baseline-labels.json" if adjust else f"{who}-labels.json"
    (out / label_name).write_text(
        json.dumps(
            {
                key: [[x, y, name] for (y, x), name in lab.items()]
                for key, lab in labels.items()
            }
        )
    )
    for key, crop in crops.items():
        extra = {"groups": adjusted_groups[key]} if key in adjusted_groups else {}
        np.savez_compressed(out / f"{who}-{key}.npz", source=crop, **extra)
    return (
        votes,
        sources,
        {
            "capture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "frames_used": used,
            "pose_count": len(labels),
            "labelled_pixels": {key: len(lab) for key, lab in labels.items()},
        },
    )


def build(
    chunli: Path,
    zangief: Path,
    palettes: Path,
    out: Path,
    idle: bool = False,
    adjust: GroupAdjust | None = None,
) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    config = json.loads(palettes.read_text())
    all_votes, all_sources, report = (
        {},
        {},
        {
            "characters": {},
            "registration_proposals": idle,
            "local_adjustment": adjust is not None,
            "production_approved": False,
            "group_mapping": GROUPS,
            "palette_catalogue_sha256": hashlib.sha256(
                palettes.read_bytes()
            ).hexdigest(),
        },
    )
    for who, capture in [("chunli", chunli), ("zangief", zangief)]:
        votes, sources, evidence = collect(capture, who, idle, out, adjust)
        merge_votes(all_votes, votes)
        all_sources.update(sources)
        report["characters"][who] = evidence
    records, omitted = records_from_votes(all_votes, all_sources)
    blob = pack_table(
        records,
        encode(config["fighters"]["CHUN-LI"]) + encode(config["fighters"]["ZANGIEF"]),
    )
    (out / "seed.ctb2").write_bytes(blob)
    report.update(
        records=len(records),
        bytes=len(blob),
        omitted=omitted,
        table_sha256=hashlib.sha256(blob).hexdigest(),
    )
    (out / "report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chunli", type=Path)
    parser.add_argument("zangief", type=Path)
    parser.add_argument("palettes", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--include-idle-proposals", action="store_true")
    parser.add_argument("--wrist-fixes", action="store_true")
    args = parser.parse_args()
    if args.wrist_fixes and args.include_idle_proposals:
        parser.error("local fixes apply to the exact basic poses only")
    adjust = None
    if args.wrist_fixes:
        from wrist_fixes import adjust
    report = build(
        args.chunli,
        args.zangief,
        args.palettes,
        args.out,
        args.include_idle_proposals,
        adjust,
    )
    print(
        json.dumps(
            {key: report[key] for key in ["records", "bytes", "registration_proposals"]}
        )
    )
