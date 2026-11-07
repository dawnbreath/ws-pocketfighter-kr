import os
from pathlib import Path
import random
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from release import make_ips, apply_ips, package

class ReleaseTests(unittest.TestCase):
    def test_ips_boundaries(self):
        rng = random.Random(42)
        cases = [(b'abc', b'abc'), (b'abcdef', b'ab'), (b'a', b'a\0\0'),
                 (b'', bytes(140000)), (bytes(0x454f48), bytes(0x454f46) + b'X\0')]
        cases += [(rng.randbytes(n), rng.randbytes(m)) for n, m in [(0, 1), (100, 999), (999, 100)]]
        for base, target in cases:
            self.assertEqual(apply_ips(base, make_ips(base, target)), target)
    def test_malformed(self):
        for p in [b'', b'PATCH', b'PATCHEOFx', b'PATCH\0\0\0\0\x02x']:
            with self.assertRaises(ValueError): apply_ips(b'', p)
    def test_rle(self):
        self.assertEqual(apply_ips(b'abc', b'PATCH\0\0\x01\0\0\0\x03ZEOF'), b'aZZZ')
    def test_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); base = root/'원본.ws'; target = root/'수정.ws'
            base.write_bytes(bytes(range(256))*8192)
            target.write_bytes(b'X' + base.read_bytes()[1:] + bytes(2*1024*1024))
            result = package(base, target, root/'package', os.environ.get('XDELTA3','xdelta3'))
            self.assertEqual(result['roundtrip'], {'ips':'PASS','xdelta3':'PASS'})
            self.assertEqual({p.name for p in (root/'package').iterdir()},
                             {'patch.ips','patch.xdelta','manifest.json','README.txt'})
            with self.assertRaises(ValueError): package(base,target,root/'package','xdelta3')

if __name__ == '__main__': unittest.main()
