"""Synthetic caller/return test for actual emitted trampoline and assembled hooks."""

import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INSN
    from unicorn.x86_const import *
except ImportError:
    Uc = None


class RecordingRom:
    def __init__(self) -> None:
        self.patches = {}
        self.writes = {}

    def put_free(self, offset: int, code: bytes, why: str) -> None:
        self.writes[offset] = code

    def patch(self, offset: int, expect: str, new: bytes, why: str) -> None:
        self.patches[offset] = new


@unittest.skipUnless(Uc and shutil.which("nasm"), "requires NASM and optional Unicorn")
class CopierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import build
        import asm

        with patch.dict(os.environ, {"PF_HYBRID": "1"}):
            cls.rom = RecordingRom()
            build.apply_engine(cls.rom)
        cls.color, _ = asm.assemble("col", {"HYBRID": "1", "BPP4": "1"})

    def run_hook(self, changed: bool) -> None:
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x100000)
        # Caller: far CALL 4000:02A4, then HLT. RAM copier is a RETF sentinel:
        # it tests ownership of the existing return frame, not copier throughput.
        u.mem_write(0x61000, bytes.fromhex("9aa4020040f4"))
        u.mem_write(0x402A4, self.rom.patches[0x1402A4])
        u.mem_write(0x5FF34, self.rom.writes[0x15FF34])
        u.mem_write(0x20000, self.color)
        u.mem_write(0x120, b"\xcb")
        staging = bytes([0x55, 0xAA] * 1024)
        u.mem_write(0x500, staging)
        u.mem_write(0x3800, bytes(2048) if changed else staging)
        sentinel = bytes([0x7E] * 4096)
        u.mem_write(0x7000, sentinel)
        # Equal-source skipping is valid only after the colour hook owns
        # these slots; first use deliberately forces conversion.
        u.mem_write(0xFD6A, b"\x5a\xa5")
        u.mem_write(0x8204, b"\x5a")
        initial = {
            UC_X86_REG_CS: 0x6000,
            UC_X86_REG_SS: 0,
            UC_X86_REG_SP: 0xF000,
            UC_X86_REG_DS: 0x1234,
            UC_X86_REG_ES: 0x2345,
            UC_X86_REG_AX: 0x123,
            UC_X86_REG_BX: 0x234,
            UC_X86_REG_CX: 0x345,
            UC_X86_REG_DX: 0x456,
            UC_X86_REG_SI: 0x567,
            UC_X86_REG_DI: 0x678,
            UC_X86_REG_BP: 0x789,
        }
        for register, value in initial.items():
            u.reg_write(register, value)
        bank = [0x91]
        u.hook_add(
            UC_HOOK_INSN,
            lambda uc, port, size, data: bank[0],
            None,
            1,
            0,
            UC_X86_INS_IN,
        )

        def output(uc, port, size, value, data):
            self.assertEqual(port, 0xC2)
            bank[0] = value

        u.hook_add(UC_HOOK_INSN, output, None, 1, 0, UC_X86_INS_OUT)
        visits = []

        def trace(uc, address, size, data):
            if address in (0x120, 0x402A9, 0x61005):
                visits.append(address)
                if address != 0x120:
                    uc.emu_stop()

        u.hook_add(UC_HOOK_CODE, trace)
        u.emu_start(0x61000, 0xFFFFF, count=30000)
        self.assertEqual(
            visits,
            [0x120, 0x61005],
            "must return directly, never run startup relocation at 02A9",
        )
        for register, value in initial.items():
            self.assertEqual(u.reg_read(register), value)
        self.assertEqual(bank[0], 0x91)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), staging)
        self.assertEqual(
            bytes(u.mem_read(0x3800, 2048)), bytes(2048) if changed else staging
        )
        expected = bytes([0x55, 0xAA, 0, 0] * 1024) if changed else sentinel
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), expected)

    def test_changed_tiles_return_and_preserve_caller(self) -> None:
        self.run_hook(True)

    def test_equal_tiles_preserve_destination_and_return(self) -> None:
        self.run_hook(False)

    def test_fight_wait_dispatch_and_return(self) -> None:
        # Signal the original VBlank counter when the assembled wait enables IRQs.
        # The ordinary path runs the real atomic copier with its original stack.
        for remaining, cursor in ((0, 0), (1, 32), (1, 0)):
            with self.subTest(remaining=remaining, cursor=cursor):
                queued = remaining > 0 and cursor == 0
                u = Uc(UC_ARCH_X86, UC_MODE_16)
                u.mem_map(0, 0x100000)
                u.mem_write(0x420AE, self.rom.patches[0x1420AE] + b"\xf4")
                u.mem_write(0x4FD22, self.rom.writes[0x14FD22])
                u.mem_write(0x400D7, bytes.fromhex("39c9cb"))  # equal CMP, RETF
                u.mem_write(0x402A4, bytes.fromhex("ea20010000"))
                u.mem_write(0x120, self.rom.patches[0x1402C0])
                u.mem_write(0x8200, bytes((remaining, 0, cursor, 0, 90)))
                u.mem_write(0x11020, b"\x55\x55")
                u.mem_write(0x1106A, b"\x55\x55")
                regs = {
                    UC_X86_REG_CS: 0x4000, UC_X86_REG_SP: 0xE000,
                    UC_X86_REG_DS: 0x1234, UC_X86_REG_ES: 0x2345,
                    UC_X86_REG_BX: 0x3333, UC_X86_REG_BP: 0x5555,
                    UC_X86_REG_SI: 0x7777, UC_X86_REG_DI: 0x8888,
                    UC_X86_REG_CX: 1, UC_X86_REG_EFLAGS: 0x603,
                }
                for reg, value in regs.items():
                    u.reg_write(reg, value)
                visits = []

                def trace(uc, address, size, _):
                    if address in (0x400D7, 0x120, 0x420B8):
                        visits.append(address)
                    if bytes(uc.mem_read(address, size)) == bytes.fromhex("390e2010"):
                        self.assertTrue(uc.reg_read(UC_X86_REG_EFLAGS) & 0x200)
                        self.assertEqual(bytes(uc.mem_read(0x8204, 1)), b"\xda")
                        self.assertEqual(bytes(uc.mem_read(0x11020, 2)), b"\0\0")
                        uc.mem_write(0x11020, b"\x01\x00")
                        visits.append("interrupt")
                    if address == 0x420B8:
                        uc.emu_stop()

                u.hook_add(UC_HOOK_CODE, trace)
                u.emu_start(0x420AE, 0xFFFFF, count=3000)
                self.assertEqual(visits, (["interrupt"] if queued else [0x400D7, 0x120]) + [0x420B8])
                if queued:
                    self.assertEqual(bytes(u.mem_read(0x1106A, 2)), b"\0\0")
                else:
                    self.assertEqual(bytes(u.mem_read(0x8204, 1)), b"\x5a")
                regs.update({UC_X86_REG_AX: 32, UC_X86_REG_CX: 0,
                             UC_X86_REG_DX: 0xE000 - 10, UC_X86_REG_EFLAGS: 0x646})
                for reg, value in regs.items():
                    self.assertEqual(u.reg_read(reg), value)

    def test_atomic_template_is_hybrid_only(self) -> None:
        import build

        self.assertEqual(len(self.rom.patches[0x1402C0]), 84)
        self.assertTrue(self.rom.patches[0x1402C0].startswith(b"\x9c\xfa"))
        plain = RecordingRom()
        with patch.dict(os.environ, {"PF_HYBRID": "0"}):
            build.apply_engine(plain)
        self.assertNotIn(0x1402C0, plain.patches)
        self.assertNotIn(0x1402A4, plain.patches)
        self.assertNotIn(0x1420AE, plain.patches)
