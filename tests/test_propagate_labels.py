"""Synthetic proposal tests: abstention, translation, provenance, source projection."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from propagate_labels import features, pose_key, choose_seeds, predict, run
from component_marks import fingerprint
from segment_frames import compose
from test_segment_frames import fixture


class PropagationTests(unittest.TestCase):
    def test_translation_dedup_and_seed_diversity(self) -> None:
        a = np.zeros((30, 40), np.int8)
        a[3:6, 4:8] = 1
        b = np.zeros_like(a)
        b[13:16, 14:18] = 1
        c = np.zeros_like(a)
        c[1:9, 2:4] = 2
        self.assertEqual(pose_key(a), pose_key(b))
        np.testing.assert_array_equal(features(a)[0], features(b)[0])
        self.assertEqual(choose_seeds([a, b, c], 12), [0, 2])

    def test_votes_abstain_on_conflict_and_distance(self) -> None:
        train = np.array([[0, 0], [0, 0], [1, 1]], np.float32)
        labels = np.array([1, 2, 2], np.int8)
        result, score, d, prob = predict(
            train, labels, np.array([[0, 0], [10, 10]], np.float32), 0.9, 0.04
        )
        self.assertEqual(result.tolist(), [-1, -1])
        np.testing.assert_allclose(prob.sum(1), 1)
        with self.assertRaises(ValueError):
            predict(train, np.ones(3, np.int8), train, 0.9, 0.04)

    def test_pipeline_preserves_abstention_and_exports(self) -> None:
        a = fixture([(1 | (4 << 9), 20, 20), (2 | (4 << 9), 30, 20)])
        b = fixture([(1 | (4 << 9), 25, 25), (2 | (4 << 9), 35, 25)])
        b["index"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap = root / "capture.json"
            marks = root / "marks.json"
            c = {
                "schema": 1,
                "status": "CAPTURED",
                "character": "synthetic",
                "rom_sha256": "synthetic",
                "side": 4,
                "frames": [a, b],
            }
            cap.write_text(json.dumps(c))
            pixels = compose(a, 4)[0]
            m = {
                "schema": 1,
                "character": "synthetic",
                "reviewer": "synthetic reviewer",
                "capture_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
                "frames": {
                    "0": {
                        "frame_sha256": fingerprint(pixels),
                        "marks": [
                            {"kind": "pixels", "pixels": [[20, 20]], "label": "skin"},
                            {"kind": "pixels", "pixels": [[30, 20]], "label": "boots"},
                            {
                                "kind": "pixels",
                                "pixels": [[31, 20]],
                                "label": "unknown",
                            },
                        ],
                    }
                },
            }
            marks.write_text(json.dumps(m))
            r = run(cap, root / "out", marks, seed_count=2)
            self.assertEqual(r["status"], "UNREVIEWED_PROPOSALS")
            self.assertFalse(r["engine_ready"])
            self.assertEqual(r["seed_frames"], [0])
            self.assertEqual(
                r["heldout_pixels"], 0
            )  # translated seed pose is not held out
            masks = json.loads((root / "out/masks.json").read_text())
            self.assertEqual(len(masks["tiles"]), 2)
            tile = hashlib.sha256(bytes.fromhex(a["vram"])[16:32]).hexdigest()
            self.assertEqual(masks["tiles"][tile]["mask"][0], 2)
            with np.load(root / "out/probabilities/0000.npz") as z:
                index = np.where(np.all(z["xy"] == [31, 20], axis=1))[0][0]
                self.assertEqual(z["accepted"][index], -1)
                np.testing.assert_allclose(z["votes"].sum(1), 1, atol=1e-6)
            self.assertTrue((root / "out/seed-comparison.png").exists())
            pending = run(cap, root / "pending", None)
            self.assertEqual(pending["status"], "SEEDS_REQUIRED")
            m["capture_sha256"] = "wrong"
            marks.write_text(json.dumps(m))
            with self.assertRaises(ValueError):
                run(cap, root / "bad", marks)
            self.assertFalse((root / "bad").exists())
