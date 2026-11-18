"""Check that CTB3 compaction retains output changes within a hash collision."""

import unittest

from class_table import FULL_RECORD, HEADER, hash16, pack_full_table
from compact_colour_table import compact, fallback_output


class CompactColourTableTests(unittest.TestCase):
    def test_keeps_transparency_preserving_edit_in_collision_run(self) -> None:
        identity = bytes(16)
        changed = b"\x01\x00\x08\x00" + bytes(12)
        self.assertEqual(hash16(identity), hash16(changed))
        explicit = bytearray(fallback_output(changed))
        # A change to a low plane can also preserve opacity and must stay.
        explicit[0] = 0
        explicit[1] = 1
        footer = b"\x11\x01" * 32
        original = pack_full_table(
            [(identity, fallback_output(identity)), (changed, bytes(explicit))],
            footer,
        )
        optimized = compact(original)
        self.assertEqual(HEADER.unpack_from(optimized), (b"CTB3", 1))
        self.assertEqual(
            FULL_RECORD.unpack_from(optimized, HEADER.size),
            (hash16(changed), changed, bytes(explicit)),
        )
        self.assertEqual(optimized[-64:], footer)
        self.assertEqual(compact(optimized), optimized)
