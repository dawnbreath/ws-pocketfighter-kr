"""Propose region masks from local mono WS captures; never marks them engine-ready."""

from __future__ import annotations
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from wsgfx import tile2
from component_marks import apply_marks, load_marks

LABELS = {
    "unknown": -1,
    "transparent": 0,
    "outline": 1,
    "skin": 2,
    "cloth": 3,
    "boots": 4,
    "hair": 5,
    "accent": 6,
    "trousers": 7,
    "white_trim": 8,
    "gloves": 9,
    "belt": 10,
    "cloth_outline": 11,
    "trunks": 12,
    "wristband": 13,
}
COLORS = [
    (210, 210, 210),
    (20, 20, 20),
    (240, 185, 130),
    (60, 110, 220),
    (235, 235, 245),
    (90, 55, 30),
    (220, 45, 45),
    (135, 90, 55),
    (255, 255, 255),
    (240, 150, 40),
    (45, 35, 30),
    (30, 55, 160),
    (215, 35, 45),
    (225, 75, 55),
]


def tile(raw: bytes) -> np.ndarray:
    if len(raw) != 16:
        raise ValueError("2bpp tile requires 16 bytes")
    return np.array(tile2(raw, 0), dtype=np.int8)


def active_sprites(frame: dict) -> list[dict]:
    oam = bytes.fromhex(frame["oam"])
    vram = bytes.fromhex(frame["vram"])
    start, count = frame["sprite_start"], frame["sprite_count"]
    if (
        len(oam) != 512
        or len(vram) != 8192
        or not 0 <= start < 128
        or not 0 <= count <= 128
    ):
        raise ValueError("invalid capture ranges")
    sprites = []
    for rank in range(count):
        slot = (start + rank) & 127
        entry = oam[slot * 4 : slot * 4 + 4]
        word = int.from_bytes(entry[:2], "little")
        raw = vram[(word & 511) * 16 : (word & 511) * 16 + 16]
        sprites.append(
            {
                "rank": rank,
                "slot": slot,
                "word": word,
                "side": (word >> 9) & 7,
                "x": entry[3],
                "y": entry[2],
                "raw": raw,
                "pixels": tile(raw),
                "hash": hashlib.sha256(raw).hexdigest(),
            }
        )
    return sprites


def compose(frame: dict, side: int) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    sprites = active_sprites(frame)
    # WS OAM priority: earlier active entry wins. Coordinates wrap modulo 256;
    # clip to LCD after wrapping, preserving offscreen/overlapped pixels as unobserved.
    pixels = np.zeros((144, 224), dtype=np.int8)
    owner = np.full((144, 224), -1, dtype=np.int16)
    for sprite in sprites:
        for sy in range(8):
            for sx in range(8):
                x = (sprite["x"] + (7 - sx if sprite["word"] & 0x4000 else sx)) & 255
                y = (sprite["y"] + (7 - sy if sprite["word"] & 0x8000 else sy)) & 255
                value = int(sprite["pixels"][sy, sx])
                if x < 224 and y < 144 and value and owner[y, x] < 0:
                    pixels[y, x] = value
                    owner[y, x] = sprite["rank"]
    selected = {s["rank"] for s in sprites if s["side"] == side}
    mask = np.isin(owner, list(selected))
    return np.where(mask, pixels, 0), np.where(mask, owner, -1), sprites


def components(pixels: np.ndarray) -> tuple[np.ndarray, int]:
    height, width = pixels.shape
    labels = np.zeros((height, width), dtype=np.int32)
    count = 0
    for y, x in zip(*np.nonzero((pixels == 1) | (pixels == 2))):
        if labels[y, x]:
            continue
        count += 1
        labels[y, x] = count
        pending = deque([(y, x)])
        while pending:
            cy, cx = pending.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if (
                    0 <= ny < height
                    and 0 <= nx < width
                    and not labels[ny, nx]
                    and pixels[ny, nx] in (1, 2)
                ):
                    labels[ny, nx] = count
                    pending.append((ny, nx))
    return labels, count


def classify(
    pixels: np.ndarray, rules: dict, marks: dict | None = None
) -> tuple[np.ndarray, int]:
    result = np.full(pixels.shape, -1, dtype=np.int8)
    result[pixels == 0] = 0
    result[pixels == 3] = 1
    yy, xx = np.nonzero(pixels)
    if not len(xx):
        return (
            apply_marks(
                pixels, result, np.zeros(pixels.shape, dtype=int), marks, LABELS
            ),
            0,
        )
    x0, x1, y0, y1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
    labs, count = components(pixels)
    # A clipped silhouette cannot use whole-body proportions safely.
    if x0 == 0 or x1 == 224 or y0 == 0 or y1 == 144:
        return apply_marks(pixels, result, labs, marks, LABELS), count
    for number in range(1, count + 1):
        ys, xs = np.nonzero(labs == number)
        cx = (float(xs.mean()) - x0) / (x1 - x0)
        cy = (float(ys.mean()) - y0) / (y1 - y0)
        span = (int(ys.max()) - int(ys.min()) + 1) / (y1 - y0)
        if span > rules["max_component_height"]:
            continue
        choices = set()
        for rule in rules["regions"]:
            left, top, right, bottom = rule["center_box"]
            if left <= cx < right and top <= cy < bottom:
                choices.add(LABELS[rule["label"]])
        if len(choices) == 1:
            result[labs == number] = choices.pop()
    return apply_marks(pixels, result, labs, marks, LABELS), count


