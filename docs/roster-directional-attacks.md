# Directional attack inputs

T70 registers the P1 drawings observed during a down, down-forward, forward-plus-attack sequence. The 31 drawings are grouped by the character that actually displayed them.

| Fighter | Drawings | Fighter | Drawings |
| --- | ---: | --- | ---: |
| Chun-Li | 1 | Dan | 3 |
| Felicia | 3 | Gouki | 4 |
| Ibuki | 1 | Ken | 2 |
| Lei-Lei | 3 | Morrigan | 3 |
| Ryu | 5 | Sakura | 2 |
| Tabasa | 4 | Zangief | 0 |

## Capture and reproduction

Start from each fighter’s active T69 state. Use `tools/capture_walk.py --motion quarter-circle --directions a b --settle-frames 0 --frames 3 6 9 12 16 20 26 34 --read-colour-buffer --read-context-map` with the matching character, ROM, table, palettes and emulator paths. The protocol holds down for three frames, down-right for three, then right plus the selected attack. Additional sweeps for Chun-Li, Dan, Tabasa and Zangief used later input or earlier battle states. The combined set contains 320 WonderSwan samples. The Japanese Saturn reference set contains 96 captures across the twelve fighters. The references establish costume and equipment colours. The two games can show different moves at the same button timings.

Run `tools/mock/roster_table.py --family directional-attacks --accept-reference-tiles` with the private source manifests in context order 0, 1, 2, 3, 4. Start with T69’s final catalogue and pass each stage to the next. Supply the retained actor manifests for Gouki, Morrigan, Tabasa and Ken. The exporter locks older tile outputs. A new tile can contain opaque cells hidden in every observation. This family preserves such cells only when the old table and every captured native 4bpp copy agree on their values. That applied to 132 cells on 13 tiles. Flipping a native colour plane in one hidden cell made the export fail. Chun-Li’s reference kick reaches the left edge of the screen. Its LCD comparison covers the visible silhouette.

The final table adds 557 canonical entries and 254 character-specific variants. Build through the existing colour pipeline with `PF_HYBRID=1`, `PF_CLASS_SHARDS` pointing to stage 4 and `PF_FIGHTER_PALETTES=data/palettes/roster.json`. Run `tools/build.py` with the usual `--img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json` inputs. Independent exports and builds produced SHA-256 `da46e9ac80b320debbbc21ab5c9a124beddbb4af46e6013d81997b4eb17b9409`.

## Verification

- The final candidate reproduced all 31 drawings in 163 aligned native observations. For the representative frames, 28,169 visible player pixels matched the authored labels in the 4bpp buffer and LCD. All 31 selected screenshots matched T69 outside the player silhouette. In the separate Felicia timing probe, all 18 opponent tile outputs, sprite positions and palette words agreed at the saved tick. After resuming the two states, frames +3, +4 and +8 matched everywhere outside P1.
- Replayed 26,254 tile instances from 1,044 earlier observations across 257 registered drawings. All retained outputs matched. Zangief yielded 47 aligned source samples with fully known tiles and 17 unaligned samples. A separate candidate replay confirmed eight of his drawings across 43 stable, aligned screens against the prior colours. The seven wrist controls, twelve roster controls, Ryu’s full-screen dash control and Ken’s P2 ownership check also passed.
- All ten cold-boot and early-battle screens matched T69 pixel for pixel. The five corresponding samples of OAM, staging, mirrors and palettes matched. Both IPS and xdelta reconstructed the same candidate from either the original ROM or T69. A fresh emulator restored all 44 supplied states. The existing suite passed 103 tests.

The private review package includes comparison sheets, the original and incremental patches, and Mednafen states for the new poses and roster controls. Frame coverage beyond the sampled inputs, final visual approval and physical hardware timing remain open.
