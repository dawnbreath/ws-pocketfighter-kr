"""Hash partitions and emitted bank switching, without game assets."""

import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import test_class_table as legacy
from class_table import HEADER, FULL_RECORD, hash16
from colour_layout import CLASS_TABLE_BASE, CLASS_SHARD_BANK_BASE
from sharded_colour_table import pack_shards, write_shards, read_shards
from test_full_colour_table import solid


def records():
    return [
        (
            bytes(14) + struct.pack("<H", n << 12 | 0x123),
            solid(bytes(14) + struct.pack("<H", n << 12 | 0x123), 2 + n % 2),
        )
        for n in range(16)
    ]


class ShardFormatTests(unittest.TestCase):
    def test_roundtrip_and_wrong_partition_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "table"
            write_shards(records(), legacy.PAL, root)
            blobs = read_shards(root)
            self.assertEqual([HEADER.unpack_from(b)[1] for b in blobs], [1] * 16)
            for n, b in enumerate(blobs):
                self.assertEqual(FULL_RECORD.unpack_from(b, 6)[1:], records()[n])
            # An internally valid blob in the wrong bucket must still fail.
            (root / "00.ctb3").write_bytes(blobs[1])
            import hashlib

            p = root / "manifest.json"
            m = json.loads(p.read_text())
            m["sha256"][0] = hashlib.sha256(blobs[1]).hexdigest()
            p.write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, "wrong hash partition"):
                read_shards(root)


