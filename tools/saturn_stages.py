"""Read Pocket Fighter's background pattern names, cells and colour RAM from track 1."""

from pathlib import Path

import numpy as np
from PIL import Image
from saturn_pac import parse

LAYERS = (
    (1, 0, 2),
    (2, 0, 1),
    (2, 0, 1),
    (0, 1, 2),
    (0, 1, 2),
    (2, 1, 0),
    (2, 0, 1),
    (2, 1, 0),
)


def stage_files(track: Path) -> list[bytes]:
    with track.open("rb") as source:

        def read(lba, size):
            source.seek(lba * 2352)
            sectors = source.read(((size + 2047) // 2048) * 2352)
            return b"".join(
                sectors[i + 16 : i + 2064] for i in range(0, len(sectors), 2352)
            )[:size]

        descriptor = read(16, 2048)
        if descriptor[1:6] != b"CD001":
            raise ValueError("expected Saturn Pocket Fighter MODE1/2352 track 1")
        root = descriptor[156:]
        directory = read(
            int.from_bytes(root[2:6], "little"), int.from_bytes(root[10:14], "little")
        )
        entries = {}
        start = 0
        while start < len(directory):
            length = directory[start]
            if not length:
                start = (start // 2048 + 1) * 2048
                continue
            record = directory[start : start + length]
            name = record[33 : 33 + record[32]].split(b";")[0]
            entries[name] = (
                int.from_bytes(record[2:6], "little"),
                int.from_bytes(record[10:14], "little"),
            )
            start += length
        return [read(*entries[f"ST{stage:02}.PAC".encode()]) for stage in range(8)]


def reference_image(pac: bytes, stage: int) -> Image.Image:
    blocks = {c.identifier: pac[c.offset : c.offset + c.size] for c in parse(pac)[1]}
    colours = np.frombuffer(blocks[0x200], ">u2")
    rgb = np.stack([((colours >> s) & 31) * 255 // 31 for s in (0, 5, 10)], axis=1)
    rgb = rgb.reshape(96, 16, 3).astype("u1")
    raw = np.frombuffer(blocks[0x201], "u1")
    tiles = np.stack((raw >> 4, raw & 15), axis=-1).reshape(-1, 8, 8)
    composite = Image.new("RGBA", (1024, 512))
    for depth, layer in enumerate(LAYERS[stage]):
        width = 64 if layer == 0 else 32
        pixels = 512 // width
        for page, names in enumerate(
            np.frombuffer(blocks[0x202 + layer], ">u2").reshape(-1, width, width, 2)
        ):
            flags = names[..., 0]
            index = names[..., 1].astype(int) - 0x2000
            valid = (index >= 0) & (index <= len(tiles) - (1 if layer == 0 else 4))
            index[~valid] = 0
            if layer == 0:
                cells = tiles[index]
            else:
                cells = np.concatenate(
                    [
                        np.concatenate((tiles[index + j], tiles[index + j + 1]), axis=3)
                        for j in (0, 2)
                    ],
                    axis=2,
                )
            cells = np.where(
                (flags & 0x4000)[:, :, None, None], cells[:, :, :, ::-1], cells
            )
            cells = np.where(
                (flags & 0x8000)[:, :, None, None], cells[:, :, ::-1, :], cells
            )
            palette = np.clip((flags.astype(int) & 127) - 32, 0, 95)
            dots = rgb[palette[:, :, None, None], cells]
            alpha = ((cells != 0) & valid[:, :, None, None]) * 255
            rgba = np.concatenate((dots, alpha[:, :, :, :, None].astype("u1")), axis=-1)
            image = Image.fromarray(
                rgba.transpose(0, 2, 1, 3, 4).reshape(width * pixels, width * pixels, 4)
            )
            composite.alpha_composite(image, (page * 512, 0))
        if depth == 0:
            # Scroll planes have different extents. Extend only the distant
            # plane across its missing margins before compositing near objects.
            back = np.array(composite)
            rows = np.flatnonzero(back[:, :, 3].any(axis=1))
            for y in rows:
                valid = np.flatnonzero(back[y, :, 3])
                for channel in range(3):
                    back[y, :, channel] = np.interp(
                        np.arange(back.shape[1]), valid, back[y, valid, channel]
                    )
            if len(rows):
                lookup = np.abs(np.arange(512)[:, None] - rows).argmin(axis=1)
                back = back[rows[lookup]]
                back[:, :, 3] = 255
                composite = Image.fromarray(back)
    return composite.crop((0, 128, 640, 512))


def stage_actors(pac: bytes, frame_ids: set[int]) -> dict[int, Image.Image]:
    """Decode the stage PAC's column-major 16x16 VDP1 sprite layouts."""
    import struct

    blocks = {c.identifier: pac[c.offset : c.offset + c.size] for c in parse(pac)[1]}
    art, layouts = blocks[0x106], blocks[0x107]
    colours = np.frombuffer(blocks[0x108], ">u2")
    rgb = np.stack([((colours >> s) & 31) * 255 // 31 for s in (0, 5, 10)], -1)
    rgb = rgb.astype("u1").reshape(-1, 16, 3)
    frames = {}
    for index in frame_ids:
        if not 0 <= index < int.from_bytes(layouts[:2], "big") // 3:
            raise ValueError(f"invalid stage actor frame {index}")
        base, w, h, _, _, count, _ = struct.unpack_from(">HBBhhHH", layouts, index * 12)
        start = base * 4
        size = (w * h + 31) // 32 * 4
        occupied = np.unpackbits(np.frombuffer(layouts, "u1", size, start))[: w * h]
        slots = np.flatnonzero(occupied)
        if len(slots) != count:
            raise ValueError(f"invalid cell count in stage actor frame {index}")
        cells = np.frombuffer(layouts, ">u4", count, start + size)
        rgba = np.zeros((h * 16, w * 16, 4), "u1")
        for slot, cell in zip(slots, cells):
            entry = int(cell)
            bank = ((entry >> 24) & 31) - 26
            if not 0 <= bank < len(rgb):
                raise ValueError(f"invalid actor palette {bank}")
            data = np.frombuffer(art, "u1", 128, entry & 0x7FFFF)
            pixels = np.stack((data >> 4, data & 15), -1).reshape(16, 16)
            if entry & 0x40000000:
                pixels = pixels[:, ::-1]
            if entry & 0x80000000:
                pixels = pixels[::-1]
            x, y = divmod(int(slot), h)
            tile = rgba[y * 16 : (y + 1) * 16, x * 16 : (x + 1) * 16]
            tile[..., :3] = rgb[bank, pixels]
            tile[..., 3] = (pixels != 0) * 255
        image = Image.fromarray(rgba)
        frames[index] = image.crop(image.getbbox())
    return frames
