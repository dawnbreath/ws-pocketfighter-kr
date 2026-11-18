# T49 Zangief crouch and air colours

The batch adds 12 exact source drawings: five crouch/low-attack drawings, one
rising-jump drawing and six air-attack drawings. Actual Saturn training captures
provide the material reference: red wristbands, boots and trunks, with exposed
hands and legs kept skin. Masks bind to exact source hashes and do not transfer
to unobserved drawings. Eight shared pixels retain their previous output,
including five sparse toe pixels (three dark red and two light inherited pixels).
Owner art review remains pending.

The expanded ROM differs from T48 only in its colour table and checksum. All
1,116 previous effective outputs and both palettes are unchanged. Of 333 newly
encountered source tiles, 162 need stored colour outputs; 171 exactly equal the
existing copier fallback. The table now stores 1,013 records and has 6,112 bytes
free (122 records).

`walk_table.py --compact-fallback` removes exact fallback outputs before checking
bank capacity and writes `fallback.ctb3` as an authoring reference. It combines
all omitted tiles with earlier protected fallback tiles: 436 records here. Pass
that reference through `--preserve-fallback-from` in subsequent work. It is not a
second runtime table. The exporter preserves its palette indices and rejects any
attempt to recolour a protected source. Existing exporter invocations keep their
previous behavior unless compaction is requested.

## Reproduction

ROMs, source captures, screens, states and tables stay in the private restart
backup. Use the final ROM and its own states; preliminary candidates are not the
final build. The backup includes the cold-boot route and native verification
scripts under `work/`.

```sh
python tools/mock/walk_table.py work/T49-low-air-offset/capture.json \
  work/T48-table/full.ctb3 work/T49-final-table --motion zangief-low-air \
  --additional-capture work/T49-low-air-source/capture.json \
  --preserve-fallback-from work/T47-basic-table/full.ctb3 --compact-fallback
PF_HYBRID=1 PF_CLASS_TABLE=work/T49-final-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T49-final.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python work/T49_static.py
python work/T49_native_qa.py low-air T49-low-air-runtime \
  T49-low-air-runtime-offset T49-jump-b-followup
PATH=/path/to/nasm:$PATH PYTHONPATH=tools:tests:work/test-deps \
  python -m unittest test_full_colour_table test_palette_compatibility test_compact_colour_table
```

## Completion evidence and limits

- Capture, classification and capacity preparation: two original source cohorts,
  exact shared-tile constraints and all 12 required drawings exported together.
- Colour insertion: 1,013 records, 436 protected fallback records, unchanged
  runtime code, exact ROM readback/checksum and original-to-candidate IPS round trip.
- Native output: all 12 drawings, 15,035 representative visible and RAM pixels in
  40 samples with zero registration offset. Twenty-one incoherent or displaced
  samples are excluded. Two other samples are outside this recipe family.
- Retained output: all 14 earlier Zangief drawings and 16,950 representative
  pixels pass from fresh candidate-ROM boots/states. Five initial fullscreens
  and four following intro screens match T48 exactly. One intro screen has a
  two-pixel difference; all 16 P1 sprite entries, colour buffers and palette
  match. That screen is excluded from identical-screen counts.
- Opponent check: all 94 sampled Ken RAM outputs equal the previous table;
  46 also match their screenshots. Forty-eight screenshot samples are excluded
  for source/display timing disagreement. Thirteen cross-build dynamic pairs
  differ outside P1 (Ken animation phase, and background scroll in one air pair);
  none is counted as an identical-screen pass. Observed Ken source tiles retain
  their previous output. This does not prove cycle timing unchanged.
- Re-export: source captures and fresh native captures each reproduce both final
  tables byte for byte. Nine focused runtime/palette/compactor tests pass.
- Restart handoff: private backup contains the original, final IPS/ROM, both
  final tables, fonts, scripts, Saturn reference captures, states and receipts.

Falling/landing frames that lacked a coherent source, other strengths/combos,
opposite-facing forms, remaining fighters and real hardware timing are not
completed. The earlier font-VRAM and translation limits still apply.

Final ROM SHA-256: `d145e091bcadd283d5b3341c4730b99c2803f9e67780768fd3d0a2b92f9151a6`.
Final table SHA-256: `04ec1af09f08fded2c25fe8b623421c8e05ae72f25684daf60f71423822eccdb`.
