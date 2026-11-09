"""Synthetic active-range, content-reuse and range-overlap coverage."""

import json
from pathlib import Path
import tempfile
import unittest
from test_segment_frames import fixture
from profile_tile_slots import profile


class SlotTests(unittest.TestCase):
    def test_ranges_reuse_and_inactive_entries(self) -> None:
        a = fixture(
            [(1 | (4 << 9), 0, 0), (384 | (4 << 9), 0, 0), (2 | (5 << 9), 0, 0)], 127
        )
        vram = bytearray.fromhex(a["vram"])
        vram[384 * 16 : 385 * 16] = vram[16:32]
        a["vram"] = vram.hex()
        b = dict(a, index=1)
        vram[384 * 16] = 0x40
        b["vram"] = vram.hex()
        cap = {
            "schema": 1,
            "status": "CAPTURED",
            "character": "synthetic",
            "rom_sha256": "synthetic",
            "side": 4,
            "frames": [a, b],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            path.write_text(json.dumps(cap))
            result = profile(path)
        self.assertEqual(
            result["counts"],
            {
                "unique_hashes": 2,
                "hashes_slots_180_1ff": 2,
                "hashes_slots_000_17f": 1,
                "hashes_in_both_ranges": 1,
                "referenced_slots": 2,
                "reused_slots": 1,
                "reused_slots_180_1ff": 1,
                "reused_slots_000_17f": 0,
            },
        )
        self.assertFalse(result["writer_verified"])

    def test_incomplete_capture_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            path.write_text('{"schema": 1, "status": "RUNNING"}')
            with self.assertRaises(ValueError):
                profile(path)
