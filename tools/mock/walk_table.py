"""Append reviewed Chun-Li movement drawings to an existing CTB3 table."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class_table import HEADER, FULL_RECORD, pack_full_table, validate_table
from segment_frames import compose, project_labels, merge_votes
from seed_recipe import crop_md5


def build(capture: Path, baseline: Path, out: Path, motion: str = "walk") -> dict:
    if motion == "dash":
        from dash_colours import POSES, author

        protocols = {
            "reload base; settle 240; tap 4 release 4 then hold",
            "reload base; settle 180; repeated two-frame taps",
        }
    elif motion == "walk":
        from walk_colours import POSES, author

        protocols = {"reload base; settle 180; single continuous hold"}
    else:
        raise ValueError("unsupported motion")
    cap = json.loads(capture.read_text())
    if (cap.get("character"), cap.get("side"), cap.get("status")) != (
        "chunli",
        4,
        "CAPTURED",
    ):
        raise ValueError("requires captured P1 Chun-Li")
    if cap.get("input_protocol") not in protocols:
        raise ValueError("capture input protocol does not match the motion")
    blob = baseline.read_bytes()
    validate_table(blob)
    magic, count = HEADER.unpack_from(blob)
    if magic != b"CTB3":
        raise ValueError("invalid baseline CTB3")
    original = {
        raw: output
        for _, raw, output in [
            FULL_RECORD.unpack_from(blob, HEADER.size + i * FULL_RECORD.size)
            for i in range(count)
        ]
    }
    votes, sources, seen = {}, {}, {}
    for n, frame in enumerate(cap["frames"]):
        if not frame.get("render_matches"):
            continue
        px, owner, sprites = compose(frame, 4)
        if not px.any():
            continue
        key, source = crop_md5(px)
        if key not in POSES:
            continue
        indices = author(source)
        yy, xx = np.nonzero(px)
        x, y = int(xx.min()), int(yy.min())
        plane = np.full(px.shape, -1, dtype=np.int8)
        plane[y : y + source.shape[0], x : x + source.shape[1]] = indices
        merge_votes(votes, project_labels(owner, sprites, plane, 4))
        sources.update({s["hash"]: s["raw"] for s in sprites if s["side"] == 4})
        seen.setdefault(key, []).append(n)
    if set(seen) != set(POSES):
        raise ValueError("required movement drawings absent")
    records = dict(original)
    for key, cells in votes.items():
        if any(len(cell) != 1 for cell in cells):
            raise ValueError("conflicting or unobserved tile pixel")
        output = bytearray(32)
        for i, cell in enumerate(cells):
            value = next(iter(cell))
            if value not in range(16):
                raise ValueError("invalid index")
            y, x = divmod(i, 8)
            for p in range(4):
                output[y * 4 + p] |= ((value >> p) & 1) << (7 - x)
        raw = sources[key]
        if raw in original and original[raw] != bytes(output):
            raise ValueError("movement mask would change an existing tile")
        records[raw] = bytes(output)
    result = pack_full_table(list(records.items()), blob[-64:])
    out.mkdir(parents=True, exist_ok=False)
    (out / "full.ctb3").write_bytes(result)
    report = {
        "motion": motion,
        "capture_sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
        "baseline_sha256": hashlib.sha256(blob).hexdigest(),
        "table_sha256": hashlib.sha256(result).hexdigest(),
        "frames": seen,
        "preserved_records": count,
        "records": len(records),
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["capture", "baseline", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument("--motion", choices=["walk", "dash"], default="walk")
    args = p.parse_args()
    print(json.dumps(build(args.capture, args.baseline, args.out, args.motion)))