@unittest.skipUnless(legacy.Uc and shutil.which("nasm"), "requires NASM and Unicorn")
class ShardRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import asm

        cls.code, _ = asm.assemble(
            "col",
            {
                "HYBRID": "1",
                "BPP4": "1",
                "CTAB": "1",
                "FULLTILE": "1",
                "FPAL": "1",
                "SHARDED": "1",
            },
        )

    def machine(self, rows):
        from unicorn import UC_HOOK_INSN
        from unicorn.x86_const import UC_X86_INS_OUT

        u = legacy.Uc(legacy.UC_ARCH_X86, legacy.UC_MODE_16)
        u.mem_map(0, 0x100000)
        images = {}
        for n, t in enumerate(pack_shards(rows, legacy.PAL)):
            b = bytearray(b"\xff" * 65536)
            b[: len(self.code)] = self.code
            b[CLASS_TABLE_BASE : CLASS_TABLE_BASE + len(t)] = t
            images[CLASS_SHARD_BANK_BASE + n] = bytes(b)
        images[0xCD] = images[CLASS_SHARD_BANK_BASE]
        images[0xA7] = b"\xa7" * 65536
        u.mem_write(0x20000, images[0xCD])
        self.ports = []

        def out(uc, port, size, value, user):
            self.assertEqual((port, size), (0xC2, 1))
            self.ports.append(value)
            uc.mem_write(0x20000, images[value])

        u.hook_add(UC_HOOK_INSN, out, None, 1, 0, UC_X86_INS_OUT)
        u.mem_write(0x61000, bytes.fromhex("9a00050020f4"))
        u.reg_write(legacy.UC_X86_REG_CS, 0x6000)
        u.reg_write(legacy.UC_X86_REG_SP, 0xF000)
        u.reg_write(legacy.UC_X86_REG_DS, 0x1234)
        u.reg_write(legacy.UC_X86_REG_ES, 0x2345)
        return u, images

    def run_source(self, u, source):
        u.mem_write(0x500, source)
        u.mem_write(0x3800, b"\xff" * 2048)
        u.emu_start(0x61000, 0xFFFFF, count=300000)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_SP), 0xF000)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_DS), 0x1234)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_ES), 0x2345)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), source)
        return bytes(u.mem_read(0x7000, 4096))

    def test_all_banks_collisions_misses_and_distinct_tiles(self):
        from unicorn import UC_HOOK_MEM_WRITE

        rows = records() + [
            (legacy.A, solid(legacy.A, 2)),
            (legacy.B, solid(legacy.B, 3)),
        ]
        sequence = [rows[n % len(rows)] for n in range(128)]
        sequence[19] = (
            legacy.C,
            b"".join(legacy.C[i : i + 2] + b"\0\0" for i in range(0, 16, 2)),
        )
        u, _ = self.machine(rows)
        tile_starts = []

        def record_write(_machine, _access, address, _size, _value, _user):
            slot, offset = divmod(address - 0x7000, 32)
            if offset == 0:
                tile_starts.append(slot)

        u.hook_add(UC_HOOK_MEM_WRITE, record_write, begin=0x7000, end=0x7FFF)
        result = self.run_source(u, b"".join(s for s, _ in sequence))
        self.assertEqual(result, b"".join(o for _, o in sequence))
        self.assertEqual(tile_starts[::2], list(range(64)))
        self.assertEqual(tile_starts[1::2], list(range(127, 63, -1)))
        self.assertEqual(
            self.ports,
            [
                CLASS_SHARD_BANK_BASE + (hash16(sequence[slot][0]) >> 12)
                for slot in tile_starts
            ],
        )

    def test_unchanged_tiles_do_not_switch_banks(self):
        source = records()[0][0] * 128
        u, _ = self.machine(records())
        u.mem_write(0x500, source)
        u.mem_write(0x3800, source)
        u.mem_write(0x7000, b"\x55" * 4096)
        u.mem_write(0xFD6A, b"\x5a\xa5")
        u.mem_write(0x8204, b"\x5a")
        u.emu_start(0x61000, 0xFFFFF, count=100000)
        self.assertEqual(self.ports, [])
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), b"\x55" * 4096)

    def test_full_partition_signed_boundary_and_more_than_one_bank_capacity(self):
        rows = []
        for n in range(1135):
            raw = bytes(14) + struct.pack("<H", 0xF000 + n)
            rows.append((raw, solid(raw, 2)))
        source, output = rows[-1]
        u, _ = self.machine(rows)
        self.assertEqual(self.run_source(u, source * 128), output * 128)
        # Four thousand globally distinct records fit distributed partitions.
        distributed = []
        for n in range(4000):
            raw = bytes(14) + struct.pack("<H", (n % 16) << 12 | (n // 16))
            distributed.append((raw, solid(raw, 2)))
        self.assertEqual(
            sum(HEADER.unpack_from(b)[1] for b in pack_shards(distributed, legacy.PAL)),
            4000,
        )
        raw = bytes(14) + struct.pack("<H", 0xF000 + 1135)
        with self.assertRaises(ValueError):
            pack_shards(rows + [(raw, solid(raw, 2))], legacy.PAL)

    def test_existing_copier_stub_restores_caller_bank(self):
        import asm
        from unicorn import UC_HOOK_INSN
        from unicorn.x86_const import UC_X86_INS_IN

        code, sym = asm.assemble("kr_stubs", {"HYBRID": "1", "COL_BANK": "0xCD"})
        u, images = self.machine(records())
        u.mem_write(0x5FF34, code)
        u.mem_write(0x20000, images[0xA7])
        u.hook_add(UC_HOOK_INSN, lambda uc, p, s, user: 0xA7, None, 1, 0, UC_X86_INS_IN)
        u.mem_write(0x61000, b"\xea" + struct.pack("<HH", sym["cpstub"], 0x5000))
        u.mem_write(0x120, b"\xf4")
        source = b"".join(records()[n % 16][0] for n in range(128))
        u.mem_write(0x500, source)
        u.mem_write(0x3800, b"\xff" * 2048)
        u.emu_start(0x61000, 0xFFFFF, count=300000)
        self.assertEqual((self.ports[0], self.ports[-1]), (0xCD, 0xA7))
        self.assertEqual(bytes(u.mem_read(0x20000, 65536)), images[0xA7])
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_SP), 0xF000)
