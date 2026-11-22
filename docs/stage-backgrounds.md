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

## T78 palette fitting

T78 uses the same eight Saturn references, landmarks, WonderSwan source patterns and stage loader as T77. The build assigns static tiles to the four hardware rows, alternately refitting the eleven available colours in each row and selecting a row for each tile. It then fits those colours to the actual indices left after repeated native patterns share a packed tile. The game uses the resulting ROM data directly.

The table measures weighted squared error against the same registered RGB444 target used for T77. For each static pixel the weights on squared red, green and blue differences are 2, 3 and 1. It measures palette reproduction after registration. The animated slots have a separate four-shade constraint.

| Stage | T77 full-map static error | T78 full-map static error | Reduction |
| --- | ---: | ---: | ---: |
| Bar | 141652 | 109667 | 22.6% |
| Toy shop | 123309 | 117736 | 4.5% |
| Ski slopes | 145249 | 116852 | 19.6% |
| Beach house | 149946 | 133359 | 11.1% |
| Chinatown | 190830 | 172784 | 9.5% |
| Furnace hall | 128710 | 115672 | 10.1% |
| Moonlit cavern | 146305 | 117723 | 19.5% |
| Mansion | 136999 | 131067 | 4.3% |

Emucap captured stage entry and combat for each of the eight stages. Across the 16 paired LCDs, 345,623 visible static background pixels matched their respective decoded cartridges. Their error against the registered target fell from 1,171,226 to 984,555. All 16 pairs improved. Another 23,581 visible animation-slot pixels passed the LCD check. The 810 animated map cells and their colours at every brightness level matched the T77 cartridge. The HUD map, fighter palette rows and fighter tile mirror matched T77 in every pair. Five cold title/menu/story screenshots matched pixel for pixel. All eight T78 combat snapshots restored their LCD.

Build with the command above. T78 SHA-256 is `27fcd00bc9064b28b4fa6b13649ef0502111c303194936900772709d385042c1`. The original and T77 IPS and xdelta patches reproduced this hash. The suite passed 107 tests. Actual hardware timing and side-by-side checks of every animation frame remain open.

## T79 background spectators

The previous whole-stage comparison missed small figures. In Dee Jay’s bar the Saturn scroll plane already contains Cammy and E. Honda. Local registration transfers the blond hair, cap and green costume of Cammy, and the light green and blue-violet stripes and belt of Honda. Build-time palette fitting reserves ten sampled RGB444 swatches for each of the two figures and weights the other registered guests when choosing tile variants. The 44 registrations cover groups, individual figures and associated display details across the eight stages. Separate Saturn actors use the stage PAC’s sprite pixels (0x106), sparse column-major layouts (0x107) and RGB555 rows (0x108). Their colour samples retain native WS shading.

The WS stage camera uses six transfer descriptors per stage. The first three supply the left edge and the last three supply the right. The same native VRAM index can refer to entirely different people on opposite sides, and the T78 colour mirror could show the old drawing after a camera move. All 810 formerly streamed cells resolve to specific ROM patterns on the appropriate side of the world map. The stage builder now packs these patterns with the interior art into the existing bank-1 upload. The original game still performs its regular camera transfers. This revision changes colour data and stage maps in the cartridge and uses the T78 runtime hooks.

Run the build above and use the scene checker with each paired capture:

```sh
python tools/check_stage_frame.py out.ws stage.mcs stage.png --original orig/pf.ws
```

At camera X-scroll 224, 0 and 32, 24 Mednafen LCD captures matched 551,006 exposed background pixels. For 1,020 visible occurrences of edge cells the live original 2bpp pattern bytes also matched the predicted left/right ROM source. Across 43 registered regions, 111 comparisons of mutually visible pixels improved absolute RGB error against the local Saturn samples compared with T78. The upper right balcony was above these gameplay viewports. Its 713 cartridge-map pixels were checked separately. The artist-authored registrations approximate poses that differ between ports.

At stage entry, Cammy’s mean absolute RGB channel difference from the registered Saturn crop fell from 50.19 in T77 to 18.75 in T79 over 504 visible pixels. Honda’s fell from 48.38 to 14.83 over 996 pixels. Both figures displayed all ten fixed colours during entry and combat. All eight combat states restored, and the title, menu and three Korean story captures matched T78 pixel for pixel. The 16 entry/combat pairs had identical HUD maps and fighter palettes. Seven combat captures differed in fighter animation phase. In 32 subsequent frames per stage, all 488 fighter samples with matching native pattern buffers reproduced the same colour buffers as T78. The other 24 had no corresponding native pose within that window. Physical hardware was not tested.

T79 SHA-256 is `73e4752c565d8277e2107e4234f60d2a9e050b99b85a42bc5cc638af5b63608f`. Both IPS and xdelta decoded to this hash from each of the original, T77 and T78 cartridges. The review bundle includes entry and right-camera bar states as well as one combat state per stage.
