"""Regression: sparse seed class IDs survive the actual prediction path."""

from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/mock"))
try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    RandomForestClassifier = None


@unittest.skipUnless(
    RandomForestClassifier, "optional scikit-learn prototype dependency"
)
class ClassIdTests(unittest.TestCase):
    def test_sparse_ids_remain_semantic_labels(self) -> None:
        from propagate_proto import features, predict_pose

        pixels = np.array([[1, 2], [1, 2]], dtype=np.int8)
        x, positions = features(pixels)
        clf = RandomForestClassifier(n_estimators=20, random_state=0).fit(
            x, [2, 8, 2, 8]
        )
        where, labels, confidence = predict_pose(clf, pixels)
        self.assertEqual(where, positions)
        self.assertEqual(set(labels), {2, 8})
        self.assertTrue(np.all((confidence >= 0) & (confidence <= 1)))
