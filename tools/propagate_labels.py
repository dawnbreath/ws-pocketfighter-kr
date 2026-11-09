"""Review-only few-shot proposals; confidence is a vote score, never approval."""

from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageDraw
from component_marks import apply_marks, load_marks, export_review
from segment_frames import (
    compose,
    components,
    LABELS,
    preview,
    project_labels,
    merge_votes,
    consensus,
)


def crop(pixels: np.ndarray) -> np.ndarray:
    yy, xx = np.nonzero(pixels)
    return (
        pixels[yy.min() : yy.max() + 1, xx.min() : xx.max() + 1]
        if len(xx)
        else np.zeros((1, 1), np.int8)
    )


def pose_key(pixels: np.ndarray) -> str:
    p = crop(pixels)
    return hashlib.sha256(str(p.shape).encode() + p.tobytes()).hexdigest()


def choose_seeds(images: list[np.ndarray], count: int) -> list[int]:
    unique = {}
    for i, p in enumerate(images):
        if np.any(p):
            unique.setdefault(pose_key(p), i)
    indices = list(unique.values())
    if not indices:
        return []
    vectors = []
    for i in indices:
        p = crop(images[i])
        vectors.append(
            np.r_[
                np.asarray(
                    Image.fromarray(p.astype(np.uint8)).resize(
                        (16, 16), Image.Resampling.NEAREST
                    )
                ).reshape(-1)
                / 3,
                p.shape[1] / max(p.shape[0], 1),
            ]
        )
    x = np.asarray(vectors)
    picked = [0]
    dist = np.full(len(x), np.inf)
    while len(picked) < min(count, len(x)):
        dist = np.minimum(dist, np.mean((x - x[picked[-1]]) ** 2, axis=1))
        dist[picked] = -1
        picked.append(int(dist.argmax()))
    return [indices[i] for i in picked]


