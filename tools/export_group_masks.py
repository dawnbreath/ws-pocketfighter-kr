"""Export diagnostic four-group bitplanes with exact-source collision checks."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib
from segment_frames import active_sprites, tile

HEADER = struct.Struct("<4sHHI")
RECORD = struct.Struct("<I16sB16s")


def encode(
    raw: bytes, labels: list[int], groups: dict[int, int]
) -> tuple[int, bytes] | None:
    """Original shade bits remain; group occupies bits 2/3; zero stays transparent."""
    if len(labels) != 64:
        raise ValueError("expected 64 source-oriented labels")
    if any(type(g) is not int or not 0 <= g <= 3 for g in groups.values()):
        raise ValueError("groups must be integers 0..3")
    pixels = tile(raw).reshape(-1)
    planes = bytearray(16)
    used = set()
    for i, shade in enumerate(pixels):
        if not shade:
            continue
        label = labels[i]
        if label < 0 or label not in groups:
            return None
        group = groups[label]
        used.add(group)
        y, x = divmod(i, 8)
        planes[2 * y] |= (group & 1) << (7 - x)
        planes[2 * y + 1] |= (group >> 1) << (7 - x)
    return (next(iter(used)) if len(used) == 1 else 255), bytes(planes)


def pack(records: list[tuple[bytes, int, bytes]]) -> bytes:
    rows = sorted(
        (zlib.crc32(raw), raw, uniform, planes) for raw, uniform, planes in records
    )
    return HEADER.pack(b"PGMD", 1, RECORD.size, len(rows)) + b"".join(
        RECORD.pack(*row) for row in rows
    )


def lookup(blob: bytes, raw: bytes) -> tuple[int, bytes] | None:
    """Reference reader: lower-bound CRC32, then exact bytes within collision run."""
    magic, version, size, count = HEADER.unpack_from(blob)
    if (magic, version, size) != (b"PGMD", 1, RECORD.size) or len(
        blob
    ) != HEADER.size + size * count:
        raise ValueError("invalid diagnostic table")
    key = zlib.crc32(raw)
    lo, hi = 0, count
    while lo < hi:
        mid = (lo + hi) // 2
        found = struct.unpack_from("<I", blob, HEADER.size + mid * size)[0]
        if found < key:
            lo = mid + 1
        else:
            hi = mid
    for index in range(lo, count):
        found, source, uniform, planes = RECORD.unpack_from(
            blob, HEADER.size + index * size
        )
        if found != key:
            break
        if source == raw:
            return uniform, planes
    return None


def export(capture: Path, masks: Path, mapping: Path, out: Path) -> dict:
    cap_bytes, mask_bytes, map_bytes = (
        p.read_bytes() for p in (capture, masks, mapping)
    )
    cap, table, config = (json.loads(b) for b in (cap_bytes, mask_bytes, map_bytes))
    if (
        cap.get("schema") != 1
        or cap.get("status") != "CAPTURED"
        or table.get("schema") != 1
    ):
        raise ValueError("need complete schema-1 capture and masks")
    if (
        table["capture_sha256"] != hashlib.sha256(cap_bytes).hexdigest()
        or cap["character"] != table["character"]
        or cap["rom_sha256"] != table["rom_sha256"]
        or config["character"] != cap["character"]
    ):
        raise ValueError("provenance mismatch")
    groups = {}
    for name, group in config["groups"].items():
        label = table["labels"][name]
        if label <= 0 or type(group) is not int or not 0 <= group <= 3:
            raise ValueError("map only opaque semantic labels to integer groups 0..3")
        groups[label] = group
    raw_tiles = {}
    for frame in cap["frames"]:
        for sprite in active_sprites(frame):
            if sprite["side"] == cap["side"]:
                raw_tiles[sprite["hash"]] = sprite["raw"]
    records, omitted = [], {}
    for digest, entry in sorted(table["tiles"].items()):
        if digest not in raw_tiles:
            raise ValueError("mask source absent from capture")
        raw = raw_tiles[digest]
        opaque = {i for i, shade in enumerate(tile(raw).reshape(-1)) if shade}
        if opaque.intersection(entry["conflicts"]) or opaque.intersection(
            entry["unobserved"]
        ):
            omitted[digest] = "conflict_or_unobserved"
            continue
        encoded = encode(raw, entry["mask"], groups)
        if encoded is None:
            omitted[digest] = "unknown_or_unmapped"
            continue
        records.append((raw, *encoded))
    blob = pack(records)
    # Validate the actual serialized result against every input before writing.
    if any(lookup(blob, raw) != (uniform, planes) for raw, uniform, planes in records):
        raise AssertionError("serialized lookup mismatch")
    report = {
        "schema": 1,
        "character": cap["character"],
        "engine_ready": False,
        "status": "DIAGNOSTIC_ONLY_UNREVIEWED",
        "format": "PGMD/1",
        "capture_sha256": hashlib.sha256(cap_bytes).hexdigest(),
        "masks_sha256": hashlib.sha256(mask_bytes).hexdigest(),
        "mapping_sha256": hashlib.sha256(map_bytes).hexdigest(),
        "binary_sha256": hashlib.sha256(blob).hexdigest(),
        "records": len(records),
        "omitted_count": len(omitted),
        "omitted": omitted,
        "warning": "Mapping is caller supplied, not palette approval. No production ASM integration or timing claim.",
    }
    out.mkdir(parents=True, exist_ok=False)
    (out / "masks.pgmd").write_bytes(blob)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("capture", "masks", "mapping", "out"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = export(args.capture, args.masks, args.mapping, args.out)
    print(
        json.dumps({k: result[k] for k in ("records", "omitted_count", "engine_ready")})
    )


if __name__ == "__main__":
    main()
