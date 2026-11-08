"""Local outline-component review and explicit pixel marks; never infers owner approval."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def fingerprint(pixels: np.ndarray) -> str:
    return hashlib.sha256(
        str(pixels.shape).encode() + pixels.astype(np.int8).tobytes()
    ).hexdigest()


def apply_marks(
    pixels: np.ndarray,
    labels: np.ndarray,
    components: np.ndarray,
    record: dict | None,
    vocabulary: dict,
) -> np.ndarray:
    if record is None:
        return labels
    if record["frame_sha256"] != fingerprint(pixels):
        raise ValueError("mark frame fingerprint mismatch")
    result = labels.copy()
    assigned = {}
    for mark in record["marks"]:
        name = mark["label"]
        if name not in vocabulary or vocabulary[name] == 0:
            raise ValueError("marks need an explicit nontransparent semantic label")
        value = vocabulary[name]
        if mark["kind"] == "component":
            number = mark["component"]
            region = components == number
            if number <= 0 or not np.any(region):
                raise ValueError("unknown component id")
            if mark["component_sha256"] != fingerprint(region):
                raise ValueError("component fingerprint mismatch")
            yy, xx = np.nonzero(region)
            coords = list(zip(xx.tolist(), yy.tolist()))
        elif mark["kind"] == "pixels":
            coords = mark["pixels"]
            if not coords:
                raise ValueError("empty pixel mark")
        else:
            raise ValueError("unknown mark kind")
        for x, y in coords:
            if (
                not isinstance(x, int)
                or not isinstance(y, int)
                or not (0 <= y < pixels.shape[0] and 0 <= x < pixels.shape[1])
                or pixels[y, x] == 0
            ):
                raise ValueError("mark outside visible fighter pixels")
            key = (x, y)
            if key in assigned and assigned[key] != value:
                raise ValueError("contradictory marks; split the component instead")
            assigned[key] = value
            result[y, x] = value
    return result


def load_marks(path: Path | None, capture_path: Path, cap: dict) -> dict:
    if path is None:
        return {}
    marks = json.loads(path.read_text())
    if (
        marks.get("schema") != 1
        or marks.get("capture_sha256")
        != hashlib.sha256(capture_path.read_bytes()).hexdigest()
        or marks.get("character") != cap["character"]
    ):
        raise ValueError("marks/capture provenance mismatch")
    if not isinstance(marks.get("reviewer"), str) or not marks["reviewer"].strip():
        raise ValueError("named reviewer required")
    valid = {str(frame["index"]) for frame in cap["frames"]}
    if set(marks["frames"]) - valid:
        raise ValueError("marks refer to absent frames")
    return marks


def export_review(capture: Path, out: Path, indices: list[int]) -> dict:
    from segment_frames import compose, components, LABELS

    cap = json.loads(capture.read_text())
    if cap.get("status") != "CAPTURED":
        raise ValueError("incomplete capture")
    selected = {frame["index"]: frame for frame in cap["frames"]}
    if len(set(indices)) != len(indices) or set(indices) - selected.keys():
        raise ValueError("invalid review frame set")
    out.mkdir(parents=True, exist_ok=False)
    review = {
        "schema": 1,
        "capture_sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
        "character": cap["character"],
        "reviewer": "",
        "legend": LABELS,
        "frames": {},
    }
    catalogue = {}
    for index in indices:
        pixels, _, _ = compose(selected[index], cap["side"])
        labs, count = components(pixels)
        source = np.array([225, 245, 140, 20], dtype=np.uint8)[pixels]
        image = (
            Image.fromarray(source)
            .convert("RGB")
            .resize((224 * 4, 144 * 4), Image.Resampling.NEAREST)
        )
        draw = ImageDraw.Draw(image)
        items = []
        for number in range(1, count + 1):
            yy, xx = np.nonzero(labs == number)
            x, y = int(xx[0]), int(yy[0])
            items.append(
                {
                    "id": number,
                    "component_sha256": fingerprint(labs == number),
                    "area": len(xx),
                    "seed": [x, y],
                    "bbox": [
                        int(xx.min()),
                        int(yy.min()),
                        int(xx.max() + 1),
                        int(yy.max() + 1),
                    ],
                }
            )
            draw.text(
                (x * 4, y * 4),
                str(number),
                fill=(255, 0, 0),
                stroke_width=1,
                stroke_fill=(255, 255, 255),
            )
        image.save(out / f"frame-{index:04d}.png")
        # Save a no-number source alongside for thin features and outline pixels.
        Image.fromarray(source).resize(
            (224 * 4, 144 * 4), Image.Resampling.NEAREST
        ).save(out / f"frame-{index:04d}-source.png")
        review["frames"][str(index)] = {
            "frame_sha256": fingerprint(pixels),
            "marks": [],
        }
        catalogue[str(index)] = items
    (out / "marks-template.json").write_text(json.dumps(review, indent=2) + "\n")
    (out / "components.json").write_text(json.dumps(catalogue, indent=2) + "\n")
    return catalogue


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, nargs="+", required=True)
    args = parser.parse_args()
    catalogue = export_review(args.capture, args.out, args.frames)
    print(json.dumps({key: len(value) for key, value in catalogue.items()}))


if __name__ == "__main__":
    main()
