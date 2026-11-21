# Standing attacks and recovery for five more fighters

T67 continues the standing A/B input survey on T66. The eight remaining fighters each received both inputs at ten durations. Of 160 captures, 76 showed an isolated, registered, staging-coherent player. These yielded 46 distinct drawings. Eleven contained new visible source tiles. Gouki, Tabasa and Zangief had seven, seven and six stable drawings respectively, all covered by previous colours.

| Fighter | Newly coloured drawings | Verified T67 samples | Representative visible pixels | Recoloured pixels |
| --- | ---: | ---: | ---: | ---: |
| Dan | 3 | 23 | 2,419 | 1,496 |
| Felicia | 3 | 39 | 2,834 | 2,041 |
| Ken | 3 | 29 | 2,605 | 1,655 |
| Lei-Lei | 1 | 3 | 1,133 | 1,080 |
| Ryu | 1 | 1 | 624 | 387 |

Materials were checked against separate Saturn training captures. Dan’s raised foot remains exposed above his pink gi. Ken’s extended punch distinguishes the wrist wrap and bare fingers. Felicia’s rear-facing movement separates her blue mane and white tail. Lei-Lei's turning pose uses her two yellow hat decorations, white claws and gold cuffs. Ryu uses his existing white gi, red headband and red gloves.

## Reproduce the candidate

Export Dan, Felicia, Lei-Lei and Ryu in context 0 against the final T66 table. Then export the three Ken drawings in context 4 against the first pass, preserving the earlier source manifests from T51–T59, T62, T64 and the T65 canonical pass. The existing owner byte in each replicated fighter row selects Ken. The copier and OAM code are identical to T66. Both command-line tools accept the family `attack-recovery`. The manifest records the T66 source frame, pose hash and stopping receipt. The private capture directories and ROM are required for replay.

```sh
python tools/mock/roster_table.py MANIFEST T66_TABLE T66_TABLE/fallback T66.ws CANONICAL --family attack-recovery --context 0 --accept-reference-tiles
python tools/mock/roster_table.py KEN_MANIFEST CANONICAL CANONICAL/fallback T66.ws T67_TABLE --family attack-recovery --context 4 --accept-reference-tiles --protect-manifest PRIOR_MANIFEST
PF_HYBRID=1 PF_CLASS_SHARDS=T67_TABLE PF_FIGHTER_PALETTES=data/palettes/roster.json python tools/build.py T67.ws --img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/verify_roster_output.py CANONICAL/labels CAPTURE_ROOT data/palettes/roster.json OUTPUT --family attack-recovery --additional-capture ATTACK_CAPTURE
```

Repeat the protection option for each retained source manifest. Verify CANONICAL/labels for context 0. For the three Ken drawings, verify T67_TABLE/labels with --require-context 4. Supply each relevant capture directory with --additional-capture.

## Native output and compatibility

95 registered native samples, 9,615 representative visible pixels and 6,659 recoloured pixels. All eleven paired screens match exactly outside P1. The twelve-fighter control covered 11,708 representative pixels. The four Chun-Li wrist drawings, three Zangief wrist drawings and five earlier Ryu poses passed. Ryu’s complete hold-24 LCD frame reproduced from a separate restore. Nine cold and follow-up screens matched T66 pixel for pixel. The first battle screenshot differed at eight pixels, with identical sampled graphics buffers. The next four screens matched exactly.

The first candidate shared four finger tiles with Ryu’s red gloves and Gouki’s hand. This mapped 122 of the 128 marked finger pixels to Ken’s brown wrap. In the final build, all 128 fit his skin ramp. Context 4 adds 61 Ken variants. The canonical catalogue grew by 196 entries and the other three actor-specific tables retained every entry. Opponent Ken was independently identified by his P2 HUD. In 91 samples his slot ownership, native 4bpp and visible LCD colours matched. One sample showed 540 visible pixels that specifically used his selector. A check of 18,056 recorded player tile uses across 225 prior drawings and 732 samples reproduced their previous outputs. All bytes outside the colour table blobs, the replicated Ken row selector and the cartridge checksum matched T66. The T65 movement manifest still rebuilds in its original three passes. Rebuilding T66 also reproduced its previous ROM hash. Independent exports and builds and both IPS paths reproduced the candidate SHA-256 `c79f909405d6d77d657f3c2418dcf8c9b5905e6f04c7cdfe5deb2fa7412d8533`. All 102 unit tests passed. All 25 candidate save states restored in Mednafen, including the second-player Ken scene. The scope is the sampled standing inputs. Additional moves and original-hardware timing remain unverified.
