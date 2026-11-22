"""Check a T77 Mednafen battle snapshot against its paired 224x144 LCD capture."""

import argparse
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image

from stage_backgrounds import BLOCK, FIRST_TILE, PALETTE_BYTES, STAGE_BANK, TILE_DATA


def field(snapshot: bytes, name: str) -> bytes:
    key = bytes([len(name)]) + name.encode()
    offset = snapshot.index(key) + len(key)
    size = struct.unpack_from("<I", snapshot, offset)[0]
    if offset + 4 + size > len(snapshot):
        raise ValueError(f"truncated state field {name}")
    return snapshot[offset + 4 : offset + 4 + size]


def plane(ram: bytes, address: int, sx: int, sy: int) -> tuple:
    y, x = np.mgrid[:144, :224]
    x, y = (x + sx) % 256, (y + sy) % 256
    tilemap = np.frombuffer(ram, "<u2", 1024, address).reshape(32, 32)
    cell = tilemap[y // 8, x // 8]
    px = np.where(cell & 0x4000, 7 - x % 8, x % 8)
    py = np.where(cell & 0x8000, 7 - y % 8, y % 8)
    off = (
        0x4000
        + np.where(cell & 0x2000, 0x4000, 0)
        + 32 * (cell.astype(int) & 511)
        + py * 4
    )
    memory = np.frombuffer(ram, "u1")
    index = sum(((memory[off + i] >> (7 - px) & 1) << i) for i in range(4))
    palette = np.frombuffer(ram[0xFE00:], "<u2").reshape(16, 16)
    word = palette[(cell >> 9) & 15, index]
    rgb = np.stack([((word >> s) & 15) * 17 for s in (8, 4, 0)], axis=2).astype("u1")
    return rgb, index, cell


def check(rom: bytes, snapshot: bytes, lcd: Image.Image) -> dict:
    ram = field(snapshot, "RAM")
    stage = struct.unpack_from("<H", field(snapshot, "SRAM"), 0x3000)[0]
    if stage >= 8 or lcd.size != (224, 144):
        raise ValueError("need a battle state and matching native LCD")

    def register(name):
        return field(snapshot, name)[0]

    loc = register("FGBGLoc")
    rgb, _, bg = plane(
        ram, (loc & 15) * 2048, register("BGXScroll"), register("BGYScroll")
    )
    _, fg, _ = plane(
        ram, (loc >> 4) * 2048, register("FGXScroll"), register("FGYScroll")
    )
    visible = fg == 0
    y, x = np.arange(144), np.arange(224)
    # The last LCD may contain sprites from either latched list while the CPU
    # is preparing the next OAM. Exclude the union for a strict BG-only check.
    oam = np.frombuffer(ram, "u1", 512, register("SPRBase") * 512).reshape(128, 4)
    slots = (register("SpriteStart") + np.arange(register("SpriteCount"))) % 128
    tables = [oam[slots]]
    for suffix in ("", "1"):
        count = int.from_bytes(field(snapshot, "SpriteCountCache" + suffix), "little")
        tables.append(
            np.frombuffer(field(snapshot, "SpriteTable" + suffix), "u1").reshape(
                128, 4
            )[:count]
        )
    for sprites in tables:
        for _, _, py, px in sprites:
            visible &= ~(
                ((y - int(py)) % 256 < 8)[:, None] & ((x - int(px)) % 256 < 8)[None, :]
            )
    start = (STAGE_BANK << 16) + stage * BLOCK
    size = struct.unpack_from("<H", rom, start + PALETTE_BYTES)[0] * 2
    destination = 0x8000 + FIRST_TILE * 32
    if (
        not size
        or rom[start + TILE_DATA : start + TILE_DATA + size]
        != ram[destination : destination + size]
    ):
        raise ValueError("stage tile upload differs from the cartridge")
    if not any(
        ram[0xFE00:0xFE80] == rom[start + i * 128 : start + (i + 1) * 128]
        for i in range(16)
    ):
        raise ValueError("stage palette differs from all sixteen brightness tables")
    matching = (rgb == np.asarray(lcd.convert("RGB"))).all(axis=2)
    fixed = visible & ((bg & 0x2000) != 0)
    live = visible & ((bg & 0x2000) == 0) & (((bg >> 9) & 15) < 4)
    if not fixed.any() or not live.any() or not matching[fixed | live].all():
        raise ValueError(
            "LCD background differs from the captured map, tiles or palette"
        )
    return dict(
        stage=stage,
        scroll=register("BGXScroll"),
        static_pixels=int(fixed.sum()),
        animated_slot_pixels=int(live.sum()),
        tile_bytes=size,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("rom", "snapshot", "lcd"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    with Image.open(args.lcd) as image:
        print(
            json.dumps(check(args.rom.read_bytes(), args.snapshot.read_bytes(), image))
        )
