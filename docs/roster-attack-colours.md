# Standing attack colours for Ibuki, Sakura and Morrigan

T66 builds on T65. Four fighters were sampled using the two WonderSwan standing attack inputs. Actual Saturn training captures supplied references for Ibuki’s mask and clothing, Sakura’s uniform and shoes, and Morrigan’s hair, clothing and transforming wings. The steel surfaces on the wide blade and drill use white, grey and dark outline swatches from Morrigan’s existing palette.

| Fighter | Newly coloured drawings | Verified T66 samples | Representative visible pixels | Pixels recoloured across the paired drawings |
| --- | ---: | ---: | ---: | ---: |
| Ibuki | 2 | 9 | 1,396 | 529 |
| Sakura | 2 | 12 | 1,540 | 671 |
| Morrigan | 6 | 23 | 6,003 | 4,312 |

The source manifest requires exact registration, HUD identity and stop receipts. The ten selected bodies also agreed with the game’s staging copy and had complete visible composition. All visible tiles in three other Chun-Li captures already had retained output, including the protected fallback tiles. The per-fighter table preserves previously registered materials when different poses share tile bytes.

## Build and verification

The exporter and native verifier both accept the family `roster-attacks`. Start with the T65 table in context 0 for Ibuki and Sakura. Pass that output and its fallback to the second export for Morrigan in existing context 2. The latter uses the retained actor-source manifests from T51–T59, T62 and T64. Build the Korean hybrid ROM with the final context-2 directory as `PF_CLASS_SHARDS`.

The result adds 179 canonical records and 129 Morrigan variants. All earlier explicit and protected fallback outputs were retained. Checking 16,909 recorded P1 tile uses reproduced the previous output across 215 drawings and 688 samples. The ROM bytes outside the table blobs and checksum matched T65. A second complete export and build, and both the original- and T65-based IPS patches, reproduced SHA-256 `ad6be8476d72d8237469b95359187364f168bed545408b1b69f90269c4745016`.

Cold-booted T66 sessions reproduced all ten drawings. The actual colour buffer, fighter identity and visible screen matched for 44 samples. Each of the ten paired screenshots was pixel-identical outside the player. The twelve-fighter check covered 11,155 representative visible pixels, the seven earlier wrist drawings covered 6,504 pixels, and all five T64 Ryu poses passed. Ryu’s full hold-24 screen reproduced on state restore. For the historical Morrigan label `36456a50`, both live T65 and T66 matched the retained T53 reference. An earlier T52 label differs by 156 pixels.

Nine cold and follow-up screenshots matched T65 exactly. The first battle screenshot differed by eight pixels with matching sampled graphics buffers. All four subsequent captures matched. The 102 repository tests passed, and the 23 T66 states in the local review package restored in Mednafen. This evidence covers the sampled moves on the emulator. The entire move lists, cartridge timing and the lower VRAM font allocation remain open.
