"""Resolve captured tile content to exact ROM candidates, without claiming copy paths."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from segment_frames import active_sprites


def offsets(rom: bytes, tile: bytes) -> list[int]:
    if len(tile) != 16:
        raise ValueError("expected one 16-byte 2bpp tile")
    result = []
    start = 0
    while (index := rom.find(tile, start)) >= 0:
        result.append(index)
        start = index + 1
    return result


def map_sources(
    rom_path: Path, capture_path: Path, masks_path: Path, out: Path
) -> dict:
    rom = rom_path.read_bytes()
    capture_bytes = capture_path.read_bytes()
    cap = json.loads(capture_bytes)
    masks = json.loads(masks_path.read_text())
    digest = hashlib.sha256(rom).hexdigest()
    if (
        cap.get("status") != "CAPTURED"
        or masks.get("capture_sha256") != hashlib.sha256(capture_bytes).hexdigest()
    ):
        raise ValueError("incomplete or mismatched capture")
    if (
        cap["rom_sha256"] != digest
        or masks["rom_sha256"] != digest
        or cap["character"] != masks["character"]
    ):
        raise ValueError("ROM/character provenance mismatch")
    raw = {}
    for frame in cap["frames"]:
        for sprite in active_sprites(frame):
            if sprite["side"] == cap["side"]:
                raw[sprite["hash"]] = sprite["raw"]
    if set(masks["tiles"]) - raw.keys():
        raise ValueError("mask tile absent from selected-side capture")
    table = {}
    for key in sorted(masks["tiles"]):
        candidates = offsets(rom, raw[key])
        table[key] = {
            "rom_offsets": candidates,
            "status": (
                "NO_EXACT_MATCH"
                if not candidates
                else ("ONE_CANDIDATE" if len(candidates) == 1 else "AMBIGUOUS")
            ),
            "copy_path_verified": False,
        }
    report = {
        "schema": 1,
        "character": cap["character"],
        "rom_sha256": digest,
        "capture_sha256": hashlib.sha256(capture_bytes).hexdigest(),
        "masks_sha256": hashlib.sha256(masks_path.read_bytes()).hexdigest(),
        "engine_ready": False,
        "scope": "exact contiguous 16-byte matches at every byte offset; no bank/alignment assumptions; no decompression or writer tracing",
        "warning": "Even a unique byte match does not prove that the game copies that location. Multiple matches stay unresolved.",
        "counts": {
            status: sum(t["status"] == status for t in table.values())
            for status in ("ONE_CANDIDATE", "AMBIGUOUS", "NO_EXACT_MATCH")
        },
        "tiles": table,
    }
    with out.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("rom", "capture", "masks", "out"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(
        json.dumps(map_sources(args.rom, args.capture, args.masks, args.out)["counts"])
    )


if __name__ == "__main__":
    main()
