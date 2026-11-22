# Close-range attack inputs

T69 adds nine registered WonderSwan drawings. Ryu contributed three. Felicia, Ibuki, Ken, Morrigan, Sakura and Tabasa contributed one each. Sakura’s drawing shows her recoiling from Ibuki’s hit. Tabasa’s drawing uses the previously labelled stance shifted one pixel left. The Saturn captures provide costume and equipment references, including Ibuki’s extended weapon, Ken’s red gi and Ryu’s headband and gloves.

## Inputs and export

From each fighter’s own T68 active battle state, hold right for 20 frames, hold the first attack for four frames, release for four, then hold the second attack. The capture tool exposes both orders as `--motion chain --directions a-b b-a`. The source sweep used `--settle-frames 0 --frames 3 6 10 14 20 28` with the colour buffer and context map enabled. This produced 144 samples across twelve fighters. The five other fighters yielded no new eligible drawing in these samples.

Registration requires a complete P1 drawing, a matching HUD identity, zero displacement from the LCD and a matching staged body. The exporter retains existing outputs and uses the preceding stage as its baseline. Run `tools/mock/roster_table.py --family close-attacks` for contexts 0, 2, 3 and 4, with the matching source manifests and the retained actor manifests for each nonzero context. The result adds 196 canonical entries, including fallback anchors, plus 22 Morrigan, 30 Tabasa and 18 Ken variants. The final catalogue has 6,608 entries.

## Reproduction and controls

Build with `PF_HYBRID=1`, `PF_CLASS_SHARDS` set to the last export, and `PF_FIGHTER_PALETTES=data/palettes/roster.json`. Pass `--img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json` to `tools/build.py`. Two independent exports and builds produced SHA-256 `e6aa515253eb9d25cb0dd6de5abdd609f83b061f0c7de8146491e254081fe95c`.

- Across 83 native samples the registered drawings matched the authored 4bpp labels and LCD. All 8,246 representative P1 pixels matched. For each of the nine before-and-after pairs every pixel outside P1 matched T68.
- The old table, protected defaults and all previous character overrides retained their values. The replay of 961 previous observations checked 24,103 fighter tile instances across 248 earlier drawings.
- All ten cold and early-battle screenshots matched T68. OAM, staging, sprite mirrors and palettes matched at all five sampled battle ticks. The twelve roster controls, seven Chun-Li and Zangief wrist drawings, Ryu’s hold-24 full LCD, and P2 Ken’s context-specific colour output passed.
- A fresh emulator restored nine new drawing states, twelve roster states and Ryu’s replay input state. IPS and xdelta round trips from both original and T68 reproduced the candidate. The existing suite passed 103 tests.

The review package contains the comparison strip and the 22 states. Other moves, opponents and physical hardware timing remain open.
