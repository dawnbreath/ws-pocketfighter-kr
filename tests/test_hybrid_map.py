"""Execute the actual prototype scanner with synthetic map entries, no ROM."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn.x86_const import UC_X86_REG_SP, UC_X86_REG_DX
except ImportError:
    Uc = None
NASM = os.environ.get("NASM") or shutil.which("nasm")


@unittest.skipUnless(Uc and NASM, "requires NASM and optional Unicorn")
class HybridMapTests(unittest.TestCase):
    def scan(self, entries: list[int], old_layer_flag: int = 0) -> bytes:
        source = Path(
            os.environ.get(
                "COL_ASM", str(Path(__file__).resolve().parents[1] / "src/col.asm")
            )
        ).read_text()
        routine = source.split("\nscanmap:\n", 1)[1].split("%endif", 1)[0]
        header = (
            "bits 16\ncpu 186\norg 0x1000\nmov si,0x2000\ncall scanmap\nhlt\nscanmap:\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            asm, binary = Path(tmp) / "test.asm", Path(tmp) / "test.bin"
            asm.write_text(header + routine)
            subprocess.run([NASM, "-f", "bin", str(asm), "-o", str(binary)], check=True)
            u = Uc(UC_ARCH_X86, UC_MODE_16)
            u.mem_map(0, 0x20000)
            u.mem_write(0x1000, binary.read_bytes())
            u.reg_write(UC_X86_REG_SP, 0xF000)
            u.reg_write(UC_X86_REG_DX, old_layer_flag << 8)
            entries = entries + [511] * (1024 - len(entries))
            u.mem_write(0x2000, b"".join(e.to_bytes(2, "little") for e in entries))
            u.emu_start(0x1000, 0x2000, count=20000)
            return bytes(u.mem_read(0x8000, 512))

    def test_every_palette_on_both_screens(self) -> None:
        for layer in (0, 1):
            with self.subTest(layer=layer):
                flags = self.scan([p | (p << 9) for p in range(16)], layer)
                self.assertEqual(
                    list(flags[:16]), [2 if p & 4 else 1 for p in range(16)]
                )

    def test_mixed_use_and_palette_eight_nine(self) -> None:
        flags = self.scan(
            [10 | (8 << 9), 10 | (9 << 9), 11 | (0 << 9), 11 | (12 << 9)], 1
        )
        self.assertEqual(flags[10], 1)
        self.assertEqual(flags[11], 3)
