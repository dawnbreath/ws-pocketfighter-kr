# Ryu’s five movement drawings after the repaired transition

T64 adds colour to five complete Ryu drawings on the T63 Ryu–Ibuki route. The new sources were captured with both fighters present on the WonderSwan LCD. A separately operated Saturn training match supplied the white gi, red hand wraps and headband, black belt, bare shoulders and feet. The two ports have different animation timing.

The crouching drawing shares its entire body with a registered T54 Ryu pose. The 27 × 34 sources differ in 33 cells, all within the swinging headband. The recipe reuses the earlier body regions and supplies the new headband tip. The other four drawings use their own coordinates. The exporter retained earlier outputs at 25 proposed cells across the five drawings.

## Verification

| Drawing | T63 input hold | T64 input hold | Changed LCD pixels inside Ryu | Changed pixels outside Ryu |
| --- | ---: | ---: | ---: | ---: |
| First complete transition | 24 | 24 | 355 | 0 |
| Crouch with trailing headband | 27 | 28 | 76 | 0 |
| Following movement | 29 | 30 | 422 | 0 |
| Returning stance | 35 | 36 | 389 | 0 |
| Following stance | 39 | 40 | 401 | 0 |

All five paired samples have byte-identical OAM and monochrome VRAM. The T64 4bpp output and its LCD colours agree on 3,475 representative Ryu pixels across eight matching samples. Eight other timing or registration samples were excluded. On the same input as the T63 fix, T64 hold 24 already displays the complete coloured body.

All 12 player characters were independently selected on T64. A HUD identity check, registered source, runtime colour buffer and exact LCD match passed for each. The representative drawings cover 10,507 visible pixels across the roster. There were 75 matching samples, including the representative ones. The four Chun-Li and three Zangief wrist controls separately passed on 6,504 visible pixels. The twelve representative game states, five new Ryu pose states and Ryu’s input state were restored in fresh emulator launches. Replaying the input state reproduced the full T64 hold-24 screen.

The original-to-T64 and T63-to-T64 IPS patches both reproduce the same 4 MiB ROM with SHA-256 `46f2c3a939650ac08b8f0d8df8ad2139a7ea26bde2181aadf47be9189b4aca57`. Re-export and a second build produced the same bytes. The 69 new canonical records bring the runtime table to 5,041 records. The previous 4,613 canonical outputs, 1,440 fallback references and 359 actor variants are retained. Checks on 636 earlier samples cover 195 drawings and 15,722 P1 tile uses. ROM bytes outside the colour tables and cartridge checksum match T63.

Nine of ten cold and follow-up screens match T63 exactly. The first battle screenshot has an eight-pixel difference, with identical sampled OAM, staging, both mirrors and palettes. The next four screenshots match. The 30 focused composition, alignment, table, context and palette tests pass.

To regenerate, use the source route in `docs/ryu-frame-timing.md`. Capture left holds 22 through 40 from the T63 input state with settle zero. Use T63 source holds 24, 27, 29, 35 and 39, in this order. Export and verify the `ryu-movement` family against the T62 tables used by T63. The source and output hashes in the local captures identify their respective cartridges. Wider moves and physical hardware timing remain open.
