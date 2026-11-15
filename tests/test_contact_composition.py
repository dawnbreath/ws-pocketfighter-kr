"""Opponent isolation must not turn hidden source into screenshot evidence."""

import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from segment_frames import compose


class ContactCompositionTests(unittest.TestCase):
    def frame(self):
        ram = bytearray(8192)
        ram[384 * 16 : 385 * 16] = bytes([255, 0]) * 8
        ram[384 * 16] = 127  # a real transparent pixel in the player's source
        ram[385 * 16 : 386 * 16] = bytes([255, 0]) * 8
        oam = bytearray(512)
        for i, (slot, palette) in enumerate([(385, 5), (384, 4)]):
            oam[i * 4 : i * 4 + 4] = (slot | (palette << 9)).to_bytes(
                2, "little"
            ) + bytes([20, 20])
        return {
            "oam": oam.hex(),
            "vram": ram.hex(),
            "sprite_start": 0,
            "sprite_count": 2,
        }

    def test_opponent_remains_an_occluder_by_default(self):
        px, owner, sprites = compose(self.frame(), 4)
        self.assertEqual(int(np.count_nonzero(px)), 0)
        self.assertTrue((owner == -1).all())
        self.assertEqual(len(sprites), 2)

    def test_isolation_keeps_source_transparency_and_original_rank(self):
        px, owner, sprites = compose(self.frame(), 4, occluders=False)
        self.assertEqual(int(np.count_nonzero(px)), 63)
        self.assertEqual(int(px[20, 20]), 0)
        self.assertEqual(int(owner[21, 21]), 1)
        self.assertEqual(len(sprites), 2)


if __name__ == "__main__":
    unittest.main()
