# T51: basic colour drawings for the remaining ten fighters

Previously only Chun-Li and Zangief had registered material palettes. This batch
connects the other ten palettes and 35 exact basic-stance drawings to the T50
partitioned lookup. Actual Saturn selection screens supply the portrait and
animated full-body material references for all twelve fighters. These references
are not combat-frame or cross-platform pixel equivalence claims.

| Fighter | New drawings | Native representative pixels | Passing samples |
|---|---:|---:|---:|
| Ryu | 2 | 1455 | 5 |
| Ken | 3 | 2260 | 10 |
| Gouki | 3 | 2328 | 8 |
| Dan | 3 | 2195 | 11 |
| Sakura | 4 | 2783 | 6 |
| Morrigan | 7 | 7095 | 19 |
| Lei-Lei | 7 | 5757 | 12 |
| Felicia | 1 | 941 | 2 |
| Tabasa | 2 | 2249 | 5 |
| Ibuki | 3 | 2379 | 5 |
| Total | 35 | 29442 | 83 |

## Authoring and source classification

All twelve WS selection routes are identified from native HUD-name hashes. Tabasa
and Ibuki finish drawing their names later, so their identity is confirmed from
the ready-state samples. Own-ROM selection states replace repeated cold boots.
Early neutral cohorts separate stable stances from entry animations, transformations,
effects and damage. Unregistered drawings are retained in the private inventory;
they are not called unused or complete.

`mock/roster_colours.py` defines material polygons only for the 35 registered
source hashes. It changes no outline or transparent pixel. New palettes use the
Saturn material families: white/red Ryu, red/blond Ken, dark gi/red-haired Gouki,
pink Dan, white/navy/red Sakura, mint/purple Morrigan, blue-skinned Lei-Lei,
white-furred/blue-haired Felicia, wine/white Tabasa and brown Ibuki. These are art
review candidates. Existing Chun-Li and Zangief colours are unchanged.

`mock/roster_table.py` projects those regions onto exact 16-byte source tiles.
Identical source tiles reuse explicitly ordered observed donors, never a predicted
nearby pose. The earlier 1,013 stored outputs and 436 fallback outputs are immutable.
The initial polygons encounter 368 constrained tile cells across the family; their
ordered-donor resolution adjusts 638 drawn pixels in total. Six original drawing
pixels also meet retained old outputs. Donor acceptance is explicit through
`--accept-reference-tiles`; without it, the exporter rejects before writing output.
Final constrained label files are saved separately for native verification.

There are 517 new source keys: 463 need stored outputs and 54 equal the existing
fallback. Final storage is 1,476 records; the cumulative fallback reference contains
490 keys. All partitions retain the old two-palette footer. The twelve-character
catalogue changes only registered palette pointers/data, with neutral fallback and
both previous fighter palettes preserved. Runtime code is byte-identical to T50.

## Reproduction

Game-derived manifests, source captures, labels, tables, images, ROMs and states
stay in the private restart package. The source manifest binds completed/stopped
T50-ROM captures; the runtime check uses independent T51-ROM captures and states.
Never load a source ROM's state into a different candidate.

```sh
python tools/mock/roster_table.py work/T51-source-manifest.json \
  work/T50-shards work/T49-final-table/fallback.ctb3 work/T50.ws \
  work/T51-table --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T51-table \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
python tools/build.py work/T51.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python work/T51_static.py
python tools/verify_roster_output.py work/T51-table/labels \
  work/T51-native-roster data/palettes/roster.json work/T51-native-check \
  --additional-capture work/T51-gouki-followup \
  --additional-capture work/T51-dan-followup \
  --additional-capture work/T51-morrigan-followup \
  --additional-capture work/T51-morrigan-second-followup \
  --additional-capture work/T51-leilei-early-followup \
  --additional-capture work/T51-leilei-late-followup
python work/T51_old_qa.py
```

Capture tools now accept all twelve fighter identifiers and use the configured
neutral palette for an unregistered fighter. The existing capture protocol and
strict native source checks remain unchanged.

## Completion evidence and remaining work

1. Capacity and preparation: T50's sixteen-partition engine is connected, all
   twelve identities/reference screens are acquired, and the 35-drawing basic
   batch is classified and exported. Other actions remain in the inventory.
2. Authoring and insertion: all ten additional palettes and the 35 drawings are
   installed. Table readback, old explicit/fallback preservation, palette pointers,
   code equivalence, checksum and original-to-candidate IPS round trip pass.
3. Native verification: all 35 drawings and 29,442 representative visible/RAM
   pixels pass in 83 zero-offset samples. Forty-eight source/display timing
   samples are excluded; another 48 samples are outside this recipe family.
   Existing Chun-Li's four idle drawings/2,721 pixels and Zangief's three idle
   drawings/3,783 pixels pass. Ten selection fullscreens match T50 exactly.
   Every partition, fallback reference and all 35 final label files reproduce
   byte for byte. Four existing emitted-palette/catalogue tests pass; T50's
   runtime code is unchanged and its 24-test evidence remains separate.
4. Restart handoff: original/current/source ROMs, IPS, matching states, fonts,
   recipes, original/derived source manifests, Saturn references, actual screen
   comparisons and receipts are included in a verified private backup.

This completes a basic-stance batch for all twelve characters, not all moves.
Other walking/attacks/guard/damage/specials can still show unseparated materials
through the existing fallback. Owner art review, further observed drawings,
all-mode/real-hardware timing and earlier translation/font-VRAM limits remain.

ROM SHA-256: `ea2fe0947d4ac19a388fb9e88fdffe2a2adf49a101a750c01927e33dee0a631b`.
