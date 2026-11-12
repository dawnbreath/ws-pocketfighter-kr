# T29: four Chun-Li walking drawings

Adds the four walking drawings shared by forward/backward movement to the T28
idle table. The materials follow actual Saturn gameplay: skin hands, opaque black
cuffs with white studs, blue tunic, brown trousers and white boots/bun. This is a
new visual proposal; the owner has not approved these walking masks.

The initial capture repeatedly tapped directions every two frames. That introduced
dash poses; some RAM snapshots also differed from the latched screenshot, and
some left-edge crops were clipped. Those drawings were not used for this export.
`tools/capture_walk.py` instead reloads a pinned pre-control state for each sample,
waits 180 frames, then issues one continuous directional hold. It compares visible
P1 pixels with the CTB3 output, preserving both matching and mismatching samples
with flags. Only matching samples can enter `walk_table.py`. This route is specific
to the saved Chun-Li fight start, not an arbitrary-state movement classifier.

Actual Saturn walking reference was captured from the existing training save with
single holds of 4/8/12/16/24 frames in both directions. Local evidence lives in
`/workspace/work/reference/saturn-walk/`; enlarged reference is
`work/saturn-backwalk-detail.png`. No promotional art or guessed PAC decoding.

`walk_colours.py` binds material polygons to four exact source hashes:

| drawing | opaque pixels |
|---|---:|
| a85e370e3e0e5d717a3ae703eba555f4 | 695 |
| 57081f8f8361794e5b160c44d64bf5cb | 672 |
| 9e1a8f58ba00c6a884a9989f0f2e5927 | 659 |
| d6c46e228e977c1b0926c66c3a76a5c5 | 663 |

The lower-body base material is trousers, so newly exposed contour pixels cannot
fall through to skin; reviewed boots, tunic and cuffs override their own regions.
`walk_table.py` projects exact indices back through OAM flips/ownership. It rejects
unknown/ambiguous cells and conflicts with the baseline. All 73 baseline records
are byte-identical; 66 new records produce 139 records / 7020 bytes. Palette footer,
engine hooks, VRAM allocation, Korean text and Zangief masks are unchanged.

## Reproduction

Use local game inputs and tools, never commit generated captures, tables or saves.
The T28 baseline can be regenerated with the recipe in `idle-cycle.md`.

```
python tools/capture_walk.py ROM SAME_ROM_IDLE_STATE CTB3 PALETTES OUT \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/mock/walk_table.py OUT/capture.json \
  work/idle-cycle-table/full.ctb3 work/walk-final-table
PF_HYBRID=1 PF_CLASS_TABLE=work/walk-final-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/walk-final.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

For this run, loading the earlier ROM's state into the candidate returned
`invalid snapshot history record`. No state bytes were modified. A new cold boot
used the same selection route, and each of the four idle poses received a fresh
candidate-ROM state. The candidate's base-pose state was then used for holds.
Original ROM, old builds and original saves remain preserved.

## Final verification

Candidate SHA256:
`d39f818483db17c932b1b7a0bb709ca8055c8c2a28552a8a5b3b8a0e67eb204c`.
Table SHA256:
`1671b094c1dba025476d2b1c1ba0d70a65f03594383f9d65d1afc6527fc9ba57`.

- Final real-game capture: 14/14 samples agree with source/table rendering.
  All four walking drawings were observed across left/right holds. The four
  representative screenshots match all 2689 opaque authoring pixels.
- Six unaffected screenshots (title, fight-start, all four idle drawings) are
  pixel-identical to T28. The full idle return sequence still matches its tiles.
- Re-exporting from the final runtime capture reproduces the table byte-for-byte.
- Original ROM SHA256 remains
  `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
- Local capture/saves: `work/walk-final-runtime/` and
  `work/walk-final-idle-chunli/`; pixel report: `work/walk-final-verification.json`;
  actual-screen enlargement: `work/walk-final-game-detail.png`.

Identical requested hold lengths do not guarantee identical game-animation or
background phases across these builds. Moving whole-screen pairs were therefore
not accepted as pixel-regression evidence; the unaffected pinned screens above
are the regression evidence. These samples establish the four drawings, not a
frame-by-frame continuous full movement-loop recording or calibrated performance.
Dash, attacks, damage, opposite facing and other fighters' remaining poses are
not covered. Table agreement proves delivery of the authored colours, not visual
approval or general VRAM lifetime safety.
