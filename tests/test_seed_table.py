"""Seed table exports preserve ambiguity and encode source-oriented group planes."""

import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/mock"))
from seed_table import records_from_votes


class SeedTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = bytes([255, 0] * 8)
        self.key = hashlib.sha256(self.raw).hexdigest()
        self.sources = {self.key: self.raw}

    def test_group_planes_are_encoded_in_source_order(self) -> None:
        rows, omitted = records_from_votes(
            {self.key: [{i % 4} for i in range(64)]}, self.sources
        )
        self.assertEqual(rows, [(self.raw, bytes([0x55, 0x33] * 8))])
        self.assertEqual(omitted, {})

    def test_unknown_and_conflicting_pixels_omit_whole_tile(self) -> None:
        for values, reason in [(set(), "unobserved"), ({1, 2}, "conflict")]:
            cells = [{0} for _ in range(64)]
            cells[17] = values
            rows, omitted = records_from_votes({self.key: cells}, self.sources)
            self.assertEqual(rows, [])
            self.assertEqual(omitted[self.key], reason)

    def test_bad_groups_and_source_identity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            records_from_votes({self.key: [{4}] * 64}, self.sources)
        with self.assertRaises(ValueError):
            records_from_votes({self.key: [{0}] * 64}, {self.key: bytes(16)})
