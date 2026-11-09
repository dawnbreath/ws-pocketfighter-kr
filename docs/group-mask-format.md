# T15 diagnostic mask exchange, PGMD version 1

`python tools/export_group_masks.py CAPTURE MASKS MAPPING work/OUTPUT`

This connects capture + source-oriented masks to a binary table and reads every
serialized record back through the reference lookup. Outputs contain source tile
bytes and must stay in ignored work/. No ROM changes or assembly wiring.

MAPPING is explicit JSON, for example the synthetic diagnostic mapping
`{"character":"test","groups":{"skin":0,"cloth":1,"hair":2,"accent":3}}`.
These numbers are *palette groups*, not semantic labels or approved colors.
Each opaque pixel becomes original shade + 4*group. Original zero stays zero;
this format cannot make a dark source-zero BG pixel opaque, remap shade ramps,
or provide arbitrary per-pixel palette indices. It is for sprite diagnostics.
Unknown, conflicting, unobserved or unmapped opaque pixels exclude the whole
tile. A missing tile must use an engine-defined fallback, never another record.
Transparent unknown pixels need no color group. No implicit truncation or
majority vote. Inputs bind character, ROM and capture SHA-256.

Header: little endian `<4sHHI`: magic `PGMD`, version 1, record size 37, count.
Records sorted by (unsigned CRC32, exact 16-byte source):

| Field | Bytes | Meaning |
|---|---:|---|
| CRC32 | 4 | Standard zlib/IEEE CRC32 of 16 source bytes, LE |
| source | 16 | Exact 2bpp source, unflipped, for collision verification |
| uniform | 1 | 0..3 if all opaque pixels use that group; FF mixed/empty |
| mask | 16 | Eight interleaved rows of bitplane 2, bitplane 3; MSB left |

Uniform records retain the mask to keep fixed stride; optimization is deferred
until the engine contract is accepted. A CRC hit is insufficient: lower-bound
binary search, scan equal-CRC run and compare all source bytes. Runtime CRC cost
still needs measuring; this is not an assertion that hashing happens offline.
Character is selected by the external table descriptor; pair the binary with its
report (character and input/output hashes). Do not share tables across actors.

The `PGMD` magic explicitly denotes DIAGNOSTIC data. Every report sets
engine_ready=false regardless of geometric completeness. These labels have not
been approved for production. Palette review, runtime fallback, initialization,
context invalidation and calibrated timing are still engine integration gates.

## Validation

Five synthetic tests cover all four groups and zero transparency, mixed/uniform
encoding, unknown rejection, forced CRC collision lookup, truncated table,
provenance rejection and conflict omission. Existing inverse-flip projection is
reused; masks are not flipped again by this exporter.

Local original-ROM captures were exported end-to-end with every known semantic
label mapped explicitly to group zero **for serialization validation only**:
Chun-Li 241 included / 399 omitted; Zangief 191 / 461. Every included record was
read back and matched its encoded input. This neutral mapping adds no colors,
is not a palette proposal, and does not imply those masks are visually correct.
No captures, binary masks, mapping files or tile graphics are in this PR.
