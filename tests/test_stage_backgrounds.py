"""Portable stage graphics contracts, using synthetic material and pixel arrays."""

import unittest

import numpy as np
from PIL import Image

from stage_backgrounds import (
    encode_tile,
    fit_palettes,
    pack_static_cells,
    registered_colours,
)


class StageBackgroundTests(unittest.TestCase):
    def test_opaque_and_high_bits_round_trip(self):
        tile = np.arange(64, dtype="u1").reshape(8, 8) % 16
        encoded = np.frombuffer(encode_tile(tile), dtype="u1").reshape(8, 4, 1)
        planes = np.unpackbits(encoded, axis=2)
        decoded = (planes * (1 << np.arange(4))[None, :, None]).sum(axis=1)
        np.testing.assert_array_equal(decoded, tile)

    def test_flipped_instances_share_a_tile_without_reversing_the_drawing(self):
        pattern = np.arange(64, dtype="u1").reshape(8, 8) % 15 + 1
        colours = np.repeat(np.arange(16)[:, None], 3, axis=1)
        palettes = np.repeat(colours[None], 4, axis=0)
        target = colours[pattern]
        pending = {9: [(0, 0, 0, target, pattern), (0, 1, 0x4000, target, pattern)]}
        mapped = np.zeros((1, 2), dtype="u2")
        display = np.zeros((1, 2, 8, 8), dtype="u1")
        self.assertEqual(len(pack_static_cells(pending, palettes, mapped, display)), 32)
        self.assertEqual(mapped[0, 0], 0x2040)
        self.assertEqual(mapped[0, 1], 0x6040)
        np.testing.assert_array_equal(display[0, 0], pattern)
        np.testing.assert_array_equal(display[0, 1], display[0, 0][:, ::-1])

    def test_static_fit_keeps_animation_slots_and_handles_a_single_colour(self):
        primary = np.arange(48).reshape(4, 4, 3) % 16
        target = np.full((2, 8, 8, 3), [12, 0, 7], dtype="u1")
        rows = fit_palettes(target, primary, np.array([0, 1]))
        np.testing.assert_array_equal(rows[:, :4], primary[:, ::-1])
        np.testing.assert_array_equal(rows[:, 4], primary[:, 3])
        self.assertTrue(np.any(np.all(rows[:, 5:] == [12, 0, 7], axis=2)))

    def test_reference_tint_keeps_native_contrast(self):
        tones = np.ones((16, 16), dtype="u1") * 3
        tones[6:10, 6:10] = 1
        image = Image.new("RGBA", (16, 16), (90, 140, 200, 255))
        result = registered_colours(
            image, [[0, 0, 0, 0]], tones, np.zeros((16, 16, 3), "u1")
        )
        self.assertGreater(result[0, 0, 2], result[0, 0, 0])
        self.assertTrue((result[8, 8] < result[0, 0]).all())


if __name__ == "__main__":
    unittest.main()
