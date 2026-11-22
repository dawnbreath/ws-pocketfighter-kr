"""Portable stage graphics contracts, using synthetic material and pixel arrays."""

import struct
import unittest

import numpy as np
from PIL import Image

from saturn_stages import stage_actors
from stage_backgrounds import (
    encode_tile,
    fit_palettes,
    pack_static_cells,
    refine_scenery,
    reuse_native_variants,
    registered_colours,
    spectator_colours,
    stage_pattern_sources,
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

    def test_camera_edges_reusing_a_slot_have_distinct_source_patterns(self):
        rom = bytearray(0x140000 + 36)
        desc = bytearray(38)
        struct.pack_into("<H", desc, 27, 12)
        struct.pack_into("<3H", rom, 0x140000, 12 * 16, 18 * 16, 16)
        struct.pack_into("<3H", rom, 0x140012, 12 * 16, 27 * 16, 16)
        entries = np.full((1, 36), 8, dtype="<u2")
        entries[0, [0, 35]] = [0x400C, 0x800C]
        expected = entries.astype(int)
        expected[0, [0, 35]] = [18, 27]
        np.testing.assert_array_equal(
            stage_pattern_sources(rom, desc, entries), expected
        )
        entries[0, 17] = 12
        with self.assertRaisesRegex(ValueError, "no source"):
            stage_pattern_sources(rom, desc, entries)

    def test_actor_cells_are_column_major_and_zero_is_transparent(self):
        layout = struct.pack(
            ">HBBhhHHIII", 3, 2, 2, 0, 0, 2, 0, 0x60000000, 0x1A000000, 0x1A000080
        )
        art = bytes([0x11]) * 128 + bytes([0x22]) * 128
        palette = struct.pack(">16H", 0, 31, 31 << 10, *([0] * 13))
        chunks = [(0x106, art), (0x107, layout), (0x108, palette)]
        data = struct.pack(">II", len(chunks), 0) + b"".join(
            struct.pack(">II", key, len(block)) for key, block in chunks
        )
        data = data.ljust(2048, b"\0") + b"".join(
            block.ljust(2048, b"\0") for _, block in chunks
        )
        frame = stage_actors(data, {0})[0]
        self.assertEqual(frame.getpixel((0, 16)), (255, 0, 0, 255))
        self.assertEqual(frame.getpixel((16, 0)), (0, 0, 255, 255))
        self.assertEqual(frame.getpixel((0, 0))[3], 0)

    def test_spectator_swatches_survive_a_dominant_background(self):
        target = np.full((16, 16, 3), 7, dtype="u1")
        image = Image.new("RGBA", (2, 2))
        image.putpixel((0, 0), (34, 68, 153, 255))
        figures = [
            {
                "name": "guest",
                "frame": 0,
                "ws": [2, 2, 4, 4],
                "row": 2,
                "swatches": ["249"],
            }
        ]
        weights, fixed = spectator_colours(
            image, {0: image}, figures, np.zeros((16, 16), "u1"), target
        )
        np.testing.assert_array_equal(target[2, 2], [2, 4, 9])
        np.testing.assert_array_equal(target[3, 3], [7, 7, 7])
        tiles = (
            target.reshape(2, 8, 2, 8, 3).transpose(0, 2, 1, 3, 4).reshape(4, 8, 8, 3)
        )
        mass = weights.reshape(2, 8, 2, 8).transpose(0, 2, 1, 3).reshape(4, 8, 8)
        rows = fit_palettes(tiles, np.zeros((4, 4, 3)), np.zeros(4), mass, fixed)
        np.testing.assert_array_equal(rows[2, 5], [2, 4, 9])

    def test_foreground_guest_accents_override_feathered_scenery(self):
        target = np.zeros((8, 8, 3), dtype="u1")
        tones = np.full((8, 8), 4, dtype="u1")
        blue = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
        red = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
        records = [
            {"name": "window", "ws": [0, 0, 8, 8], "detail": [0, 0, 8, 8]},
            {
                "name": "guest",
                "ws": [3, 3, 5, 5],
                "frame": 0,
                "row": 1,
                "swatches": ["DDD"],
                "accents": [["DDD", 1, 0, 2]],
            },
        ]
        weights, fixed = spectator_colours(blue, {0: red}, records, tones, target)
        np.testing.assert_array_equal(target[0, 0], [0, 0, 5])
        np.testing.assert_array_equal(target[2, 2], [0, 0, 15])
        np.testing.assert_array_equal(target[3, 3], [15, 0, 0])
        np.testing.assert_array_equal(target[4, 3:5], [fixed[1, 5]] * 2)
        self.assertGreater(weights[4, 3], weights[3, 3])
        records[1]["accents"][0][3] = 3
        with self.assertRaisesRegex(ValueError, "invalid colour accent"):
            spectator_colours(blue, {0: red}, records, tones, target)

    def test_scenery_fit_preserves_flipped_shared_tiles_and_protected_pixels(self):
        mapped = np.array([[0x2040, 0x6040, 0x2041]], dtype="<u2")
        displayed = np.ones((1, 3, 8, 8), dtype="u1")
        palettes = np.zeros((4, 16, 3), dtype="u1")
        palettes[:, 1:] = [0, 0, 15]
        palettes[0, 2] = [4, 0, 12]
        palettes[1, 2] = [15, 0, 0]
        packed = bytearray(encode_tile(displayed[0, 0]) * 2)
        tones = np.zeros((8, 24), dtype="u1")
        reference = Image.new("RGBA", (24, 8), (255, 0, 0, 255))
        regions = [
            {"name": "rail", "ws": [0, 0, 8, 8], "detail": [0, 0, 8, 8]},
            {"name": "gate", "ws": [16, 0, 24, 8], "detail": [16, 0, 24, 8]},
        ]
        refine_scenery(reference, tones, regions, [{"ws": [18, 2, 20, 4]}],
                      mapped, displayed, palettes, packed)
        np.testing.assert_array_equal(mapped, [[0x2040, 0x6040, 0x2241]])
        np.testing.assert_array_equal(displayed[0, :2], 1)
        np.testing.assert_array_equal(displayed[0, 2, 2:4, 2:4], 1)
        self.assertEqual(displayed[0, 2, 5, 5], 2)
        self.assertEqual(packed[:32], encode_tile(displayed[0, 0]))
        self.assertEqual(packed[32:], encode_tile(displayed[0, 2]))

    def test_variant_reuse_respects_native_source_flip_and_protected_pixels(self):
        patterns = np.ones((3, 8, 8), dtype="u1")
        patterns[1, 1, 2] = 2
        patterns[2] = 2
        packed = bytearray().join(encode_tile(pattern) for pattern in patterns)
        mapped = np.array([[0x6040, 0x2041, 0x2042, 0x6040]], dtype="<u2")
        displayed = patterns[[0, 1, 2, 0]][None].copy()
        palettes = np.zeros((4, 16, 3), dtype=np.int16)
        palettes[:, 2] = [15, 0, 0]
        target = np.broadcast_to([15, 0, 0], (1, 4, 8, 8, 3))
        active = np.ones((1, 4, 8, 8), dtype=bool)
        active[:, 1:3] = False
        active[0, 3, 1, 5] = False
        reuse_native_variants(
            mapped, displayed, palettes, packed, np.array([[7, 7, 8, 7]]),
            target, active,
        )
        np.testing.assert_array_equal(mapped, [[0x6041, 0x2041, 0x2042, 0x6040]])
        np.testing.assert_array_equal(displayed[0, 0], patterns[1, :, ::-1])
        np.testing.assert_array_equal(displayed[0, 3], patterns[0])

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
