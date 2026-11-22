# T77 battle backgrounds

All eight WonderSwan battle descriptors have a matching Japanese Saturn stage. In cartridge order they are the bar, toy shop, ski slopes, beach house, Chinatown, furnace hall, moonlit cavern and mansion. The recipes use the same order as ST00.PAC through ST07.PAC.

## Build

Use the T76 fighter shards, the Japanese WonderSwan cartridge in `orig/pf.ws`, and the MODE1/2352 data track from Pocket Fighter for Saturn. The verified track 1 SHA-256 is `b3d8134cb472326dd125821e3795385fa746db7ef303106e46b2dec1f4642d7b`. The review build used Pillow 12.3.0 and NumPy. Median-cut palette fitting runs on the build machine.

```sh
export PF_HYBRID=1
export PF_FIGHTER_PALETTES=data/palettes/roster.json
export PF_CLASS_SHARDS=work/T76/tables/4
export PF_STAGE_BACKGROUNDS=1
export PF_SATURN_TRACK="/path/to/Pocket Fighter (Japan) (Track 01).bin"
python tools/build.py out.ws --img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

The normal local disc location is `work/saturn-reference/disc/`. Sharded builds enable backgrounds when this data track or an explicit track path is present. `PF_STAGE_BACKGROUNDS=0` reproduces T76 from the same fighter tables.

## Colour and memory

The builder decodes the Saturn VDP2 palette, character patterns and three pattern-name layers. Stage-specific landmarks align shared objects across the two world maps. The distant layer supplies colour at parallax margins. The WonderSwan pattern supplies local luminance edges. A tile uses a single hardware palette and each stage has four background rows. Static tiles can use indices 1 through 15. Animated tiles retain their native IDs and flips and use their original four shade indices. The recipe and input assets fully determine the output.

Stage entry at 4000:8787 uploads static tiles once. The eight blocks occupy expansion banks CE and CF. Bank 1 tile RAM begins at 8800 for these patterns and the highest upload ends at BFDF inclusive. Existing bank-0 shadow, fighter mirror, context map and Korean text storage retain their ranges. The loader uses six bytes starting at 8380 for a bank, offset and validity marker. Stage lighting selects one of sixteen precomputed RGB444 tables on a palette input change. The bank-0 transparency scan ignores bank-1 cells. Camera updates use the original scrolling maps. The maximum measured upload is 14,304 bytes.

## Verification

Two builds reproduced SHA-256 `023a617abcbd48f26e60a7ac569316c3f2f00e447da5b50ccfac0a08841da433`. The background-disabled build reproduced the released T76 hash. The original and incremental IPS and xdelta patches each decoded to the T77 hash. The unit suite passed 106 tests.

Eight emucap/Mednafen battles ran through the actual stage loader. A test snapshot at the loader entry selected each descriptor in turn by setting the stage number. The release cartridge uses the game's normal stage selection. Captures covered BG X-scroll values 0 and 224. For all eight active battle snapshots, the loaded tile bytes, palette table and visible background pixels matched the cartridge and the captured LCD. There were 174,767 compared static pixels and 9,397 compared pixels in native animation slots. The check excludes the foreground and current and latched sprite rectangles. All eight review snapshots restored their paired LCD exactly.

```sh
python tools/check_stage_frame.py out.ws states/ST00.mcs paired-ST00.png
```

The T76 and T77 cold title, menu and three story captures were pixel-identical. The eight paired battle-entry samples had identical HUD name tiles, foreground maps and fighter palette rows. The complete fighter classifier and palette data matched T76 in all shards. Equal elapsed time from stage entry can produce a different fighter animation phase after the tile upload. Physical hardware timing and exhaustive visual coverage of effects are open. Image-text translation and fighter pose coverage remain tracked separately.
