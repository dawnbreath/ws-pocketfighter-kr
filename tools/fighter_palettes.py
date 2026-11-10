"""Optional CTB2 per-fighter palette catalogue; design colours, not game assets."""

from __future__ import annotations
import re
import struct

BASE = 0x7000
LIMIT = 0x8000
ROW_BASE = 0xE00
ROW_SIZE = 24
POINTER_OFFSET = 22


def encode(colors: list[str]) -> bytes:
    if not isinstance(colors, list) or len(colors) != 16:
        raise ValueError("fighter palette needs exactly 16 RGB444 colours")
    if any(
        not isinstance(c, str) or not re.fullmatch("[0-9a-fA-F]{3}", c) for c in colors
    ):
        raise ValueError("palette colours must be three hex RGB444 digits")
    return struct.pack("<16H", *(int(c, 16) for c in colors))


def install(
    bank: bytearray, characters: list[dict], config: dict, scene_end: int
) -> None:
    if config.get("version") != 1 or scene_end > BASE or len(bank) != 0x10000:
        raise ValueError("unsupported palette catalogue or overlapping scene tables")
    names = [c["name"] for c in characters]
    if len(set(names)) != len(names):
        raise ValueError("duplicate character identity")
    palettes = config["fighters"]
    if not isinstance(palettes, dict) or set(palettes) - set(names):
        raise ValueError(
            "palette catalogue names must match existing character identities"
        )
    data = bytearray(encode(config["fallback"]))
    pointers = []
    for name in names:
        if name not in palettes:
            pointers.append(0)
        else:
            pointers.append(BASE + len(data))
            data.extend(encode(palettes[name]))
    if BASE + len(data) > LIMIT or ROW_BASE + len(names) * ROW_SIZE > 0x1000:
        raise ValueError("fighter palette catalogue exceeds reserved space")
    # Validate completely before modifying the bank.
    bank[BASE : BASE + len(data)] = data
    for i, pointer in enumerate(pointers):
        struct.pack_into("<H", bank, ROW_BASE + i * ROW_SIZE + POINTER_OFFSET, pointer)
