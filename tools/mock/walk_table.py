"""Append exact source-bound fighter drawings to an existing CTB3 table."""

from __future__ import annotations
import argparse
import hashlib
import json
from collections.abc import Iterable
from itertools import chain
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class_table import HEADER, FULL_RECORD, pack_full_table, validate_table
from compact_colour_table import fallback_output, read_full_records
from segment_frames import compose, project_labels, merge_votes
from seed_recipe import crop_md5
from fighter_palettes import encode


def compatible_palettes(
    blob: bytes, config: dict, protected_outputs: Iterable[bytes] = ()
) -> bytes:
    """Change only swatches unreferenced by any baseline output, in both footers."""
    new = encode(config["fighters"]["CHUN-LI"]) + encode(config["fighters"]["ZANGIEF"])
    used = set()
    outputs = (
        output for _, _, output in FULL_RECORD.iter_unpack(blob[HEADER.size : -64])
    )
    for output in chain(outputs, protected_outputs):
        for y in range(8):
            for x in range(8):
                used.add(
                    sum(((output[y * 4 + p] >> (7 - x)) & 1) << p for p in range(4))
                )
    old = blob[-64:]
    if any(
        old[base + index * 2 : base + index * 2 + 2]
        != new[base + index * 2 : base + index * 2 + 2]
        for base in (0, 32)
        for index in used
    ):
        raise ValueError("palette update would recolour an existing output")
    return new


def build(
    capture: Path,
    baseline: Path,
    out: Path,
    motion: str = "walk",
    additional_captures: list[Path] | None = None,
    palettes: Path | None = None,
    preserve_fallback_from: list[Path] | None = None,
) -> dict:
    character = "chunli"
    if motion == "dash":
        from dash_colours import POSES, author

        protocols = {
            "reload base; settle 240; tap 4 release 4 then hold",
            "reload base; settle 180; repeated two-frame taps",
        }
    elif motion == "walk":
        from walk_colours import POSES, author

        protocols = {"reload base; settle 180; single continuous hold"}
    elif motion == "attack":
        from attack_colours import POSES, author

        protocols = {"reload base; settle 240; single attack hold"}
    elif motion == "low-air":
        from low_air_colours import POSES, author

        protocols = {"reload base; settle 240; crouch12 or jump4-release8; action hold"}
    elif motion == "defence":
        from defence_colours import POSES, author

        protocols = {
            "reload base; settle 180; single continuous hold",
            "reload base; settle 180; single continuous hold; settle override 0",
        }
    elif motion == "damage":
        from damage_colours import POSES, author

        protocols = {
            "reload base; settle 180; single no-input step; settle override 600",
        }
    elif motion == "contact":
        from contact_colours import POSES, author

        protocols = {
            "reload base; settle 180; single no-input step; settle override 400",
            "reload base; settle 180; single no-input step; settle override 600",
        }
    elif motion == "ball":
        from ball_colours import POSES, author

        protocols = {
            "reload base; settle 180; single no-input step; settle override 400"
        }
    elif motion == "zangief-idle":
        from zangief_idle_colours import POSES, author

        character = "zangief"
        protocols = {
            "reload base; settle 180; single no-input step; settle override 240"
        }
    elif motion == "zangief-walk":
        from zangief_walk_colours import POSES, author

        character = "zangief"
        protocols = {
            "reload base; settle 180; single continuous hold; settle override 600",
            "reload base; settle 180; single continuous hold; settle override 0",
        }
    elif motion == "zangief-basic":
        from zangief_basic_colours import POSES, author

        character = "zangief"
        protocols = {
            "reload base; settle 240; single attack hold; settle override 0",
            "reload base; settle 180; single continuous hold; settle override 0",
        }
    else:
        raise ValueError("unsupported motion")
    if motion == "ball" and palettes is None:
        raise ValueError("ball export requires --palettes to synchronize gold swatches")
    paths = [capture, *(additional_captures or [])]
    caps = []
    for path in paths:
        cap = json.loads(path.read_text())
        if (cap.get("character"), cap.get("side"), cap.get("status")) != (
            character,
            4,
            "CAPTURED",
        ):
            raise ValueError(f"requires captured P1 {character}")
        if cap.get("input_protocol") not in protocols:
            raise ValueError("capture input protocol does not match the motion")
        caps.append(cap)
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
    protected = {}
    for path in preserve_fallback_from or []:
        for _, raw, output in read_full_records(path.read_bytes()):
            if output == fallback_output(raw):
                if original.get(raw, output) != output:
                    raise ValueError("baseline recolours a protected fallback tile")
                protected[raw] = output
    votes, sources, seen = {}, {}, {}
    frames = [
        (i, n, f) for i, cap in enumerate(caps) for n, f in enumerate(cap["frames"])
    ]
    for cap_index, n, frame in frames:
        if not frame.get("render_matches"):
            continue
        px, owner, sprites = compose(frame, 4, occluders=motion != "contact")
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
        seen.setdefault(key, []).append(
            n if len(caps) == 1 else {"capture": cap_index, "frame": n}
        )
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
        if raw in protected:
            if protected[raw] != bytes(output):
                raise ValueError(
                    "movement mask would recolour a protected fallback tile"
                )
        else:
            records[raw] = bytes(output)
    footer = (
        compatible_palettes(blob, json.loads(palettes.read_text()), protected.values())
        if palettes
        else blob[-64:]
    )
    result = pack_full_table(list(records.items()), footer)
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
    if palettes:
        report["palettes_sha256"] = hashlib.sha256(palettes.read_bytes()).hexdigest()
    if preserve_fallback_from:
        report["protected_fallback_sources"] = len(protected)
        report["fallback_reference_sha256"] = [
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in preserve_fallback_from
        ]
    if len(paths) > 1:
        report["captures"] = [
            {
                "path": str(p),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "protocol": c["input_protocol"],
            }
            for p, c in zip(paths, caps)
        ]
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["capture", "baseline", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument(
        "--motion",
        choices=[
            "walk",
            "dash",
            "attack",
            "low-air",
            "defence",
            "damage",
            "contact",
            "ball",
            "zangief-idle",
            "zangief-walk",
            "zangief-basic",
        ],
        default="walk",
    )
    p.add_argument(
        "--palettes",
        type=Path,
        help="Update only unused footer swatches from the fighter catalogue",
    )
    p.add_argument("--additional-capture", type=Path, action="append", default=[])
    p.add_argument(
        "--preserve-fallback-from",
        type=Path,
        action="append",
        help="Protect fallback tiles in a CTB3 table saved before compaction",
    )
    args = p.parse_args()
    print(
        json.dumps(
            build(
                args.capture,
                args.baseline,
                args.out,
                args.motion,
                args.additional_capture,
                args.palettes,
                args.preserve_fallback_from,
            )
        )
    )