def features(pixels: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    yy, xx = np.nonzero(pixels)
    if not len(xx):
        return np.empty((0, 27), np.float32), yy, xx
    patches = (
        np.lib.stride_tricks.sliding_window_view(np.pad(pixels, 2), (5, 5))[
            yy, xx
        ].reshape(-1, 25)
        / 3
    )
    position = np.column_stack(
        (
            (xx - xx.min()) / max(int(xx.max() - xx.min()), 1),
            (yy - yy.min()) / max(int(yy.max() - yy.min()), 1),
        )
    )
    return np.column_stack((patches, position)).astype(np.float32), yy, xx


def predict(
    train: np.ndarray,
    labels: np.ndarray,
    query: np.ndarray,
    threshold: float,
    radius: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    classes = np.unique(labels)
    if len(classes) < 2:
        raise ValueError(
            "at least two explicitly marked opaque classes required; one-class certainty is not meaningful"
        )
    answers = []
    scores = []
    supports = []
    probabilities = []
    k = min(5, len(train))
    for start in range(0, len(query), 256):
        q = query[start : start + 256]
        # Mean squared feature distance; memory bounded by 256*training_count.
        distances = (
            np.maximum(
                (q * q).sum(1)[:, None]
                + (train * train).sum(1)[None, :]
                - 2 * q @ train.T,
                0,
            )
            / train.shape[1]
        )
        nearest = np.argsort(distances, axis=1, kind="stable")[:, :k]
        d = np.take_along_axis(distances, nearest, axis=1)
        weights = 1 / (d + 0.001)
        probs = np.stack(
            [(weights * (labels[nearest] == c)).sum(1) for c in classes], axis=1
        )
        probs /= probs.sum(1, keepdims=True)
        best = probs.argmax(1)
        score = probs[np.arange(len(q)), best]
        answer = classes[best].copy()
        answer[(score < threshold) | (d[:, 0] > radius)] = -1
        answers.extend(answer)
        scores.extend(score)
        supports.extend(d[:, 0])
        probabilities.extend(probs)
    return (
        np.asarray(answers, dtype=np.int8),
        np.asarray(scores),
        np.asarray(supports),
        np.asarray(probabilities, dtype=np.float32).reshape(-1, len(classes)),
    )


def run(
    capture: Path,
    out: Path,
    marks_path: Path | None,
    seed_count: int = 12,
    threshold: float = 0.9,
    radius: float = 0.04,
) -> dict:
    started = time.perf_counter()
    raw = capture.read_bytes()
    cap = json.loads(raw)
    if cap.get("schema") != 1 or cap.get("status") != "CAPTURED":
        raise ValueError("need completed schema-1 capture")
    if not 1 <= seed_count <= 32 or not 0.5 < threshold <= 1 or not 0 <= radius <= 1:
        raise ValueError("invalid seed count/threshold/radius")
    marks = load_marks(marks_path, capture, cap)
    images = [compose(f, cap["side"])[0] for f in cap["frames"]]
    selected = choose_seeds(images, seed_count)
    report = {
        "schema": 1,
        "character": cap["character"],
        "capture_sha256": hashlib.sha256(raw).hexdigest(),
        "rom_sha256": cap["rom_sha256"],
        "engine_ready": False,
        "unique_poses": len({pose_key(p) for p in images if np.any(p)}),
        "recommended_frames": [cap["frames"][i]["index"] for i in selected],
        "status": "SEEDS_REQUIRED",
        "threshold": threshold,
        "support_radius_mse": radius,
        "feature": "5x5 shade patch /3 plus bbox-relative xy; k<=5 inverse-distance votes",
        "limitations": [
            "not calibrated correctness probabilities",
            "selected palette may include effects",
            "no motion tracking",
            "no owner-approval inference",
            "missing classes cannot be learned",
            "no blanket component smoothing",
        ],
    }
    out.mkdir(parents=True, exist_ok=False)
    if selected:
        export_review(capture, out / "seed-review", report["recommended_frames"])
    train_x = []
    train_y = []
    seed_labels = {}
    for i, (frame, pixels) in enumerate(zip(cap["frames"], images)):
        record = marks.get("frames", {}).get(str(frame["index"]))
        if not record or not record["marks"]:
            continue
        labs, _ = components(pixels)
        values = apply_marks(
            pixels, np.full(pixels.shape, -1, np.int8), labs, record, LABELS
        )
        values[pixels == 0] = 0
        x, yy, xx = features(pixels)
        y = values[yy, xx]
        known = y > 0
        if known.any():
            train_x.append(x[known])
            train_y.append(y[known])
            seed_labels[i] = values
    if not train_x or len(np.unique(np.concatenate(train_y))) < 2:
        report["blocked_reason"] = (
            "Need at least two opaque classes in explicit fingerprint-bound marks. Approved seeds not inferred from automatic rules."
        )
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        return report
    train = np.concatenate(train_x)
    labels = np.concatenate(train_y)
    # Duplicate features with contradicting seed labels retain both votes.
    report.update(
        status="UNREVIEWED_PROPOSALS",
        reviewer=marks["reviewer"],
        marks_sha256=hashlib.sha256(marks_path.read_bytes()).hexdigest(),
        seed_frames=[cap["frames"][i]["index"] for i in seed_labels],
        training_pixels=len(labels),
        learned_classes=[int(c) for c in np.unique(labels)],
    )
    seed_pose_keys = {pose_key(images[i]) for i in seed_labels}
    votes = {}
    evidence = {}
    rows = []
    previous = {}
    temporal = []
    proposals = []
    (out / "probabilities").mkdir()
    for i, (frame, pixels) in enumerate(zip(cap["frames"], images)):
        x, yy, xx = features(pixels)
        predicted, score, distance, probs = predict(train, labels, x, threshold, radius)
        image_labels = np.full(pixels.shape, -1, np.int8)
        image_labels[pixels == 0] = 0
        image_labels[yy, xx] = predicted
        record = marks.get("frames", {}).get(str(frame["index"]))
        if record:
            labs, _ = components(pixels)
            image_labels = apply_marks(pixels, image_labels, labs, record, LABELS)
        _, owner, sprites = compose(frame, cap["side"])
        local = project_labels(owner, sprites, image_labels, cap["side"])
        merge_votes(votes, local, evidence, frame["index"])
        disagreements = sum(
            len(a) == len(b) == 1 and a != b and 0 not in a and 0 not in b
            for key in previous.keys() & local.keys()
            for a, b in zip(previous[key], local[key])
        )
        if disagreements:
            temporal.append(
                {
                    "previous_frame": cap["frames"][i - 1]["index"],
                    "frame": frame["index"],
                    "same_source_pixel_disagreements": disagreements,
                }
            )
        previous = local
        rejected = int(np.sum(image_labels[yy, xx] < 0))
        total = len(yy)
        rows.append(
            {
                "frame": frame["index"],
                "seed_frame": i in seed_labels,
                "seed_pose": pose_key(pixels) in seed_pose_keys,
                "opaque_pixels": total,
                "rejected_pixels": rejected,
                "rejected_fraction": rejected / max(total, 1),
                "mean_vote_score": float(score.mean()) if total else 0,
                "pose_sha256": pose_key(pixels),
            }
        )
        proposals.append(image_labels)
        np.savez_compressed(
            out / "probabilities" / f"{frame['index']:04d}.npz",
            xy=np.column_stack((xx, yy)),
            classes=np.unique(labels),
            votes=probs,
            nearest_mse=distance,
            accepted=image_labels[yy, xx],
        )
    ranked = sorted(
        range(len(rows)),
        key=lambda i: (
            -rows[i]["rejected_fraction"],
            rows[i]["mean_vote_score"],
            rows[i]["frame"],
        ),
    )
    unique = []
    seen = set()
    for i in ranked:
        if rows[i]["pose_sha256"] not in seen:
            unique.append(i)
            seen.add(rows[i]["pose_sha256"])
    review = unique[:seed_count]
    if review:
        export_review(
            capture, out / "uncertain-review", [rows[i]["frame"] for i in review]
        )
    sheet = Image.new(
        "RGB", (224 * 4, 164 * ((min(32, len(unique)) + 3) // 4)), (220, 220, 220)
    )
    for n, i in enumerate(unique[:32]):
        x, y = (n % 4) * 224, (n // 4) * 164
        sheet.paste(preview(proposals[i]), (x, y))
        ImageDraw.Draw(sheet).text(
            (x + 2, y + 144),
            f"frame {rows[i]['frame']} unknown {rows[i]['rejected_fraction']:.0%}",
            fill="black",
        )
    if unique:
        sheet.save(out / "least-confident.png")
    seed_sheet = Image.new("RGB", (224 * 3, 164 * len(seed_labels)), (220, 220, 220))
    for n, i in enumerate(seed_labels):
        gray = np.array([225, 245, 140, 20], dtype=np.uint8)[images[i]]
        seed_sheet.paste(Image.fromarray(gray).convert("RGB"), (0, n * 164))
        seed_sheet.paste(preview(seed_labels[i]), (224, n * 164))
        seed_sheet.paste(preview(proposals[i]), (448, n * 164))
        ImageDraw.Draw(seed_sheet).text(
            (2, n * 164 + 144),
            f"frame {rows[i]['frame']}: source | explicit seed (pink=unknown) | proposal",
            fill="black",
        )
    seed_sheet.save(out / "seed-comparison.png")
    tiles = {
        key: {
            "mask": consensus(cells),
            "conflicts": [i for i, v in enumerate(cells) if len(v) > 1],
            "unobserved": [i for i, v in enumerate(cells) if not v],
        }
        for key, cells in sorted(votes.items())
    }
    masks = {
        **report,
        "labels": LABELS,
        "tiles": tiles,
        "confidence_location": "probabilities/*.npz; scores are not calibrated; PGMD/1 unchanged",
    }
    (out / "masks.json").write_text(json.dumps(masks, indent=2) + "\n")
    held = [r for r in rows if not r["seed_pose"]]
    report.update(
        frames=rows,
        uncertainty_order=[rows[i]["frame"] for i in unique],
        temporal_disagreements=temporal,
        tiles=len(tiles),
        conflicting_tiles=sum(bool(t["conflicts"]) for t in tiles.values()),
        heldout_pixels=sum(r["opaque_pixels"] for r in held),
        heldout_rejected_pixels=sum(r["rejected_pixels"] for r in held),
        heldout_frames_with_rejection=sum(r["rejected_pixels"] > 0 for r in held),
        runtime_seconds=time.perf_counter() - started,
    )
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("capture", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--marks", type=Path)
    p.add_argument("--seed-count", type=int, default=12)
    p.add_argument("--threshold", type=float, default=0.9)
    p.add_argument("--radius", type=float, default=0.04)
    a = p.parse_args()
    r = run(a.capture, a.out, a.marks, a.seed_count, a.threshold, a.radius)
    print(
        json.dumps(
            {
                k: r[k]
                for k in (
                    "status",
                    "unique_poses",
                    "recommended_frames",
                    "heldout_pixels",
                    "heldout_rejected_pixels",
                    "runtime_seconds",
                )
                if k in r
            }
        )
    )


if __name__ == "__main__":
    main()
