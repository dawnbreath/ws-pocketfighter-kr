# T21: restore the selected middle version and limit corrections

Owner steering supersedes T20: retain the middle column of `work/fresh-comparison.png`
(the #41 contrast-restoration build), change only Zangief's wristbands and the area
below Chun-Li's hand on the displayed image right. The broad T20 redraw is rejected.
No skin, face, beard, hairstyle, other clothing or global contrast redesign is applied.

`tools/mock/wrist_fixes.py` contains source-pose-bound polygons for these regions.
Chun-Li's cuff uses existing white/brown colours, and the lower patch uses the existing
brown trousers ramp. Zangief's wristbands use his existing red; previously unused
palette group 3 supplies their gold trim. All previously used palette entries remain
identical to #41. The separate `wrist-fixes.json` preserves prior palette files.

The existing seed exporter accepts `--wrist-fixes`. Its optional offline adjustment
runs after baseline group mapping and before the unchanged source-oriented projection.
It cannot combine with idle proposals: coordinates belong to the two exact basic
poses. Historical source labels are explicitly written as `baseline-labels.json`;
the NPZ contains final adjusted groups, avoiding misidentification of baseline labels
as the corrected output. No runtime code or VRAM layout changes.

```
python tools/mock/seed_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  data/palettes/wrist-fixes.json work/wrist-table --wrist-fixes
PF_HYBRID=1 PF_CLASS_TABLE=work/wrist-table/seed.ctb2 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/wrist-fixes.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

## Scope evidence and verification

The regenerated baseline was compared to the actual #41 game screenshots before
editing. Every opaque baseline pixel matched. Export without the new option remains
byte-identical to the old `work/saturn-contrast-table/seed.ctb2`.

The adjusted preview changes exactly 58 of Chun-Li's 677 pixels, confined to the cuff
and trousers directly below the displayed right hand. It changes 26 of Zangief's 1269
pixels, confined to the wristbands. Zero changes occur outside the selected polygons.
Source shades and transparency remain unchanged. This is a bounded visual proposal,
not evidence of owner approval. Comparison with changed-pixel highlights:
`work/wrist-fixes-preview.png`; scope audit: `work/wrist-fixes-scope.json`.

Exporter: 46 exact-source records; no omitted tiles; three existing exporter tests pass.
Default Korean ROM is still
`1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`;
original remains `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
Trial ROM: `5c350f3581f5acdf59616eaf3181230aad61194b1562ba91809a391921d1977d`.

Local outputs: `work/wrist-fixes-table/`, `work/wrist-fixes.ws`,
`work/wrist-runtime-chunli/`, `work/wrist-runtime-zangief/` (screenshots, savestates,
frame dumps and launch/stop reports). Earlier ROMs, saves and captures are retained.
No game-derived data is committed. No additional poses were authored. Shared source tiles may also occur in other
animations, which are not certified as correctly coloured.

Actual-game checks: all 18 Chun-Li and 28 Zangief active tile mirrors match the table.
All 1946 opaque fighter pixels match the adjusted previews. Comparing the entire
224x144 actual screenshots against #41 gives exactly 58 / 26 changed pixels and
zero changes outside the selected regions, including backgrounds and the opponent.
Report: `work/wrist-runtime-scope.json`.

Six unaffected regression screens (title, menus, story1/2/3, Ryu/Ibuki fight) are
pixel-identical to #41. Regenerating after final output-label provenance changes
produced a byte-identical table in `work/wrist-fixes-final/`.
