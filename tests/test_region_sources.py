import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from map_region_sources import offsets, map_sources


class SourceTests(unittest.TestCase):
    def test_all_offsets_and_overlap(self) -> None:
        tile = bytes(range(16))
        self.assertEqual(offsets(b"x" + tile + b"y" + tile, tile), [1, 18])
        self.assertEqual(offsets(bytes(18), bytes(16)), [0, 1, 2])
        self.assertEqual(offsets(b"abc", tile), [])
        with self.assertRaises(ValueError):
            offsets(b"abc", b"a")

    def test_linked_provenance_and_no_overwrite(self) -> None:
        tile = bytes(range(16))
        key = hashlib.sha256(tile).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rom = root / "original"
            cap = root / "capture"
            masks = root / "masks"
            out = root / "mapping"
            rom.write_bytes(b"x" + tile)
            digest = hashlib.sha256(rom.read_bytes()).hexdigest()
            oam = bytearray(512)
            oam[1] = 8
            capture = {
                "status": "CAPTURED",
                "rom_sha256": digest,
                "character": "synthetic",
                "side": 4,
                "frames": [
                    {
                        "oam": oam.hex(),
                        "vram": (tile + bytes(8192 - 16)).hex(),
                        "sprite_start": 0,
                        "sprite_count": 1,
                    }
                ],
            }
            cap.write_text(json.dumps(capture))
            mask = {
                "capture_sha256": hashlib.sha256(cap.read_bytes()).hexdigest(),
                "rom_sha256": digest,
                "character": "synthetic",
                "tiles": {key: {"mask": [0] * 64}},
            }
            masks.write_text(json.dumps(mask))
            report = map_sources(rom, cap, masks, out)
            self.assertEqual(report["tiles"][key]["rom_offsets"], [1])
            self.assertFalse(report["engine_ready"])
            with self.assertRaises(FileExistsError):
                map_sources(rom, cap, masks, out)
            rom.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                map_sources(rom, cap, masks, root / "other")


if __name__ == "__main__":
    unittest.main()
