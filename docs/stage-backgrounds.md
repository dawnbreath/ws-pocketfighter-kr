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

## T80 scenery details and bartender

The build registers 57 smaller regions from the Saturn scenery in `data/stages/details.json`. Both rectangles use 288×208 world coordinates with exclusive right and bottom edges. Area sampling transfers local colour. Native luminance supplies linework and a three-pixel edge blends each region into the surrounding drawing. Guests take precedence where rectangles overlap. For the bartender, `accents` holds local rows of the form [RGB444, y, first x, exclusive end x]. The tooth highlight, blue-gray tooth shadow, forehead and yellow fabric follow the WS pixels and use colours sampled from Saturn sprite frame 0.

| Stage | Regions | Examples | T79 RGB error | T80 RGB error |
|---|---:|---|---:|---:|
| Bar | 8 | Bottles, wall lamp, stools | 38.31 | 25.07 |
| Toy shop | 6 | Tree, wrapped presents, window shelf | 41.23 | 21.60 |
| Ski slopes | 7 | Chairlift, lodge gable, igloo entrance | 34.48 | 18.68 |
| Beach house | 8 | Awning, stairs, animal ornament | 43.88 | 19.87 |
| Chinatown | 6 | Dragon, stall curtain, lantern | 34.98 | 19.40 |
| Furnace hall | 8 | Furnace, flue, books, chairs | 28.46 | 15.25 |
| Moonlit cavern | 7 | Castle, wheel, hanging lamp bracket | 39.98 | 17.76 |
| Mansion | 7 | Chandelier, arched windows, sofa | 26.60 | 16.01 |

The table measures mean absolute channel error (0–255) on the compiled maps against the locally registered, area-sampled Saturn images. Overlapping foreground guests, later prop rectangles and transparent Saturn pixels are excluded. In 24 Mednafen captures all 57 regions appeared at least in part. All 152 comparisons of the same exposed pixels across versions moved closer to their reference. The scene checker matched 551,006 exposed LCD pixels and 1,020 occurrences of native camera cells.

All 32 marked bartender pixels showed their intended Saturn RGB444 colour at entry and at both camera extremes. At entry the error on Cammy's 504 exposed pixels fell from 18.75 to 16.27, and on Honda's 996 from 14.83 to 8.04. T80 displayed all ten specified colours for each guest at all three camera positions. A recount of the T79 entry LCD against the current ten-colour lists found eight on Honda and ten on Cammy.

The HUD map, fighter palettes and fighter tile mirror matched T79 on all 16 paired entry/combat states. Eight combat saves restored the captured LCD. Title, menu and three Korean story captures matched T79 pixel for pixel. Stage graphics, stage maps and the cartridge checksum account for all changed ROM bytes. The suite passed 111 tests. Six verified xdelta/IPS patches from the Japanese original, T77 and T79 produced T80 SHA-256 `17932ddd17dd24476c645a54bc92f55f78bba64c89e47fb8bf8d2f4850ec012f`. These measurements cover the listed regions and camera positions in Mednafen. Physical hardware and exhaustive animation coverage remain open.

## T81 remaining scenery

T81 registers 35 additional scenery details with the Japanese Saturn stage art. The list in `data/stages/scenery-insets.json` uses the same world coordinates and exclusive rectangle bounds as the earlier registrations.

| Stage | New regions | Examples |
|---|---:|---|
| Bar | 2 | Upper balcony rails and counter footrail |
| Toy shop | 4 | Roof corner and bridge arches |
| Ski slopes | 5 | Right chairlift, red pylon padding and snowbank |
| Beach house | 5 | Mast, palm trunk and pier timbers |
| Chinatown | 4 | Gate post, shop eaves and side canopy |
| Furnace hall | 4 | Ceiling drawings, wall niche and library ladder |
| Moonlit cavern | 6 | Overhanging roots, wagon skull crest and body |
| Mansion | 5 | Upper oval window, smaller windows and courtyard carriage |

The build fits indices within the existing stage palettes after the main colour fit. When a flipped or repeated tile is shared, its users must all retain the original colours on protected pixels. A tile used once can select another palette row that meets the same constraint. The packed tile inventory, brightness tables and upload sizes are identical to T80. Across the eight full maps 17,382 pixels changed. All 432,865 pixels outside the eligible regions, including all previously registered guests and props, matched T80 exactly. Over the 46,367 eligible pixels the area-weighted mean absolute channel error against the registered Saturn crops went from 33.23 to 24.03 (0–255 scale). All 35 regions improved on the full maps.

For each stage we captured the top of the scenery 84 frames after the stage loader entry, the standing entry view, active combat on the left and combat on the right. The 32 paired Mednafen captures had 28,880 changed LCD samples, all at the coordinates of actual changes in the map. The scene checker matched 760,110 exposed background pixels and 1,204 native camera-cell occurrences. Of 107 jointly visible comparisons, 104 improved and three had equal error where only part of the object was exposed. Every region improved in at least one capture. The bartender's 32 accents and both ten-colour guest palettes matched T80 in the three bar combat/entry views.

