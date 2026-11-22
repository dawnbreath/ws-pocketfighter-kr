# T76 airborne fighter drawings

Starting from T75, replay both jump attack inputs for all twelve fighters at holds of 7, 13, 19, 27 and 35 frames. The route uses the existing low-air protocol with zero extra settling. The four drawings below had uncoloured tiles, an exact HUD identity and matching staging and visible source pixels. Previously registered tiles retain their colours.

| Fighter | Drawing | T75 / T76 hold in preview | Changed fighter pixels | Visible fighter pixels |
| --- | --- | --- | ---: | ---: |
| Felicia | Curled roll | 27 / 28 | 627 | 812 |
| Gouki | Extended airborne kick | 7 / 7 | 489 | 989 |
| Ken | Rising with fists raised | 36 / 37 | 613 | 837 |
| Tabasa | Raised arm and billowing garment | 35 / 35 | 965 | 1,230 |

Felicia's 32×32 source is an exact clockwise quarter-turn of her previously reviewed roll. Rotating the reconciled colour indices gives the same result at all 1,024 positions. The other drawings use source-bound material masks. The Japanese Saturn references show Gouki's dark gi and bare foot, Ken's red gi and blond hair, and Tabasa's dark cape and light garment. For Tabasa, the Saturn C-button sample at hold 24 shows the raised-arm silhouette. Reference inputs and animation durations differ between ports.

## Build and verification

Start from the T75 stage 1 table. Export the four source manifests in contexts 0, 1, 3 and 4 with `tools/mock/roster_table.py --family air-transitions --accept-reference-tiles`. For character contexts, include that fighter's protected source manifests through T74. Build the last table with the normal game inputs.

```sh
PF_CLASS_SHARDS=work/T76/tables/4 PF_HYBRID=1 PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py T76.ws --img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock python -m unittest discover -s tests
```

Use `tools/verify_roster_output.py --family air-transitions` on the new labels and cartridge-specific captures. The four drawings matched LCD and colour RAM in 15 native samples. Each representative also matched staged and published source graphics. The four full-screen pairs had zero changed pixels outside P1. Felicia and Ken use adjacent input holds in the preview to align the native poses.

- The catalogue grew from 8,617 to 8,760 records. The complete bank comparison reproduced the ROM from T75 by replacing the colour tables, their prefix indices and the cartridge checksum. Earlier output was retained for 339 drawings across 1,566 samples and 38,956 fighter tile uses.
- All ten T75 cold-boot screenshots, five graphics-memory checkpoints and fifteen fixed-input Gouki scanout screens matched. The twelve-fighter controls, seven approved wrist drawings, five Ryu dash drawings and restored Ryu hold-24 screen passed.
- Two table exports and builds, both original/T75 IPS paths and both xdelta paths reproduced SHA-256 `982154f6267b665396aaadfd584cc8c63bc6f8be1a0e28d2cfbcecb6996fcc30`. All 103 tests passed. The 17 delivered states restored in a fresh Mednafen session.

Additional unsampled moves, final visual approval and physical WonderSwan timing remain open.
