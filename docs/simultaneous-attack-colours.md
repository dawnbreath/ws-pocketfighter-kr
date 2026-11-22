# T72 simultaneous attack colours

The new colour table covers 31 P1 battle drawings across all twelve fighters. Thirty came from holding A+B. One additional Lei-Lei drawing came from the forward quarter-circle A recovery. A neutral and a right+A+B run sampled each fighter at 4, 9, 15, 23 and 32 frames. Every distinct A+B drawing accepted in this batch was available on the neutral route. Chun-Li's two drawings use a 47-frame settle after the active state.

| Fighter | Drawings | Source hold in frames |
| --- | ---: | --- |
| CHUN-LI | 2 | 4, 15 |
| DAN | 3 | 4, 15, 32 |
| FELICIA | 2 | 4, 23 |
| GOUKI | 3 | 4, 15, 23 |
| IBUKI | 3 | 4, 15, 32 |
| KEN | 4 | 4, 15, 23, 32 |
| LEI-LEI | 2 | 41, 4 |
| MORRIGAN | 3 | 4, 9, 15 |
| RYU | 3 | 4, 15, 23 |
| SAKURA | 2 | 4, 15 |
| TABASA | 1 | 9 |
| ZANGIEF | 3 | 4, 9, 23 |

## Saturn comparison

The Japanese Saturn disc ran in Mednafen. Each of the twelve fighters has nine reference captures from A+B, right+A+B and C at 5, 13 and 25 frames. The reference images show costumes and equipment. The two ports use different animation frames. On WonderSwan, native palette samples confirm the boundary between Chun-Li’s black cuffs, light studs and skin on both new drawings. All three new Zangief drawings have a red cuff adjacent to the bare hand. His beard and hair retain the established dark skin ramp.

## Build and verification

- Use T71 table stage 2 as the base. Export private source manifests with `tools/mock/roster_table.py --family simultaneous-attacks --accept-reference-tiles` in contexts 0, 1, 2, 3 and 4. Supply historical manifests for matching actors to protect previous context-specific tiles. Two tiles had 22 opaque cells hidden by self-overlap. They retained their verified T71 native values.
- Build with `PF_HYBRID=1`, `PF_CLASS_SHARDS` pointing to the final stage, `PF_FIGHTER_PALETTES=data/palettes/roster.json` and `tools/build.py --img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json`. Two exports and builds produced `e665bdfd18b736eb018659719d75ba354176300f4751479de279b0405cf6f05c`. Original-ROM and T71 IPS and xdelta patches reproduced those bytes.
- `tools/verify_roster_output.py --family simultaneous-attacks` matched 223 real emulator samples against the colour buffer and LCD. The 31 representative bodies contain 27,190 visible pixels. 15,225 differ from T71 inside P1. 31 of 31 representative full-screen pairs match outside P1.
- In the fixed-input Ryu replay, all 495 changed LCD pixels correspond to the opposing Ibuki's new colours. Verified her palette, 24 changed slots and the donor tiles from her own three drawings. On Dan holds 12–15, 258 changed opponent pixels retained the same before/after LCD colours across those four holds. All 258 match Zangief's own new donor tiles at holds 12–14. At Lei-Lei hold 41 and Dan hold 16, 185 and 11 LCD pixels outside P1 differed. Opponent OAM, source tiles, colour buffer and palette matched across versions at those two holds. Lei-Lei hold 43 and Dan hold 18 matched outside P1.
- Replayed all twelve fighters and all seven earlier wrist drawings. Verified the five earlier Ryu dash drawings and a full-screen Ryu input replay. Verified 31,900 earlier tile uses across 297 drawings from 1,266 samples. Reloaded 44 candidate states in a fresh emulator. The test suite passed all 103 tests.
- Title, menu, three story screens and four battle follow-ups match T71 pixel for pixel. The first battle LCD differs on eight pixels at x=32–39, y=100. The OAM, source and staging RAM, colour buffer and palette samples matched at all five checkpoints.

The patch changes colour-table data and its checksum. The engine hooks, Korean text paths and save format are byte-identical to T71. Unsampled moves, player-two coverage, final art review and physical-device timing remain open.
