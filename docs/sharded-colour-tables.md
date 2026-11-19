# T50: hash-partitioned colour tables

T49 left 122 stored-tile slots. The optional sharded build distributes exact-source
CTB3 records across sixteen expanded-ROM banks, keeping the existing global tile
identity. It avoids assigning P1/P2 by slot number: native captures show that both
sides use some of the same slot numbers at different times. No new actor-ownership
inference, VRAM reservation or text-path processing is needed for this partition.

## Runtime and storage contract

The high four bits of the existing hash select one of banks 10..1F (C2 values
D0..DF). Each image repeats the same colour code, scene data and fighter catalogue
at the same offsets; only its CTB3 data at 2200 differs. A changed tile computes
the same hash as before, selects its bank, and runs the existing sorted search and
exact 16-byte source comparison. Collision records remain in one partition. A
miss retains the existing fallback. An unchanged tile adds no bank selection.
The copier trampoline already saves/restores C2 around the hook and is unchanged.

The added selection is nine instruction bytes and one OUT per changed tile. It
has no extra far call or bank restore per tile. The final return uses the existing
trampoline's bank restore. IRQ palette hooks already save/restore C2; their code
and the palette catalogue are identical in each image. The T45 atomic original
copier is unchanged. Cycle timing and physical hardware remain unmeasured.

Each partition holds at most 1,135 CTB3 records. Aggregate capacity is 18,160, with
17,147 currently free; a concentrated hash distribution can fill one partition
before the aggregate limit. The writer rejects that case. All banks are checked
empty before installation. The original game region, fonts, story bank, VRAM and
palette values remain unchanged.

## Authoring and build

`tools/sharded_colour_table.py` converts a single CTB3 to a directory containing
00.ctb3..0f.ctb3 plus a digest manifest. The reader validates each table, sorting,
hash partition, identical footers and file digests. Source/output ambiguity is
still rejected by the existing CTB3 validator; partitioning does not author new
material labels or solve conflicting semantic masks.

`capture_walk.py` accepts either a table file or a partition directory.
`mock/walk_table.py` likewise accepts either baseline. A directory baseline emits
a directory of partitions; with `--compact-fallback`, its cumulative protection
reference is the `fallback/` subdirectory. Subsequent exports pass that directory
through `--preserve-fallback-from`. Existing single-table invocation behavior is
preserved, including the single-file fallback reference.

```sh
python tools/sharded_colour_table.py work/T49-final-table/full.ctb3 work/T50-shards
PF_HYBRID=1 PF_CLASS_SHARDS=work/T50-shards \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T50.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/mock/walk_table.py work/T50-low-air-runtime/capture.json \
  work/T50-shards work/T50-native-reexport --motion zangief-low-air \
  --preserve-fallback-from work/T49-final-table/fallback.ctb3 --compact-fallback
```

`PF_CLASS_SHARDS` requires HYBRID and fighter palettes, and excludes
`PF_CLASS_TABLE`. With no shard option, rebuilding the T49 configuration is
byte-identical to T49. No mask bytes are embedded in public source.

## Validation and limits

Static readback preserves all 1,013 explicit outputs and 436 protected fallback
outputs. All sixteen code/catalogue prefixes are identical. Only colour bank0D,
replicated banks10..1F and the ROM checksum differ. IPS round trip succeeds.

Tests execute emitted instructions with bank-window changes: all sixteen banks,
exact-source collisions, missing source, distinct staging tiles, zero bank writes
for unchanged tiles, partition capacity/signed-offset boundary, 4,000 distributed
records, and the unchanged copier trampoline's restoration of the caller's bank.
The original CTB2/CTB3 and palette tests remain applicable.

Fresh candidate-ROM boots/states verify all 26 existing Zangief drawings through
actual buffers and zero-offset screenshots: 31,985 representative pixels. Native
re-export reproduces all sixteen partitions and the cumulative fallback reference.
Five initial fullscreens match T49 exactly. The Chun-Li intro capture differs by
162 pixels; all sixteen P1 OAM entries, buffers and palette agree. The next capture
differs by 228 pixels, followed by three exact screens. Both differing captures
are exclusions from identical-screen counts. This is not cycle-equivalence proof.

This completes the scalable storage/search connection, not the remaining fighter
art. The new batch capture uses an own-ROM selection state and identifies fighters
from their actual HUD hashes; routes and assets stay private. Remaining art,
all-mode/real-hardware timing, and earlier translation/font-VRAM limits stay open.
