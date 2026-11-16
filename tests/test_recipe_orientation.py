"""Reflection must be explicit, exact and applied to output labels too."""

from pathlib import Path
import sys
from types import ModuleType
import unittest
import numpy as np

sys.path[:0] = [
    str(Path(__file__).resolve().parents[1] / "tools"),
    str(Path(__file__).resolve().parents[1] / "tools/mock"),
]
from verify_contact_output import resolve_recipe
from seed_recipe import crop_md5


class RecipeOrientationTests(unittest.TestCase):
    def setUp(self):
        self.source = np.array([[0, 1, 2], [3, 1, 0]], dtype=np.int8)
        self.recipe = ModuleType("synthetic_recipe")
        self.recipe.POSES = (crop_md5(self.source)[0],)
        self.recipe.author = lambda s: np.array([0, 13, 12, 4], dtype=np.int8)[s]

    def test_mirror_requires_explicit_permission_and_reflects_labels(self):
        mirrored = np.fliplr(self.source)
        self.assertIsNone(resolve_recipe(mirrored, self.recipe, "source"))
        key, labels, reflected = resolve_recipe(mirrored, self.recipe, "mirror")
        self.assertEqual(key, self.recipe.POSES[0])
        self.assertTrue(reflected)
        np.testing.assert_array_equal(
            labels, np.fliplr(self.recipe.author(self.source))
        )

    def test_either_prefers_direct_match_and_rejects_similar_drawing(self):
        self.assertFalse(resolve_recipe(self.source, self.recipe, "either")[2])
        changed = self.source.copy()
        changed[0, 1] = 2
        self.assertIsNone(resolve_recipe(changed, self.recipe, "either"))


if __name__ == "__main__":
    unittest.main()
