# T75 fighter tile upload order

In the Gouki battle capture, the first fighter's sprite rows use slots starting at 0 and increasing. The opponent's rows start at 127 and decrease. For example, the opponent's three head tiles on LCD row 84 use slots 127, 126 and 125. The previous pass uploaded those tiles after the lower rows. The old and new upper rows could appear together while the LCD scanned the opponent.

The converter now visits 0, 127, 1, 126 and continues inward through 63, 64. A 128-byte successor table in the existing code bank sets the order. Each slot derives both source addresses from its physical index. An unchanged tile still skips the conversion unless its context is dirty. The stub restores the caller's bank. The original monochrome upload still runs after the colour pass. The Korean text, artwork, character palettes and all 8,617 table records are byte-identical to T74.

## Emulator results

Each cartridge was booted on its own. After the Gouki base state, advance 580 frames and reload that state separately for each simultaneous A+B hold from 53 to 67. Read OAM, 2bpp and 4bpp fighter tiles, both live palettes and the LCD. Apply the sprite flips and priority before comparing visible pixels. A match to the previous drawing counts only within its visible silhouette.

| Mednafen check | T74 | T75 |
| --- | ---: | ---: |
| Holds matching the current P1 drawing | 15/15 | 15/15 |
| Opponent drawing matching either the current or preceding sample | 14/15 | 15/15 |
| Mismatches on the opponent's visible pixels at the same native pose (T74 hold 61, T75 hold 59) | 20 | 0 |
| First cold battle, P1 visible pixels differing from the current colour buffer | 104 | 0 |
| First cold battle, P2 visible pixels differing from the current colour buffer | 0 | 0 |

Ten T75 opponent samples matched the current drawing. The other five matched the preceding drawing. Identical inputs can reach an opponent pose two frames earlier than in T74. Only four of the fifteen same-hold screenshots are pixel-identical between releases. The preview's upper row compares identical native poses at holds 61 and 59. The 33 differing LCD pixels there include the edge of the previous silhouette.

For the cold comparison, use the Ryu route in `tools/regress.py`. Reducing its final 50-frame release to 48 gives the two frames preceding the first battle checkpoint. Compare the following nine frames as well. Only the checkpoint itself changed in these twelve consecutive screenshots. All 113 changed pixels fall within the previous or current fighter silhouettes. The two fighters match the current colour buffers at that checkpoint. Graphics memory at the five original checkpoints is identical to T74. The title, menu and three story screenshots are identical. At +1 the opponent matches the preceding visible drawing in both releases. Eight of its pixels differ from the newer RAM sample. Physical WonderSwan timing and other battle inputs remain open.

## Rebuild and regression

Use the T74 stage 1 table, the original Japanese ROM and the project's existing Korean text and font inputs.

```sh
PF_CLASS_SHARDS=work/T74/tables/1 PF_HYBRID=1 PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py T75.ws --img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock python -m unittest discover -s tests
```

The tested ROM has SHA-256 `1563e2fca5af1993aa107482e32613547d78f5664144e9b9b5e5b4007acdc773`. Replacing only the converter images in the T74 cartridge and updating its header checksum reproduced every byte of the full build. All 103 tests passed with NASM, Unicorn and xdelta3 present. The sharded copier test records the first write to each of the 128 destination tiles, the mapped banks and every output byte. Original-to-T75 and T74-to-T75 IPS and xdelta patches all reproduced the tested ROM.

All twelve fighters passed the native roster check. The seven reviewed Chun-Li and Zangief wrist drawings, five Ryu dash drawings and two T74 Gouki guard transitions matched their authored colours on the LCD. The 17 delivered checkpoints restored in a fresh emulator, including the two scanout examples in the preview.
