from pathlib import Path
import json
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from regress import compare,digest
class CompareTests(unittest.TestCase):
    def fixtures(self,root):
        for tag in ('a','b'):
            d=root/tag;d.mkdir();Image.new('RGB',(224,144),'black').save(d/'screen.png')
            r={'status':'CAPTURED','sequence':[['shot','screen']], 'emucap_sha256':'x',
               'mednafen_sha256':'y','start':'cold','rom_sha256':tag,
               'screens':{'screen':{'file':'screen.png','sha256':digest(d/'screen.png')}}}
            (d/'capture.json').write_text(json.dumps(r))
    def test_identical_and_one_pixel(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);self.fixtures(r)
            self.assertTrue(compare(r/'a',r/'b',r/'same')['identical'])
            p=r/'b/screen.png';im=Image.open(p).convert('RGB');im.putpixel((3,4),(1,0,0));im.save(p)
            meta=r/'b/capture.json';d=json.loads(meta.read_text());d['screens']['screen']['sha256']=digest(p);meta.write_text(json.dumps(d))
            result=compare(r/'a',r/'b',r/'different')
            self.assertFalse(result['identical']);self.assertEqual(result['screens'][0]['changed_pixels'],1)
    def test_missing_and_tampered(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);self.fixtures(r)
            Image.new('RGB',(224,144),'white').save(r/'b/screen.png')
            with self.assertRaises(ValueError):compare(r/'a',r/'b',r/'tampered')
            meta=r/'b/capture.json';d=json.loads(meta.read_text());d['screens']={};meta.write_text(json.dumps(d))
            with self.assertRaises(ValueError):compare(r/'a',r/'b',r/'missing')
if __name__=='__main__':unittest.main()
