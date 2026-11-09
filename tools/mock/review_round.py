"""Reproduce an offline seed/correction round with pose-disjoint spot evaluation.

All images, annotations, predictions and reports are local game-derived outputs.
Annotations use crop MD5 and explicit [x, y, class] points in train/eval splits.
Spot error rates do not measure full-pose accuracy or authorize ROM export.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import pickle

import numpy as np
from PIL import Image, ImageDraw
from propagate_proto import poses, predict_pose, train
from seed_recipe import RECIPES, classify, crop_md5
from segment_frames import compose

COLORS = {
    "skin": (240, 185, 130),
    "hair": (90, 55, 30),
    "blue": (60, 110, 220),
    "brown": (135, 90, 55),
    "white": (250, 250, 255),
    "silver": (190, 190, 210),
    "red": (215, 35, 45),
    "pants": (35, 30, 30),
}


# Source-only spot recipe; exact pose hash prevents coordinate reuse on other art.
REFERENCE_SPOTS = {
    "chunli": [
        ("04e879c18591883671038dd65079cefc", "train", "white", (26, 9, 37, 16)),
        ("dd118167e6a0c76d0c92ffde3a963831", "eval", "white", (9, 43, 14, 49)),
    ],
    "zangief": [
        ("350910abbe1ad26a1f76dd971e23ac97", "train", "red", (5, 3, 12, 12)),
        ("edd4fba9cfbfacd21fb470890470a3e4", "eval", "red", (1, 28, 10, 37)),
    ],
}


def reference_spots(pose_list: list, character: str) -> dict:
    """Recreate reviewed non-outline boot-interior marks; not full-pose labels."""
    crops = {crop_md5(px)[0]: px for _, _, px in pose_list}
    rows = []
    for key, split, label, rect in REFERENCE_SPOTS[character]:
        px = crops[key]
        x0, y0, x1, y1 = rect
        points = [
            [x, y, label]
            for y in range(y0, y1)
            for x in range(x0, x1)
            if px[y, x] in (1, 2)
        ]
        rows.append({"pose_md5": key, "split": split, "points": points})
    return {"reviewer": "Codex Saturn default-costume boot spot checks", "poses": rows}


def prepare(
    pose_list: list, character: str, annotations: dict
) -> tuple[dict, dict, list]:
    """Validate every annotation before training; split at normalized-pose level."""
    by_hash = {crop_md5(px)[0]: (n, frame, px) for n, frame, px in pose_list}
    recipe = RECIPES[character]
    if recipe["pose_md5"] not in by_hash:
        raise ValueError("approved seed pose missing")
    n, _, px = by_hash[recipe["pose_md5"]]
    baseline = {n: classify(px, recipe)}
    corrected = {n: dict(baseline[n])}
    seen: dict = {}
    evaluation = []
    for row in annotations["poses"]:
        key, split = row["pose_md5"], row["split"]
        if key in seen or split not in ("train", "eval"):
            raise ValueError("duplicate pose or invalid split")
        seen[key] = split
        n, frame, px = by_hash[key]
        if split == "eval" and n in baseline:
            raise ValueError("evaluation pose is an approved training seed")
        points = {}
        for x, y, label in row["points"]:
            if not (0 <= y < px.shape[0] and 0 <= x < px.shape[1]) or px[y, x] == 0:
                raise ValueError("annotation outside visible sprite")
            if label not in COLORS or (y, x) in points:
                raise ValueError("invalid class or duplicate annotation")
            points[y, x] = label
        if split == "train":
            corrected.setdefault(n, {}).update(points)
        else:
            evaluation.append((n, frame, points))
    return baseline, corrected, evaluation


def render(px: np.ndarray, labels: np.ndarray) -> Image.Image:
    rgb = np.full((*px.shape, 3), 220, np.uint8)
    for name, color in COLORS.items():
        for shade, scale in [(1, 1.0), (2, 0.7), (3, 0.12)]:
            rgb[(labels == name) & (px == shade)] = np.array(color) * scale
    return Image.fromarray(rgb)


def run(capture: Path, character: str, marks: Path, out: Path) -> dict:
    cap = json.loads(capture.read_text())
    pose_list = poses(capture)
    annotations = (
        reference_spots(pose_list, character)
        if str(marks) == "reference"
        else json.loads(marks.read_text())
    )
    baseline, corrected, evaluation = prepare(pose_list, character, annotations)
    out.mkdir(parents=True, exist_ok=False)
    (out / "marks.json").write_text(json.dumps(annotations, indent=2))
    frequencies = Counter(
        crop_md5(compose(f, cap["side"])[0])[0] for f in cap["frames"]
    )
    ranked = sorted(pose_list, key=lambda p: (-frequencies[crop_md5(p[2])[0]], p[1]))[
        :20
    ]
    report = {
        "character": character,
        "capture_sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
        "marks_sha256": hashlib.sha256(
            json.dumps(annotations, sort_keys=True).encode()
        ).hexdigest(),
        "scope": "reviewed spot errors on pose-disjoint evaluation; not full-pose accuracy",
        "rounds": [],
        "top20_frames": [f for _, f, _ in ranked],
        "engine_ready": False,
    }
    for round_no, seeds in enumerate([baseline, corrected]):
        clf = train(pose_list, seeds)
        predictions = {}
        for n, _, px in pose_list:
            positions, classes, votes = predict_pose(clf, px)
            labels = np.full(px.shape, "", dtype="<U12")
            confidence = np.zeros(px.shape)
            for (y, x), label, vote in zip(positions, classes, votes):
                labels[y, x], confidence[y, x] = label, vote
            predictions[n] = labels, confidence
        errors = []
        for n, frame, points in evaluation:
            labels, confidence = predictions[n]
            for (y, x), expected in points.items():
                errors.append(
                    {
                        "pose": n,
                        "frame": frame,
                        "xy": [x, y],
                        "expected": expected,
                        "actual": str(labels[y, x]),
                        "vote": float(confidence[y, x]),
                        "wrong": bool(labels[y, x] != expected),
                    }
                )
        report["rounds"].append(
            {
                "round": round_no,
                "training_poses": sorted(seeds),
                "training_pixels": sum(map(len, seeds.values())),
                "evaluation_pixels": len(errors),
                "errors": sum(e["wrong"] for e in errors),
                "checks": errors,
            }
        )
        sheet = Image.new("RGB", (1200, 1100), (220, 220, 220))
        for rank, (n, frame, px) in enumerate(ranked):
            labels, _ = predictions[n]
            source = Image.fromarray(
                np.array([220, 245, 140, 20], np.uint8)[px]
            ).convert("RGB")
            for offset, im in [(0, source), (150, render(px, labels))]:
                im = im.resize(
                    (px.shape[1] * 4, px.shape[0] * 4), Image.Resampling.NEAREST
                )
                im.thumbnail((145, 190), Image.Resampling.NEAREST)
                sheet.paste(im, ((rank % 4) * 300 + offset, (rank // 4) * 220 + 20))
            ImageDraw.Draw(sheet).text(
                ((rank % 4) * 300, (rank // 4) * 220),
                f"{rank+1}: pose{n} frame{frame}",
                fill="black",
            )
        sheet.save(out / f"round-{round_no}-top20.png")
        with (out / f"round-{round_no}-predictions.pkl").open("wb") as stream:
            pickle.dump(predictions, stream)
    (out / "report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("character", choices=RECIPES)
    parser.add_argument(
        "marks",
        type=Path,
        help="local annotation JSON or reference for the built-in spot recipe",
    )
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    result = run(args.capture, args.character, args.marks, args.out)
    print(
        json.dumps(
            [
                {
                    k: r[k]
                    for k in ["round", "training_pixels", "evaluation_pixels", "errors"]
                }
                for r in result["rounds"]
            ]
        )
    )
