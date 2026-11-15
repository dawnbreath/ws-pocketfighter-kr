# T38: Chun-Li knockdown, rolling and recovery colours

Completion items are: (1) identify and author the complete new drawings against
original WS pixels and the Saturn material reference, (2) integrate and verify
actual game output, (3) preserve old output and a restart/package backup. This
is a review candidate; same-instant Saturn roll comparisons and owner art
approval remain open.

## Scope and source decisions

Four passive probes reload the existing guard/hit states, settle for0/180/300/
600 frames and sample16 times each. Reconstructing P1 separately distinguishes
opponent occlusion from a new drawing. Full unoccluded, coherent samples supply
five new drawings; occluded/mixed samples remain recorded in the local inventory
and are neither exported as complete drawings nor labelled unused. Four other
crop hashes in the180-frame probe consist entirely of existing coloured raw
tiles; their637-record baseline mappings remain unchanged.

| Drawing | Source crop MD5 | Size (w x h) | Opaque pixels | New raw tiles |
|---|---|---:|---:|---:|
| Prone |6f73c2e917875cb479b12764005555d9|43x22|499|13|
| Roll A |4221c2788e85fc1618ab339e08a3ee6a|39x28|608|15|
| Roll B |b1f44f9bcd965ea2e3d7a030ee64e151|33x31|550|14|
| Sitting |fbb30ac0a00e3ce166716d3c68dda0ab|37x31|556|15|
| Rising |731dc3ec66b6db1b21817598cd0aea9c|26x32|539|13|

The hashes include source bytes followed by shape bytes, as in seed_recipe.py.
These are captured left-facing source crops; no mirror/nearest-label transfer is
used. tools/mock/damage_colours.py contains only geometry and hashes, requiring
the exact source drawing. Material choices reuse the established skin hands,
black cuffs/white studs, blue tunic, brown hair/trousers and white boots/buns.
Original transparency is exact. Five edge pixels recur in previously coloured
raw tiles; their existing outputs are retained explicitly rather than overwriting
an old record or adding a runtime exception. All tile-cell votes must agree and
all required drawings must be observed before export.

The supplied Saturn disc runs locally in Mednafen with P1 Ken/P2 Chun-Li as a
training dummy. C8 followed by4/8/12/16/24/40 passive frames gives the knockdown;
12-frame passive steps give sitting/rising reference screenshots. These are
actual reference captures, not extracted assets or visual approval. The two WS
roll intermediates do not yet have exact same-instant Saturn pairs. Existing
T36 exact standing-guard comparison, unobserved contact/KO/combo drawings and
other fighters remain open; this task does not label the whole damage animation
or all gameplay complete.

## Integration and reproduction

The existing exporter gains a damage family bound to the actual600-frame
no-input protocol. The existing screenshot checker gains a direct-source damage
family; earlier mirrored families keep their normalization. No ROM code, palette,
font, VRAM allocation, sound or unrelated text path changes.

```
python tools/mock/walk_table.py work/damage-late/capture.json \
  work/defence-preview-table/full.ctb3 work/damage-table --motion damage
PF_HYBRID=1 PF_CLASS_TABLE=work/damage-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/damage.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/capture_walk.py work/damage.ws work/damage-states/guard.mcs \
  work/damage-table/full.ctb3 data/palettes/wrist-fixes.json work/damage-runtime \
  --motion idle --settle-frames 600 --frames 2 10 18 26 34 42 50 58 66 74 82 90 98 106 114 120 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
```

NASM must be on PATH. Work inputs, captured source pixels and states are local
or in the owner's Drive backups, never Git. Cold-boot scripts create this ROM's
own base/guard states instead of loading a different ROM's snapshot.

```
python tools/verify_reverse_actions.py work/reverse-standing work/reverse-walk \
  work/damage-checked --damage work/damage-runtime work/damage-runtime-fine
python tools/mock/walk_table.py work/damage-runtime/capture.json \
  work/defence-preview-table/full.ctb3 work/damage-runtime-reproduced \
  --motion damage --additional-capture work/damage-runtime-fine/capture.json
```

The fine capture uses the same state/protocol with durations28/30/32/36/38/40.

## Results for the completion items

1. The five recipes add70 records:637 old records plus707 total,35420 table
   bytes and21412 free bytes at bank offset2200. Existing record outputs and
   the64-byte palette footer remain identical. Source transparency/range and
   wrong-input-protocol rejection pass without output mutation.
2. All5 drawings/2752 representative opaque pixels match in12 actual samples,
   each at zero registration offset. Of22 captured samples,19 pass the generic
   render check; the other3 remain recorded as excluded transitions/occlusions.
   Additional timing36/38 isolates the previously obscured roll A. Runtime
   re-export reproduces the exact707-record table. Runtime results are recorded in work/damage-checked/report.json. Historical
   standing/walk inputs used by that shared command remain separately attributed;
   only the damage family represents new-ROM gameplay evidence. ROM readback at
   D2200, checksum and whole-ROM difference bounds pass: all31269 changed bytes
   lie within the new table span or the two checksum bytes. Selection screenshots
   match the previous build pixel for pixel.
3. The original/previous ROMs and states are preserved. New own-ROM restart states,
   accepted sample states, capture reports and stop receipts accompany the ROM,
   IPS and source/verification tools in the restart backup. IPS round-trip from
   the original reconstructs the ROM exactly. ZIP integrity and approved Drive
   upload metadata are checked. No game assets are committed.

ROM SHA256:58756b2618db3f81acfa3dd7cb207affd13fd7ef01c8041a249f9ea2bd1df72c.
CTB3 SHA256:8fd0bdb4f79c3992c12089fa9ce8f85ae187d9382d22cf7923746d2fe74e8af0.
Original SHA256:b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e.

Affected Python files pass Black, py_compile and diff checks. Unchanged assembly
suites are not repeated. This does not establish general VRAM font residency or
whole-population performance; earlier coverage/translation limitations persist.
Sol/Medium remains sufficient; no model escalation is needed.
