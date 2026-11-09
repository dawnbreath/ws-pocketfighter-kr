# T17: collision-safe diagnostic class-table contract

The previous table stored only hash16 + mask16. A matching 16-bit hash is not
proof of matching tile bytes: unseen animation tiles can collide with a known
entry even if the entries have no mutual collisions. For example, little-endian
word sequences [0,0,0,0,0,0,0,0], [1,8,0,0,0,0,0,0], and [2,16,0,0,0,0,0,0]
all have rol3/xor hash zero. The previous hook applies the first entry's mask.

## CTB2 (diagnostic only)

One color-bank table at CS:8000; maximum length 8000 hex bytes:

| Offset | Field |
|---|---|
| 0 | ASCII `CTB2` (4 bytes) |
| 4 | little-endian u16 record count |
| 6 | count records, each `<H16s16s>` = hash16, exact source16, mask16 |
| after records | 64 bytes: palette 12 then palette 13, 16 LE RGB444 words each |

Maximum count is 961 (capacity bound, NOT a feasible runtime-performance claim).
The loader checks magic, exact length, capacity, source hashes, duplicate source
bytes and RGB444 range before inserting the file. Legacy tables and direct PGMD
files are rejected; arbitrary file length cannot overwrite the following bank.
Duplicate source entries are rejected even when masks agree: deduplicate offline
and resolve conflicting semantics/context explicitly.

The linear lookup retains its bounded count. After a hash hit it compares all
16 source bytes, preserving staging/output pointers, destination segment and
remaining count. A false hit continues searching. No exact match uses the
existing plain group-zero path. Exact comparison adds cost only to candidate
hits; runtime hash generation is now compiled only for CTAB, avoiding wasted
work in plain HYBRID builds. No unrelated graphics/sound/battle path is changed.
CTAB assembly is 1464 bytes, below the existing 1536-byte code boundary.

## Convert existing diagnostic masks

```sh
python tools/class_table.py work/fighter/masks.pgmd work/palettes.rgb444 work/fighter.ctb2
PF_HYBRID=1 PF_CLASS_TABLE=work/fighter.ctb2 python tools/build.py ...
```

PGMD/1 comes from the exporter merged in #26. Supply exactly 32 RGB444 words
for the two experimental palettes. The converter verifies its input record
checksums and retains source-oriented masks without flipping again. It does
not invent an approved palette or make an unreviewed mask production-ready.
Old hash-only tables cannot be safely upgraded without their source bytes.
Use pack_table([(source16,mask16),...], palette64) when recreating a table from
source tiles; it writes the validated CTB2 layout.

The global table still does not distinguish two semantic uses of identical
bytes in different actor contexts. Fixed palette12/13 selection, linear-search
cost, pose coverage, owner review, dirty-output initialization and rolling
resync ownership remain open. In particular, rsyn can still overwrite class
planes then cphook can skip an equal source; this patch does not claim stable
per-pixel color across all frames. Claude was notified separately about that
existing integration issue. No production gate passes here.

## Verification

Six new tests: malformed/version/count/hash/palette rejection; capacity boundary;
PGMD conversion; actual NASM/Unicorn collision-hit traversal, unseen collision
fallback, empty table. The three assembled cases check source preservation,
DS/ES/SP/far return and palette output. The two collision cases fail against the
old assembled code/legacy tables, and pass after this fix. Existing copier
return-contract tests (2) also pass. Unicorn is not a V30MZ timing measurement.

Real local PGMD from the prior Chun-Li serialization run converted end-to-end:
241 records, 8264 CTB2 bytes (legacy comparison: 4404 bytes). All semantic labels
in that prior run map to group zero; both experimental palettes here use a
neutral repeated gray ramp. This validates format/integration, not final colors
or the owner-approved pose. No game-derived table/graphics are committed.

Build SHA-256:

- Default: `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279` (v007 unchanged).
- CTB2: `f0b3ca2e7a4a1d2d9b638814701631dee2ecfa3403569a96d9d2a272349a2995`.
- Old source + equivalent legacy records/palettes: `f65da1c4a42bb21d7b4e419062c263778394b712c5aa89ba8af66e1310341253`.

Both diagnostic builds use --img and story/fixed/wg Korean JSON with the pinned
existing v007 assets. No source ROM or save modification. Full table evidence
and captures remain under ignored work/.

Runtime comparison used regress.py default SEQ in two fresh runtimes. All
captures completed and both exact launch IDs stopped. Title, menus and the
three story checkpoints were pixel-identical (5/6). Both final screenshots
show an actual RYU vs IBUKI fight on the bar stage, but one says ROUND1 and the
other NO MERCY; 3162 differing pixels include that animation/pose phase. Do not
claim the fight screenshot passed pixel regression or attribute every difference
to the table. No calibrated timing claim is made. Remaining prototype text and
color-persistence issues are not covered by this narrow lookup/loader correction.
