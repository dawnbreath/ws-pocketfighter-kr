# T23 current update: separate hand and outer cuff

The new candidate preserves the central hand (crop x<=22) and colours only the
outer cuff at x=23..24, y=22..28. Two existing bright protrusions use white;
the band uses the existing dark brown ramp. Relative to #44 this changes exactly
10 Chun-Li pixels and zero Zangief pixels. His red-only wristbands and the lower
trousers correction are retained. This is a narrow visual candidate, not approval.

Local outputs: `work/cuff-table/`, `work/cuff.ws`, `work/cuff-preview.png`,
`work/cuff-runtime-{chunli,zangief}/`. Use the same build command below with
these table/output paths. No palette or engine edits.

Actual-game validation: 18/18 and 28/28 active tile mirrors match. All 1946
opaque fighter pixels match the preview. Whole screenshots against #44 differ
by exactly 10 Chun-Li pixels and zero Zangief pixels (including background/opponent).
The unchanged Zangief screen is the targeted unaffected-screen regression.
Trial SHA256: `fb79428cd31904763b4bef13a5243a6be8f2293b08538183bb6f2eee163f25a7`.
Comparison: `work/cuff-latest-comparison.png`.

## Earlier T21/T22 history

# T21/T22: local fixes on the selected middle version

Current owner direction (T22): the upper Chun-Li patch is hand anatomy, not a cuff
that should be recoloured; restore it. Zangief's wristbands must be red, with no gold.
The basis remains the middle column of `work/fresh-comparison.png` (#41). The broad
T20 redraw is rejected and is not used by this build.

## Current correction

`tools/mock/wrist_fixes.py` changes only the lower brown trousers patch below the
hand on the displayed image right and Zangief's two red wristband regions. Original
monochrome pixel inspection and actual Saturn hand/forearm reference exposed the
mistake in T21: its upper polygon included light hand pixels and the hand/wrist
junction. That polygon and its highlight rule have been removed, not narrowed by
another guessed cuff boundary. All 25 pixels changed there by T21 are restored
exactly to #41. The remaining lower polygon is unchanged.

Zangief's gold strokes are removed. Both wristband polygons use existing red group 1
only. The palette file is now byte-identical to #41's `ctab-fighters.json`; no palette
entry has a new colour. This restores nine former gold pixels to the red ramp.
The now-unused line-selection option was removed as well.

`seed_table.py --wrist-fixes` applies this offline adjustment before the existing
source-oriented projection. It rejects combination with idle proposals: coordinates
belong to the two exact source poses. Baseline labels and adjusted NPZ groups are
explicitly distinguished. No assembly, VRAM layout or text path changes.

```
python tools/mock/seed_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  data/palettes/wrist-fixes.json work/hand-red-table --wrist-fixes
PF_HYBRID=1 PF_CLASS_TABLE=work/hand-red-table/seed.ctb2 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/hand-red.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

## Current scope evidence

Regenerated baseline colours match the actual #41 screenshots on every opaque
fighter pixel. The current preview changes 33 Chun-Li pixels, all inside the lower
trousers patch (crop x=17..23, y=29..34); the entire upper hand region matches #41.
Zangief changes 21 pixels, confined to the wristbands. Zero pixels outside the
selected polygons change. Compared with T21, only the 25 hand pixels and nine gold
wristband pixels differ. Source shade planes and transparency remain unchanged.

Local comparison: `work/hand-red-preview.png`; source-bound arrays and 46-record CTB2:
`work/hand-red-table/`; scope reports: `work/hand-red-scope.json`,
`work/hand-red-vs-T21.json`. Original ROM SHA256 is unchanged:
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
Trial ROM SHA256:
`08b93b01e4ba3590525e17facaa901dadc28db4e0e835327d7d9575983c5e89e`.

Prior T21 reports (58/26 changed pixels and six unaffected screen comparisons)
remain historical evidence for that rejected upper patch/gold version, not the
current counts. T22 uses targeted in-game checks for both affected fighters and the
title/menu route, rather than repeating unrelated assembly or translation tests.
Runtime screenshots, frame dumps, savestates and stop receipts are retained under
`work/hand-red-runtime-{chunli,zangief}/`; prior saves/builds remain preserved.
No game-derived data is committed. Other poses can reuse source tiles and remain
unverified; this is not full-animation or full-game approval.

Actual-game checks: 18/18 Chun-Li and 28/28 Zangief tile mirrors match. All 1946
opaque pixels match the intended preview. Whole game screenshots against #41
change exactly 33/21 pixels with zero differences outside the target polygons.
Every pixel above Chun-Li crop row 29, including the restored hand, matches #41.
Evidence: `work/hand-red-runtime-scope.json`.

Targeted cold-boot title/menu captures are pixel-identical to #41 using its same
input prefix. Report: `work/hand-red-menu-comparison.json`.
