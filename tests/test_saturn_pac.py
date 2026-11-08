import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from saturn_pac import parse, palette_image, inspect


class PacTests(unittest.TestCase):
    def make(self):
        data = bytearray(0x1020)
        struct.pack_into(">II", data, 0, 2, 36)
        struct.pack_into(">IIII", data, 8, 0x101, 4, 0x102, 32)
        data[0x800:0x804] = b"TEST"
        struct.pack_into(">HHH", data, 0x1000, 31, 31 << 5, 31 << 10)
        return bytes(data)

    def test_alignment(self):
        total, c = parse(self.make())
        self.assertEqual(total, 36)
        self.assertEqual([(x.offset, x.size) for x in c], [(0x800, 4), (0x1000, 32)])

    def test_bounds(self):
        for data in (b"", bytes(0x800), self.make()[:-1]):
            with self.assertRaises(ValueError):
                parse(data)
        data = bytearray(self.make())
        struct.pack_into(">I", data, 0, 256)
        with self.assertRaises(ValueError):
            parse(bytes(data))

    def test_rgb_and_report(self):
        data = self.make()
        im = palette_image(data[0x1000:])
        self.assertEqual(
            [im.getpixel((i * 16, 0)) for i in range(3)],
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
        )
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "local.pac").write_bytes(data)
            r = inspect(root / "local.pac", root / "out")
            self.assertEqual(r["chunks"][1]["palettes"], 1)
            self.assertEqual(len(list((root / "out").iterdir())), 2)
            with self.assertRaises(ValueError):
                inspect(root / "local.pac", root / "out")

    def test_partial_palette(self):
        with self.assertRaises(ValueError):
            palette_image(bytes(31))


if __name__ == "__main__":
    unittest.main()
