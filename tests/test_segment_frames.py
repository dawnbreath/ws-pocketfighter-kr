"""Synthetic tile/OAM tests; no game fixtures."""

import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from segment_frames import (
    compose,
    components,
    observations,
    merge_votes,
    consensus,
    process,
)

RULES = {
    "character": "synthetic",
    "max_component_height": 1.1,
    "regions": [{"label": "skin", "center_box": [0, 0, 1, 1]}],
}


def fixture(entries: list[tuple[int, int, int]], start: int = 0) -> dict:
    oam = bytearray(512)
    vram = bytearray(8192)
    # Tile 1: one shade-1 pixel top-left; tile 2: solid shade 3.
    vram[16] = 0x80
    vram[32:48] = bytes([255] * 16)
    for rank, (word, x, y) in enumerate(entries):
        struct.pack_into("<HBB", oam, ((start + rank) & 127) * 4, word, y, x)
    return {
        "index": 0,
        "oam": oam.hex(),
        "vram": vram.hex(),
        "sprite_start": start,
        "sprite_count": len(entries),
    }


class SegmentTests(unittest.TestCase):
    def test_empty_and_inactive(self) -> None:
        frame = fixture([(1 | (4 << 9), 50, 50)])
        frame["sprite_count"] = 0
        pixels, owner, sprites = compose(frame, 4)
        self.assertFalse(pixels.any())
        self.assertEqual(sprites, [])
        self.assertTrue(np.all(owner == -1))

    def test_active_ring_and_wrapping(self) -> None:
        frame = fixture([(1 | (4 << 9) | 0x4000, 255, 20)], 127)
        pixels, _, _ = compose(frame, 4)
        self.assertEqual(pixels[20, 6], 1)
        self.assertEqual(int(pixels.sum()), 1)

    def test_priority_across_sides(self) -> None:
        frame = fixture([(2 | (5 << 9), 50, 50), (1 | (4 << 9), 50, 50)])
        pixels, _, _ = compose(frame, 4)
        self.assertFalse(pixels.any())
        frame = fixture([(1 | (4 << 9), 50, 50), (2 | (5 << 9), 50, 50)])
        pixels, _, _ = compose(frame, 4)
        self.assertEqual(pixels[50, 50], 1)

    def test_inverse_both_flips(self) -> None:
        for flip in (0, 0x4000, 0x8000, 0xC000):
            votes, _, _, _ = observations(
                fixture([(1 | (4 << 9) | flip, 50, 50)]), 4, RULES
            )
            cells = next(iter(votes.values()))
            self.assertEqual(consensus(cells), [2] + [0] * 63)

    def test_outline_separates_components(self) -> None:
        pixels = np.array([[1, 3, 2], [1, 3, 2]], dtype=np.int8)
        labs, count = components(pixels)
        self.assertEqual(count, 2)
        self.assertNotEqual(labs[0, 0], labs[0, 2])

    def test_conflict_is_unknown(self) -> None:
        votes = {}
        a = [set() for _ in range(64)]
        b = [set() for _ in range(64)]
        a[0].add(2)
        b[0].add(3)
        a[1].add(0)
        merge_votes(votes, {"tile": a})
        merge_votes(votes, {"tile": b})
        self.assertEqual(consensus(votes["tile"])[:3], [-1, 0, -1])

    def test_end_to_end_and_character_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap = root / "capture.json"
            rules = root / "rules.json"
            cap.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "status": "CAPTURED",
                        "character": "synthetic",
                        "side": 4,
                        "rom_sha256": "synthetic",
                        "frames": [fixture([(1 | (4 << 9), 50, 50)])],
                    }
                )
            )
            rules.write_text(json.dumps(RULES))
            r = process(cap, rules, root / "out")
            self.assertFalse(r["engine_ready"])
            self.assertEqual(r["unique_tile_hashes"], 1)
            self.assertTrue((root / "out" / "proposals.png").exists())
            with self.assertRaises(FileExistsError):
                process(cap, rules, root / "out")
            rules.write_text(json.dumps(dict(RULES, character="different")))
            with self.assertRaises(ValueError):
                process(cap, rules, root / "out2")

    def test_truncated_memory_rejected(self) -> None:
        frame = fixture([])
        frame["vram"] = "00"
        with self.assertRaises(ValueError):
            compose(frame, 4)


if __name__ == "__main__":
    unittest.main()
