"""Partition exact-source CTB3 records by hash prefix; keep game data local."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from class_table import (
    HEADER,
    FULL_RECORD,
    CONTEXT_RECORD,
    hash16,
    pack_full_table,
    validate_table,
)
from colour_layout import CLASS_SHARD_COUNT


def pack_shards(records: list[tuple[bytes, bytes]], palettes: bytes) -> list[bytes]:
    groups: list[list[tuple[bytes, bytes]]] = [[] for _ in range(CLASS_SHARD_COUNT)]
    for source, output in records:
        groups[hash16(source) >> 12].append((source, output))
    return [pack_full_table(group, palettes) for group in groups]


def read_shards(root: Path) -> list[bytes]:
    manifest = json.loads((root / "manifest.json").read_text())
    version = manifest.get("version")
    if version not in (1, 2) or manifest.get("partition") != "hash16-high4":
        raise ValueError("unsupported shard manifest")
    suffix, magic, record = (
        ("ctb4", b"CTB4", CONTEXT_RECORD)
        if version == 2
        else ("ctb3", b"CTB3", FULL_RECORD)
    )
    blobs = [
        (root / f"{n:02x}.{suffix}").read_bytes() for n in range(CLASS_SHARD_COUNT)
    ]
    if manifest.get("sha256") != [hashlib.sha256(b).hexdigest() for b in blobs]:
        raise ValueError("shard digest mismatch")
    for n, blob in enumerate(blobs):
        validate_table(blob)
        if HEADER.unpack_from(blob)[0] != magic or blob[-64:] != blobs[0][-64:]:
            raise ValueError("shards require CTB3 and identical palette footers")
        rows = list(record.iter_unpack(blob[HEADER.size : -64]))
        if rows != sorted(rows) or any(row[0] >> 12 != n for row in rows):
            raise ValueError("unsorted records or wrong hash partition")
    return blobs


def write_shards(
    records: list[tuple[bytes, bytes]],
    palettes: bytes,
    out: Path,
    *,
    contexts: dict[int, dict[bytes, bytes]] | None = None,
) -> dict:
    if contexts is not None:
        from compact_colour_table import fallback_output

        canonical = dict(records)
        if len(canonical) != len(records):
            raise ValueError("duplicate canonical source")
        for variants in contexts.values():
            for source in variants:
                canonical.setdefault(source, fallback_output(source))
        return write_context_shards(list(canonical.items()), contexts, palettes, out)
    return _write_blobs(pack_shards(records, palettes), out, 1)


def _write_blobs(blobs: list[bytes], out: Path, version: int) -> dict:
    manifest = {
        "version": version,
        "partition": "hash16-high4",
        "counts": [HEADER.unpack_from(b)[1] for b in blobs],
        "sha256": [hashlib.sha256(b).hexdigest() for b in blobs],
    }
    out.mkdir(parents=True, exist_ok=False)
    suffix = "ctb4" if version == 2 else "ctb3"
    for n, blob in enumerate(blobs):
        (out / f"{n:02x}.{suffix}").write_bytes(blob)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def write_context_shards(
    canonical: list[tuple[bytes, bytes]],
    overrides: dict[int, dict[bytes, bytes]],
    palettes: bytes,
    out: Path,
) -> dict:
    """Keep canonical fallback and add only explicitly supplied character variants."""
    source_outputs = dict(canonical)
    if len(palettes) != 64 or any(len(s) != 16 or len(o) != 32 for s, o in canonical):
        raise ValueError("invalid canonical source/output/palettes")
    if len(source_outputs) != len(canonical):
        raise ValueError("duplicate canonical source")
    rows = [(hash16(s), s, 255, 0, o) for s, o in canonical]
    for context, records in overrides.items():
        if context not in range(1, 16):
            raise ValueError("context must be 1..15")
        for source, output in records.items():
            if source not in source_outputs or len(output) != 32:
                raise ValueError("context source lacks canonical fallback")
            rows.append((hash16(source), source, context, 0, output))
    rows.sort()
    blobs = []
    for n in range(CLASS_SHARD_COUNT):
        group = [row for row in rows if row[0] >> 12 == n]
        blob = (
            HEADER.pack(b"CTB4", len(group))
            + b"".join(CONTEXT_RECORD.pack(*row) for row in group)
            + palettes
        )
        validate_table(blob)
        blobs.append(blob)
    return _write_blobs(blobs, out, 2)


def read_catalogue(
    path: Path, context: int = 0
) -> tuple[list[tuple[int, bytes, bytes]], bytes]:
    """Read a single table or a validated directory with sixteen partitions."""
    blobs = read_shards(path) if path.is_dir() else [path.read_bytes()]
    rows = []
    for blob in blobs:
        validate_table(blob)
        magic = HEADER.unpack_from(blob)[0]
        if magic == b"CTB4":
            selected = {}
            for h, source, selector, _, output in CONTEXT_RECORD.iter_unpack(
                blob[HEADER.size : -64]
            ):
                if selector in (context, 255):
                    selected.setdefault(source, (h, source, output))
            rows.extend(selected.values())
        elif magic != b"CTB3":
            raise ValueError("requires CTB3 colour catalogue")
        else:
            rows.extend(FULL_RECORD.iter_unpack(blob[HEADER.size : -64]))
    return rows, blobs[0][-64:]


def read_context_overrides(path: Path) -> dict[int, dict[bytes, bytes]] | None:
    """Return the variants writers must retain; None denotes a legacy catalogue."""
    blobs = read_shards(path) if path.is_dir() else [path.read_bytes()]
    result = {}
    for blob in blobs:
        validate_table(blob)
        if HEADER.unpack_from(blob)[0] != b"CTB4":
            return None
        for _, source, context, _, output in CONTEXT_RECORD.iter_unpack(
            blob[HEADER.size : -64]
        ):
            if context != 255:
                result.setdefault(context, {})[source] = output
    return result


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
