"""Character-scoped exact-source lookup and owner changes with unchanged 2bpp."""

import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import test_class_table as legacy
from test_full_colour_table import solid
from class_table import HEADER, CONTEXT_RECORD, validate_table
from sharded_colour_table import (
    write_context_shards,
    read_shards,
    read_catalogue,
    read_context_overrides,
    write_shards,
)
from colour_layout import CLASS_TABLE_BASE, CLASS_SHARD_BANK_BASE
from fighter_contexts import active_contexts


class ContextFormatTests(unittest.TestCase):
    def test_owner_mapping_requires_a_present_assigned_selector(self):
        self.assertEqual(active_contexts({1, 255}), {"GOUKI": 1})
        self.assertEqual(active_contexts({1, 2, 255}), {"GOUKI": 1, "MORRIGAN": 2})
        self.assertEqual(active_contexts({255}), {})
        with self.assertRaises(ValueError):
            active_contexts({3, 255})

    def test_variants_fall_back_and_do_not_change_canonical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "table"
            write_context_shards(
                [(legacy.A, solid(legacy.A, 2))],
                {1: {legacy.A: solid(legacy.A, 0)}},
                legacy.PAL,
                root,
            )
            self.assertEqual(read_catalogue(root)[0][0][2], solid(legacy.A, 2))
            self.assertEqual(read_catalogue(root, 1)[0][0][2], solid(legacy.A, 0))
            self.assertEqual(read_catalogue(root, 2)[0], read_catalogue(root)[0])
            self.assertEqual(
                sum(HEADER.unpack_from(b)[1] for b in read_shards(root)), 2
            )

    def test_duplicate_context_missing_fallback_and_reserved_rejected(self):
        output = solid(legacy.A, 0)
        from class_table import hash16

        h = hash16(legacy.A)
        for rows in [
            [(h, legacy.A, 1, 0, output)],
            [(h, legacy.A, 255, 0, output)] * 2,
            [(h, legacy.A, 255, 1, output)],
        ]:
            blob = (
                HEADER.pack(b"CTB4", len(rows))
                + b"".join(CONTEXT_RECORD.pack(*row) for row in rows)
                + legacy.PAL
            )
            with self.assertRaises(ValueError):
                validate_table(blob)

    def test_partition_capacity_and_invalid_output_rejected(self):
        rows = []
        for n in range(1091):
            raw = bytes(14) + struct.pack("<H", 0xF000 + n)
            rows.append((raw, solid(raw, 2)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_context_shards(rows, {}, legacy.PAL, root / "full")
            with self.assertRaises(ValueError):
                write_context_shards(
                    rows,
                    {1: {rows[-1][0]: solid(rows[-1][0], 0)}},
                    legacy.PAL,
                    root / "overflow",
                )
            with self.assertRaises(ValueError):
                write_context_shards(
                    rows, {1: {rows[-1][0]: bytes(33)}}, legacy.PAL, root / "bad"
                )

    def test_existing_writer_retains_variants_after_canonical_compaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_context_shards(
                [(legacy.A, solid(legacy.A, 0))],
                {1: {legacy.A: solid(legacy.A, 2)}},
                legacy.PAL,
                root / "before",
            )
            contexts = read_context_overrides(root / "before")
            write_shards([], legacy.PAL, root / "after", contexts=contexts)
            self.assertEqual(read_shards(root / "before"), read_shards(root / "after"))
            self.assertEqual(
                read_catalogue(root / "after", 1)[0][0][2], solid(legacy.A, 2)
            )
            with self.assertRaises(ValueError):
                write_shards(
                    [(legacy.A, solid(legacy.A, 0))] * 2,
                    legacy.PAL,
                    root / "duplicate",
                    contexts=contexts,
                )


@unittest.skipUnless(legacy.Uc and shutil.which("nasm"), "requires NASM and Unicorn")
class ContextRuntimeTests(unittest.TestCase):
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
                "CONTEXT": "1",
            },
        )

    def machine(self, canonical=None, overrides=None, owners=(1, 0)):
        from unicorn import UC_HOOK_INSN
        from unicorn.x86_const import UC_X86_INS_OUT, UC_X86_INS_IN

        canonical = canonical or [
            (legacy.A, solid(legacy.A, 2)),
            (legacy.B, solid(legacy.B, 3)),
        ]
        overrides = (
            overrides if overrides is not None else {1: {legacy.A: solid(legacy.A, 0)}}
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "table"
            write_context_shards(canonical, overrides, legacy.PAL, root)
            tables = read_shards(root)
        u = legacy.Uc(legacy.UC_ARCH_X86, legacy.UC_MODE_16)
        u.mem_map(0, 0x100000)
        images = {}
        for n, table in enumerate(tables):
            b = bytearray(b"\xff" * 65536)
            b[: len(self.code)] = self.code
            b[CLASS_TABLE_BASE : CLASS_TABLE_BASE + len(table)] = table
            b[0xE15], b[0xE2D] = owners
            images[CLASS_SHARD_BANK_BASE + n] = bytes(b)
        u.mem_write(0x20000, images[CLASS_SHARD_BANK_BASE])
        self.ports = []

        def out(uc, port, size, value, user):
            self.assertEqual((port, size), (0xC2, 1))
            self.ports.append(value)
            uc.mem_write(0x20000, images[value])

        def inp(uc, port, size, user):
            self.assertEqual((port, size), (4, 1))
            return 7

        u.hook_add(UC_HOOK_INSN, out, None, 1, 0, UC_X86_INS_OUT)
        u.hook_add(UC_HOOK_INSN, inp, None, 1, 0, UC_X86_INS_IN)
        u.mem_write(0x61000, bytes.fromhex("9a00050020f4"))
        u.mem_write(0x61020, bytes.fromhex("9a40020020f4"))
        u.mem_write(0xFD6A, b"\x5a\xa5")
        u.mem_write(0x8204, b"\x5a")
        u.reg_write(legacy.UC_X86_REG_SP, 0xF000)
        return u

    def call(self, u, address):
        u.reg_write(legacy.UC_X86_REG_CS, 0x6000)
        u.emu_start(address, 0xFFFFF, count=500000)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_SP), 0xF000)

    def oam(self, u, entries, start=0):
        for i, (slot, side) in enumerate(entries):
            address = 0xE00 + ((start + i) & 127) * 4
            u.mem_write(address, struct.pack("<HBB", slot | (side << 9), 20, 20))
        from unicorn.x86_const import UC_X86_REG_CX

        u.reg_write(UC_X86_REG_CX, (start << 8) | len(entries))
        self.call(u, 0x61020)

    def test_ownership_change_recolours_identical_source_and_restores_canonical(self):
        u = self.machine()
        source = legacy.A * 128
        u.mem_write(0x500, source)
        u.mem_write(0x3800, source)
        u.mem_write(0x7000, solid(legacy.A, 2) * 128)
        u.mem_write(0xFD72, struct.pack("<HH", 0xE00, 0xE18))
        self.oam(u, [(384, 4), (385, 5)])
        self.assertEqual(bytes(u.mem_read(0x8300, 2)), b"\x81\0")
        self.call(u, 0x61000)
        self.assertEqual(
            bytes(u.mem_read(0x7000, 64)), solid(legacy.A, 0) + solid(legacy.A, 2)
        )
        self.assertEqual(len(self.ports), 1)
        self.oam(u, [(384, 4), (385, 5)])
        self.call(u, 0x61000)
        self.assertEqual(len(self.ports), 1)
        u.mem_write(0xFD72, b"\0" * 4)
        self.oam(u, [(384, 4), (385, 5)])
        self.call(u, 0x61000)
        self.assertEqual(bytes(u.mem_read(0x7000, 64)), solid(legacy.A, 2) * 2)
        self.assertEqual(len(self.ports), 2)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), source)

    def test_both_character_contexts_distinguish_identical_source_on_two_sides(self):
        u = self.machine(
            overrides={
                1: {legacy.A: solid(legacy.A, 0)},
                2: {legacy.A: solid(legacy.A, 1)},
            },
            owners=(1, 2),
        )
        u.mem_write(0x500, legacy.A * 128)
        u.mem_write(0x3800, legacy.A * 128)
        u.mem_write(0xFD72, struct.pack("<HH", 0xE00, 0xE18))
        self.oam(u, [(384, 4), (385, 5)])
        self.assertEqual(bytes(u.mem_read(0x8300, 2)), b"\x81\x82")
        self.call(u, 0x61000)
        self.assertEqual(
            bytes(u.mem_read(0x7000, 64)), solid(legacy.A, 0) + solid(legacy.A, 1)
        )

    def test_second_side_and_wrapped_oam_use_the_new_count(self):
        u = self.machine()
        u.mem_write(0xFD72, struct.pack("<HH", 0xE18, 0xE00))
        self.oam(u, [(384, 4), (385, 5)], start=127)
        self.assertEqual(bytes(u.mem_read(0x8300, 2)), b"\0\x81")

    def test_hash_collision_context_miss_and_unknown_source(self):
        u = self.machine()
        source = (legacy.A + legacy.B + legacy.C) * 42 + legacy.A * 2
        u.mem_write(0x500, source)
        u.mem_write(0x3800, b"\xff" * 2048)
        u.mem_write(0x8300, b"\x81" * 128)
        self.call(u, 0x61000)
        plain = b"".join(legacy.C[i : i + 2] + b"\0\0" for i in range(0, 16, 2))
        expected = (solid(legacy.A, 0) + solid(legacy.B, 3) + plain) * 42 + solid(
            legacy.A, 0
        ) * 2
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), expected)
        self.assertEqual(len(self.ports), 128)

    def test_initial_and_reacquired_ownership_force_only_the_reserved_map(self):
        u = self.machine()
        u.mem_write(0xFD6A, b"\0\0")
        u.mem_write(0x82FF, b"Q" + b"\x37" * 128 + b"R")
        u.mem_write(0x500, legacy.A * 128)
        u.mem_write(0x3800, legacy.A * 128)
        u.reg_write(legacy.UC_X86_REG_DS, 0x1234)
        u.reg_write(legacy.UC_X86_REG_ES, 0x2345)
        self.call(u, 0x61000)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_DS), 0x1234)
        self.assertEqual(u.reg_read(legacy.UC_X86_REG_ES), 0x2345)
        self.assertEqual(bytes(u.mem_read(0x82FF, 1)), b"Q")
        self.assertEqual(bytes(u.mem_read(0x8380, 1)), b"R")
        self.assertEqual(bytes(u.mem_read(0x8300, 128)), bytes(128))
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), solid(legacy.A, 2) * 128)

    def test_all_shards_select_the_character_variant(self):
        from class_table import hash16

        canonical = []
        for n in range(16):
            raw = bytes(14) + struct.pack("<H", (n << 12) | 0x123)
            canonical.append((raw, solid(raw, 2)))
        override = {s: solid(s, 0) for s, _ in canonical}
        u = self.machine(canonical, {1: override})
        source = b"".join(canonical[n % 16][0] for n in range(128))
        u.mem_write(0x500, source)
        u.mem_write(0x3800, b"\xff" * 2048)
        u.mem_write(0x8300, b"\x81" * 128)
        self.call(u, 0x61000)
        self.assertEqual(
            bytes(u.mem_read(0x7000, 4096)),
            b"".join(override[canonical[n % 16][0]] for n in range(128)),
        )
        self.assertEqual(
            self.ports,
            [
                CLASS_SHARD_BANK_BASE + (hash16(canonical[n % 16][0]) >> 12)
                for n in range(128)
            ],
        )

    def test_full_partition_variant_near_the_bank_end(self):
        rows = []
        for n in range(1090):
            raw = bytes(14) + struct.pack("<H", 0xF000 + n)
            rows.append((raw, solid(raw, 2)))
        raw = rows[-1][0]
        u = self.machine(rows, {1: {raw: solid(raw, 0)}})
        u.mem_write(0x500, raw * 128)
        u.mem_write(0x3800, b"\xff" * 2048)
        u.mem_write(0x8300, b"\x81" * 128)
        self.call(u, 0x61000)
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), solid(raw, 0) * 128)
