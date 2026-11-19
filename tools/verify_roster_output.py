"""Verify registered roster labels against native buffers and screenshots."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
from verify_contact_output import verify_frame, save_gallery, source_region
from regress import digest
import roster_colours


def check(
    labels: Path,
    capture_root: Path,
    palettes: Path,
    out: Path,
    additional_captures: list[Path] | None = None,
) -> dict:
    report = json.loads((capture_root / "report.json").read_text())
    if report["status"] != "CAPTURED" or not report["stop"]["stopped"]:
        raise ValueError("native capture incomplete or stop unconfirmed")
    config = json.loads(palettes.read_text())
    recipes = {}
    seen = {}
    excluded = []
    panes = {}
    for name in config["fighters"]:
        data = {}
        for path in labels.glob(name + "-*.npz"):
            a = np.load(path)
            source = a["source"]
            indices = a["indices"]
            key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
            if not np.array_equal(source > 0, indices > 0) or indices.max() > 15:
                raise ValueError("invalid source-bound label")
            data[key] = (source, indices)
        if data:
            recipes[name] = data
    expected_keys = {
        name + "-" + key
        for name, recipe in roster_colours.RECIPES.items()
        for key in recipe["poses"]
    }
    actual_keys = {name + "-" + key for name, data in recipes.items() for key in data}
    if actual_keys != expected_keys:
        raise ValueError("label files do not cover the registered roster drawings")
    captures = [
        (root, json.loads((root / "capture.json").read_text()))
        for root in sorted(capture_root.glob("route-*"))
    ]
    for root in additional_captures or []:
        cap = json.loads((root / "capture.json").read_text())
        if cap["status"] != "CAPTURED" or not cap["stop"]["stopped"]:
            raise ValueError("additional capture incomplete or stop unconfirmed")
        captures.append((root, cap))
    for root, cap in captures:
        name = {"chunli": "CHUN-LI", "leilei": "LEI-LEI"}.get(
            cap["character"], cap["character"].upper()
        )
        if name not in recipes:
            continue
        if cap.get("ROM_SHA256", cap.get("rom_sha256")) != report["ROM_SHA256"]:
            raise ValueError("mixed ROM captures")
        data = recipes[name]

        def author(source):
            key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
            expected, indices = data[key]
            if not np.array_equal(source, expected):
                raise ValueError("source differs from label")
            return indices

        family = SimpleNamespace(POSES=tuple(data), author=author)
        colors = np.array(
            [[int(n, 16) * 17 for n in w] for w in config["fighters"][name]],
            dtype=np.uint8,
        )
        ticks = {}
        for n, f in enumerate(cap["frames"]):
            direction = f["direction"]
            tick = ticks.get(direction, 0)
            ticks[direction] = tick + 1
            if not f["render_matches"] or f["render_offset"] != [0, 0]:
                excluded.append(
                    {
                        "character": name,
                        "capture": str(root),
                        "frame": n,
                        "reason": "incoherent source or registration offset",
                    }
                )
                continue
            shot = np.array(
                Image.open(root / f"{direction}-{tick:02}.png").convert("RGB")
            )
            result = verify_frame(f, shot, colors, family)
            if result is None:
                continue
            key = name + "-" + result["key"]
            result.update(
                character=name,
                capture=str(root),
                frame=n,
                phase=f.get("source_phase", "followup"),
                duration=f["requested_frames"],
            )
            seen.setdefault(key, []).append(result)
            if key not in panes:
                x, y, w, h = result["box"]
                source = source_region(f)[3]
                panes[key] = (
                    Image.fromarray(shot[y : y + h, x : x + w]),
                    Image.fromarray(colors[author(source)]),
                )
    required = tuple(name + "-" + key for name, data in recipes.items() for key in data)
    missing = sorted(set(required) - set(seen))
    r = {
        "ROM_SHA256": report["ROM_SHA256"],
        "capture_sha256": digest(capture_root / "report.json"),
        "capture_files": [
            {"path": str(root), "sha256": digest(root / "capture.json")}
            for root, _ in captures
        ],
        "drawings": len(seen),
        "samples": sum(map(len, seen.values())),
        "representative_pixels": sum(
            rows[0]["buffer_pixels"] for rows in seen.values()
        ),
        "missing": missing,
        "poses": seen,
        "excluded": excluded,
        "scope": "exact source-bound labels, actual RAM and zero-offset screenshot pixels; art approval separate",
    }
    out.mkdir(parents=True, exist_ok=False)
    (out / "report.json").write_text(json.dumps(r, indent=2))
    save_gallery(panes, required, out / "detail.png")
    print({k: v for k, v in r.items() if k not in ["poses", "excluded"]})
    return r


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["labels", "capture_root", "palettes", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument("--additional-capture", type=Path, action="append")
    a = p.parse_args()
    r = check(a.labels, a.capture_root, a.palettes, a.out, a.additional_capture)
    if r["missing"]:
        raise SystemExit("required roster drawings missing")
