"""Unused swatches may change; retained CTB3 pixels must keep both fighter RGBs."""

import copy
import sys
import unittest
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[1] / "tools"),
    str(Path(__file__).resolve().parents[1] / "tools/mock"),
]
from class_table import pack_full_table
from fighter_palettes import encode
from walk_table import compatible_palettes


class PaletteCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "fighters": {name: ["000"] * 16 for name in ["CHUN-LI", "ZANGIEF"]}
        }
        for pal in self.config["fighters"].values():
            pal[13] = "eee"
        raw = b"\x80\0" + bytes(14)
        output = b"\x80\0\x80\x80" + bytes(28)  # one opaque index13 pixel
        footer = b"".join(encode(p) for p in self.config["fighters"].values())
        self.blob = pack_full_table([(raw, output)], footer)

    def test_unused_gold_slot_is_accepted(self):
        config = copy.deepcopy(self.config)
        config["fighters"]["CHUN-LI"][12] = "fd0"
        result = compatible_palettes(self.blob, config)
        self.assertEqual(result[24:26], bytes.fromhex("d00f"))
        self.assertEqual(result[26:], self.blob[-64:][26:])

    def test_used_white_recolour_is_rejected_for_each_fighter(self):
        for name in self.config["fighters"]:
            with self.subTest(name=name):
                config = copy.deepcopy(self.config)
                config["fighters"][name][13] = "f00"
                with self.assertRaisesRegex(ValueError, "recolour an existing output"):
                    compatible_palettes(self.blob, config)


if __name__ == "__main__":
    unittest.main()