def observations(
    frame: dict, side: int, rules: dict, marks: dict | None = None
) -> tuple[dict, np.ndarray, int, int]:
    pixels, owner, sprites = compose(frame, side)
    labels, n = classify(pixels, rules, marks)
    votes = defaultdict(lambda: [set() for _ in range(64)])
    for sprite in sprites:
        if sprite["side"] != side:
            continue
        cells = votes[sprite["hash"]]
        for sy in range(8):
            for sx in range(8):
                if sprite["pixels"][sy, sx] == 0:
                    cells[sy * 8 + sx].add(0)
                    continue
                x = (sprite["x"] + (7 - sx if sprite["word"] & 0x4000 else sx)) & 255
                y = (sprite["y"] + (7 - sy if sprite["word"] & 0x8000 else sy)) & 255
                if (
                    x < 224
                    and y < 144
                    and owner[y, x] == sprite["rank"]
                    and labels[y, x] >= 0
                ):
                    cells[sy * 8 + sx].add(int(labels[y, x]))
    return votes, labels, n, sum(s["side"] == side for s in sprites)


def merge_votes(
    target: dict, source: dict, evidence: dict | None = None, frame: int | None = None
) -> None:
    if evidence is not None and frame is None:
        raise ValueError("evidence requires a frame index")
    for key, cells in source.items():
        if key not in target:
            target[key] = [set() for _ in range(64)]
        if evidence is not None and key not in evidence:
            evidence[key] = [{} for _ in range(64)]
        for pixel, (dst, src) in enumerate(zip(target[key], cells)):
            dst.update(src)
            if evidence is not None:
                for label in sorted(src):
                    record = evidence[key][pixel].setdefault(
                        label, {"first_frame": frame, "sample_count": 0}
                    )
                    record["sample_count"] += 1


def consensus(cells: list[set[int]]) -> list[int]:
    return [next(iter(values)) if len(values) == 1 else -1 for values in cells]


def preview(labels: np.ndarray) -> Image.Image:
    rgb = np.full((*labels.shape, 3), (230, 70, 200), dtype=np.uint8)
    for index, color in enumerate(COLORS):
        rgb[labels == index] = color
    return Image.fromarray(rgb)


def process(
    capture: Path, rule_path: Path, out: Path, marks_path: Path | None = None
) -> dict:
    cap = json.loads(capture.read_text())
    rules = json.loads(rule_path.read_text())
    if cap.get("status") != "CAPTURED" or cap.get("schema") != 1:
        raise ValueError("need complete schema-1 capture")
    if cap["character"] != rules["character"]:
        raise ValueError("character/rules mismatch")
    marks = load_marks(marks_path, capture, cap)
    out.mkdir(parents=True, exist_ok=False)
    votes = {}
    evidence = {}
    counts = []
    thumbnails = []
    for index, frame in enumerate(cap["frames"]):
        local, labels, n, sprites = observations(
            frame, cap["side"], rules, marks.get("frames", {}).get(str(frame["index"]))
        )
        merge_votes(votes, local, evidence, frame["index"])
        counts.append(
            {
                "frame": frame["index"],
                "sprites": sprites,
                "components": n,
                "tile_hashes": len(local),
            }
        )
        if index % 8 == 0 and len(thumbnails) < 64:
            im = preview(labels)
            draw = ImageDraw.Draw(im)
            draw.text((2, 2), str(frame["index"]), fill="black")
            thumbnails.append(im)
    if thumbnails:
        sheet = Image.new(
            "RGB", (224 * 4, 144 * ((len(thumbnails) + 3) // 4)), (210, 210, 210)
        )
        for i, im in enumerate(thumbnails):
            sheet.paste(im, ((i % 4) * 224, (i // 4) * 144))
        sheet.save(out / "proposals.png")
    table = {
        key: {
            "mask": consensus(cells),
            "conflicts": [i for i, v in enumerate(cells) if len(v) > 1],
            "unobserved": [i for i, v in enumerate(cells) if not v],
            "conflict_evidence": {
                str(i): evidence[key][i]
                for i, values in enumerate(cells)
                if len(values) > 1
            },
        }
        for key, cells in sorted(votes.items())
    }
    report = {
        "schema": 1,
        "character": cap["character"],
        "rom_sha256": cap["rom_sha256"],
        "capture_sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
        "rules_sha256": hashlib.sha256(rule_path.read_bytes()).hexdigest(),
        "marks_sha256": (
            hashlib.sha256(marks_path.read_bytes()).hexdigest() if marks_path else None
        ),
        "reviewer": marks.get("reviewer"),
        "marked_frames": sum(
            bool(r["marks"]) for r in marks.get("frames", {}).values()
        ),
        "engine_ready": False,
        "status": "UNREVIEWED_GEOMETRIC_PROPOSALS",
        "limitations": [
            "not all animations",
            "palette-side grouping can include fighter effects",
            "identity requires screenshot review",
            "outline assumes shade 3",
            "geometry cannot reliably separate every pose",
            "no BG/window/scanline-limit rendering simulation",
            "tile content is not a ROM address; conflicts stay unknown",
        ],
        "labels": LABELS,
        "sample_count": len(counts),
        "unique_tile_hashes": len(table),
        "empty_samples": sum(c["sprites"] == 0 for c in counts),
        "conflicting_tiles": sum(bool(t["conflicts"]) for t in table.values()),
        "conflicting_pixels": sum(len(t["conflicts"]) for t in table.values()),
        "unobserved_pixels": sum(len(t["unobserved"]) for t in table.values()),
        "frames": counts,
        "tiles": table,
    }
    (out / "masks.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("rules", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--marks", type=Path)
    args = parser.parse_args()
    r = process(args.capture, args.rules, args.out, args.marks)
    print(
        json.dumps(
            {
                k: r[k]
                for k in (
                    "character",
                    "sample_count",
                    "unique_tile_hashes",
                    "empty_samples",
                    "conflicting_tiles",
                    "conflicting_pixels",
                    "unobserved_pixels",
                    "engine_ready",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
