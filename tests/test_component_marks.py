import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from component_marks import apply_marks, fingerprint, load_marks
from segment_frames import components, classify, LABELS, observations, process
from test_segment_frames import fixture, RULES


class MarkTests(unittest.TestCase):
    def test_component_follows_outline_not_box(self) -> None:
        pixels = np.array([[1, 3, 1], [1, 3, 1]], dtype=np.int8)
        regions, _ = components(pixels)
        record = {
            "frame_sha256": fingerprint(pixels),
            "marks": [
                {
                    "kind": "component",
                    "component": 1,
                    "component_sha256": fingerprint(regions == 1),
                    "label": "white_trim",
                }
            ],
        }
        result = apply_marks(
            pixels, np.full(pixels.shape, -1, dtype=np.int8), regions, record, LABELS
        )
        self.assertTrue(np.all(result[:, 0] == 8))
        self.assertTrue(np.all(result[:, 1:] == -1))
        record["frame_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            apply_marks(pixels, result, regions, record, LABELS)

    def test_thin_feature_and_colored_outline(self) -> None:
        pixels = np.array([[1, 1, 1], [3, 3, 3]], dtype=np.int8)
        regions, _ = components(pixels)
        record = {
            "frame_sha256": fingerprint(pixels),
            "marks": [
                {"kind": "pixels", "pixels": [[1, 0]], "label": "wristband"},
                {"kind": "pixels", "pixels": [[1, 1]], "label": "cloth_outline"},
            ],
        }
        result = apply_marks(
            pixels, np.full(pixels.shape, 2, dtype=np.int8), regions, record, LABELS
        )
        self.assertEqual(result.tolist(), [[2, 13, 2], [2, 11, 2]])
        record["marks"].append({"kind": "pixels", "pixels": [[1, 0]], "label": "skin"})
        with self.assertRaises(ValueError):
            apply_marks(pixels, result, regions, record, LABELS)

    def test_real_pipeline_synthetic_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap = root / "capture"
            rules = root / "rules"
            marks = root / "marks"
            frame = fixture([(1 | (4 << 9) | 0x4000, 50, 50)])
            record = {
                "schema": 1,
                "status": "CAPTURED",
                "character": "synthetic",
                "side": 4,
                "rom_sha256": "synthetic",
                "frames": [frame],
            }
            cap.write_text(json.dumps(record))
            rules.write_text(json.dumps(RULES))
            from segment_frames import compose

            pixels, _, _ = compose(frame, 4)
            marks.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "capture_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
                        "character": "synthetic",
                        "reviewer": "synthetic test",
                        "frames": {
                            "0": {
                                "frame_sha256": fingerprint(pixels),
                                "marks": [
                                    {
                                        "kind": "pixels",
                                        "pixels": [[57, 50]],
                                        "label": "gloves",
                                    }
                                ],
                            }
                        },
                    }
                )
            )
            result = process(cap, rules, root / "out", marks)
            self.assertEqual(next(iter(result["tiles"].values()))["mask"][0], 9)
            self.assertEqual(result["marked_frames"], 1)
            self.assertFalse(result["engine_ready"])
            changed = json.loads(marks.read_text())
            changed["reviewer"] = ""
            marks.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                load_marks(marks, cap, record)

    def test_roster_parts_have_explicit_vocabulary(self) -> None:
        root = Path(__file__).resolve().parents[1] / "data/rules"
        names = [
            "ryu",
            "ken",
            "chunli",
            "zangief",
            "sakura",
            "ibuki",
            "dan",
            "gouki",
            "felicia",
            "morrigan",
            "lei_lei",
            "tabasa",
        ]
        for name in names:
            rule = json.loads((root / (name + ".json")).read_text())
            self.assertEqual(rule["character"], name)
            self.assertTrue(rule["parts"])
            self.assertEqual(len(rule["parts"]), len({p["id"] for p in rule["parts"]}))
            for part in rule["parts"]:
                self.assertIn(part["label"], LABELS)
                self.assertIn(part["palette_role"], rule["slot_plan"])
                self.assertIsInstance(part["thin_feature_review"], bool)


if __name__ == "__main__":
    unittest.main()
