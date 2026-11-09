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
        self.code = b""

    def put_free(self, offset: int, code: bytes, why: str) -> None:
        self.code = code

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
        u.mem_write(0x5FF34, self.rom.code)
        u.mem_write(0x20000, self.color)
        u.mem_write(0x120, b"\xcb")
        staging = bytes([0x55, 0xAA] * 1024)
        u.mem_write(0x500, staging)
        u.mem_write(0x3800, bytes(2048) if changed else staging)
        sentinel = bytes([0x7E] * 4096)
        u.mem_write(0x7000, sentinel)
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
