"""Build coloured static tiles from the cartridge's eight battle descriptors.

Only the stage loader writes tile bank 1. Animated cells retain their original
bank, pattern number and flips, so the game's animation commands still apply.
"""

import json
import os
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from paths import ROOT
from saturn_stages import reference_image, stage_files

DESCRIPTORS = 0x148C50
STAGE_BANK = 0x0E
BLOCK = 0x4000
FIRST_TILE = 64
PALETTE_BYTES = 16 * 128
TILE_DATA = PALETTE_BYTES + 4
MATERIALS = Path(ROOT) / "data/stages/saturn-materials.json"


def word(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def rgb444(value: str) -> list[int]:
    return [int(c, 16) for c in value]


def material_map(spec: dict, tones: np.ndarray) -> tuple[list[str], np.ndarray]:
    names = list(spec["materials"])
    im = Image.new("L", (tones.shape[1], tones.shape[0]), names.index(spec["base"]))
    draw = ImageDraw.Draw(im)
    for name, polygon in spec["regions"]:
        draw.polygon(
            [(round(x * 8), round(y * 8)) for x, y in polygon], names.index(name)
        )
    classes = np.asarray(im).copy()
    # Snap a guide that just crosses a flat pixel cluster to its actual outline.
    seen = np.zeros_like(tones, dtype=bool)
    height, width = tones.shape
    for y, x in np.ndindex(tones.shape):
        if seen[y, x]:
            continue
        value = tones[y, x]
        points = [(y, x)]
        seen[y, x] = True
        for py, px in points:
            for ny, nx in ((py - 1, px), (py + 1, px), (py, px - 1), (py, px + 1)):
                if (
                    0 <= ny < height
                    and 0 <= nx < width
                    and not seen[ny, nx]
                    and tones[ny, nx] == value
                ):
                    seen[ny, nx] = True
                    points.append((ny, nx))
        iy, ix = np.asarray(points).T
        counts = np.bincount(classes[iy, ix])
        if counts.max() >= len(points) * 0.65:
            classes[iy, ix] = counts.argmax()
    return names, classes


def encode_tile(indices: np.ndarray) -> bytes:
    bitplanes = indices[:, None, :] >> np.arange(4)[None, :, None] & 1
    return np.packbits(bitplanes, axis=2).tobytes()


def registered_colours(
    reference: Image.Image, landmarks: list, tones: np.ndarray, fallback: np.ndarray
) -> np.ndarray:
    """Transfer local colour and illumination while retaining native WS edges."""
    height, width = tones.shape
    y, x = np.mgrid[:height, :width]
    marks = np.array(landmarks, dtype=float) * 8
    # Nearby named landmarks carry most of the displacement. Clamp the weight
    # at half a tile to keep the transform smooth at a control point.
    delta = np.stack((x, y), axis=-1)[..., None, :] - marks[:, :2]
    weights = 1 / (np.sum(delta**2, axis=-1) + 16) ** 1.5
    shift = (weights @ (marks[:, 2:] - marks[:, :2])) / weights.sum(axis=-1)[..., None]
    sx = np.clip(
        np.rint((x + shift[..., 0]) * reference.width / width).astype(int),
        0,
        reference.width - 1,
    )
    sy = np.clip(
        np.rint((y + shift[..., 1]) * reference.height / height).astype(int),
        0,
        reference.height - 1,
    )
    ref = np.asarray(reference)[sy, sx]
    # Where parallax leaves no source pixel, extend the nearest true background
    # colour in the same scanline. Entirely empty scanlines use the art guide.
    target = fallback.copy()
    for row in range(height):
        good = np.flatnonzero(ref[row, :, 3])
        if len(good):
            for channel in range(3):
                target[row, :, channel] = np.interp(
                    x[row], good, ref[row, good, channel]
                )
    source = np.asarray(
        Image.fromarray(target).filter(ImageFilter.GaussianBlur(2.8)), dtype=float
    )
    mono = np.uint8(tones * 36)
    local = np.asarray(
        Image.fromarray(mono).filter(ImageFilter.GaussianBlur(3.4)), dtype=float
    )
    contrast = mono.astype(float) - local
    # Remove Saturn raster detail at the portable pixel scale. WS strokes and
    # silhouette boundaries supply the high-frequency luminance information.
    rgb = source + contrast[..., None] * 0.93
    return np.clip(np.rint(rgb / 17), 0, 15).astype("u1")


def fit_palettes(
    target: np.ndarray, primary: np.ndarray, initial: np.ndarray
) -> np.ndarray:
    """Quantize reference colours by tile, respecting the per-cell palette latch."""
    groups = initial.copy()
    tiles = target.reshape(-1, 8, 8, 3)
    for _ in range(3):
        palettes = []
        for bank in range(4):
            pixels = tiles[groups == bank]
            if not len(pixels):
                pixels = tiles
            strip = Image.fromarray((pixels * 17).reshape(-1, 8, 3))
            reduced = strip.quantize(
                colors=11, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
            )
            colours = np.array(reduced.getpalette()[:33]).reshape(11, 3)
            colours = np.rint(colours / 17).clip(0, 15).astype(int)
            row = primary[bank]
            palettes.append(np.array([*row[::-1], row[3], *colours]))
        palettes = np.array(palettes)
        # RGB444 limits the input alphabet to 4096 values.
        grid = np.indices((16, 16, 16)).reshape(3, -1).T
        costs = ((grid[:, None, None] - palettes[None, :, 1:]) ** 2 * [2, 3, 1]).sum(
            axis=-1
        )
        keys = (
            tiles[..., 0].astype(int) * 256
            + tiles[..., 1].astype(int) * 16
            + tiles[..., 2]
        )
        groups = costs.min(axis=-1)[keys].sum(axis=(1, 2)).argmin(axis=1)
    return palettes


def pack_static_cells(
    pending: dict, palettes: np.ndarray, mapped: np.ndarray, rendered: np.ndarray
) -> bytearray:
    """Select extra colour variants where they buy the greatest error reduction.

    Candidates compete only among instances of the same native tile. Flips
    are normalized first, so a capacity limit cannot substitute another drawing.
    """
    from heapq import heappush, heappop

    capacity = min(512 - FIRST_TILE, (BLOCK - TILE_DATA) // 32)
    heap = []
    groups = []
    for rows in pending.values():
        targets = np.stack([r[3] for r in rows]).astype(int)
        variants = np.unique(np.stack([r[4] for r in rows]), axis=0)
        cost = np.zeros((len(variants), len(rows), 4), dtype="i4")
        for i, pattern in enumerate(variants):
            colours = palettes[:, pattern]
            cost[i] = (((colours[None] - targets[:, None]) ** 2) * [2, 3, 1]).sum(
                axis=(2, 3, 4)
            )
        errors = cost.min(axis=2)
        first = int(errors.sum(axis=1).argmin())
        groups.append([rows, variants, cost, errors, [first], errors[first].copy()])

    def enqueue(group_index):
        rows, variants, cost, errors, chosen, best = groups[group_index]
        gain = np.maximum(best - errors, 0).sum(axis=1)
        i = int(gain.argmax())
        if gain[i]:
            heappush(heap, (-int(gain[i]), group_index, i))

    for g in range(len(groups)):
        enqueue(g)
    if len(groups) > capacity:
        raise ValueError("native static tile inventory exceeds bank 1")
    for _ in range(capacity - len(groups)):
        if not heap:
            break
        _, g, i = heappop(heap)
        group = groups[g]
        group[4].append(i)
        group[5] = np.minimum(group[5], group[3][i])
        enqueue(g)
    packed = bytearray()
    dictionary = {}
    for rows, variants, cost, _, chosen, _ in groups:
        for j, (y, x, flip, _, _) in enumerate(rows):
            best_variant, pal = np.unravel_index(
                cost[chosen, j].argmin(), (len(chosen), 4)
            )
            pattern = variants[chosen[best_variant]]
            key = encode_tile(pattern)
            if key not in dictionary:
                dictionary[key] = FIRST_TILE + len(dictionary)
                packed.extend(key)
            mapped[y, x] = 0x2000 | flip | int(pal) << 9 | dictionary[key]
            actual = palettes[pal][pattern]
            if flip & 0x8000:
                actual = actual[::-1]
            if flip & 0x4000:
                actual = actual[:, ::-1]
            rendered[y, x] = actual * 17
    return packed


def compile_stage(
    original: bytes, number: int, spec: dict, reference: Image.Image
) -> tuple[int, np.ndarray, bytes, Image.Image]:
    address = 0x140000 + word(original, DESCRIPTORS + number * 2)
    desc = original[address : address + 38]
    if (
        desc[:3] != b"\x00\x00\xd0"
        or desc[5:8] != b"\x01\x00\xe0"
        or desc[29:34] != bytes.fromhex("0324001a00")
    ):
        raise ValueError(f"unrecognized stage {number} descriptor")
    offset = 0x1D0000 + word(desc, 3)
    tiles = 0x1E0000 + word(desc, 8)
    palette = 0x1E0000 + word(desc, 15)
    static = word(desc, 27)
    width, height = word(desc, 30), word(desc, 32)
    entries = np.frombuffer(original, "<u2", height * 64, offset).reshape(height, 64)[
        :, :width
    ]
    words = np.frombuffer(original, "<u2", 4, palette)
    tile_ids = entries & 511
    # The alternate camera loads use source offsets distinct from their VRAM
    # destinations. Use descriptor animation frames for fitting live cells.
    art = bytearray(original[tiles : tiles + (int(tile_ids.max()) + 1) * 16])
    animation_table = 0x140000 + word(desc, 35)
    for row in (0, 1, 2, 3):
        dest, source, count = struct.unpack_from(
            "<3H", original, animation_table + row * 6
        )
        end = min(dest + count, len(art))
        if end > dest:
            art[dest:end] = original[tiles + source : tiles + source + end - dest]
    raw = np.frombuffer(art, "u1")
    bits = np.unpackbits(raw.reshape(-1, 8, 2), axis=2).reshape(-1, 8, 2, 8)
    cells = (bits[:, :, 0] + 2 * bits[:, :, 1])[tile_ids]
    cells = np.where((entries & 0x8000)[:, :, None, None], cells[:, :, ::-1], cells)
    cells = np.where((entries & 0x4000)[:, :, None, None], cells[:, :, :, ::-1], cells)
    shades = words[(entries >> 9) & 15][:, :, None, None] >> (cells.astype(int) * 4) & 7
    tones = shades.transpose(0, 2, 1, 3).reshape(height * 8, width * 8)
    names, classes = material_map(spec, tones)
    ramps = np.array([[rgb444(c) for c in spec["materials"][n]] for n in names])
    # Preserve the contrast of the WS linework within each painted material.
    level = np.clip(np.rint((tones.astype(float) - 1) * 0.6), 0, 3).astype(int)
    fallback = (ramps[classes, level] * 17).astype("u1")
    pixels = registered_colours(reference, spec["landmarks"], tones, fallback)
    target = pixels.reshape(height, 8, width, 8, 3).transpose(0, 2, 1, 3, 4)
    primary = np.array([ramps[names.index(bank[0])] for bank in spec["banks"]])
    animated = tile_ids >= static
    if np.any(animated):
        guide = primary.copy()
        samples = cells[animated]
        desired = target[animated].astype(int)
        for _ in range(3):
            difference = primary[:, ::-1][:, samples] - desired[None]
            owners = (difference**2 * [2, 3, 1]).sum(axis=(2, 3, 4)).argmin(axis=0)
            for bank, ramp in enumerate(primary):
                for shade in range(4):
                    values = desired[
                        (owners == bank)[:, None, None] & (samples == shade)
                    ]
                    if len(values):
                        # Retain a small material prior for rarely used shades.
                        ramp[3 - shade] = np.rint(
                            (values.sum(axis=0) + 32 * guide[bank, 3 - shade])
                            / (len(values) + 32)
                        )
    init_classes = classes.reshape(height, 8, width, 8).transpose(0, 2, 1, 3)[
        :, :, 4, 4
    ]
    owner = [
        next(i for i, bank in enumerate(spec["banks"]) if name in bank)
        for name in names
    ]
    palettes = fit_palettes(target, primary, np.array(owner)[init_classes].ravel())
    mapped = entries.copy()
    pending = {}
    rendered = np.zeros_like(target, dtype="u1")
    for y, x in np.ndindex(entries.shape):
        cell = target[y, x].astype(int)
        # RGB444 error over the visible tile, with a heavier green luminance weight.
        distances = np.sum(
            (cell[None, :, :, None, :] - palettes[:, None, None]) ** 2 * [2, 3, 1],
            axis=-1,
        )
        if tile_ids[y, x] >= static:
            # Animated tiles keep the loader's live image. Choose a material row
            # by the whole cell, constrained to its original four shade indices.
            cols = palettes[:, cells[y, x]]
            errors = ((cols - cell) ** 2 * [2, 3, 1]).sum(axis=(1, 2, 3))
            pal = int(errors.argmin())
            mapped[y, x] = (int(entries[y, x]) & ~0x1E00) | pal << 9
            rendered[y, x] = cols[pal] * 17
            continue
        distances[..., 0] = 8192  # hardware index zero is transparent
        pal = int(distances.min(axis=-1).sum(axis=(1, 2)).argmin())
        indices = distances[pal].argmin(axis=-1)
        flip = int(entries[y, x]) & 0xC000
        if flip & 0x8000:
            cell, indices = cell[::-1], indices[::-1]
        if flip & 0x4000:
            cell, indices = cell[:, ::-1], indices[:, ::-1]
        pending.setdefault(int(tile_ids[y, x]), []).append((y, x, flip, cell, indices))
    packed = pack_static_cells(pending, palettes, mapped, rendered)
    # One table per effective brightness. The unmodified palette-zero port and
    # shade LUT supply the brightness key, including the game's dim/flash modes.
    nominal = [15, 13, 11, 9, 7, 5, 3, 0]
    normal = (
        sum(nominal[7 - (int(words[0]) >> shift & 7)] for shift in (0, 4, 8, 12)) // 4
    )
    lut = bytearray()
    for brightness in range(16):
        if brightness < normal:
            rgb = np.rint(palettes * brightness / normal)
        else:
            rgb = np.rint(
                palettes + (15 - palettes) * (brightness - normal) / (15 - normal)
            )
        rgb = rgb.astype("<u2")
        lut.extend(
            ((rgb[..., 0] << 8) | (rgb[..., 1] << 4) | rgb[..., 2])
            .astype("<u2")
            .tobytes()
        )
    payload = lut + struct.pack("<HH", len(packed) // 2, normal * 128) + packed
    preview = rendered.transpose(0, 2, 1, 3, 4).reshape(height * 8, width * 8, 3)
    return offset, mapped, payload, Image.fromarray(preview)


def reference_track() -> Path:
    default = (
        Path(ROOT) / "work/saturn-reference/disc/Pocket Fighter (Japan) (Track 01).bin"
    )
    return Path(os.environ.get("PF_SATURN_TRACK", default))


def install(rom, assemble, far):
    stages = json.loads(MATERIALS.read_text())
    if len(stages) != 8:
        raise ValueError("expected eight battle stages")
    sources = stage_files(reference_track())
    for number, spec in enumerate(stages):
        offset, mapped, payload, _ = compile_stage(
            rom.orig, number, spec, reference_image(sources[number], number)
        )
        address = (STAGE_BANK << 16) + number * BLOCK
        if rom.b[address : address + BLOCK] != b"\xff" * BLOCK:
            raise ValueError("stage data overlaps an allocated ROM bank")
        rom.b[address : address + len(payload)] = payload
        for row, entries in enumerate(mapped):
            start = rom.o4(offset + row * 128)
            rom.b[start : start + entries.nbytes] = entries.astype("<u2").tobytes()
    loader, _ = assemble("stage_load")
    lighting, _ = assemble("stage_light")
    rom.put_free(0x17FF63, lighting, "battle background brightness lookup")
    rom.put_free(0x16FF51, loader, "battle background tile upload")
    rom.patch(
        0x148787,
        "c70626110000",
        far(0x6000, 0xFF51) + b"\x90",
        "stage descriptor dispatch completed",
    )
