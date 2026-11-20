"""Verify registered roster labels against native buffers and screenshots."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace, ModuleType
import numpy as np
from PIL import Image
from verify_contact_output import verify_frame, save_gallery, source_region
from regress import digest
from segment_frames import active_sprites
from colour_layout import CONTEXT_MAP_BASE, CONTEXT_MAP_SIZE
import roster_colours


def check(
    labels: Path,
    capture_root: Path,
    palettes: Path,
    out: Path,
    additional_captures: list[Path] | None = None,
    family_module: ModuleType = roster_colours,
    required_context: int | None = None,
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
        for name, recipe in family_module.RECIPES.items()
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
            # Roster labels are authored with opponent occlusion retained.
            # Contact families default to isolated P1, including hidden pixels.
            result = verify_frame(f, shot, colors, family, visible_source=True)
            if result is None:
                continue
            if required_context is not None:
                context_map = bytes.fromhex(f.get("context_map", ""))
                if (
                    f.get("context_map_base") != CONTEXT_MAP_BASE
                    or len(context_map) != CONTEXT_MAP_SIZE
                ):
                    raise ValueError("requires actual 128-byte context-map read")
                for sprite in active_sprites(f):
                    if sprite["side"] != 4:
                        continue
                    slot = (sprite["word"] & 511) - 384
                    if (
                        not 0 <= slot < 128
                        or context_map[slot] & 15 != required_context
                    ):
                        raise ValueError("runtime P1 ownership context mismatch")
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
                source = source_region(f, visible_source=True)[3]
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
        "source_visibility": "visible P1; opponent occlusion retained as in roster export",
        "missing": missing,
        "poses": seen,
        "excluded": excluded,
        "scope": "exact source-bound labels, actual RAM and zero-offset screenshot pixels; art approval separate",
    }
    if required_context is not None:
        r["required_context"] = required_context
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
    p.add_argument(
        "--family",
        choices=["basics", "motions", "gouki-context", "low-air"],
        default="basics",
    )
    p.add_argument("--require-context", type=int)
    a = p.parse_args()
    family = roster_colours
    if a.family == "motions":
        import roster_motion_colours as family
    elif a.family == "gouki-context":
        import gouki_context_colours as family
    elif a.family == "low-air":
        import roster_low_air_colours as family
    r = check(
        a.labels,
        a.capture_root,
        a.palettes,
        a.out,
        a.additional_capture,
        family,
        a.require_context,
    )
    if r["missing"]:
        raise SystemExit("required roster drawings missing")
