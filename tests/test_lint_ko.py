from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from lint_ko import wg_size, build, Scratch
class LintTests(unittest.TestCase):
    def setUp(self): self.kr=build.KR(Scratch())
    def test_width_limit(self):
        with self.assertRaises(AssertionError):self.kr.enc_line('한'*30,22)
    def test_controls(self):
        self.assertEqual(wg_size(self.kr,'{f:01}{x:8140}ｅ'),7)
        for text in ('abc','{bad}ｅ','ｅX','{col:4}{col:2}ｅ'):
            with self.assertRaises(ValueError):wg_size(self.kr,text)
    def test_wrap_uses_renderer(self):
        for line in build.wrap(self.kr,'나는 더 강한 상대를 찾기 위해 여행을 떠난다.',23):
            self.assertLessEqual(len(self.kr.enc_line(line)),23)
if __name__=='__main__':unittest.main()
