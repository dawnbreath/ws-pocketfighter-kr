"""Unsigned OAM source coordinates must remain distinct from LCD visibility."""

import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from segment_frames import compose, cyclic_crop


class CyclicSourceTests(unittest.TestCase):
    def frame(self):
        ram = bytearray(8192)
        ram[384 * 16 : 385 * 16] = bytes([255, 0]) * 8
        oam = bytearray(512)
        for i, xy in enumerate([(252, 252), (4, 4)]):
            x, y = xy
            oam[i * 4 : i * 4 + 4] = (384 | (4 << 9)).to_bytes(2, "little") + bytes(
                [y, x]
            )
        return {
            "oam": oam.hex(),
            "vram": ram.hex(),
            "sprite_start": 0,
            "sprite_count": 2,
        }

    def test_wrapped_source_does_not_inflate_visible_evidence(self):
        visible = compose(self.frame(), 4)[0]
        full = compose(self.frame(), 4, occluders=False, viewport=(256, 256))[0]
        source, box = cyclic_crop(full)
        self.assertEqual(box, (252, 252, 16, 16))
        self.assertEqual(int(np.count_nonzero(visible)), 80)
        self.assertEqual(int(np.count_nonzero(source)), 128)
        self.assertEqual(int(source[0, 0]), 1)
        self.assertEqual(int(source[8, 8]), 1)
        self.assertEqual(int(source[0, 8]), 0)

    def test_nonwrapped_source_origin_and_values_are_unchanged(self):
        full = np.zeros((256, 256), dtype=np.int8)
        full[50:53, 25:29] = 2
        source, box = cyclic_crop(full)
        self.assertEqual(box, (25, 50, 4, 3))
        self.assertTrue((source == 2).all())

    def test_empty_surface_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty 256x256"):
            cyclic_crop(np.zeros((256, 256), dtype=np.int8))

    def test_full_axis_is_not_cropped_to_zero(self):
        full = np.zeros((256, 256), dtype=np.int8)
        full[8, :] = 1
        source, box = cyclic_crop(full)
        self.assertEqual(box[1:], (8, 256, 1))
        self.assertEqual(source.shape, (1, 256))


if __name__ == "__main__":
    unittest.main()
