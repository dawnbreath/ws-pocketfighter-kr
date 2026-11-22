"""Build coloured static tiles from the cartridge's eight battle descriptors.

Only the stage loader writes tile bank 1. Resolve the two camera-dependent
source sets before packing coloured tiles for the handheld world map.
"""

import json
import os
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from paths import ROOT
from saturn_stages import reference_image, stage_actors, stage_files

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


def spectator_colours(
    reference: Image.Image,
    frames: dict[int, Image.Image],
    figures: list[dict],
    tones: np.ndarray,
    target: np.ndarray,
) -> tuple[np.ndarray, dict[tuple[int, int], list[int]]]:
    """Register scenery details first, then paint the guests in front of them."""
    height, width = tones.shape
    # Preserve the handheld's linework inside each local colour sample.
    mono = Image.fromarray((tones * 36).astype("u1"))
    detail = np.asarray(mono, dtype=float) - np.asarray(
        mono.filter(ImageFilter.GaussianBlur(1.25))
    )
    importance = np.ones(tones.shape, dtype="u1")
    fixed = {}
    for figure in figures:
        x, y, right, bottom = figure["ws"]
        if not (0 <= x < right <= width and 0 <= y < bottom <= height):
            raise ValueError(f"invalid WS bounds for {figure['name']}")
        is_prop = "detail" in figure
        if "frame" in figure:
            source = frames[figure["frame"]]
        else:
            box = [
                v * scale
                for v, scale in zip(
                    figure["detail"] if is_prop else figure["background"],
                    (reference.width / width, reference.height / height) * 2,
                )
            ]
            source = reference.crop(tuple(round(v) for v in box))
        size = (right - x, bottom - y)
        filter_mode = Image.Resampling.BOX if is_prop else Image.Resampling.NEAREST
        sample = np.asarray(source.resize(size, filter_mode), dtype=float)
        weights = importance[y:bottom, x:right]
        weights[sample[..., 3] > 0] = 4 if is_prop else 12
        if "swatches" in figure:
            row = figure["row"]
            for slot, colour in enumerate(figure["swatches"], 5):
                fixed[row, slot] = rgb444(colour)
            weights[sample[..., 3] > 0] = 40
        alpha = sample[..., 3:] / 255
        rgb = sample[..., :3] + 0.38 * detail[y:bottom, x:right, None]
        if is_prop:
            # Keep small WS strokes. Reduce the Saturn luminance edges that would
            # otherwise draw the same outline again a pixel or two away.
            light = Image.fromarray(sample[..., :3].astype("u1")).convert("L")
            relief = np.asarray(light, dtype=float) - np.asarray(
                light.filter(ImageFilter.GaussianBlur(1.25))
            )
            contrast = 0.85 * detail[y:bottom, x:right] - 0.65 * relief
            rgb = sample[..., :3] + contrast[..., None]
            iy, ix = np.indices((bottom - y, right - x))
            edge = np.minimum.reduce(
                [iy + 1, bottom - y - iy, ix + 1, right - x - ix]
            )
            alpha *= np.minimum(edge / 3, 1)[..., None]
        if "frame" in figure:
            # The ports redraw moving guests in different poses. Transfer their
            # colours while keeping the WS drawing's own light/dark structure.
            light = sample[..., :3] @ [0.299, 0.587, 0.114]
            native = tones[y:bottom, x:right].astype(float) * 36
            occupied = alpha[..., 0] > 0
            if occupied.any():
                shift = light[occupied].mean() - native[occupied].mean()
                rgb = sample[..., :3] + 0.8 * (native + shift - light)[..., None]
        if "background" in figure and "swatches" in figure:
            # Retain identifying colours in the sampled guest even when nearby
            # scenery competes for the same per-tile palette.
            snapped = np.rint(sample[..., :3] / 17).astype("u1")
            for colour in figure["swatches"]:
                exact = (snapped == rgb444(colour)).all(axis=-1) & (alpha[..., 0] > 0)
                rgb[exact] = np.array(rgb444(colour)) * 17
                weights[exact] = 180
        old = target[y:bottom, x:right]
        old[:] = np.rint(np.clip(rgb / 17, 0, 15) * alpha + old * (1 - alpha))
        for colour, line, start, end in figure.get("accents", ()):
            if not (
                0 <= line < size[1]
                and 0 <= start < end <= size[0]
                and colour in figure["swatches"]
            ):
                raise ValueError(f"invalid colour accent for {figure['name']}")
            old[line, start:end] = rgb444(colour)
            weights[line, start:end] = 160
    return importance, fixed


