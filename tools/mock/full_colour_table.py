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


def build(captures: list[Path], baseline: Path, palettes: Path, out: Path) -> None:
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
            for x, y in [(24, 22), (24, 26)]:
                if not crop[y, x]:
                    raise ValueError("spike is not opaque")
                indices[y, x] = 13
        np.savez_compressed(out / f"{who}.npz", source=crop, indices=indices)
        used = []
        for i, frame in enumerate(cap["frames"]):
            px, owner, sprites = compose(frame, cap["side"])
            if not px.any() or crop_md5(px)[0] != key:
                continue
            yy, xx = np.nonzero(px)
            x, y = int(xx.min()), int(yy.min())
            plane = np.full(px.shape, -1, dtype=np.int8)
            plane[y : y + crop.shape[0], x : x + crop.shape[1]] = indices
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
    a = p.parse_args()
    build([a.chunli, a.zangief], a.baseline, a.palettes, a.out)
