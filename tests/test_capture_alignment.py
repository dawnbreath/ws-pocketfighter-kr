"""Horizontal screenshot registration must not conceal colour or shape errors."""

import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from capture_walk import match_render


class RenderAlignment(unittest.TestCase):
    def setUp(self):
        self.expected = np.zeros((12, 32, 3), dtype=np.uint8)
        self.visible = np.zeros((12, 32), dtype=bool)
        self.visible[4:6, 14:16] = True
        self.expected[4:6, 14:16] = np.arange(12).reshape(2, 2, 3) + 30

    def test_exact_offset_and_walk_refusal(self):
        actual = np.roll(self.expected, 3, axis=1)
        self.assertEqual(
            match_render(self.expected, actual, self.visible, True), (True, 0, [3, 0])
        )
        self.assertFalse(match_render(self.expected, actual, self.visible, False)[0])

    def test_changed_pixel_is_not_accepted(self):
        actual = np.roll(self.expected, 3, axis=1)
        actual[4, 17, 0] += 1
        self.assertFalse(match_render(self.expected, actual, self.visible, True)[0])

    def test_ambiguous_position_is_not_accepted(self):
        actual = np.roll(self.expected, 3, axis=1) + np.roll(self.expected, -3, axis=1)
        self.assertFalse(match_render(self.expected, actual, self.visible, True)[0])


if __name__ == "__main__":
    unittest.main()
