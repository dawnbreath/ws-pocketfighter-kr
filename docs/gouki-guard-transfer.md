# T74 Gouki guard and fighter tile transfer

Two Gouki guard transitions reuse his reviewed stance material boundaries. The native source drawings have crop hashes `6291d5f78a492d991250352b06c7f0ab` and `767eb4459b2b4ceeeaed84cd9345adb9`. Both are available from Gouki's own base state after 579 settling frames followed by a neutral A+B hold of 56 or 64 frames. The Japanese Saturn reference uses the same two hold lengths to compare the gi, beads, hair and gloves.

## Changed-tile transfer

In `cphook`, a full-tile table hit copies one 32-byte tile from the mapped cartridge bank to ES:DI. The old loop issued sixteen loads, pointer additions, stores and loop instructions. The new path uses one 16-word `rep movsw` with DS temporarily equal to CS. BP preserves the staging address while SI addresses ROM. The routine restores DS and advances the staging pointer by 16 bytes. The fallback conversion, equal-tile skip, bank selection and lookup are unchanged.

The following native breakpoints bracket converter entry at `2000:0500` and the original monochrome copier at `0000:0120`. The controls used the same new table. All four pairs had identical staging hashes. The measurements cover the converter as a whole.

| Changed source tiles | Previous transfer, clocks | New transfer, clocks |
| ---: | ---: | ---: |
| 23 | 24,135 | 22,745 |
| 21 | 22,983 | 21,773 |
| 24 | 24,919 | 23,324 |
| 0 | 13,695 | 13,685 |

## Fixed-input timing

Each cartridge was cold-booted separately on the same Japanese game route. The active Gouki state was captured 580 frames after the base state. Each sample reloaded its own cartridge's state and held A+B for 54 through 66 frames, inclusive. Reads included OAM, monochrome VRAM, the live 4bpp mirror, both fighter palettes and the LCD. The comparison counts screen pixels outside the union of the paired P1 silhouettes.

The new colours with the previous transfer had 3,788 outside-P1 pixel differences summed across thirteen holds against T73. The release had 101: 21 at hold 57 and 80 at hold 61. The other eleven matched T73 outside P1. Gouki's visible pixels matched his native colour buffer at all thirteen holds. The opponent's LCD pixels matched the current buffer at eight holds. At holds 60, 62, 64 and 66 the LCD matched the preceding sampled opponent drawing within its visible silhouette. At hold 61, twenty visible opponent pixels differed from the current buffer. These measurements describe emulator timing. A physical-device result is still open.

The first cold battle LCD differed from T73 on sixteen pixels in two scanlines. Title, menu, three story screens and battle follow-ups at +1, +2, +4 and +8 matched exactly. The five graphics-memory checkpoints matched.

## Build and regression

Start with the T73 stage 4 table and the source and protection manifests through T73. Export `tools/mock/roster_table.py --family gouki-guard --context 1 --accept-reference-tiles` and verify with `tools/verify_roster_output.py --family gouki-guard --require-context 1`. Build the resulting stage 1 with `PF_CLASS_SHARDS`, `PF_HYBRID=1`, `PF_FIGHTER_PALETTES=data/palettes/roster.json`, image insertion and the three Korean JSON inputs. The seven added canonical records all reproduce their original fallback. Seven variants apply to Gouki.

- Both new drawings matched the live buffer and LCD in 19 native samples, covering 1,510 representative P1 pixels. 2/2 representative full-screen pairs matched outside P1.
- All twelve roster controls, seven Chun-Li and Zangief wrist drawings, five Ryu dash drawings and the full restored Ryu hold-24 screen passed. Verified 337 earlier drawings across 1,547 samples covering 38,557 tile uses.
- All 15 delivered states restored in a fresh emulator. Independent table exports and ROM builds, the original and T73 IPS/xdelta round trips and private recovery reproduced `7aad5b2e37e58cd9ddf28c5241c706d70d628fc6f133e7e8600f80f97f248185`. All 103 tests passed, including the exact-source transfer with alternating staging tiles.

Other moves, opponent timing on routes beyond this sample and final art review remain open.
