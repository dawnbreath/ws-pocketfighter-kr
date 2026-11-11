"""CTB2 group planes / CTB3 full colours, with exact source verification."""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import struct
import zlib

HEADER = struct.Struct("<4sH")
RECORD = struct.Struct("<H16s16s")
FULL_RECORD = struct.Struct("<H16s32s")
MAX_SIZE = 0x8000


def hash16(raw: bytes) -> int:
    if len(raw) != 16:
        raise ValueError("one source tile must be 16 bytes")
    value = 0
    for (word,) in struct.iter_unpack("<H", raw):
        value = ((value << 3) | (value >> 13)) & 0xFFFF
        value ^= word
    return value


def validate_table(blob: bytes) -> None:
    if len(blob) < HEADER.size + 64 or len(blob) > MAX_SIZE:
        raise ValueError(
            "CTB2/CTB3 must fit color-bank 8000..FFFF and include 64 palette bytes"
        )
    magic, count = HEADER.unpack_from(blob)
    record = FULL_RECORD if magic == b"CTB3" else RECORD
    if (
        magic not in (b"CTB2", b"CTB3")
        or len(blob) != HEADER.size + count * record.size + 64
    ):
        raise ValueError(
            "invalid CTB2 version/count/length; legacy and PGMD tables need conversion"
        )
    seen = set()
    for index in range(count):
        digest, raw, mask = record.unpack_from(blob, HEADER.size + index * record.size)
        if magic == b"CTB3":
            for y in range(8):
                if (raw[2 * y] | raw[2 * y + 1]) != (
                    mask[4 * y] | mask[4 * y + 1] | mask[4 * y + 2] | mask[4 * y + 3]
                ):
                    raise ValueError("full tile must preserve source transparency")
        if hash16(raw) != digest:
            raise ValueError("incorrect source hash")
        if raw in seen:
            raise ValueError(
                "duplicate source tile: unresolved context/semantic ambiguity"
            )
        seen.add(raw)
    if any(color > 0xFFF for (color,) in struct.iter_unpack("<H", blob[-64:])):
        raise ValueError("palette entries must be RGB444")


def pack_table(records: list[tuple[bytes, bytes]], palettes: bytes) -> bytes:
    if (
        len(palettes) != 64
        or len(records) > (MAX_SIZE - HEADER.size - 64) // RECORD.size
    ):
        raise ValueError("invalid palette length or table exceeds reserved bank half")
    rows = []
    for raw, mask in records:
        if len(raw) != 16 or len(mask) != 16:
            raise ValueError("source and mask must each be 16 bytes")
        rows.append((hash16(raw), raw, mask))
    rows.sort()
    blob = (
        HEADER.pack(b"CTB2", len(rows))
        + b"".join(RECORD.pack(*row) for row in rows)
        + palettes
    )
    validate_table(blob)
    return blob


def pack_full_table(records: list[tuple[bytes, bytes]], palettes: bytes) -> bytes:
    rows = sorted((hash16(raw), raw, output) for raw, output in records)
    if len(palettes) != 64 or any(
        len(raw) != 16 or len(output) != 32 for _, raw, output in rows
    ):
        raise ValueError("invalid full tile/palettes")
    blob = (
        HEADER.pack(b"CTB3", len(rows))
        + b"".join(FULL_RECORD.pack(*row) for row in rows)
        + palettes
    )
    validate_table(blob)
    return blob


def records_from_votes(votes: dict, sources: dict) -> tuple[list, dict]:
    records, omitted = [], {}
    for key, cells in sorted(votes.items()):
        if len(cells) != 64 or any(
            any(v not in range(4) for v in cell) for cell in cells
        ):
            raise ValueError("need 64 source pixels with group values 0..3")
        if any(len(cell) != 1 for cell in cells):
            omitted[key] = (
                "conflict" if any(len(cell) > 1 for cell in cells) else "unobserved"
            )
            continue
        mask = bytearray(16)
        for i, cell in enumerate(cells):
            g = next(iter(cell))
            y, x = divmod(i, 8)
            mask[y * 2] |= (g & 1) << (7 - x)
            mask[y * 2 + 1] |= ((g >> 1) & 1) << (7 - x)
        raw = sources[key]
        if len(raw) != 16 or hashlib.sha256(raw).hexdigest() != key:
            raise ValueError("source identity mismatch")
        records.append((raw, bytes(mask)))
    return records, omitted


def convert_pgmd(blob: bytes, palettes: bytes) -> bytes:
    # PGMD is diagnostic, not production approval. Preserve its exact source/mask;
    # CTB2's runtime ignores the uniform optimization and verifies every hash hit.
    header = struct.Struct("<4sHHI")
    record = struct.Struct("<I16sB16s")
    if len(blob) < header.size:
        raise ValueError("short PGMD header")
    magic, version, size, count = header.unpack_from(blob)
    if (magic, version, size) != (b"PGMD", 1, record.size) or len(
        blob
    ) != header.size + count * size:
        raise ValueError("invalid PGMD version/length")
    rows = []
    for index in range(count):
        checksum, raw, uniform, mask = record.unpack_from(
            blob, header.size + index * size
        )
        if zlib.crc32(raw) != checksum or uniform not in (0, 1, 2, 3, 255):
            raise ValueError("invalid PGMD record")
        rows.append((raw, mask))
    return pack_table(rows, palettes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pgmd", type=Path)
    parser.add_argument(
        "palettes", type=Path, help="exactly 32 little-endian RGB444 words: P1 then P2"
    )
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    blob = convert_pgmd(args.pgmd.read_bytes(), args.palettes.read_bytes())
    with args.output.open("xb") as output:
        output.write(blob)
    print(
        f"DIAGNOSTIC ONLY: {HEADER.unpack_from(blob)[1]} records, {len(blob)} bytes; no palette or owner approval implied"
    )


if __name__ == "__main__":
    main()
