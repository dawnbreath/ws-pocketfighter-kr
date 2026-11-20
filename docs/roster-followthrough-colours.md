# T55: remaining captured crouch/air follow-through colours

T55 connects 44 further exact source-bound drawings from the existing T54
source cohort. Thirty-six require additional exact-source colour data; eight
use already-coloured tile combinations and receive native composition checks.
This is a review candidate, not a claim of complete game/action coverage.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Classify remaining captured drawings and source coverage | All 48 previously unregistered hashes classified: 44 selected with zero missing required opaque-source pixels; four explicitly held. Existing source captures reused. | Head-occluded Ken one; Sakura two with unseen opaque source pixels; Tabasa aircraft/familiar one without matching material evidence. Prior T54 three holds remain. |
| Connect compatible colours while preserving old outputs | 44 drawings connected through existing CTB4. All 3310 prior canonical outputs, 1033 fallback references and 157 Gouki variants preserved. No engine, palette, ROM-size or VRAM change. | Art approval and seven total held cohort drawings remain; none is declared unused. |
| Verify native output and required regression | 44 drawings / 35,268 representative visible+RAM pixels / 77 zero-offset samples, missing[]. Earlier 110 registered drawings / 448 certified samples retain actual P1 outputs offline in 10,800 tile comparisons (2298 context/source pairs). | Offline preservation is not a fresh native replay of every earlier action. |
| Retain own-ROM states/restart backup and draft PR | Original/candidate ROMs, IPS, matching states, source/native captures, material references, report hashes and rebuild inputs in private restart archive; draft PR targets T54. | No game data in Git and no self-merge. |

| Fighter | Newly registered drawings | Existing-colour combinations within that count |
| --- | ---: | ---: |
| Ryu | 10 | 3 |
| Ken | 8 | 2 |
| Dan | 9 | 0 |
| Sakura | 12 | 3 |
| Morrigan | 4 | 0 |
| Felicia | 1 | 0 |
| Total | 44 | 8 |

The observed cohort now has 94 registered drawings (T54 50 + T55 44) and seven
held hashes, accounting for all 101 previously observed coherent hashes. This
counts drawings, not complete moves, and does not cover unobserved frames,
strengths, facing, contacts, effects or modes. Gouki, Lei-Lei and Ibuki's already
registered cohort drawings need no new material recipe in this batch.

## Material and source bounds

All proposals are enabled by exact cropped-source hashes, not extrapolation to
unseen poses. Input protocol names establish how a capture was obtained; they
do not by themselves prove action identity. Actual WS silhouettes/shade values
are retained. Actual Saturn portraits and animated miniature captures supply
material references in different poses, not frame-identical animation evidence.

Enlarged source grids distinguish Ryu's extended fist from the bare foot,
Dan's face and wrist/foot boundaries, Sakura shirt/skirt/ribbons from exposed
skin and Morrigan face/hair from wings. Felicia's curled takeoff source visibly
contains the hair, face and forepaws; its exact registered proposal separates
those regions. Its final art approval remains open. Tabasa's aircraft/familiar
is not guessed from body-only colours.

Immutable previous outputs and explicitly ordered exact-source donors take
priority in the exporter. Final NPZ labels describe inserted outputs, including
reported adjustments to proposal regions. Native agreement proves insertion,
not aesthetic correctness. The eight known-source combinations add no new raw
source colour requirement; they are not presented as eight newly painted poses.

Final table: 4030 physical records (3873 canonical and the unchanged 157 Gouki
variants), with 1152 protected fallback references. Largest partition is
280/1091 slots. Existing text hooks, fonts, palettes and colour assembly bytes
are unchanged. No lower-two-thirds font-VRAM residency claim is made.

## Reproduction from the private restart archive

Use NASM/Python with numpy/Pillow/fontTools; adapt local emulator paths. Use
fresh output directories and keep savestates with their exact recorded ROM.
The source cohort belongs to T53, while candidate runtime states belong to T55.
Do not substitute cross-ROM states.

```sh
python tools/mock/roster_table.py work/T55-source-manifest.json \
  work/T54-table work/T54-table/fallback work/T53.ws work/T55-new \
  --family followthrough --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T55-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T55-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_sharded_colour_table test_fighter_palettes test_contact_composition
```

Candidate SHA-256:
`8e2cfe9641db6413ef6a8b7472fd192428555779404735cd40f9623539618770`.
Thirteen focused tests pass. Forty-four exact source hashes, transparency and
index ranges pass; an unknown drawing is rejected. Public-recipe re-export
matches all 79 table/fallback/label/provenance files; rebuilt ROM equals the
candidate. Original IPS roundtrip, checksum and replicated-bank checks pass.
Native harnesses, stop receipts and restoration notes are retained privately.

## Native results and limits

All 44 registered drawings pass actual 4bpp memory and zero-offset screenshot
checks: 35,268 representative pixels in 77 matching samples. The first replay
verified 35 drawings. Selected-direction neighbouring-duration captures verified
the remaining nine without modifying the ROM. Sixty-five incoherent/offset
samples are excluded from drawing proof. Earlier output preservation covers all
110 prior registered drawings but is explicitly offline for those retained moves.

Old Chun-Li four and Zangief three idle drawings pass in the actual candidate:
2721 + 3783 = 6504 representative pixels. Eight relevant native selection screens
and five cold title/menu/story screens are pixel-identical to T54. The initial
cold battle has a 15-pixel scanout exclusion despite identical OAM, 2bpp VRAM,
staging, 4bpp RAM, palettes and sprite start/count. Subsequent 1, 2, 4 and 8-frame
fullscreens are exact. This does not prove calibrated hardware timing.

`capture_walk.py --directions` restricts collection to named members of the
selected existing input protocol. It validates the selection once before
launch, preserving default direction lists and per-sample rendering checks.
The missing-case followup uses only 52 samples across Ken, Ryu and Sakura,
instead of repeating every direction for those fighters. Five existing capture
alignment tests also pass (18 focused tests total for this batch).

The comparison PNG contains actual visible P1 screenshot pixels. Before/after
panels match the exact source drawing hash in separate T54/T55 captures;
obscured pixels are omitted. Saturn is a different-pose material reference.
Final art approval, seven held cohort drawings, unobserved moves/strengths/
facing/effects/modes, Gouki P2 native, simultaneous mixed-owner aliases,
all-mode RAM lifetime, physical hardware timing and prior text/font-VRAM work
remain open. No complete hidden-art or all-game completion claim is made.
