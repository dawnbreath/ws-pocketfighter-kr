"""Profile selected active OAM tile content; snapshots do not identify writers."""

from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from segment_frames import active_sprites


def profile(capture: Path) -> dict:
    raw = capture.read_bytes()
    cap = json.loads(raw)
    if cap.get("schema") != 1 or cap.get("status") != "CAPTURED":
        raise ValueError("need complete schema-1 capture")
    slots = defaultdict(set)
    inside, outside = set(), set()
    for frame in cap["frames"]:
        for sprite in active_sprites(frame):
            if sprite["side"] != cap["side"]:
                continue
            slot = sprite["word"] & 511
            digest = sprite["hash"]
            slots[slot].add(digest)
            (inside if slot >= 0x180 else outside).add(digest)
    return {
        "schema": 1,
        "character": cap["character"],
        "rom_sha256": cap["rom_sha256"],
        "capture_sha256": hashlib.sha256(raw).hexdigest(),
        "samples": len(cap["frames"]),
        "scope": "selected palette field, active OAM references including occluded/offscreen; captured fight only",
        "writer_verified": False,
        "counts": {
            "unique_hashes": len(inside | outside),
            "hashes_slots_180_1ff": len(inside),
            "hashes_slots_000_17f": len(outside),
            "hashes_in_both_ranges": len(inside & outside),
            "referenced_slots": len(slots),
            "reused_slots": sum(len(hashes) > 1 for hashes in slots.values()),
            "reused_slots_180_1ff": sum(
                slot >= 0x180 and len(hashes) > 1 for slot, hashes in slots.items()
            ),
            "reused_slots_000_17f": sum(
                slot < 0x180 and len(hashes) > 1 for slot, hashes in slots.items()
            ),
        },
        "slots": {
            str(slot): {"distinct_contents": len(hashes), "hashes": sorted(hashes)}
            for slot, hashes in sorted(slots.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    report = profile(args.capture)
    with args.out.open("x") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print(json.dumps(report["counts"]))


if __name__ == "__main__":
    main()
