"""Diagnostic table bounds and real assembled collision handling; no game data."""

import os
from pathlib import Path
import shutil
import struct
import sys
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from class_table import hash16, pack_table, validate_table, convert_pgmd, MAX_SIZE

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn.x86_const import (
        UC_X86_REG_CS,
        UC_X86_REG_SP,
        UC_X86_REG_DS,
        UC_X86_REG_ES,
        UC_X86_REG_IP,
    )
except ImportError:
    Uc = None

A = bytes(16)
B = struct.pack("<8H", 1, 8, 0, 0, 0, 0, 0, 0)
C = struct.pack("<8H", 2, 16, 0, 0, 0, 0, 0, 0)
PAL = struct.pack("<32H", *range(32))


class FormatTests(unittest.TestCase):
    def test_bounds_version_hash_and_palette(self) -> None:
        good = pack_table([(B, bytes(16))], PAL)
        validate_table(good)
        for bad in [
            good[:-1],
            good + b"\x00",
            b"PGMD" + good[4:],
            bytes(MAX_SIZE + 1),
            good[:6] + b"\x01\x00" + good[8:],
            good[:-2] + b"\xff\xff",
        ]:
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                validate_table(bad)
        with self.assertRaises(ValueError):
            pack_table([(B, bytes(16)), (B, bytes([255] * 16))], PAL)

    def test_capacity_limit(self) -> None:
        records = [(i.to_bytes(16, "little"), bytes(16)) for i in range(961)]
        self.assertLessEqual(len(pack_table(records, PAL)), MAX_SIZE)
        with self.assertRaises(ValueError):
            pack_table(records + [((961).to_bytes(16, "little"), bytes(16))], PAL)

    def test_pgmd_roundtrip(self) -> None:
        pgmd = struct.pack("<4sHHI", b"PGMD", 1, 37, 1) + struct.pack(
            "<I16sB16s", zlib.crc32(B), B, 255, bytes([85] * 16)
        )
        blob = convert_pgmd(pgmd, PAL)
        self.assertEqual(blob[8:24], B)
        self.assertEqual(blob[24:40], bytes([85] * 16))
        with self.assertRaises(ValueError):
            convert_pgmd(b"bad", PAL)


@unittest.skipUnless(Uc and shutil.which("nasm"), "requires NASM and optional Unicorn")
class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import asm

        cls.code, _ = asm.assemble("col", {"HYBRID": "1", "BPP4": "1", "CTAB": "1"})

    def run_table(self, source: bytes, records: list[tuple[bytes, bytes]]) -> bytes:
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x100000)
        u.mem_write(0x20000, self.code)
        u.mem_write(0x28000, pack_table(records, PAL))
        u.mem_write(0x61000, bytes.fromhex("9a00050020f4"))
        u.mem_write(0x500, source * 128)
        u.mem_write(0x3800, bytes([255] * 2048))
        u.reg_write(UC_X86_REG_CS, 0x6000)
        u.reg_write(UC_X86_REG_SP, 0xF000)
        u.reg_write(UC_X86_REG_DS, 0x1234)
        u.reg_write(UC_X86_REG_ES, 0x2345)
        u.emu_start(0x61000, 0xFFFFF, count=100000)
        self.assertEqual(u.reg_read(UC_X86_REG_CS), 0x6000)
        self.assertEqual(u.reg_read(UC_X86_REG_IP), 0x1006)
        self.assertEqual(u.reg_read(UC_X86_REG_SP), 0xF000)
        self.assertEqual(u.reg_read(UC_X86_REG_DS), 0x1234)
        self.assertEqual(u.reg_read(UC_X86_REG_ES), 0x2345)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), source * 128)
        self.assertEqual(bytes(u.mem_read(0xFF80, 64)), PAL)
        return bytes(u.mem_read(0x7000, 4096))

    def test_collision_hit_checks_exact_source(self) -> None:
        self.assertEqual(hash16(A), hash16(B))
        self.assertEqual(hash16(B), hash16(C))
        mask = bytes([0, 255] * 8)
        result = self.run_table(B, [(A, bytes([255, 0] * 8)), (B, mask)])
        expected = b"".join(
            B[i : i + 2] + bytes([0, B[i] | B[i + 1]]) for i in range(0, 16, 2)
        )
        self.assertEqual(result, expected * 128)

    def test_unseen_hash_collision_falls_back(self) -> None:
        result = self.run_table(C, [(A, bytes([255] * 16)), (B, bytes([255] * 16))])
        expected = b"".join(C[i : i + 2] + b"\0\0" for i in range(0, 16, 2))
        self.assertEqual(result, expected * 128)

    def test_empty_table_falls_back(self) -> None:
        result = self.run_table(B, [])
        expected = b"".join(B[i : i + 2] + b"\0\0" for i in range(0, 16, 2))
        self.assertEqual(result, expected * 128)
