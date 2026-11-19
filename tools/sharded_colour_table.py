"""Partition exact-source CTB3 records by hash prefix; keep game data local."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from class_table import HEADER, FULL_RECORD, hash16, pack_full_table, validate_table
from colour_layout import CLASS_SHARD_COUNT


def pack_shards(records: list[tuple[bytes, bytes]], palettes: bytes) -> list[bytes]:
    groups: list[list[tuple[bytes, bytes]]] = [[] for _ in range(CLASS_SHARD_COUNT)]
    for source, output in records:
        groups[hash16(source) >> 12].append((source, output))
    return [pack_full_table(group, palettes) for group in groups]


def read_shards(root: Path) -> list[bytes]:
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest.get("version") != 1 or manifest.get("partition") != "hash16-high4":
        raise ValueError("unsupported shard manifest")
    blobs = [(root / f"{n:02x}.ctb3").read_bytes() for n in range(CLASS_SHARD_COUNT)]
    if manifest.get("sha256") != [hashlib.sha256(b).hexdigest() for b in blobs]:
        raise ValueError("shard digest mismatch")
    for n, blob in enumerate(blobs):
        validate_table(blob)
        if HEADER.unpack_from(blob)[0] != b"CTB3" or blob[-64:] != blobs[0][-64:]:
            raise ValueError("shards require CTB3 and identical palette footers")
        rows = list(FULL_RECORD.iter_unpack(blob[HEADER.size : -64]))
        if rows != sorted(rows) or any(digest >> 12 != n for digest, _, _ in rows):
            raise ValueError("unsorted records or wrong hash partition")
    return blobs


def write_shards(
    records: list[tuple[bytes, bytes]], palettes: bytes, out: Path
) -> dict:
    blobs = pack_shards(records, palettes)
    manifest = {
        "version": 1,
        "partition": "hash16-high4",
        "counts": [HEADER.unpack_from(b)[1] for b in blobs],
        "sha256": [hashlib.sha256(b).hexdigest() for b in blobs],
    }
    out.mkdir(parents=True, exist_ok=False)
    for n, blob in enumerate(blobs):
        (out / f"{n:02x}.ctb3").write_bytes(blob)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def read_catalogue(path: Path) -> tuple[list[tuple[int, bytes, bytes]], bytes]:
    """Read a single table or a validated directory with sixteen partitions."""
    blobs = read_shards(path) if path.is_dir() else [path.read_bytes()]
    rows = []
    for blob in blobs:
        validate_table(blob)
        if HEADER.unpack_from(blob)[0] != b"CTB3":
            raise ValueError("requires CTB3 colour catalogue")
        rows.extend(FULL_RECORD.iter_unpack(blob[HEADER.size : -64]))
    return rows, blobs[0][-64:]


def catalogue_digest(path: Path) -> str:
    blobs = read_shards(path) if path.is_dir() else [path.read_bytes()]
    return hashlib.sha256(b"".join(blobs)).hexdigest()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("table", type=Path)
    p.add_argument("out", type=Path)
    args = p.parse_args()
    blob = args.table.read_bytes()
    validate_table(blob)
    if HEADER.unpack_from(blob)[0] != b"CTB3":
        raise ValueError("requires full CTB3 records")
    print(
        json.dumps(
            write_shards(
                [
                    (s, o)
                    for _, s, o in FULL_RECORD.iter_unpack(blob[HEADER.size : -64])
                ],
                blob[-64:],
                args.out,
            )
        )
    )
