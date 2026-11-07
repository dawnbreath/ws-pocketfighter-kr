from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import pieces

class PiecesTests(unittest.TestCase):
    def test_decode_and_flip(self):
        rom=bytearray(65536);rom[0]=128;rom[1]=64
        self.assertEqual(pieces.tile2(rom,0)[0][:3],[1,2,0])
        image=pieces.render(rom,0,0,[(0xC001,-8,-8)])
        self.assertEqual(image.getpixel((7,7)),85)
        self.assertEqual(image.getpixel((6,7)),170)
    def test_signed_parse_and_terminator(self):
        rom=bytes([1,0,255,128])+bytes(12)
        self.assertEqual(pieces.parse(rom,0,0),[(1,-1,-128)])
        with self.assertRaises(ValueError):pieces.parse(bytes(512),0,0)
        with self.assertRaises(ValueError):pieces.parse(bytes(65536),0,65534)
    def test_tile_bounds(self):
        with self.assertRaises(ValueError):pieces.tile2(bytes(15),0)
        with self.assertRaises(ValueError):pieces.render(bytes(131072),0,65530,[(1,0,0)])
    def test_shared_source_mapping(self):
        rom=bytearray(65536);rom[0]=128
        image=pieces.render(rom,0,0,[(0,0,0),(0x4001,0,8)])
        self.assertEqual(image.getpixel((0,0)),85)
        self.assertEqual(image.getpixel((15,0)),85)
if __name__=='__main__':unittest.main()
