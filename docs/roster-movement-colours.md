# Six fighters’ movement colours

T65 colours fifteen drawings captured on T64. The movement input was a four-frame direction tap, four frames of release, then a held direction. The Saturn training comparisons cover Ken’s red gi and blond hair, Dan’s pink gi, Felicia’s blue mane and white fur, Lei-Lei’s cap and sleeves, Gouki’s hair and gi, and Tabasa’s hat and cloak.

| Fighter | Drawings | Matching T65 samples | Representative visible pixels |
| --- | ---: | ---: | ---: |
| Ken | 2 | 6 | 1,501 |
| Dan | 2 | 2 | 1,284 |
| Felicia | 3 | 11 | 2,748 |
| Lei-Lei | 2 | 7 | 1,688 |
| Gouki | 5 | 12 | 3,860 |
| Tabasa | 1 | 6 | 1,086 |

## Source and insertion

Source selection required the correct HUD, a complete body, exact screenshot registration and agreement between the fighter’s staging and monochrome tiles. A Gouki source at right hold 24 was still in transition. Hold 22 supplied the same drawing with matching buffers. The Felicia drawing at left hold 30 also mixed two updates. The next hold supplied a distinct, complete pose. Previously coloured bodies appearing behind opponents were identified through isolated composition.

The exporter and native verifier accept the family `roster-movement`. Export the four canonical fighters with context 0 using the T64 tables. Then export Gouki with context 1 and Tabasa with context 3 against the preceding export. For actor-specific exports, supply the retained source manifests through T64. The same actor selectors and palettes were already active in T64.

T65 adds 223 canonical entries and 88 actor variants, bringing the total to 5,352 entries. The T64 canonical entries, fallback references and actor variants retain their outputs. A separate replay of 15,872 earlier P1 tile uses across 200 drawings and 644 stored samples also matched. All ROM bytes outside the sharded tables and cartridge checksum matched T64.

## Native verification

Independent T65 cold boots reproduced all fifteen drawings. Each representative sample matched the 2bpp staging composition, actual 4bpp buffer and visible LCD pixels. The 44 verified samples cover 12,167 representative visible pixels. Across fifteen paired captures, 7,257 pixels inside P1 changed. Ten pairs were exact outside P1. In the other five pairs, 5, 19, 31, 35 and 172 pixels differed outside P1. All five had identical sampled opponent 4bpp tiles and monochrome VRAM; one pair had different OAM.

The twelve-fighter regression covered 10,787 visible pixels on twelve representative drawings. The earlier four Chun-Li and three Zangief wrist drawings passed on 6,504 pixels. The five T64 Ryu poses passed and the full hold-24 Ryu screen reproduced after a separate state restore. Nine cold and follow-up screens matched T64 exactly. The first battle screenshot differed by five pixels with identical sampled graphics buffers; the next four screens matched.

The original-to-T65 and T64-to-T65 IPS patches both reconstruct a 4 MiB ROM with SHA-256 `a5c738c1301c678ca1a4cbda555280827f7087d0f23ba44292e59ed06e601bba`. Independent re-export and rebuild reproduced those bytes. The local review package includes fifteen pose states, twelve roster states and Ryu’s input state. All 28 were restored on the T65 ROM. The 30 context, shard, composition, palette and alignment tests passed. Additional actions and hardware timing remain open.
