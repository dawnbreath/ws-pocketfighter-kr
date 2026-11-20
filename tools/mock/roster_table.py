"""Export registered roster drawings using exact, explicitly ordered tile donors.

All captures, masks and output tables are private game-derived data. Reuse is
limited to identical 16-byte sources. No nearest-pose or component prediction.
"""

from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys
from types import ModuleType
import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parents[1])]
from class_table import hash16
from sharded_colour_table import (
    read_catalogue,
    write_shards,
    write_context_shards,
    catalogue_digest,
    read_context_overrides,
)
from compact_colour_table import fallback_output
from segment_frames import compose
from seed_recipe import crop_md5
import roster_colours


def pixels(blob: bytes) -> np.ndarray:
    return np.array(
        [
            sum(((blob[y * 4 + p] >> (7 - x)) & 1) << p for p in range(4))
            for y in range(8)
            for x in range(8)
        ],
        dtype=np.uint8,
    )


def encode(values: np.ndarray) -> bytes:
    return bytes(
        sum(((int(values[y * 8 + x]) >> p) & 1) << (7 - x) for x in range(8))
        for y in range(8)
        for p in range(4)
    )


def build(
    manifest: Path,
    baseline: Path,
    fallback: Path,
    source_rom: Path,
    out: Path,
    accept_reference_tiles: bool = False,
    family_module: ModuleType = roster_colours,
    context: int = 0,
    protection_manifests: list[Path] | None = None,
) -> dict:
    spec = json.loads(manifest.read_text())
    rom = source_rom.read_bytes()
    rom_hash = hashlib.sha256(rom).hexdigest()
    for receipt in spec["stop_receipts"]:
        if not json.loads(Path(receipt).read_text())["stop"]["stopped"]:
            raise ValueError("source emulator stop unconfirmed")
    import colorlib

    names = [c["name"] for c in colorlib.load_spec(colorlib.SPEC)["chars"]]
    lookup = {
        struct.unpack_from("<H", rom, 0xD0D40 + i * 4)[0]: name
        for i, name in enumerate(names)
    }
    old_rows, footer = read_catalogue(baseline)
    retained_contexts = read_context_overrides(baseline)
    protected, _ = read_catalogue(fallback)
    original = {s: o for _, s, o in old_rows}
    old = {**original, **{s: o for _, s, o in protected}}
    if any(o != fallback_output(s) for _, s, o in protected):
        raise ValueError("fallback reference contains nonidentity output")
    canonical = dict(old)
    protected_sources = set()
    if context:
        if (
            context != 1
            or set(family_module.RECIPES) != {"GOUKI"}
            or not protection_manifests
        ):
            raise ValueError(
                "context 1 requires the Gouki family and retained-source manifests"
            )
        for path in protection_manifests:
            previous = json.loads(path.read_text())
            for receipt in previous["stop_receipts"]:
                if not json.loads(Path(receipt).read_text())["stop"]["stopped"]:
                    raise ValueError("protected-source emulator stop unconfirmed")
            for entry in previous["entries"]:
                if entry["character"] != "GOUKI":
                    continue
                cap = json.loads(Path(entry["capture"]).read_text())
                frame = cap["frames"][entry["frame"]]
                full, _, sprites = compose(frame, 4)
                if crop_md5(full)[0] != entry["pose"]:
                    raise ValueError("protected source drawing mismatch")
                protected_sources.update(s["raw"] for s in sprites if s["side"] == 4)
        if not protected_sources:
            raise ValueError("no retained Gouki sources")
        actor = {s: o for _, s, o in read_catalogue(baseline, context)[0]}
        old = {s: actor.get(s, fallback_output(s)) for s in protected_sources}
        old.update((retained_contexts or {}).get(context, {}))
    votes = {}
    drawings = []
    seen = set()
    for entry in spec["entries"]:
        who = entry["character"]
        capture = Path(entry["capture"])
        cap = json.loads(capture.read_text())
        frame = cap["frames"][entry["frame"]]
        if (
            cap.get("ROM_SHA256", cap.get("rom_sha256")) != rom_hash
            or not frame["render_matches"]
            or frame["render_offset"] != [0, 0]
        ):
            raise ValueError("requires coherent, own-ROM source capture")
        raw_hud = bytes.fromhex(frame["vram"])[0x1620:0x1660]
        h = 0
        for (w,) in struct.iter_unpack("<H", raw_hud):
            h = (((h << 3) | (h >> 13)) & 65535) ^ w
        if lookup.get(h) != who:
            raise ValueError("fighter HUD identity mismatch")
        full, owner, sprites = compose(frame, 4)
        key, source = crop_md5(full)
        if key != entry["pose"] or (who, key) in seen:
            raise ValueError("duplicate or mismatched drawing")
        seen.add((who, key))
        indices = family_module.author(who, source)
        yy, xx = np.nonzero(full)
        x0, y0 = int(xx.min()), int(yy.min())
        index = len(drawings)
        drawings.append((who, key, source, indices, x0, y0, owner, sprites))
        for s in sprites:
            if s["side"] != 4:
                continue
            cells = votes.setdefault(s["raw"], [[] for _ in range(64)])
            for y in range(8):
                for x in range(8):
                    gx = (s["x"] + (7 - x if s["word"] & 0x4000 else x)) & 255
                    gy = (s["y"] + (7 - y if s["word"] & 0x8000 else y)) & 255
                    if gx >= 224 or gy >= 144 or owner[gy, gx] != s["rank"]:
                        continue
                    rx, ry = gx - x0, gy - y0
                    value = (
                        int(indices[ry, rx])
                        if 0 <= ry < source.shape[0] and 0 <= rx < source.shape[1]
                        else 0
                    )
                    cells[y * 8 + x].append((value, index, rx, ry))
    required = {
        (name, key)
        for name, recipe in family_module.RECIPES.items()
        for key in recipe["poses"]
    }
    if seen != required:
        raise ValueError("required registered drawings missing")
    records = dict(original)
    all_outputs = dict(old)
    conflicts = []
    for source, cells in votes.items():
        if source in old:
            values = pixels(old[source])
        else:
            missing = [
                i
                for i, cell in enumerate(cells)
                if not cell
                and (source[2 * (i // 8)] | source[2 * (i // 8) + 1])
                & (1 << (7 - i % 8))
            ]
            if missing:
                raise ValueError(
                    f"unobserved opaque tile pixels: {hashlib.sha256(source).hexdigest()} {missing}"
                )
            values = np.array(
                [cell[0][0] if cell else 0 for cell in cells], dtype=np.uint8
            )
        for i, cell in enumerate(cells):
            disagree = [q for q in cell if q[0] != values[i]]
            if disagree:
                conflicts.append(
                    {
                        "source_sha256": hashlib.sha256(source).hexdigest(),
                        "pixel": i,
                        "retained": int(values[i]),
                        "old_output": source in old,
                        "donor": None if source in old else cell[0][1],
                        "changed_votes": len(disagree),
                    }
                )
        output = encode(values)
        all_outputs[source] = output
        if output != fallback_output(source):
            records[source] = output
        else:
            old[source] = output
    if conflicts and not accept_reference_tiles:
        raise ValueError(
            f"{len(conflicts)} exact-tile constraints require explicit donor review"
        )
    variants = {}
    if context:
        contexts = {key: dict(rows) for key, rows in (retained_contexts or {}).items()}
        variants = contexts.setdefault(context, {})
        for source, output in all_outputs.items():
            if output != canonical.get(source, fallback_output(source)):
                variants[source] = output
            else:
                variants.pop(source, None)
        canonical_records = dict(original)
        for rows in contexts.values():
            for source in rows:
                canonical_records.setdefault(
                    source, canonical.get(source, fallback_output(source))
                )
        write_context_shards(list(canonical_records.items()), contexts, footer, out)
        references = {s: o for _, s, o in protected}
        for source in votes:
            if canonical.get(source, fallback_output(source)) == fallback_output(
                source
            ):
                references[source] = fallback_output(source)
        write_shards(list(references.items()), footer, out / "fallback")
    else:
        written = write_shards(
            list(records.items()), footer, out, contexts=retained_contexts
        )
        write_shards(
            [(s, o) for s, o in old.items() if o == fallback_output(s)],
            footer,
            out / "fallback",
        )
    labels = out / "labels"
    labels.mkdir()
    corrections = Counter()
    for who, key, source, proposed, x0, y0, owner, sprites in drawings:
        final = np.zeros_like(source)
        for s in sprites:
            if s["side"] != 4:
                continue
            values = pixels(all_outputs[s["raw"]]).reshape(8, 8)
            for y in range(8):
                for x in range(8):
                    gx = (s["x"] + (7 - x if s["word"] & 0x4000 else x)) & 255
                    gy = (s["y"] + (7 - y if s["word"] & 0x8000 else y)) & 255
                    if (
                        gx < 224
                        and gy < 144
                        and owner[gy, gx] == s["rank"]
                        and x0 <= gx < x0 + source.shape[1]
                        and y0 <= gy < y0 + source.shape[0]
                    ):
                        final[gy - y0, gx - x0] = values[y, x]
        if not np.array_equal(source > 0, final > 0):
            raise ValueError("final drawing transparency mismatch")
        corrections[who] += int((final != proposed).sum())
        np.savez_compressed(
            labels / (who + "-" + key + ".npz"), source=source, indices=final
        )
    report = {
        "ROM_SHA256": rom_hash,
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "recipe_sha256": hashlib.sha256(
            Path(family_module.__file__).read_bytes()
        ).hexdigest(),
        "fallback_reference_sha256": catalogue_digest(fallback),
        "capture_files": [
            {
                "path": path,
                "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            }
            for path in sorted({entry["capture"] for entry in spec["entries"]})
        ],
        "baseline_sha256": catalogue_digest(baseline),
        "table_sha256": catalogue_digest(out),
        "records": len(records),
        "preserved_explicit_outputs": len(original),
        "drawings": len(drawings),
        "fighters": len(family_module.RECIPES),
        "constraints": conflicts,
        "corrected_pixels": dict(corrections),
        "scope": "ordered exact-source tile donors, immutable prior outputs; final labels require art review",
    }
    if context:
        report.update(
            context=context,
            context_variants=len(variants),
            retained_actor_sources=len(protected_sources),
            canonical_records=len(canonical_records),
            records=len(canonical_records) + sum(len(v) for v in contexts.values()),
            protection_manifests=[
                {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in protection_manifests
            ],
        )
    elif retained_contexts is not None:
        report.update(
            records=sum(written["counts"]),
            inherited_context_variants=sum(len(v) for v in retained_contexts.values()),
        )
    (out / "report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["manifest", "baseline", "fallback", "source_rom", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument("--accept-reference-tiles", action="store_true")
    p.add_argument(
        "--family",
        choices=[
            "basics",
            "motions",
            "gouki-context",
            "low-air",
            "followthrough",
            "dash",
        ],
        default="basics",
    )
    p.add_argument("--context", type=int, choices=[0, 1], default=0)
    p.add_argument("--protect-manifest", type=Path, action="append")
    a = p.parse_args()
    family = roster_colours
    if a.family == "motions":
        import roster_motion_colours as family
    elif a.family == "gouki-context":
        import gouki_context_colours as family
    elif a.family == "dash":
        import roster_dash_colours as family
    elif a.family == "followthrough":
        import roster_followthrough_colours as family
    elif a.family == "low-air":
        import roster_low_air_colours as family
    if a.family in ("low-air", "dash"):
        from types import SimpleNamespace

        family = SimpleNamespace(
            __file__=family.__file__,
            author=family.author,
            RECIPES={
                name: row
                for name, row in family.RECIPES.items()
                if (name == "GOUKI") == bool(a.context)
            },
        )
    r = build(
        a.manifest,
        a.baseline,
        a.fallback,
        a.source_rom,
        a.out,
        a.accept_reference_tiles,
        family,
        a.context,
        a.protect_manifest,
    )
    print({k: v for k, v in r.items() if k != "constraints"})
