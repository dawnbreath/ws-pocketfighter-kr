"""Export exact 4bpp colours for the two local basic poses; game data stays local."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class_table import pack_full_table
from fighter_palettes import encode
from segment_frames import compose, merge_votes, project_labels
from seed_recipe import crop_md5, RECIPES


def build(
    captures: list[Path],
    baseline: Path,
    palettes: Path,
    out: Path,
    idle: bool = False,
    idle_cycle: bool = False,
) -> None:
    out.mkdir(parents=True, exist_ok=False)
    config = json.loads(palettes.read_text())
    votes = {}
    sources = {}
    report = {}
    for who, path in zip(["chunli", "zangief"], captures):
        cap = json.loads(path.read_text())
        if cap.get("character") != who or cap.get("status") != "CAPTURED":
            raise ValueError("capture provenance")
        key = RECIPES[who]["pose_md5"]
        z = np.load(baseline / f"{who}-{key}.npz")
        crop = z["source"]
        indices = (z["groups"] * 4 + crop).astype(np.int8)
        indices[crop == 0] = 0
        if who == "chunli":
            # Central hand retains the original skin shade; the narrow outer band
            # uses opaque black index 4, which CTB2 cannot express for shades 1..3.
            for y in range(23, 28):
                for x in range(19, 23):
                    if crop[y, x]:
                        indices[y, x] = crop[y, x]
            for y in range(22, 28):
                for x in (23, 24):
                    if crop[y, x]:
                        indices[y, x] = 4
            # Saturn shows another black cuff to the left of the lower hand.
            # Preserve the knuckles below/right; mark the upper/left band only.
            inner_band = {22: range(16, 23), 23: range(16, 20), 24: range(17, 19)}
            for y, xs in inner_band.items():
                for x in xs:
                    if crop[y, x]:
                        indices[y, x] = 4
            # Lower cuff under the skin-coloured fist, above the trousers.
            lower_band = {28: range(18, 23), 29: range(18, 24), 30: range(19, 24)}
            for y, xs in lower_band.items():
                for x in xs:
                    if crop[y, x]:
                        indices[y, x] = 4
            for x, y in [(24, 22), (24, 26), (18, 24), (20, 28), (22, 30)]:
                if not crop[y, x]:
                    raise ValueError("spike is not opaque")
                indices[y, x] = 13
        np.savez_compressed(out / f"{who}.npz", source=crop, indices=indices)
        pose_indices = {key: indices}
        if (idle or idle_cycle) and who == "chunli":
            from idle_neighbor import TARGET, author

            for frame in cap["frames"]:
                px, _, _ = compose(frame, cap["side"])
                if px.any() and crop_md5(px)[0] == TARGET:
                    target = crop_md5(px)[1]
                    pose_indices[TARGET] = author(crop, indices, target)
                    np.savez_compressed(
                        out / f"{who}-{TARGET}.npz",
                        source=target,
                        indices=pose_indices[TARGET],
                    )
                    break
            if TARGET not in pose_indices:
                raise ValueError("requested idle neighbour absent")
        if idle_cycle and who == "chunli":
            from idle_neighbor import REMAINING

            pending = set(REMAINING)
            for frame in cap["frames"]:
                px, _, _ = compose(frame, cap["side"])
                if not px.any():
                    continue
                other_key, other_crop = crop_md5(px)
                if other_key not in pending:
                    continue
                pose_indices[other_key] = author(
                    target, pose_indices[TARGET], other_crop
                )
                np.savez_compressed(
                    out / f"{who}-{other_key}.npz",
                    source=other_crop,
                    indices=pose_indices[other_key],
                )
                pending.remove(other_key)
            if pending:
                raise ValueError("idle cycle poses absent")
        used = []
        for i, frame in enumerate(cap["frames"]):
            px, owner, sprites = compose(frame, cap["side"])
            if not px.any():
                continue
            pose_key, pose_crop = crop_md5(px)
            if pose_key not in pose_indices:
                continue
            yy, xx = np.nonzero(px)
            x, y = int(xx.min()), int(yy.min())
            plane = np.full(px.shape, -1, dtype=np.int8)
            plane[y : y + pose_crop.shape[0], x : x + pose_crop.shape[1]] = (
                pose_indices[pose_key]
            )
            merge_votes(votes, project_labels(owner, sprites, plane, cap["side"]))
            sources.update(
                {s["hash"]: s["raw"] for s in sprites if s["side"] == cap["side"]}
            )
            used.append(i)
        if not used:
            raise ValueError("pose absent")
        report[who] = {
            "frames": used,
            "capture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    records = []
    for key, cells in votes.items():
        if any(len(c) != 1 for c in cells):
            raise ValueError("ambiguous or unobserved pixel")
        values = [next(iter(c)) for c in cells]
        output = bytearray(32)
        for i, value in enumerate(values):
            if value not in range(16):
                raise ValueError("invalid palette index")
            y, x = divmod(i, 8)
            for plane in range(4):
                output[y * 4 + plane] |= ((value >> plane) & 1) << (7 - x)
        records.append((sources[key], bytes(output)))
    blob = pack_full_table(
        records,
        encode(config["fighters"]["CHUN-LI"]) + encode(config["fighters"]["ZANGIEF"]),
    )
    (out / "full.ctb3").write_bytes(blob)
    report["table_sha256"] = hashlib.sha256(blob).hexdigest()
    report["records"] = len(records)
    (out / "report.json").write_text(json.dumps(report, indent=2))
    print(len(records), "records")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["chunli", "zangief", "baseline", "palettes", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument("--idle-neighbor", action="store_true")
    p.add_argument("--idle-cycle", action="store_true")
    a = p.parse_args()
    build(
        [a.chunli, a.zangief],
        a.baseline,
        a.palettes,
        a.out,
        a.idle_neighbor,
        a.idle_cycle,
    )
