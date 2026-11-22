# Crouching and airborne attacks

T68 registers twelve P1 drawings from T67. Two independent builds produce SHA-256 `a5731828eb5537f6b711c7ec88a28f16762a9087d09c417afc7efe4bf6b1ae07`.

| Fighter | Drawings | Saturn reference used |
|---|---:|---|
| Morrigan | 5 | Inverted crouching attack, head wings, green hair and airborne kick |
| Felicia | 2 | Blue mane, white fur and exposed skin |
| Lei-Lei | 2 | Cap, gold edging, claws and dark sleeves |
| Ryu | 1 | White gi, headband and gloves |
| Tabasa | 1 | Airborne toothed familiar with a violet body, yellow eyes and white teeth |
| Zangief | 1 | Dropkick recovery at Saturn hold 30, including the red boots, trunks and both wristbands |

## Source and runtime

T67 supplied 120 crouching and 72 airborne samples across the twelve fighters. Captures had to identify P1 by the HUD, agree with the LCD at its recorded position, and provide a complete source with matching staging tiles. The six other fighters contributed no new eligible drawing in this input sweep. Saturn footage provides material boundaries and colour references. The WS engine retains its original silhouettes.

The exporter adds 276 canonical records (including fallback anchors), 133 Morrigan variants and 16 Tabasa variants. The resulting table has 6,342 entries. Existing explicit outputs and protected defaults were checked along with 19,618 tile observations from 236 older drawings.

## Lookup cost and controls

With the enlarged table, three of the four cold follow-up shots differed from T67. The builder now emits seventeen 16-bit offsets in each CTB4 shard at bank offset `0x21D0`. The existing lower-bound search starts in the range for the second hash nibble. The remaining full hash, context and sixteen source bytes still determine the result. This changes only lookup of a changed fighter tile in indexed sharded builds.

The final build matched T67 at the title, menu, three story screens and all four short battle follow-ups. The first battle LCD differed at 128 pixels, while its OAM, source, staging, colour buffer and palettes matched. At ticks 9–49, 37 of 41 full screens were identical. At the four differing ticks, the P1 screenshot-to-buffer match status was the same on both cartridges. Real hardware timing remains open.

Runs started independently on the candidate ROM matched all twelve registered drawings in 163 native samples (12,486 representative P1 pixels). All twelve selected states matched the staged body. Eleven paired screenshots were pixel-identical outside P1. The remaining Lei-Lei pair differed at 40 pixels outside her silhouette. All twelve roster controls, the four Chun-Li and three Zangief wrist drawings, and Ryu’s full hold-24 screen passed. P2 Ken was checked in 32 samples, including eight with visible context-specific pixels. Twenty-five state files restored in a fresh emulator. The original and T67 patch paths reproduced the candidate. The regression suite passed 103 tests.

## Reproduction

Run `tools/mock/roster_table.py --family low-air-attacks` for contexts 0, 2 and 3 in order with their corresponding source and protection manifests. Use the preceding stage as the baseline for each export. Build with `PF_HYBRID=1`, `PF_CLASS_SHARDS` pointing at the final directory, and `PF_FIGHTER_PALETTES=data/palettes/roster.json`. Pass `--img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json` to `tools/build.py`. Use the same family and context for `tools/verify_roster_output.py`. The private handoff contains the inputs, label tables, controls and both patch formats.

Additional moves, opponents and hardware timing require separate evidence.
