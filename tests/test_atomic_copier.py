"""Interrupt delivery while the real RAM copier borrows SP as its source pointer."""

from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
    from unicorn.x86_const import *
except ImportError:
    Uc = None


@unittest.skipUnless(Uc and shutil.which("nasm"), "requires NASM and Unicorn")
class AtomicCopierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import asm

        cls.code, _ = asm.assemble("copier")

    def execute(self, code: bytes, flags: int, interrupt: bool) -> tuple:
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x100000)
        u.mem_write(0x120, code)
        u.mem_write(0x61000, bytes.fromhex("9a20010000f4"))
        # A legal interrupt handler that saves/restores registers and returns.
        # Handler code must be outside the borrowed stack/source range.
        u.mem_write(0x11000, b"\x60\x61\xcf")
        source = bytes((i * 37 + i // 17) & 255 for i in range(2048))
        u.mem_write(0x500, source)
        u.mem_write(0x37F0, bytes([0xCC]) * 16)
        u.mem_write(0x4000, bytes([0xCC]) * 16)
        initial = {
            UC_X86_REG_CS: 0x6000,
            UC_X86_REG_SS: 0,
            UC_X86_REG_SP: 0xF000,
            UC_X86_REG_DS: 0x1234,
            UC_X86_REG_ES: 0x2345,
            UC_X86_REG_DI: 0x5678,
            UC_X86_REG_BX: 0x3456,
            UC_X86_REG_BP: 0x4567,
            UC_X86_REG_SI: 0x6789,
            UC_X86_REG_EFLAGS: flags,
        }
        for reg, value in initial.items():
            u.reg_write(reg, value)
        pending, delivered, borrowed_if = [False], [], []

        def instruction(uc, address, size, data):
            sp = uc.reg_read(UC_X86_REG_SP)
            psw = uc.reg_read(UC_X86_REG_EFLAGS)
            if address == 0x61005:
                uc.emu_stop()
                return
            # Request IRQ partway through the copy. Delivery obeys x86 IF.
            if 0x600 <= sp < 0xC00 and address < 0x180:
                borrowed_if.append(bool(psw & 0x200))
                if interrupt and not delivered:
                    pending[0] = True
            if pending[0] and psw & 0x200:
                cs = uc.reg_read(UC_X86_REG_CS)
                ip = uc.reg_read(UC_X86_REG_IP)
                ss = uc.reg_read(UC_X86_REG_SS)
                for word in (psw, cs, ip):
                    sp = (sp - 2) & 0xFFFF
                    uc.mem_write(ss * 16 + sp, (word & 0xFFFF).to_bytes(2, "little"))
                uc.reg_write(UC_X86_REG_SP, sp)
                uc.reg_write(UC_X86_REG_EFLAGS, psw & ~0x300)
                uc.reg_write(UC_X86_REG_CS, 0x1000)
                uc.reg_write(UC_X86_REG_IP, 0x1000)
                delivered.append(sp)
                pending[0] = False

        u.hook_add(UC_HOOK_CODE, instruction)
        u.emu_start(0x61000, 0xFFFFF, count=10000)
        self.assertTrue(borrowed_if)
        self.assertEqual(u.reg_read(UC_X86_REG_CS), 0x6000)
        self.assertEqual(u.reg_read(UC_X86_REG_IP), 0x1005)
        for reg, value in initial.items():
            if reg != UC_X86_REG_EFLAGS:
                self.assertEqual(u.reg_read(reg), value)
        self.assertEqual(u.reg_read(UC_X86_REG_AX), 32)
        self.assertEqual(u.reg_read(UC_X86_REG_CX), 0)
        self.assertEqual(u.reg_read(UC_X86_REG_EFLAGS) & 0x600, flags & 0x600)
        self.assertEqual(bytes(u.mem_read(0x37F0, 16)), bytes([0xCC]) * 16)
        self.assertEqual(bytes(u.mem_read(0x4000, 16)), bytes([0xCC]) * 16)
        return (
            source,
            bytes(u.mem_read(0x500, 2048)),
            bytes(u.mem_read(0x3800, 2048)),
            delivered,
            borrowed_if,
        )

    def test_relocation_keeps_original_size(self) -> None:
        self.assertEqual(len(self.code), 84)

    def test_pending_irq_delivered_after_stack_restore(self) -> None:
        source, after, dest, delivered, enabled = self.execute(self.code, 0x602, True)
        self.assertEqual(source, after)
        self.assertEqual(source, dest)
        self.assertEqual(len(delivered), 1)
        self.assertGreater(delivered[0], 0xCFF)
        self.assertFalse(any(enabled))

    def test_disabled_irq_and_direction_flag_restored(self) -> None:
        source, after, dest, delivered, enabled = self.execute(self.code, 0x402, True)
        self.assertEqual(source, after)
        self.assertEqual(source, dest)
        self.assertEqual(delivered, [])
        self.assertFalse(any(enabled))

    def test_unmasked_control_reproduces_source_damage(self) -> None:
        # Removing the mask from this same routine is a negative control, not
        # a copy of copyrighted original code in the test fixture.
        unmasked = self.code.replace(b"\xfa", b"\x90", 1)
        source, after, dest, delivered, enabled = self.execute(unmasked, 0x202, True)
        self.assertNotEqual(source, after)
        self.assertTrue(delivered)
        self.assertLess(delivered[0], 0xD00)
        self.assertTrue(any(enabled))
