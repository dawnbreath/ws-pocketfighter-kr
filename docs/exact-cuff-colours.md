# T26 current correction: cuff directly below the skin-coloured hand

Owner clarified the target is below the skin-coloured hand on the image right.
Recompare with the actual Saturn Training reference: the band underneath the fist
is black with white studs, rather than skin/trousers. Change only crop row28 x18..22,
row29 x18..23, row30 x19..23 to opaque black, with existing opaque studs (20,28) and
(22,30) white. Preserve every pixel above row28 (including the hand), every pixel
below row30 (trousers), existing upper/outer cuffs, and all Zangief indices.

Exactly 16 Chun-Li pixels change from T25. Palette/engine unchanged. Regenerate
with `full_colour_table.py` using `work/lower-cuff-table`, then build
`work/lower-cuff.ws` with the same flags below. Local comparison with actual Saturn:
`work/lower-cuff-comparison.png`. Runtime screenshots, save and source frame:
`work/lower-cuff-runtime-chunli/`. Only the selected basic pose is reviewed here;
no all-pose or owner visual approval is implied.

Current game check: 18/18 active tiles and all 677 opaque pixels match. Whole
screenshot against T25 changes exactly 16 pixels; title is pixel-identical.
Report: `work/lower-cuff-runtime-verification.json`. ROM SHA256:
`ab1d607945707ae9a8b78fc9eae3a7320cc627501730e949a07a8a90926398c7`.

## Earlier T25/T24 history

# T25 current correction: include the inner cuff

Actual Saturn Training reference (`work/saturn-chunli-detail.png`, derived from
`reference/saturn-run/fighters.png`) shows the black cuff and white stud on the left
of the lower hand as well as its outer edge. T24's rectangular skin assignment
incorrectly included this inner/upper band. The current source-bound correction
sets crop row 22 x16..22, row23 x16..19, row24 x17..18 to black where opaque,
with the existing bright pixel at (18,24) white. Lower/right knuckle pixels
remain skin. Existing outer cuff and spikes remain unchanged.

Exactly 13 Chun-Li indices differ from T24, all within that region. The lower/right
hand indices and every Zangief index are unchanged. Palette and runtime engine
are unchanged. Candidate preview: `work/inner-cuff-comparison.png`, with actual
Saturn reference, previous result and current interpretation side by side. No
all-pose or owner visual approval is implied.

Regenerate with the command below using `work/inner-cuff-table` and `work/inner-cuff.ws`.
ROM SHA256: `ae5af23fe35aeb904a15050a1b5d3a1f6ab824ec5c99f8402b498fef19299224`.
Runtime evidence/save: `work/inner-cuff-runtime-chunli/`.

Current real-game verification: all 18 active tile mirrors and 677 opaque pixels
match the new table. Whole screenshot versus T24 differs by exactly 13 pixels;
title is pixel-identical. Report: `work/inner-cuff-runtime-verification.json`.

## T24 implementation and historical verification

# T24: opaque black cuff, white spikes, skin-coloured hand

The owner specifies Chun-Li's bracelet as black with white spikes and the hand as
skin. CTB2 retains the original two low shade bits; all twelve nonzero-shade colour
slots are used by the selected pose. Changing a shared ramp would change other body
parts. CTB3 permits exact 4bpp indices for matched tiles, including existing opaque
black index 4, without changing any palette entry or unrelated pixel.

## Format and runtime

CTB3 header is `<4sH>`, followed by sorted `{hash16, exact source16, output32}` records
(50 bytes) and the existing 64-byte palette footer. The bank limit remains 0x8000.
Validation checks lengths, source hashes, duplicate sources, RGB444 colours and exact
transparent/opaque pixel preservation. The builder validates the table once and selects
FULLTILE at assembly time. CTB2 remains the original 34-byte format and instruction path.

The existing copier hook still binary-searches hashes and verifies exact source bytes.
For CTB3, a matched record copies 16 precomputed words; the staging-source pointer
advances by 16 bytes. Unknown tiles use the existing plain expansion. Record stride
also determines collision scanning and footer location. No extra RAM, VRAM allocation,
per-pixel runtime check or bank switch is added. Performance is not cycle-calibrated.

An initial trial failed real-game mirror checks because the new copy path did not
advance the staging pointer. That trial (`work/black-cuff.ws`) is rejected. The fixed
path includes the advance and a new alternating-source assembly test; repeated identical
source tiles in the old test harness could not expose this bug. Only the fixed build
is a current candidate.

## Offline authoring and bounded scope

First regenerate the T23 CTB2 baseline using `seed_table.py --wrist-fixes`. Then:

```
python tools/mock/full_colour_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  BASELINE_OUTPUT data/palettes/wrist-fixes.json work/black-cuff-table
PF_HYBRID=1 PF_CLASS_TABLE=work/black-cuff-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/black-cuff-fixed.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

The author uses the exact two source poses. Chun-Li's central hand uses original skin
shade indices 1..3; the outer band uses opaque black index 4 and the two opaque spike
pixels use white index 13. The lower spike is at crop (24,26); the previous assumed
(24,28) was transparent, which the corrected exporter no longer accepts as a spike.
The resulting preview changes nine pixels from T23; Zangief is unchanged. No new
silhouette pixels are invented. Shared projection still preserves OAM flips, visibility
and conflicts; incomplete or ambiguous full tiles reject export.

CTB3 export: 46 records, 2370 bytes. Output arrays, frames, tables and screenshots stay
local. `work/black-cuff-comparison.png` compares T23 to the intended exact colours.
Other poses remain unverified; no full-game visual approval is claimed.

## Validation

- Five CTB3 tests pass: exact-source collision handling, unseen-source fallback,
  empty table, transparency rejection and alternating staging tiles.
- Six existing CTB2 tests pass with NASM/Unicorn.
- Default Korean ROM remains SHA256
  `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`.
- Rebuilding T23 using CTB2 is byte-identical to `work/cuff.ws`.
- Original ROM remains unchanged. Fixed candidate SHA256:
  `0624dc0455b624ccdbdc58983cfdbf93b993f8e92221bb5468f4304dd775380c`.

Runtime evidence and savestates are under `work/black-cuff-fixed-runtime-{chunli,zangief}/`.
Earlier builds/saves are preserved, including the rejected trial for diagnosis.

Fixed real-game checks pass for both fighters: 18/18 and 28/28 active tile mirrors
match; all 1946 opaque screenshot pixels match their intended colours. Opaque black
is RGB(0,0,0); both spikes are RGB(238,238,238). Whole screenshots compared with T23
differ by exactly nine Chun-Li pixels and zero Zangief pixels, including backgrounds
and opponents. Report: `work/black-cuff-runtime-pixels.json`.

Six unaffected regression captures (title, menus, story1/2/3, Ryu/Ibuki fight) are
pixel-identical to the prior baseline. Detail view: `work/black-cuff-detail.png`.
