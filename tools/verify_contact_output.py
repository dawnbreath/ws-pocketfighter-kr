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
from segment_frames import compose, cyclic_crop
from seed_recipe import crop_md5
from regress import digest
import contact_colours
import ball_colours
import defence_colours
import zangief_idle_colours
import zangief_walk_colours
import zangief_basic_colours
from types import ModuleType


def source_region(
    frame: dict, wrapped: bool = False
) -> (
    tuple[np.ndarray, np.ndarray, list[dict], np.ndarray, tuple[int, int, int, int]]
    | None
):
    viewport = (256, 256) if wrapped else (224, 144)
    full, owners, sprites = compose(frame, 4, occluders=False, viewport=viewport)
    if not full.any():
        return None
    if wrapped:
        source, box = cyclic_crop(full)
    else:
        _, source = crop_md5(full)
        yy, xx = np.nonzero(full)
        box = (int(xx.min()), int(yy.min()), source.shape[1], source.shape[0])
    return full, owners, sprites, source, box


def resolve_recipe(
    source: np.ndarray, recipes: ModuleType, orientation: str
) -> tuple[str, np.ndarray, bool] | None:
    # Reflection is exact source matching, never a nearest-pose transfer.
    choices = (False, True) if orientation == "either" else (orientation == "mirror",)
    for mirrored in choices:
        canonical = np.fliplr(source) if mirrored else source
        key, _ = crop_md5(canonical)
        if key in recipes.POSES:
            expected = recipes.author(canonical)
            return key, np.fliplr(expected) if mirrored else expected, mirrored
    return None


def verify_frame(
    frame: dict,
    screenshot: np.ndarray,
    colors: np.ndarray,
    recipes: ModuleType = contact_colours,
    *,
    wrapped: bool = False,
    orientation: str = "source",
) -> dict | None:
    region = source_region(frame, wrapped)
    if region is None:
        return None
    full, owners, sprites, source, box = region
    if max(source.shape) > 255:
        return None  # Cannot be an exact recipe with the existing shape-byte hash.
    recipe = resolve_recipe(source, recipes, orientation)
    if recipe is None:
        return None
    key, expected, mirrored = recipe
    if frame.get("colour_vram_base") != 0x7000:
        raise ValueError("requires explicit fighter colour-buffer read")
    buffer = bytes.fromhex(frame["colour_vram"])
    if len(buffer) != 4096:
        raise ValueError("short fighter colour-buffer read")
    indices = np.zeros(full.shape, dtype=np.uint8)
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
                if (
                    x < full.shape[1]
                    and y < full.shape[0]
                    and owners[y, x] == s["rank"]
                ):
                    indices[y, x] = value
    x, y, w, h = box
    grid = np.ix_((y + np.arange(h)) & 255, (x + np.arange(w)) & 255)
    if not np.array_equal(indices[grid][source > 0], expected[source > 0]):
        raise ValueError("runtime buffer does not match authored contact drawing")
    visible, _, _ = compose(frame, 4)
    mask = visible > 0
    if not mask.any() or not np.array_equal(
        screenshot[mask], colors[indices[:144, :224][mask]]
    ):
        raise ValueError("visible screenshot does not match runtime contact output")
    return {
        "key": key,
        "mirrored": mirrored,
        "buffer_pixels": int((source > 0).sum()),
        "visible_pixels": int(mask.sum()),
        "hidden_pixels": int((full > 0).sum() - mask.sum()),
        "offscreen_pixels": int((full > 0).sum() - (full[:144, :224] > 0).sum()),
        "occluded_pixels": int((full[:144, :224] > 0).sum() - mask.sum()),
        "box": [x, y, w, h],
    }


