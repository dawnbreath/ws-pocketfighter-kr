# T48 colour table compaction

T47 had room for 19 more records. T48 removes 265 records whose complete 32-byte output already equals the existing copier fallback. That fallback copies both source planes and fills both added planes with zeros. The comparison uses all output bytes, so a record that changes low-plane shades or adds an opaque palette index is retained.

The ROM table contains 851 records and has 14,212 bytes free for 284 additional records. All 1,116 original keys still produce their exact previous output, including the 265 routes through the fallback. The CTB3 format, record order, palette footer and runtime code are preserved. ROM readback and the IPS round trip from the original ROM succeeded.

When extending the compacted baseline, pass the T47 table through `--preserve-fallback-from` in `tools/mock/walk_table.py`. The exporter rejects changes to any previously removed fallback output and checks its palette indices when a palette update is requested. Keep the full pre-compaction tables as authoring references. The flag is repeatable for additional references from later compactions.

```sh
python tools/compact_colour_table.py work/T47-basic-table/full.ctb3 work/T48-table/full.ctb3
PF_HYBRID=1 PF_CLASS_TABLE=work/T48-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T48-zangief.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json

python tools/mock/walk_table.py work/T48-attack-runtime/capture.json \
  work/T48-table/full.ctb3 work/T48-protected-reexport --motion zangief-basic \
  --additional-capture work/T48-walk-runtime/capture.json \
  --preserve-fallback-from work/T47-basic-table/full.ctb3
cmp work/T48-table/full.ctb3 work/T48-protected-reexport/full.ctb3
```

Fresh Mednafen boots and ready states for the candidate prove exact RAM and screenshot pixels for all 14 previously checked Zangief drawings, covering 16,950 representative visible pixels. Samples with inconsistent screen and RAM timing are excluded. Nine Chun-Li and Zangief fullscreens match T47. One Chun-Li intro capture differs by seven pixels near the shoulder. Both captures have identical Chun-Li OAM, all 16 colour tile buffers and the same palette. The next four intro screens are exact. The difference is recorded as an exclusion from identical-screen counts. Cycle timing and physical hardware remain unmeasured.

The protected runtime re-export reproduces the compact table byte for byte. A negative control with a modified previously omitted tile fails before generating output. Nine focused compactor, CTB3 runtime and palette tests pass. The private backup contains the original and candidate ROMs, IPS, both tables, new own-ROM states and verification data. Use states with their matching ROMs.

Candidate ROM SHA-256 `6d36576e8ed4c72cee5e192e0e8f912327546326b5c35b29c0ba6c653c1a7f0c`.
CTB3 SHA-256 `f02c31ed35dd265807ae01fe555303cdd1e0f75c4a30b5a06ceb83ee8b69a767`.