We restored all 17 delivered states (eight fights, eight intros and the right-side ski camera). The title, menu and three Korean story screens matched T80 pixel for pixel. All 16 paired entry/combat states had matching HUD maps, fighter palettes and fighter tile buffers. The test suite passed 112 tests. Two source builds produced SHA-256 `5081bfd05fceaacf5497cb81380ed134d889a9ae023b32280ce43a949b2c3448`. The original, T77 and T80 IPS and xdelta paths all reproduced those bytes. The gallery uses complete cartridge-map crops followed by paired emulator screenshots. Hardware and exhaustive animation coverage remain open.

## T82 upper and outer scenery

The 38 local registrations in `data/stages/scenery-edges.json` cover the bar roof and balcony supports, both toy shop walkways, the left chairlift and distant peaks, beach shop timbers and waterline, Chinatown's upper windows and paving, the clock case and fireplace base, cavern rocks and the mansion's curtain, portrait frame and stair edges.

The native tile inventory constrains each registration. In an initial build the beach waterline retained every T81 pixel, and the left roof truss could change only 22 pixels, because the patterns were shared with protected scenery. The build can now select another packed pattern already used for the same native source with the destination cell's original flips. It chooses among the existing palette rows and rejects a candidate if any pixel outside the eligible area would change colour. This works at build time with the existing stage upload and brightness tables.

| Stage | Regions | Changed map pixels |
|---|---:|---:|
| Bar | 5 | 10,789 |
| Toy shop | 5 | 5,963 |
| Ski slopes | 4 | 2,855 |
| Beach house | 5 | 980 |
| Chinatown | 6 | 6,271 |
| Furnace hall | 5 | 3,511 |
| Moonlit cavern | 2 | 1,696 |
| Mansion | 6 | 6,697 |

The full maps have 38,762 changed pixels and preserve all 402,466 pixels outside the eligible regions. On the 76,766 eligible pixels, mean absolute channel difference from the registered Saturn colours fell from 28.59 to 20.43 (0–255). Each region improved. The beach waterline accounted for 32 changed pixels. On the three combat/entry bar views all 32 bartender accents and both guests' ten selected colours matched T81.

The 32 T81/T82 Mednafen screenshot pairs cover the upper intro, standing entry and both horizontal camera extremes. The scene checker verified 760,110 exposed background pixels and 1,204 native camera-cell occurrences. All 59,535 changed LCD samples corresponded to differences in the decoded stage maps. All 38 regions improved in at least one actual capture. Of 122 object/view comparisons, 119 moved closer to Saturn and three partially exposed views had equal error.

The HUD, fighter palettes and fighter tile buffers matched on all 16 paired entry/combat states. Title, menu and three Korean story screens matched T81 exactly. All 17 packaged states restored their LCD, including the right-side Chinatown state. The test suite passed 113 tests. All six original/T77/T81 IPS and xdelta paths produced SHA-256 `b8c578b77931e994e16aebb165455f90a922429ebfff837882c2ddea696894c7`. The gallery shows full cartridge-map crops and a paired Chinatown combat screenshot. Testing covered Mednafen and the recorded poses and camera positions.

## T83 backdrops between registered scenery

The second layer in `data/stages/scenery-edges.json` registers 33 additional areas on the eight stage maps. The offline builder fits the original regions first, then locks them while it fits later layers with the same tile inventory. Stage code, VRAM allocation and upload sizes are unchanged. The bar sign and toy shop billboard lettering lie outside the new areas.

| Stage | Examples | Regions | Changed map pixels |
|---|---|---:|---:|
| Bar | Roof opening, overhead panels and left doorway | 4 | 4,210 |
| Toy shop | Night sky around the billboard and east arcade | 4 | 2,123 |
| Ski slopes | Aurora, western skyline and snow dome | 5 | 6,398 |
| Beach house | Sky, western sea and front boardwalk | 4 | 1,711 |
| Chinatown | Cloudbank, roofline and stone paving | 4 | 2,360 |
| Furnace hall | Ceiling painting, open hall and rug | 4 | 7,524 |
| Moonlit cavern | Cavern roof, gorge and carriage paving | 4 | 6,088 |
| Mansion | Wall below the portrait, courtyard floor and sky | 4 | 1,325 |

The decoded cartridge maps have 31,739 changed pixels. All 377,991 pixels outside the eligible areas match T82, including all prior spectator and scenery rectangles. Each of the 33 regions improved against its registered Saturn sample. On the 101,241 eligible pixels the mean absolute RGB channel difference fell from 18.90 to 13.93 on the 0–255 scale. During visual review the mansion sky registration was narrowed to exclude the curved building silhouette and the boardwalk registration was restricted to its upper plank. The gallery shows eight examples at a common scale per row and matched ski-stage LCDs.

Across 32 paired Mednafen views, the stage checker matched 760,110 exposed background pixels to the cartridge. All 43,582 changed LCD pixels were at coordinates that changed in the decoded stage maps. Of 90 region/view observations, 85 moved closer to Saturn and five tied. The HUD, fighter tile buffer and fighter palette rows matched T82 in 16 entry/combat pairs. Title, menu and three Korean story screenshots matched on cold boot. All 17 delivered states restored the recorded LCD. The 113 repository tests passed and all six original/T77/T82 IPS and xdelta patches decoded to SHA-256 `33228f64ef7e4c6f2311232b0565180b42b60e5e05be3efc3901987fe4c7b6f6`. These comparisons cover the recorded scenes on the emulator.