def save_gallery(
    panes: dict[str, tuple[Image.Image, Image.Image]],
    poses: tuple[str, ...],
    path: Path,
) -> None:
    """Size cells from captured drawings: a wide kick must not cover its pair."""
    width = max((im.width for pair in panes.values() for im in pair), default=48)
    height = max((im.height for pair in panes.values() for im in pair), default=48)
    cell_width, cell_height = max(300, width * 6 + 24), height * 6 + 50
    sheet = Image.new(
        "RGB", (cell_width * 4, ((len(poses) + 1) // 2) * cell_height), "#333333"
    )
    draw = ImageDraw.Draw(sheet)
    for key, pair in panes.items():
        i = poses.index(key)
        x, y = i % 2 * cell_width * 2, i // 2 * cell_height
        for n, im in enumerate(pair):
            sheet.paste(
                im.resize((im.width * 6, im.height * 6), Image.Resampling.NEAREST),
                (x + n * cell_width, y + 40),
            )
        draw.text((x, y), key[:8] + " actual screenshot", fill="white")
        draw.text((x + cell_width, y), "verified RAM reconstruction", fill="white")
    sheet.save(path)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("out", type=Path)
    p.add_argument("captures", type=Path, nargs="+")
    p.add_argument(
        "--palettes",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/palettes/wrist-fixes.json",
    )
    p.add_argument(
        "--family",
        choices=[
            "contact",
            "ball",
            "defence",
            "zangief-idle",
            "zangief-walk",
            "zangief-basic",
        ],
        default="contact",
    )
    p.add_argument("--wrapped-source", action="store_true")
    p.add_argument(
        "--orientation", choices=["source", "mirror", "either"], default="source"
    )
    args = p.parse_args()
    recipes, character = {
        "ball": (ball_colours, "chunli"),
        "contact": (contact_colours, "chunli"),
        "defence": (defence_colours, "chunli"),
        "zangief-idle": (zangief_idle_colours, "zangief"),
        "zangief-walk": (zangief_walk_colours, "zangief"),
        "zangief-basic": (zangief_basic_colours, "zangief"),
    }[args.family]
    args.out.mkdir(parents=True, exist_ok=False)
    palette_name = "ZANGIEF" if character == "zangief" else "CHUN-LI"
    pal = json.loads(args.palettes.read_text())["fighters"][palette_name]
    colors = np.array([[int(n, 16) * 17 for n in word] for word in pal], dtype=np.uint8)
    seen = {}
    provenance = []
    excluded = []
    panes = {}
    for root in args.captures:
        cap = json.loads((root / "capture.json").read_text())
        if (cap["character"], cap["side"], cap["status"], cap["stop"]["stopped"]) != (
            character,
            4,
            "CAPTURED",
            True,
        ):
            raise ValueError(f"requires completed {character} capture and stop receipt")
        provenance.append(
            {
                "path": str(root),
                "capture_sha256": digest(root / "capture.json"),
                "rom_sha256": cap["rom_sha256"],
                "state_sha256": cap["state_sha256"],
                "stop": True,
            }
        )
        direction_ticks: dict[str, int] = {}
        for n, f in enumerate(cap["frames"]):
            tick = direction_ticks.get(f["direction"], 0)
            direction_ticks[f["direction"]] = tick + 1
            screenshot_name = f["direction"] + f"-{tick:02}.png"
            if not f.get("render_matches"):
                excluded.append(
                    {
                        "capture": str(root),
                        "frame": n,
                        "reason": "source/screenshot incoherent in capture",
                    }
                )
                continue
            shot = Image.open(root / screenshot_name).convert("RGB")
            result = verify_frame(
                f,
                np.array(shot),
                colors,
                recipes,
                wrapped=args.wrapped_source,
                orientation=args.orientation,
            )
            if result is None:
                continue
            key = result["key"]
            result["capture"] = str(root)
            result["frame"] = n
            result["screenshot"] = screenshot_name
            if key not in seen:
                x, y, w, h = result["box"]
                # Grey denotes coordinates outside the LCD, never generated pixels.
                screen = np.full((256, 256, 3), 96, dtype=np.uint8)
                screen[:144, :224] = np.array(shot)
                grid = np.ix_((y + np.arange(h)) & 255, (x + np.arange(w)) & 255)
                source = source_region(f, args.wrapped_source)[3]
                expected = resolve_recipe(source, recipes, args.orientation)[1]
                panes[key] = (
                    Image.fromarray(screen[grid]),
                    Image.fromarray(colors[expected]),
                )
            seen.setdefault(key, []).append(result)
    if len({c["rom_sha256"] for c in provenance}) != 1:
        raise ValueError("contact verification requires one ROM build")
    r = {
        "excluded": excluded,
        "family": args.family,
        "wrapped_source": args.wrapped_source,
        "orientation": args.orientation,
        "poses": seen,
        "missing": sorted(set(recipes.POSES) - set(seen)),
        "captures": provenance,
        "scope": "hidden pixels: actual RAM; visible pixels: exact screenshot; visibility measured per sample; reconstructions are not screenshots",
    }
    (args.out / "report.json").write_text(json.dumps(r, indent=2) + "\n")
    save_gallery(panes, recipes.POSES, args.out / "detail.png")
    print(json.dumps(r, indent=2))
    if r["missing"]:
        raise SystemExit("required contact drawing missing")


if __name__ == "__main__":
    main()
