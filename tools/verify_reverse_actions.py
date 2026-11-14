"""Verify mirrored standing/walking drawings against actual screenshots."""

from pathlib import Path
import argparse
import json, sys, numpy as np
from PIL import Image, ImageDraw

sys.path[:0] = [
    str(Path(__file__).resolve().parent),
    str(Path(__file__).resolve().parent / "mock"),
]
from segment_frames import compose
from capture_walk import match_render
from regress import digest
from seed_recipe import crop_md5
import attack_colours, walk_colours

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("standing", type=Path)
parser.add_argument("walk", type=Path)
parser.add_argument("out", type=Path)
parser.add_argument(
    "--palettes",
    type=Path,
    default=Path(__file__).resolve().parents[1] / "data/palettes/wrist-fixes.json",
)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=False)
pal = json.loads(args.palettes.read_text())["fighters"]["CHUN-LI"]
colors = np.array([[int(n, 16) * 17 for n in p] for p in pal], dtype=np.uint8)
report = {}
sheet = Image.new("RGB", (5 * 300, 2 * 300), "#333333")
draw = ImageDraw.Draw(sheet)
slot = 0
for family, mod in [("standing", attack_colours), ("walk", walk_colours)]:
    root = getattr(args, family)
    cap = json.loads((root / "capture.json").read_text())
    seen = {}
    others = {}
    if (cap["character"], cap["side"], cap["status"], cap["stop"]["stopped"]) != (
        "chunli",
        4,
        "CAPTURED",
        True,
    ):
        raise ValueError("requires completed P1 Chun-Li capture and stop receipt")
    per = sum(f["direction"] == cap["frames"][0]["direction"] for f in cap["frames"])
    for n, f in enumerate(cap["frames"]):
        px, owner, sprites = compose(f, 4)
        key, source = crop_md5(px)
        mirrored = np.fliplr(source)
        reversekey, _ = crop_md5(mirrored)
        if reversekey not in mod.POSES:
            others.setdefault(key, []).append(n)
            continue
        xx = np.nonzero(px)[1]
        yy = np.nonzero(px)[0]
        x = int(xx.min())
        y = int(yy.min())
        h, w = source.shape
        name = f["direction"] + f"-{n%per:02}.png"
        im = Image.open(root / name).convert("RGB")
        expected = colors[np.fliplr(mod.author(mirrored))]
        plane = np.zeros((144, 224, 3), dtype=np.uint8)
        plane[y : y + h, x : x + w] = expected
        valid, count, offset = match_render(
            plane, np.array(im), px > 0, family == "walk"
        )
        if not valid:
            continue
        x += offset[0]
        y += offset[1]
        actual = np.array(im)[y : y + h, x : x + w]
        assert np.array_equal(actual[source > 0], expected[source > 0])
        if reversekey not in seen:
            seen[reversekey] = {"pixels": int((source > 0).sum()), "samples": []}
            sheet.paste(
                im.crop((x, y, x + w, y + h)).resize(
                    (w * 5, h * 5), Image.Resampling.NEAREST
                ),
                (slot % 5 * 300, slot // 5 * 300 + 25),
            )
            draw.text(
                (slot % 5 * 300, slot // 5 * 300),
                family + " " + reversekey[:8],
                fill="white",
            )
            slot += 1
        seen[reversekey]["samples"].append(
            {
                "index": n,
                "registration": offset,
                "capture_render_matches": f["render_matches"],
            }
        )
    report[family] = {
        "seen": seen,
        "missing": sorted(set(mod.POSES) - set(seen)),
        "other_drawings": others,
        "coherent_samples": sum(f["render_matches"] for f in cap["frames"]),
        "total_samples": len(cap["frames"]),
        "stop": cap["stop"]["stopped"],
        "capture_sha256": digest(root / "capture.json"),
        "rom_sha256": cap["rom_sha256"],
        "state_sha256": cap["state_sha256"],
        "protocol": cap["input_protocol"],
    }
(args.out / "report.json").write_text(json.dumps(report, indent=2))
sheet.save(args.out / "detail.png")
print(json.dumps(report, indent=2))

if any(r["missing"] for r in report.values()):
    raise SystemExit("Required mirrored drawings missing; see report")
