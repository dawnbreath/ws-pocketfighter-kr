"""Check occluded contact draws: actual 4bpp RAM plus visible screenshot pixels.

RAM proof covers hidden output; it is not a full unoccluded screenshot proof.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw

sys.path[:0] = [
    str(Path(__file__).resolve().parent),
    str(Path(__file__).resolve().parent / "mock"),
]
from segment_frames import compose
from seed_recipe import crop_md5
from regress import digest
from contact_colours import POSES, author


def verify_frame(
    frame: dict, screenshot: np.ndarray, colors: np.ndarray
) -> dict | None:
    full, owners, sprites = compose(frame, 4, occluders=False)
    key, source = crop_md5(full)
    if key not in POSES:
        return None
    if frame.get("colour_vram_base") != 0x7000:
        raise ValueError("requires explicit fighter colour-buffer read")
    buffer = bytes.fromhex(frame["colour_vram"])
    if len(buffer) != 4096:
        raise ValueError("short fighter colour-buffer read")
    indices = np.zeros((144, 224), dtype=np.uint8)
    for s in sprites:
        if s["side"] != 4:
            continue
        slot = s["word"] & 511
        if not 384 <= slot < 512:
            raise ValueError("contact source outside fighter mirror")
        raw = buffer[(slot - 384) * 32 : (slot - 383) * 32]
        for yy in range(8):
            for xx in range(8):
                value = sum(((raw[yy * 4 + p] >> (7 - xx)) & 1) << p for p in range(4))
                if (value == 0) != (s["pixels"][yy, xx] == 0):
                    raise ValueError("runtime transparency mismatch")
                x = (s["x"] + (7 - xx if s["word"] & 0x4000 else xx)) & 255
                y = (s["y"] + (7 - yy if s["word"] & 0x8000 else yy)) & 255
                if x < 224 and y < 144 and owners[y, x] == s["rank"]:
                    indices[y, x] = value
    yy, xx = np.nonzero(full)
    x = int(xx.min())
    y = int(yy.min())
    h, w = source.shape
    expected = author(source)
    if not np.array_equal(
        indices[y : y + h, x : x + w][source > 0], expected[source > 0]
    ):
        raise ValueError("runtime buffer does not match authored contact drawing")
    visible, _, _ = compose(frame, 4)
    mask = visible > 0
    if not mask.any() or not np.array_equal(screenshot[mask], colors[indices[mask]]):
        raise ValueError("visible screenshot does not match runtime contact output")
    return {
        "key": key,
        "buffer_pixels": int((source > 0).sum()),
        "visible_pixels": int(mask.sum()),
        "hidden_pixels": int((full > 0).sum() - mask.sum()),
        "box": [x, y, w, h],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("out", type=Path)
    p.add_argument("captures", type=Path, nargs="+")
    p.add_argument(
        "--palettes",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/palettes/wrist-fixes.json",
    )
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    pal = json.loads(args.palettes.read_text())["fighters"]["CHUN-LI"]
    colors = np.array([[int(n, 16) * 17 for n in word] for word in pal], dtype=np.uint8)
    seen = {}
    provenance = []
    sheet = Image.new("RGB", (1200, 700), "#333333")
    draw = ImageDraw.Draw(sheet)
    for root in args.captures:
        cap = json.loads((root / "capture.json").read_text())
        if (cap["character"], cap["side"], cap["status"], cap["stop"]["stopped"]) != (
            "chunli",
            4,
            "CAPTURED",
            True,
        ):
            raise ValueError("requires completed Chun-Li capture and stop receipt")
        provenance.append(
            {
                "path": str(root),
                "capture_sha256": digest(root / "capture.json"),
                "rom_sha256": cap["rom_sha256"],
                "state_sha256": cap["state_sha256"],
                "stop": True,
            }
        )
        for n, f in enumerate(cap["frames"]):
            shot = Image.open(root / (f["direction"] + f"-{n:02}.png")).convert("RGB")
            result = verify_frame(f, np.array(shot), colors)
            if result is None:
                continue
            key = result["key"]
            result["capture"] = str(root)
            result["frame"] = n
            if key not in seen:
                i = POSES.index(key)
                sx = i % 2 * 600
                sy = i // 2 * 350
                x, y, w, h = result["box"]
                sheet.paste(
                    shot.crop((x, y, x + w, y + h)).resize(
                        (w * 6, h * 6), Image.Resampling.NEAREST
                    ),
                    (sx, sy + 40),
                )
                _, source = crop_md5(compose(f, 4, occluders=False)[0])
                sheet.paste(
                    Image.fromarray(colors[author(source)]).resize(
                        (w * 6, h * 6), Image.Resampling.NEAREST
                    ),
                    (sx + 300, sy + 40),
                )
                draw.text((sx, sy), key[:8] + " screenshot (occluded)", fill="white")
                draw.text((sx + 300, sy), "verified RAM reconstruction", fill="white")
            seen.setdefault(key, []).append(result)
    if len({c["rom_sha256"] for c in provenance}) != 1:
        raise ValueError("contact verification requires one ROM build")
    r = {
        "poses": seen,
        "missing": sorted(set(POSES) - set(seen)),
        "captures": provenance,
        "scope": "hidden pixels: actual RAM; visible pixels: exact screenshot; no unoccluded-screen claim",
    }
    (args.out / "report.json").write_text(json.dumps(r, indent=2) + "\n")
    sheet.save(args.out / "detail.png")
    print(json.dumps(r, indent=2))
    if r["missing"]:
        raise SystemExit("required contact drawing missing")


if __name__ == "__main__":
    main()
