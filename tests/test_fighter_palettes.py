"""Per-fighter catalogue validation and emitted HUD lookup/palette selection."""

import copy
from pathlib import Path
import shutil
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from fighter_palettes import install, encode, BASE

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_SP
except ImportError:
    Uc = None

CHARS = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
CONFIG = {
    "version": 1,
    "fallback": ["111"] * 16,
    "fighters": {"A": ["123"] * 16, "B": ["abc"] * 16},
}


def hud_hash(raw: bytes) -> int:
    h = 0
    for (word,) in struct.iter_unpack("<H", raw):
        h = ((h << 3) | (h >> 13)) & 65535
        h ^= word
    return h


class CatalogueTests(unittest.TestCase):
    def test_catalogue_pointers_and_unknown_character(self) -> None:
        bank = bytearray(65536)
        install(bank, CHARS, CONFIG, 0x2000)
        self.assertEqual(struct.unpack_from("<H", bank, 0xE00 + 22)[0], BASE + 32)
        self.assertEqual(struct.unpack_from("<H", bank, 0xE18 + 22)[0], BASE + 64)
        self.assertEqual(struct.unpack_from("<H", bank, 0xE30 + 22)[0], 0)
        self.assertEqual(bank[BASE : BASE + 32], encode(CONFIG["fallback"]))

    def test_invalid_catalogue_does_not_mutate_bank(self) -> None:
        bad = copy.deepcopy(CONFIG)
        bad["fighters"]["A"] = ["fff"] * 15
        for config, end in [
            (bad, 0x2000),
            (CONFIG, BASE + 1),
            ({**CONFIG, "fighters": {"wrong": ["123"] * 16}}, 0x2000),
        ]:
            bank = bytearray(65536)
            with self.assertRaises(ValueError):
                install(bank, CHARS, config, end)
            self.assertFalse(any(bank))


@unittest.skipUnless(Uc and shutil.which("nasm"), "requires NASM and Unicorn")
class EmittedPaletteTests(unittest.TestCase):
    def test_name_changes_swap_palettes_and_unknown_falls_back(self) -> None:
        import asm

        code, _ = asm.assemble(
            "col", {"HYBRID": "1", "BPP4": "1", "CTAB": "1", "FPAL": "1"}
        )
        bank = bytearray(65536)
        bank[: len(code)] = code
        bank[0x800:0x802] = b"\xff\xff"
        install(bank, CHARS, CONFIG, 0x2000)
        p1 = [bytes([n, 0]) + bytes(62) for n in [1, 2, 3]]
        p2 = [bytes([n, 0]) + bytes(110) for n in [4, 5, 6]]
        for start, sources in [(0xD40, p1), (0xD80, p2)]:
            for i, raw in enumerate(sources):
                struct.pack_into(
                    "<HH", bank, start + 4 * i, hud_hash(raw), 0xE00 + 24 * i
                )
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x100000)
        u.mem_write(0x20000, bytes(bank))
        u.mem_write(0x61000, bytes.fromhex("9a00000020f4"))
        u.mem_write(0xFD6A, b"\x5a\xa5")
        u.mem_write(0x8204, b"\x5a")

        def invoke(left: bytes, right: bytes) -> tuple[bytes, bytes]:
            u.mem_write(0x3620, left)
            u.mem_write(0x36B0, right)
            u.reg_write(UC_X86_REG_CS, 0x6000)
            u.reg_write(UC_X86_REG_SP, 0xF000)
            u.emu_start(0x61000, 0xFFFFF, count=100000)
            self.assertEqual(u.reg_read(UC_X86_REG_SP), 0xF000)
            return bytes(u.mem_read(0xFF80, 32)), bytes(u.mem_read(0xFFA0, 32))

        a, b = encode(CONFIG["fighters"]["A"]), encode(CONFIG["fighters"]["B"])
        fallback = encode(CONFIG["fallback"])
        self.assertEqual(invoke(p1[0], p2[1]), (a, b))
        marker = bytes([0x55]) * 32
        u.mem_write(0xFF80, marker)
        self.assertEqual(invoke(p1[0], p2[1]), (marker, b))
        self.assertEqual(invoke(p1[1], p2[0]), (b, a))
        self.assertEqual(invoke(bytes(64), p2[0]), (fallback, a))
        self.assertEqual(invoke(p1[2], p2[1]), (fallback, b))
        # With neither name recognized, leave higher scene entries untouched.
        u.mem_write(0xFF80, marker)
        u.mem_write(0xFFA0, marker)
        left, right = invoke(bytes(64), bytes(112))
        self.assertEqual(left[10:], marker[10:])
        self.assertEqual(right[10:], marker[10:])
