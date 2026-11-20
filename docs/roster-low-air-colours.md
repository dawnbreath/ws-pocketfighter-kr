# T54: observed roster crouch and air colour batch

This review candidate adds 50 exact source-bound drawings across the other ten
fighters. It reuses T53's CTB4 runtime and the existing twelve palettes. It does
not complete every action, strength, facing or final art approval.

## Completion checklist

| Unit | Result and evidence | Remaining scope |
| --- | --- | --- |
| Prepare compatible real sources | Ten native source routes, 360 sampled situations; 101 new coherent drawing hashes observed. Of 53 selected material proposals, 50 have complete required opaque-source coverage. | Sakura one low kick and Tabasa two familiar-bearing composites have genuinely unobserved opaque pixels; held explicitly. Other 48 observed hashes are unregistered, not declared unused or completed. |
| Connect the colour batch | 50 drawings exported, built and connected using existing CTB4. All 2447 parent canonical records, 753 fallback references and 37 Gouki variants preserved. | Art approval and unregistered drawings remain. |
| Verify actual insertion and regression | 50 drawings / 42,996 representative visible+RAM pixels / 158 zero-offset samples; no missing registered drawings. Previous 60 drawings' 290 certified samples retain identical P1 outputs in 7327 tile comparisons (1254 context/source pairs). Runtime bytes and all twelve palettes unchanged. | Offline preservation of old samples is not a fresh native replay of every old move. Earlier hardware/font-VRAM limits remain. |
| Preserve a reproducible handoff | Original/candidate, IPS, matching states, tables, source/native captures, references and hashes retained in the private restart archive; draft PR targets T53. | Game data stays outside Git; no self-merge. |

| Fighter | Added drawings | Source scope |
| --- | ---: | --- |
| Ryu | 6 | crouch, low kick/punch, jump and air kick |
| Ken | 6 | crouch, low kick/punch, jump and air punch |
| Dan | 6 | crouch, low kick/punch, jump and air kick |
| Sakura | 5 | crouch, low punch, jump and air kick |
| Gouki | 8 | observed crouch, low attacks and air sequence, context 1 |
| Morrigan | 4 | crouch, low attack and air sequence |
| Lei-Lei | 2 | observed crouch and jump-protocol takeoff drawing |
| Felicia | 5 | crouch, low attacks and air attacks |
| Tabasa | 2 | body-only crouch and jump-protocol drawing |
| Ibuki | 6 | crouch, low attacks and jump sequence |

## Source and material handling

Sources come from T53's own states and ROM, with zero-offset actual screenshot
registration and fighter HUD identity. Separate fresh T54 cold boots create its
native test states; cross-ROM state substitution is not used. Input protocol
names alone do not prove an animation's full action coverage. Only exact hashes
in `tools/mock/roster_low_air_colours.py` enable a recipe.

The retained actual Saturn portraits and full-body miniatures are material
references in different poses. WS silhouettes, transparency and shade values
are preserved. Enlarged source-grid review separates Morrigan face/hair, Felicia
face/fur, Tabasa hat/robe and Sakura shirt/gloves. Earlier accepted Chun-Li and
Zangief data are preserved. Final NPZ labels reflect immutable prior tile outputs
and explicitly ordered exact-source donors; native agreement checks insertion,
not aesthetic approval. No nearest-pose inference or broad smoothing is used.

Canonical nine-fighter export and Gouki context-1 export form one connected
batch. The existing context exporter freezes 315 retained Gouki source tiles
before adding its new outputs. Both stages retain inherited variants and
mandatory canonical rows. Final table: 3467 physical records, 3310 canonical
and 157 Gouki variants, plus 1033 protected fallback references. The largest
partition has 246 of 1091 slots. No assembly, palette, VRAM or ROM-size change.

The three held drawings are recorded by exact source in private
`T54-initial-preflight.json`: Sakura's selected low-kick source has two unseen
opaque pixels; the two Tabasa composites involve ten source tiles with unseen
opaque pixels. The final selected manifest has zero such missing pixels. This
is a concrete visibility limitation, not evidence that these frames are unused.
The Felicia curled transformation and Tabasa aircraft/familiar composite are
not extrapolated into body colour recipes.

## Reproduction from the private archive

Use fresh output directories and the archive's source commit. The first
manifest contains the 42 canonical drawings; the second contains Gouki's eight.

```sh
python tools/mock/roster_table.py work/T54-source-0.json \
  work/T53-table work/T53-table/fallback work/T53.ws work/T54-canonical-new \
  --family low-air --accept-reference-tiles
python tools/mock/roster_table.py work/T54-source-1.json \
  work/T54-canonical-new work/T54-canonical-new/fallback work/T53.ws work/T54-new \
  --family low-air --context 1 --accept-reference-tiles \
  --protect-manifest work/T51-source-manifest.json \
  --protect-manifest work/T52-source-manifest.json \
  --protect-manifest work/T53-source-manifest.json
# Keep both stages' label/provenance files; final table uses stage two.
PF_HYBRID=1 PF_CLASS_SHARDS=work/T54-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T54-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_sharded_colour_table test_fighter_palettes test_contact_composition
```

Candidate SHA-256:
`4d4b5d799ffe8a0c12b6b00650ad1b2146e5f5b278fe1ac278d7a413a32ac478`.
Thirteen focused tests pass. Fifty registered source hashes, alpha and index
bounds pass; an unknown drawing is rejected. Public-recipe re-export reproduces
every table/fallback/label byte, and its rebuilt ROM equals the native candidate.
Original IPS roundtrip and checksum pass. Native harnesses and scripts are kept
privately; adapt installed emulator paths and use fresh output directories.

## Native results and limits

All 50 drawings pass actual 4bpp buffer and zero-offset screenshot checks:
42,996 representative pixels in 158 matching samples. The initial replay
verified 47 drawings; neighbouring-duration captures for Ken and Morrigan
verified the remaining three without changing the ROM. A total of 146
incoherent/offset samples are excluded from the drawing proof. Gouki's eight
new drawings separately require actual context 1: 6536 pixels / 21 samples,
with 15 excluded samples in that subset.

Old Chun-Li four and Zangief three idle drawings pass in the actual candidate:
2721 + 3783 = 6504 representative pixels. All twelve selection screens and five
cold title/menu/story screens are pixel-identical to T53. Initial cold battle
has a 32-pixel scanout exclusion: OAM, 2bpp VRAM, staging, 4bpp RAM, palettes
and sprite start/count are identical. Subsequent 1, 2, 4 and 8-frame fullscreens
are pixel-identical. This is bounded timing evidence, not calibrated hardware
proof or a claim that the initial screenshot is identical.

The actual comparison PNG contains visible P1 screenshot pixels only;
occluded pixels are omitted, and Saturn panels are different-pose material
references. No complete hidden-art or all-mode coverage is claimed. Native
Gouki P2, simultaneous mixed-owner aliases, physical hardware timing, all-mode
RAM lifetime, remaining translation and font-VRAM requirements remain open.