def fit_palettes(
    target: np.ndarray,
    primary: np.ndarray,
    initial: np.ndarray,
    weights: np.ndarray | None = None,
    fixed: dict | None = None,
) -> np.ndarray:
    """Quantize reference colours by tile, respecting the per-cell palette latch."""
    tiles = target.reshape(-1, 8, 8, 3)
    groups = initial.ravel()
    palettes = []
    for bank, row in enumerate(primary):
        sample = tiles[groups == bank]
        if not len(sample):
            sample = tiles
        strip = Image.fromarray((sample * 17).reshape(-1, 8, 3))
        seed = strip.quantize(colors=11, method=Image.Quantize.MEDIANCUT)
        colours = np.array(seed.getpalette()[:33]).reshape(-1, 3)
        colours = np.pad(colours, ((0, 11 - len(colours)), (0, 0)), mode="edge")
        palettes.append([*row[::-1], row[3], *np.rint(colours / 17).astype(int)])
    palettes = np.array(palettes)
    # Keep the four base shades and their opaque zero alias. Static tiles can
    # also use those colours; the other slots fit the stage and its spectators.
    rgb = np.indices((16, 16, 16)).reshape(3, -1).T
    keys = tiles.astype(int) @ [256, 16, 1]
    fixed = fixed or {}
    for (bank, slot), colour in fixed.items():
        palettes[bank, slot] = colour
    previous_loss = None
    for _ in range(32):
        distances = ((rgb[:, None, None] - palettes[None, :, 1:]) ** 2 * [2, 3, 1]).sum(
            axis=-1
        )
        cost = distances.min(axis=-1)
        tile_cost = (
            cost[keys] if weights is None else cost[keys] * weights[..., None]
        ).sum(axis=(1, 2))
        groups = tile_cost.argmin(axis=1)
        loss = tile_cost.min(axis=1).sum()
        if loss == previous_loss:
            break
        previous_loss = loss
        for bank in range(len(palettes)):
            mask = groups == bank
            counts = np.bincount(
                keys[mask].ravel(),
                weights=None if weights is None else weights[mask].ravel(),
                minlength=len(rgb),
            )
            assigned = distances[:, bank].argmin(axis=1) + 1
            residual = counts * cost[:, bank]
            for slot in range(5, 16):
                if (bank, slot) in fixed:
                    continue
                mass = counts * (assigned == slot)
                if mass.any():
                    palettes[bank, slot] = np.rint((mass @ rgb) / mass.sum())
                elif residual.any():
                    # Reuse a redundant slot for a frequently misrepresented colour.
                    worst = residual.argmax()
                    palettes[bank, slot] = rgb[worst]
                    residual[worst] = 0
    return palettes


