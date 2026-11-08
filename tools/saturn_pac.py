"""Bounded Saturn Pocket Fighter PAC inspector; no speculative decompression."""

from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image, ImageDraw

ALIGN = 0x800


@dataclass(frozen=True)
class Chunk:
    identifier: int
    offset: int
    size: int


def parse(data: bytes) -> tuple[int, list[Chunk]]:
    if len(data) < 8:
        raise ValueError("truncated PAC header")
    count, declared_total = struct.unpack_from(">II", data)
    if not 1 <= count <= (ALIGN - 8) // 8:
        raise ValueError("chunk table does not fit first 0x800 bytes")
    if len(data) < ALIGN:
        raise ValueError("truncated PAC table block")
    offset = ALIGN
    chunks = []
    for index in range(count):
        ident, size = struct.unpack_from(">II", data, 8 + index * 8)
        if offset + size > len(data):
            raise ValueError(f"chunk {index} exceeds input length")
        chunks.append(Chunk(ident, offset, size))
        offset = (offset + size + ALIGN - 1) // ALIGN * ALIGN
    # declared_total is recorded, not assumed to mean physical file length.
    return declared_total, chunks


def palette_image(data: bytes) -> Image.Image:
    if not data or len(data) % 32:
        raise ValueError("RGB555 palette chunk must contain complete 16-word rows")
    rows = len(data) // 32
    image = Image.new("RGB", (16 * 16, rows * 12))
    draw = ImageDraw.Draw(image)
    for row in range(rows):
        for index in range(16):
            word = struct.unpack_from(">H", data, row * 32 + index * 2)[0]
            rgb = tuple(((word >> shift) & 31) * 255 // 31 for shift in (0, 5, 10))
            draw.rectangle(
                (index * 16, row * 12, index * 16 + 15, row * 12 + 11), fill=rgb
            )
    return image


def inspect(path: Path, out: Path) -> dict:
    data = path.read_bytes()
    declared, chunks = parse(data)
    if out.exists():
        raise ValueError("output directory must be new")
    out.mkdir(parents=True)
    report = {
        "input_name": path.name,
        "input_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "declared_total": declared,
        "alignment": ALIGN,
        "sprite_decode": "NOT IMPLEMENTED: codec unconfirmed",
        "palette_assumption": "big-endian words, RGB bits 0..4/5..9/10..14; bit15 retained only in source",
        "chunks": [],
    }
    for index, chunk in enumerate(chunks):
        payload = data[chunk.offset : chunk.offset + chunk.size]
        entry = {
            "id": hex(chunk.identifier),
            "offset": chunk.offset,
            "size": chunk.size,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
        if chunk.identifier in (0x102, 0x105):
            if payload and len(payload) % 32 == 0:
                name = f"{index:02d}-{chunk.identifier:03x}-palettes.png"
                palette_image(payload).save(out / name)
                entry.update(palettes=len(payload) // 32, swatches=name)
            else:
                entry["palette_status"] = "not a whole number of 16-color palettes"
        report["chunks"].append(entry)
    (out / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pac", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.pac, args.out), indent=2))


if __name__ == "__main__":
    main()
