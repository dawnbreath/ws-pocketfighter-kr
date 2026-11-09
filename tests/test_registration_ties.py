"""Ambiguous registration matches must not acquire arbitrary part labels."""

import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/mock"))
from register_transfer import transfer


class RegistrationTieTests(unittest.TestCase):
    def test_equal_matches_with_different_parts_abstain(self) -> None:
        source = np.array([[1, 0, 1]], dtype=np.int8)
        target = np.array([[0, 1, 0]], dtype=np.int8)
        self.assertEqual(
            transfer(
                source, {(0, 0): "blue", (0, 2): "skin"}, target, rad=1, pr=0, maxbad=0
            ),
            {},
        )

    def test_equal_matches_agreeing_on_part_are_retained(self) -> None:
        source = np.array([[1, 0, 1]], dtype=np.int8)
        target = np.array([[0, 1, 0]], dtype=np.int8)
        self.assertEqual(
            transfer(
                source, {(0, 0): "blue", (0, 2): "blue"}, target, rad=1, pr=0, maxbad=0
            ),
            {(0, 1): "blue"},
        )
