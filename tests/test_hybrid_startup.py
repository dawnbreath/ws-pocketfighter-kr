"""Execute emitted colour/copy entry paths with dirty initial scratch RAM."""

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_SP
except ImportError:
    Uc = None


@unittest.skipUnless(Uc and shutil.which("nasm"), "requires NASM and Unicorn")
class HybridStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import asm

        cls.code, _ = asm.assemble("col", {"HYBRID": "1", "BPP4": "1"})

    def machine(self):
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x100000)
        u.mem_write(0x20000, self.code)
        u.reg_write(UC_X86_REG_SP, 0xF000)
        u.mem_write(0x8204, b"\xff\xff")
        return u

    def test_colour_entry_initializes_ownership_before_resync(self) -> None:
        u = self.machine()
        u.reg_write(UC_X86_REG_CS, 0x2000)

        def stop_at_first_call(uc, address, size, data):
            if bytes(uc.mem_read(address, 1)) == b"\xe8":
                uc.emu_stop()

        u.hook_add(UC_HOOK_CODE, stop_at_first_call)
        u.emu_start(0x20000, 0xFFFFF, count=100)
        self.assertEqual(bytes(u.mem_read(0x8204, 2)), b"\0\0")

    def test_copier_before_colour_entry_forces_equal_source_refresh(self) -> None:
        u = self.machine()
        u.reg_write(UC_X86_REG_CS, 0x6000)
        u.mem_write(0x61000, bytes.fromhex("9a00050020f4"))
        source = bytes([1, 2]) * 1024
        u.mem_write(0x500, source)
        u.mem_write(0x3800, source)
        u.mem_write(0x7000, bytes([204]) * 4096)
        u.emu_start(0x61000, 0xFFFFF, count=200000)
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), bytes([1, 2, 0, 0]) * 1024)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), source)
        self.assertEqual(bytes(u.mem_read(0x3800, 2048)), source)
