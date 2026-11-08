"""Execute only the diagnostic assembly with synthetic memory/ports (no ROM)."""

import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

try:
    import unicorn as u
    from unicorn import x86_const as x
except ImportError:
    u = None

NASM = os.environ.get("NASM") or shutil.which("nasm")
ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    u is not None and NASM,
    "requires NASM and Python unicorn for isolated 16-bit execution",
)
class OamDiagnosticTests(unittest.TestCase):
    def run_code(
        self, start: int, count: int, fields: dict[int, int], oamtest: bool = True
    ):
        source = Path(
            os.environ.get("OAM_DIAG_SOURCE", ROOT / "src/diag/bpp4_oamtest.asm")
        ).resolve()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asm = root / "test.asm"
            binary = root / "test.bin"
            asm.write_text(
                "bits 16\ncpu 186\norg 0x1000\n%define BPP4DIAG 1\n"
                + ("%define OAMTEST 1\n%define DIAG_RECORD 0xFDA8\n" if oamtest else "")
                + 'call mirror4\nhlt\n%include "'
                + str(source)
                + '"\n'
            )
            subprocess.run(
                [str(NASM), "-f", "bin", str(asm), "-o", str(binary)],
                check=True,
                capture_output=True,
            )
            code = binary.read_bytes()
        emu = u.Uc(u.UC_ARCH_X86, u.UC_MODE_16)
        emu.mem_map(0, 0x20000)
        emu.mem_write(0x1000, code)
        emu.mem_write(0x2000, bytes([255, 0]) * 4096)
        oam = bytearray(512)
        for slot in range(128):
            struct.pack_into(
                "<HBB",
                oam,
                slot * 4,
                slot | (fields.get(slot, 2) << 9) | 0xC000,
                20,
                30,
            )
        emu.mem_write(0xE00, bytes(oam))
        emu.mem_write(0xFDA8, b"\xaa" * 6)
        emu.mem_write(0xFD60, b"\x5a" * 6)
        initial = {
            x.UC_X86_REG_AX: 0x1234,
            x.UC_X86_REG_BX: 0x2345,
            x.UC_X86_REG_CX: (start << 8) | count,
            x.UC_X86_REG_DX: 0x4567,
            x.UC_X86_REG_SI: 0x5678,
            x.UC_X86_REG_DI: 0x6789,
            x.UC_X86_REG_BP: 0x789A,
            x.UC_X86_REG_SP: 0xF000,
            x.UC_X86_REG_ES: 0x1111,
        }
        for reg, value in initial.items():
            emu.reg_write(reg, value)
        emu.reg_write(x.UC_X86_REG_EFLAGS, 0x2)
        # Ports 5/6 intentionally describe a stale list, unlike caller CH/CL.
        emu.hook_add(
            u.UC_HOOK_INSN,
            lambda uc, port, size, data: {4: 7, 5: 0, 6: 128}.get(port, 0),
            None,
            1,
            0,
            x.UC_X86_INS_IN,
        )
        emu.emu_start(0x1000, 0x1000 + len(code), count=100000)
        self.assertEqual(
            emu.reg_read(x.UC_X86_REG_IP), 0x1004, "wrapper must reach HLT"
        )
        return emu, bytes(oam), initial

    def test_caller_range_not_stale_ports(self) -> None:
        emu, before, _ = self.run_code(10, 2, {0: 4, 10: 4, 11: 5})
        after = bytes(emu.mem_read(0xE00, 512))
        self.assertEqual(after[:40], before[:40])
        self.assertEqual(after[48:], before[48:])
        self.assertEqual((int.from_bytes(after[40:42], "little") >> 9) & 7, 0)
        self.assertEqual((int.from_bytes(after[44:46], "little") >> 9) & 7, 1)
        self.assertEqual(bytes(emu.mem_read(0xFDA8, 2)), bytes([2, 0]))
        self.assertEqual(bytes(emu.mem_read(0xFDAC, 2)), bytes([10, 2]))
        self.assertEqual(emu.mem_read(0x4000 + 10 * 32 + 2, 1)[0], 15)
        self.assertEqual(emu.mem_read(0x4000 + 2, 1)[0], 0)

    def test_ring_wrap(self) -> None:
        emu, before, _ = self.run_code(126, 4, {126: 4, 127: 5, 0: 4, 1: 5, 10: 4})
        after = bytes(emu.mem_read(0xE00, 512))
        changed = [
            i
            for i in range(128)
            if before[4 * i : 4 * i + 4] != after[4 * i : 4 * i + 4]
        ]
        self.assertEqual(changed, [0, 1, 126, 127])
        self.assertEqual(emu.mem_read(0xFDA8, 1)[0], 4)

    def test_field5_only_does_not_require_a_field4_sprite(self) -> None:
        emu, before, _ = self.run_code(10, 2, {10: 5})
        after = bytes(emu.mem_read(0xE00, 512))
        self.assertEqual(after[:40], before[:40])
        self.assertEqual(after[44:], before[44:])
        self.assertEqual((int.from_bytes(after[40:42], "little") >> 9) & 7, 1)
        self.assertEqual(emu.mem_read(0xFDA8, 1)[0], 1)

    def test_empty_range_has_no_selected_tile(self) -> None:
        emu, before, _ = self.run_code(10, 0, {0: 4})
        self.assertEqual(bytes(emu.mem_read(0xE00, 512)), before)
        self.assertEqual(bytes(emu.mem_read(0xFD60, 6)), b"\x5a" * 6)
        self.assertEqual(bytes(emu.mem_read(0xFDA8, 6)), bytes([0, 255, 0, 0, 10, 0]))
        self.assertEqual(emu.mem_read(0x4002, 1)[0], 0)

    def test_call_preserves_registers_and_direction(self) -> None:
        for mode in (False, True):
            emu, _, initial = self.run_code(10, 2, {10: 4, 11: 5}, mode)
            for reg, value in initial.items():
                self.assertEqual(emu.reg_read(reg), value, (mode, reg))
            self.assertEqual(emu.reg_read(x.UC_X86_REG_EFLAGS) & 0x400, 0)


if __name__ == "__main__":
    unittest.main()
