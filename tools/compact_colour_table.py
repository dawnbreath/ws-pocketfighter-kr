"""Omit CTB3 records that duplicate the copier's exact fallback output."""

import argparse
from pathlib import Path

from class_table import FULL_RECORD, HEADER, validate_table


def read_full_records(blob: bytes) -> list[tuple[int, bytes, bytes]]:
    validate_table(blob)
    magic, _ = HEADER.unpack_from(blob)
    if magic != b"CTB3":
        raise ValueError("compaction requires CTB3")
    return list(FULL_RECORD.iter_unpack(blob[HEADER.size : -64]))


def fallback_output(source: bytes) -> bytes:
    return b"".join(source[i : i + 2] + bytes(2) for i in range(0, 16, 2))


def compact(blob: bytes) -> bytes:
    records = [
        (digest, source, output)
        for digest, source, output in read_full_records(blob)
        if output != fallback_output(source)
    ]
    return (
        HEADER.pack(b"CTB3", len(records))
        + b"".join(FULL_RECORD.pack(*record) for record in records)
        + blob[-64:]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source = args.source.read_bytes()
    result = compact(source)
    with args.destination.open("xb") as output:
        output.write(result)
    removed = (len(source) - len(result)) // FULL_RECORD.size
    print(
        f"Removed {removed} redundant records, saved {len(source) - len(result)} bytes"
    )


if __name__ == "__main__":
    main()
