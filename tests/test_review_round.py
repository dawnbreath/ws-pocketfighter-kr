"""Training/evaluation isolation and reproducible outline ties."""

import sys
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/mock"))
from review_round import prepare
from seed_recipe import classify, crop_md5


class ReviewRoundTests(unittest.TestCase):
    def test_seed_pose_cannot_be_evaluation(self) -> None:
        px = np.array([[1, 2], [3, 1]], dtype=np.int8)
        key = crop_md5(px)[0]
        recipe = {"pose_md5": key, "comp": {}, "rects": [], "default": "skin"}
        with patch.dict("review_round.RECIPES", {"test": recipe}):
            with self.assertRaisesRegex(ValueError, "training seed"):
                prepare(
                    [(1, 0, px)],
                    "test",
                    {
                        "poses": [
                            {
                                "pose_md5": key,
                                "split": "eval",
                                "points": [[0, 0, "skin"]],
                            }
                        ]
                    },
                )

    def test_one_pose_cannot_enter_both_splits(self) -> None:
        px = np.array([[1, 2], [3, 1]], dtype=np.int8)
        key = crop_md5(px)[0]
        recipe = {"pose_md5": key, "comp": {}, "rects": [], "default": "skin"}
        with patch.dict("review_round.RECIPES", {"test": recipe}):
            with self.assertRaisesRegex(ValueError, "duplicate pose"):
                prepare(
                    [(1, 0, px)],
                    "test",
                    {
                        "poses": [
                            {
                                "pose_md5": key,
                                "split": "train",
                                "points": [[0, 0, "skin"]],
                            },
                            {
                                "pose_md5": key,
                                "split": "eval",
                                "points": [[0, 0, "skin"]],
                            },
                        ]
                    },
                )

    def test_outline_tie_uses_stable_label_order(self) -> None:
        px = np.array([[1, 3, 1]], dtype=np.int8)
        recipe = {
            "comp": {},
            "rects": [("red", (0, 0, 1, 1)), ("blue", (2, 0, 3, 1))],
            "default": "skin",
        }
        self.assertEqual(classify(px, recipe)[(0, 1)], "blue")
