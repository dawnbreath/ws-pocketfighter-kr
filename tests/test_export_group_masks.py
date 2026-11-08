"""No game fixtures: verify bitplane semantics, unknowns and hash collisions."""

import hashlib
import json
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from export_group_masks import encode, pack, lookup, export
from test_segment_frames import fixture


class ExportTests(unittest.TestCase):
    def test_all_groups_and_transparent_pixels(self) -> None:
        raw = bytes([0b10101010, 0b01100110] * 8)
        labels = [-1 if x % 4 == 3 else x % 4 + 1 for y in range(8) for x in range(8)]
        # Set labels by actual source shade: columns 3/7 are transparent.
        groups = {1: 0, 2: 1, 3: 2, 4: 3}
        for g in range(4):
            uniform, planes = encode(raw, [1] * 64, {1: g})
            self.assertEqual(uniform, g)
            for y in range(8):
                for x in range(8):
                    bit = 7 - x
                    shade = ((raw[2 * y] >> bit) & 1) | (
                        ((raw[2 * y + 1] >> bit) & 1) << 1
                    )
                    actual = (
                        shade
                        | (((planes[2 * y] >> bit) & 1) << 2)
                        | (((planes[2 * y + 1] >> bit) & 1) << 3)
                    )
                    self.assertEqual(actual, shade + 4 * g if shade else 0)
        self.assertIsNotNone(encode(raw, labels, groups))

    def test_unknown_and_unmapped_are_not_filled(self) -> None:
        raw = bytes([128, 0] + [0] * 14)
        self.assertIsNone(encode(raw, [-1] * 64, {1: 0}))
        self.assertIsNone(encode(raw, [9] * 64, {1: 0}))
        self.assertIsNotNone(encode(raw, [1] + [-1] * 63, {1: 0}))
        with self.assertRaises(ValueError):
            encode(raw, [1] * 64, {1: 4})

    def test_collision_scan_uses_exact_bytes(self) -> None:
        a, b, missing = bytes(16), bytes([1] * 16), bytes([2] * 16)
        with patch("export_group_masks.zlib.crc32", return_value=123):
            blob = pack([(b, 1, bytes([85] * 16)), (a, 0, bytes(16))])
            self.assertEqual(lookup(blob, b), (1, bytes([85] * 16)))
            self.assertEqual(lookup(blob, a), (0, bytes(16)))
            self.assertIsNone(lookup(blob, missing))
        with self.assertRaises(ValueError):
            lookup(blob[:-1], a)

    def test_mixed_groups_are_not_uniform(self) -> None:
        uniform, planes = encode(bytes([255] * 16), [1, 2] * 32, {1: 0, 2: 3})
        self.assertEqual(uniform, 255)
        self.assertEqual(planes, bytes([85] * 16))


class PipelineTests(unittest.TestCase):
    def test_provenance_and_conflict_omission(self) -> None:
        frame = fixture([(1 | (4 << 9), 40, 40)])
        raw = bytes.fromhex(frame["vram"])[16:32]
        digest = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap, masks, mapping = (
                root / n for n in ("cap.json", "masks.json", "map.json")
            )
            cap.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "status": "CAPTURED",
                        "character": "test",
                        "side": 4,
                        "rom_sha256": "original",
                        "frames": [frame],
                    }
                )
            )
            table = {
                "schema": 1,
                "character": "test",
                "rom_sha256": "original",
                "capture_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
                "labels": {"skin": 2},
                "tiles": {
                    digest: {"mask": [2] + [0] * 63, "conflicts": [], "unobserved": []}
                },
            }
            mapping.write_text(json.dumps({"character": "test", "groups": {"skin": 3}}))
            masks.write_text(json.dumps(table))
            result = export(cap, masks, mapping, root / "good")
            self.assertEqual(result["records"], 1)
            self.assertFalse(result["engine_ready"])
            self.assertEqual(
                lookup((root / "good/masks.pgmd").read_bytes(), raw),
                encode(raw, [2] + [0] * 63, {2: 3}),
            )
            table["tiles"][digest]["conflicts"] = [0]
            masks.write_text(json.dumps(table))
            self.assertEqual(
                export(cap, masks, mapping, root / "conflict")["records"], 0
            )
            table["capture_sha256"] = "wrong"
            masks.write_text(json.dumps(table))
            with self.assertRaises(ValueError):
                export(cap, masks, mapping, root / "bad")
            self.assertFalse((root / "bad").exists())
