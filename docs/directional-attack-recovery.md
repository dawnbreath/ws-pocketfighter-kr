# Directional attack and dash follow-throughs

T71 colours nine additional battle drawings found between the sampled T70 frames. Felicia contributes four drawings. Gouki, Ibuki, Lei-Lei, Morrigan and Ryu contribute one each.

The Saturn version shows Morrigan’s three wing blades with forward plus punch held for 16–24 frames. The comparison sheet uses frame 18. The material map distinguishes the dark wing and shafts, light cutting edges, hair and face. For Lei-Lei, the WonderSwan blade retracts twelve pixels. The sleeve, cuff and inner blade use the registered T70 regions. Ryu’s dash frame uses the existing T64 regions shifted one pixel right. The Saturn captures for the other fighters reference costume and equipment colours.

## Reproduction

Start from the T70 battle states for the six fighters. Use `tools/capture_walk.py` with the native colour buffer and context map enabled. Registration requires matching staged and displayed source pixels and a zero-offset LCD sample.

| Fighter | Input | Settle after loading | Final hold |
| --- | --- | --- | --- |
| Felicia | quarter-circle B | 0, 185, 231, 330 | 4, 2, 2, 2 respectively |
| Gouki | quarter-circle A | 0 | 29 |
| Ibuki | quarter-circle A | 1 | 6 |
| Lei-Lei | quarter-circle A | 0 | 37 |
| Morrigan | quarter-circle B | 0 | 15 |
| Ryu | left dash | 0 | 33 |

Pass the private manifests to `tools/mock/roster_table.py --family directional-recovery --accept-reference-tiles` for contexts 0, 1 and 2 in order. Begin with T70’s stage 4. Supply the previous actor manifests through T70 when exporting Gouki and Morrigan. Every new opaque tile cell had a visible donor. The existing colour tables gain 189 canonical entries, 20 Gouki variants and 43 Morrigan variants. The final catalogue holds 7,671 entries.

Build through `tools/build.py` with `PF_HYBRID=1`, `PF_CLASS_SHARDS` set to stage 2, `PF_FIGHTER_PALETTES=data/palettes/roster.json`, and `--img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json`. Independent builds produced SHA-256 `b844f9f635c9621e78d6f1f2d88906e2a3cc0ed905a253ca69d7bdbbdaf8eba4`.

## Native checks

- All nine drawings matched the authored 4bpp output and LCD in 59 native observations. The representative frames cover 9,285 visible P1 pixels. All nine representative scene pairs matched T70 outside P1. A separate Ryu hold-33 comparison had 122 differing LCD pixels near the opponent. The opponent’s OAM, source bytes, 4bpp output and palette matched. The next native frame and the +2, +3, +4 and +8 samples matched outside P1.
- In the cold run, nine of ten full screenshots matched T70. The tenth displayed the newly red headband on another Ryu pose. All 23 differences matched the RGB computed from two shared Ryu tiles at slots 125 and 126. Every other pixel in that frame matched T70.
- Replayed 30,203 tile instances across 1,207 observations from 288 previously registered drawings. The roster controls covered twelve fighters. The four Chun-Li and three Zangief wrist drawings, five earlier Ryu movement drawings and the Ryu dash input replay passed.
- Both IPS and xdelta decoded to the build hash from the original and from T70. A fresh emulator loaded nine drawing states, twelve roster states and the Ryu input state. The existing 103 tests passed.

Other actions, opponents, final visual review and physical hardware timing remain open.
