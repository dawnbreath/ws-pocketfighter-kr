"""Reject scene/table overlap even without optional fighter palettes."""

from pathlib import Path
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import colorlib
from colour_layout import FIGHTER_PALETTE_BASE, CLASS_TABLE_BASE, COLOUR_BANK_END


class LayoutTests(unittest.TestCase):
    def test_full_catalogue_and_table_have_distinct_regions(self) -> None:
        self.assertGreaterEqual(CLASS_TABLE_BASE - FIGHTER_PALETTE_BASE, 13 * 32)
        self.assertEqual(COLOUR_BANK_END, 65536)

    def test_scene_bound_checked_without_fighter_catalogue(self) -> None:
        spec = {
            "scenes": [{"name": "scene", "keys": ["0001,0002"]}],
            "chars": [],
            "band": {str(p): "white" for p in range(8, 12)},
            "shaderamps": {"white": {str(s): "fff" for s in range(8)}},
        }
        with patch("builtins.open", mock_open(read_data=bytes(16))):
            with self.assertRaisesRegex(ValueError, "overlap"):
                colorlib.build_bank(b"", spec, data_limit=0x1000)
            bank, _, _ = colorlib.build_bank(b"", spec, data_limit=0x1100)
        self.assertEqual(len(bank), 65536)
        self.assertNotEqual(bank[0x1000:0x1100], bytes([255]) * 256)