def pack_static_cells(
    pending: dict,
    palettes: np.ndarray,
    mapped: np.ndarray,
    displayed_indices: np.ndarray,
    weights: np.ndarray | None = None,
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
        importance = (
            1
            if weights is None
            else np.stack(
                [
                    weights[y, x][
                        :: -1 if flip & 0x8000 else 1, :: -1 if flip & 0x4000 else 1
                    ]
                    for y, x, flip, _, _ in rows
                ]
            )[:, None, :, :, None]
        )
        for i, pattern in enumerate(variants):
            colours = palettes[:, pattern]
            cost[i] = (
                ((colours[None] - targets[:, None]) ** 2) * [2, 3, 1] * importance
            ).sum(axis=(2, 3, 4))
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
            actual = pattern
            if flip & 0x8000:
                actual = actual[::-1]
            if flip & 0x4000:
                actual = actual[:, ::-1]
            displayed_indices[y, x] = actual
    return packed


def stage_pattern_sources(
    original: bytes, desc: bytes, entries: np.ndarray
) -> np.ndarray:
    """Resolve pattern slots shared by opposite edges of the 36-column world.

    The camera dispatch at 4000:8949 uses three descriptor transfers for
    each side. Only six columns at either edge reference streamed patterns.
    Two identical VRAM indices may therefore denote different ROM drawings.
    """
    ids = (entries & 511).astype(int)
    threshold = word(desc, 27)
    sources = np.where(ids < threshold, ids, -1)
    table = 0x140000 + word(desc, 35)
    x = np.arange(entries.shape[1])
    for slot in range(6):
        dest, source, count = struct.unpack_from("<3H", original, table + 6 * slot)
        if (dest | source | count) & 15:
            raise ValueError("unaligned stage pattern transfer")
        side = x < 6 if slot < 3 else x >= entries.shape[1] - 6
        selected = side & (ids >= dest // 16) & (ids < (dest + count) // 16)
        if np.any(sources[selected] >= 0):
            raise ValueError("overlapping stage pattern sources")
        sources[selected] = ids[selected] + (source - dest) // 16
    if np.any(sources < 0):
        raise ValueError("stage cell has no source on its side of the map")
    return sources


def compile_stage(
    original: bytes,
    number: int,
    spec: dict,
    reference: Image.Image,
    figures: tuple[list[dict], dict[int, Image.Image]] | None = None,
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
    width, height = word(desc, 30), word(desc, 32)
    entries = np.frombuffer(original, "<u2", height * 64, offset).reshape(height, 64)[
        :, :width
    ]
    words = np.frombuffer(original, "<u2", 4, palette)
    tile_ids = stage_pattern_sources(original, desc, entries)
    raw = np.frombuffer(original, "u1", (int(tile_ids.max()) + 1) * 16, tiles)
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
    importance = np.ones(tones.shape, dtype="u1")
    fixed = {}
    if figures is not None:
        records, frames = figures
        importance, fixed = spectator_colours(reference, frames, records, tones, pixels)
    weights = importance.reshape(height, 8, width, 8).transpose(0, 2, 1, 3)
    target = pixels.reshape(height, 8, width, 8, 3).transpose(0, 2, 1, 3, 4)
    primary = np.array([ramps[names.index(bank[0])] for bank in spec["banks"]])
    init_classes = classes.reshape(height, 8, width, 8).transpose(0, 2, 1, 3)[
        :, :, 4, 4
    ]
    owner = [
        next(i for i, bank in enumerate(spec["banks"]) if name in bank)
        for name in names
    ]
    palettes = fit_palettes(
        target,
        primary,
        np.array(owner)[init_classes],
        weights.reshape(-1, 8, 8),
        fixed,
    )
    mapped = entries.copy()
    pending = {}
    displayed_indices = cells.copy()
    for y, x in np.ndindex(entries.shape):
        cell = target[y, x].astype(int)
        # RGB444 error over the visible tile, with a heavier green luminance weight.
        distances = np.sum(
            (cell[None, :, :, None, :] - palettes[:, None, None]) ** 2 * [2, 3, 1],
            axis=-1,
        )
        distances[..., 0] = 8192  # hardware index zero is transparent
        pal = int((distances.min(axis=-1) * weights[y, x]).sum(axis=(1, 2)).argmin())
        indices = distances[pal].argmin(axis=-1)
        flip = int(entries[y, x]) & 0xC000
        if flip & 0x8000:
            cell, indices = cell[::-1], indices[::-1]
        if flip & 0x4000:
            cell, indices = cell[:, ::-1], indices[:, ::-1]
        pending.setdefault(int(tile_ids[y, x]), []).append((y, x, flip, cell, indices))
    packed = pack_static_cells(pending, palettes, mapped, displayed_indices, weights)
    # Shared patterns can make a slot represent several originally distinct
    # colours. Refit those slots using the indices the packed map actually draws.
    banks = ((mapped >> 9) & 15)[:, :, None, None]
    for bank in range(4):
        for slot in range(5, 16):
            if (bank, slot) in fixed:
                continue
            mask = (banks == bank) & (displayed_indices == slot)
            samples = target[mask]
            if len(samples):
                palettes[bank, slot] = np.rint(
                    np.average(samples, axis=0, weights=weights[mask])
                )
    rendered = (palettes[banks, displayed_indices] * 17).astype("u1")
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
    spectators = json.loads(MATERIALS.with_name("spectators.json").read_text())
    details = json.loads(MATERIALS.with_name("details.json").read_text())
    if len(spectators) != len(stages) or len(details) != len(stages):
        raise ValueError("expected scenery and spectator lists for each stage")
    for number, spec in enumerate(stages):
        figures = details[number] + spectators[number]
        frames = stage_actors(
            sources[number], {f["frame"] for f in figures if "frame" in f}
        )
        offset, mapped, payload, _ = compile_stage(
            rom.orig,
            number,
            spec,
            reference_image(sources[number], number),
            (figures, frames),
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
