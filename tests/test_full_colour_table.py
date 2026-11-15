"""Exercise emitted CTB3 lookup/copy, including collisions and transparent pixels."""

import test_class_table as legacy
from colour_layout import CLASS_TABLE_BASE
from class_table import pack_full_table, validate_table


def solid(raw, plane):
    out = bytearray(32)
    for y in range(8):
        out[4 * y + plane] = raw[2 * y] | raw[2 * y + 1]
    return bytes(out)


class FullRuntimeTests(legacy.RuntimeTests):
    @classmethod
    def setUpClass(cls):
        import asm

        cls.code, _ = asm.assemble(
            "col", {"HYBRID": "1", "BPP4": "1", "CTAB": "1", "FULLTILE": "1"}
        )

    def run_table(self, source, records):
        old = legacy.pack_table
        try:
            legacy.pack_table = pack_full_table
            return super().run_table(source, records)
        finally:
            legacy.pack_table = old

    def test_collision_hit_checks_exact_source(self):
        output = solid(legacy.B, 2)
        self.assertEqual(
            self.run_table(
                legacy.B, [(legacy.A, solid(legacy.A, 3)), (legacy.B, output)]
            ),
            output * 128,
        )

    def test_unseen_hash_collision_falls_back(self):
        result = self.run_table(
            legacy.C, [(legacy.A, solid(legacy.A, 3)), (legacy.B, solid(legacy.B, 2))]
        )
        expected = b"".join(legacy.C[i : i + 2] + b"\0\0" for i in range(0, 16, 2))
        self.assertEqual(result, expected * 128)

    def test_full_capacity_crosses_signed_offset_boundary(self) -> None:
        from class_table import MAX_SIZE, HEADER, FULL_RECORD, hash16

        capacity = (MAX_SIZE - HEADER.size - 64) // FULL_RECORD.size
        records = [
            (n.to_bytes(16, "little"), solid(n.to_bytes(16, "little"), 2))
            for n in range(capacity)
        ]
        source, output = max(records, key=lambda row: (hash16(row[0]), row[0]))
        self.assertGreater((capacity - 1) * FULL_RECORD.size, 0x7FFF)
        self.assertEqual(self.run_table(source, records), output * 128)
        with self.assertRaises(ValueError):
            pack_full_table(
                records
                + [
                    (
                        capacity.to_bytes(16, "little"),
                        solid(capacity.to_bytes(16, "little"), 2),
                    )
                ],
                legacy.PAL,
            )

    def test_transparency_cannot_be_changed(self):
        with self.assertRaises(ValueError):
            pack_full_table([(legacy.B, bytes(32))], legacy.PAL)

    def test_distinct_staging_tiles_advance_source(self):
        u = legacy.Uc(legacy.UC_ARCH_X86, legacy.UC_MODE_16)
        u.mem_map(0, 0x100000)
        u.mem_write(0x20000, self.code)
        oa, ob = solid(legacy.A, 3), solid(legacy.B, 2)
        u.mem_write(
            0x20000 + CLASS_TABLE_BASE,
            pack_full_table([(legacy.A, oa), (legacy.B, ob)], legacy.PAL),
        )
        u.mem_write(0x61000, bytes.fromhex("9a00050020f4"))
        source = (legacy.A + legacy.B) * 64
        u.mem_write(0x500, source)
        u.mem_write(0x3800, bytes([255] * 2048))
        u.reg_write(legacy.UC_X86_REG_CS, 0x6000)
        u.reg_write(legacy.UC_X86_REG_SP, 0xF000)
        u.emu_start(0x61000, 0xFFFFF, count=100000)
        self.assertEqual(bytes(u.mem_read(0x7000, 4096)), (oa + ob) * 64)
        self.assertEqual(bytes(u.mem_read(0x500, 2048)), source)
