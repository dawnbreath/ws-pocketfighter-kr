# T19: direct Saturn reference and proposal QA

This is reference evidence and an offline classifier fix, not a completed colour patch.

## Reference provenance

The owner supplied the Pocket Fighter (Japan) disc archive and a 512 KiB
`Sega Saturn BIOS v1.01 (Multi Region)(J).bin`. The disc identifies itself as
`T-1230G`, `POCKET FIGHTER`, region `JT`; Mednafen selects the 4 MiB expansion cart.
Archive SHA-256: `0d371c7fff54cdf7b704531cca0091e826ace335c2fe8e1d76a3d0e1033fd03f`.
BIOS SHA-256: `785c67183e8934f46929171b576648f50ce38f19e151e48d193c08bb32cd15e2`.
Emulator: emucap 1.0.0 Mednafen package, upstream 1.32.1;
binary SHA-256 `920e59a239f2fcd5610cf67d135a67ab5adff65e0fdce6a15e7b6ca98a80b328`.

The supplied multiregion BIOS differs from Mednafen's expected stock BIOS hash.
Only the isolated Saturn reference profile uses `ss.bios_sanity 0`; the BIOS
bytes were not patched. All 35 tracks are extracted from the supplied archive,
and the original CUE is loaded through emucap's reviewed media manifest.
Fresh internal RAM was selected; this does not overwrite any existing save.
ROM, BIOS, screenshots, model seeds, masks and savestates remain local.

Cold-boot route: choose internal RAM, wait through initial loading, Start,
Battle Select → Training (Down three times, A). At Player Select, Down/Left
from Ryu selects Chun-Li; A selects her default colour. From opponent Ken,
Down twice selects Zangief; A selects his default colour. After loading, confirm Training Start with A.
Emulator frame-step requests and screenshot receipts are retained locally;
they do not establish matching animation frames across the two platforms.

## How the reference is used

Compare semantic regions in a matching action/default costume before RGB.
Saturn and WonderSwan differ in sprite geometry, resolution and available
palette groups; screenshots must not be treated as pixel-aligned masks.
Transformation costumes, hit flashes, effects and alternate colours need their
own references. Printed box screenshots and promotional illustrations are
secondary references, not direct Saturn framebuffer captures.

Local Codex proposal sheets contain the 20 most frequent captured poses each:
Chun-Li 192/256 samples, Zangief 182/256. These are flat semantic proposals
trained with partial provisional Codex marks, not Claude's unseen approved
seed/prediction files and not final shaded ROM screenshots. Missing semantic
classes cannot be recovered simply by increasing classifier confidence.

## Concrete classifier correction

`predict_proba(...).argmax(1)` returns a column index, not the original class ID.
When seeds contain classes 2 and 8, the old prediction path saves 0 and 1.
The corrected path indexes `clf.classes_`, retaining 2 and 8. A real random
forest regression test exercises the prediction helper used by the CLI.
This fixes corrupted class identities; it does not fix semantic misclassification.

Verification: `python -m unittest discover -s tests -p test_proto_class_ids.py`
passes (one test). No ROM code or production table changed.

Remaining: top-20 per-pixel reviewed error records, corrected training marks,
held-out before/after measurements, broader action captures, exact-source-safe
engine table integration and runtime colour regression. No T19 acceptance or
4bpp/VRAM safety gate is claimed here.

## Direct framebuffer comparison (first spot checks)

Captured both fighters together in Saturn Training, then Chun-Li jumping and
attacking. Default costume confirms bare hands/arms and brown trousers for
Chun-Li; bare fists/thighs and red trunks/boots/wristbands for Zangief.
The local WonderSwan proposals have four explicitly reviewed incorrect points:
Chun-Li frame 0 hand and trouser leg predicted cloth (votes .765/.565), and
Zangief frame 1 thigh and fist predicted trunks (votes .965/.525).
These are Codex's partial-seed reproduction, not an assertion about Claude's
unseen 661-tile table. Vote confidence is demonstrably not correctness.

Four fingerprint-bound pixel marks were applied through `apply_marks`; all
four now have the expected class and all other label pixels remain unchanged.
This is a spot correction, NOT a retrained model or held-out convergence result.
Exact coordinates, pose fingerprints, before/after arrays, errors and marks
remain in ignored `work/{chunli,zangief}-qa/reference-*.json` locally.
The Saturn idle savestate and capture receipts remain with the local reference
runtime; they are not interchangeable with WonderSwan saves.

## T19 round 1: approved seed reproduction and pose-disjoint boot checks

Claude's `seed_recipe.py` now reproduces the supplied seed contract locally:
Chun-Li pose 1 (677 pixels), Zangief pose 5 (1269 pixels). The recipe is reported
by Claude as within two pixels of the owner-approved Chun-Li mock; this round
uses the recipe as the baseline, not an independently verified exact original.
Its outline-majority tie used set iteration order: Python hash seeds 1 vs 2
changed five Chun-Li boundary labels. Sorting tied labels makes regeneration
stable (three hash seeds now give the same pickle SHA-256
`d1edca631cb77cf9c0d465ef053d5827392b1a299b3becf8d6406b746f145b2f`).
Alphabetical tie-breaking is reproducibility policy, not a semantic correction.

`tools/mock/review_round.py` runs the approved baseline and corrected forest,
exports all-pose local predictions, and produces shaded before/after sheets for
the top 20 poses. Shading is a diagnostic preview, not hardware palette output.
The built-in source-only `reference` recipe binds boot-interior annotations to
exact normalized pose hashes. No game graphics, arrays or masks are in git.

| Fighter | Added training points | Evaluation pose (capture frame) | Held-out points | Wrong before → after |
|---|---:|---|---:|---:|
| Chun-Li | 66, high-kick boot (frame 39) | airborne pose (frame 61) | 23 | 12 → 10 |
| Zangief | 18, inverted boot (frame 209) | horizontal pose (frame 214) | 31 | 16 → 15 |

Annotations were inspected against the original WS pose and Saturn default
costume reference. Only non-outline boot interiors were marked; uncertain
boundaries remain unlabelled. Evaluation poses and translation-equivalent
copies cannot appear in training. Metrics describe these 54 reviewed points,
not all pixels or all poses. Small improvements do not justify engine export;
remaining boot errors, clothing boundaries and effects still need review.

Reproduce against the existing local captures (each output directory must be new):

```sh
python tools/mock/review_round.py CHUNLI_CAPTURE.json chunli reference work/chunli-round
python tools/mock/review_round.py ZANGIEF_CAPTURE.json zangief reference work/zangief-round
python -m unittest discover -s tests -p test_review_round.py
```

Each output contains marks/provenance, a per-point expected/actual/vote report,
round-0/1 predictions and both top-20 sheets. The three focused tests cover
training/evaluation pose leakage and deterministic tie behaviour. Original
ROM and Saturn idle savestate remain untouched. No CTB2 table is promoted and
T19/#31 acceptance, PR #27 engine review and full runtime regression remain open.

## T19 round 2: actual jump poses, rejected augmentation, skin controls

A bounded rotation/reflection experiment on the existing training marks made
the reused boot validation worse: Chun-Li 15/23 wrong and Zangief 17/31 wrong,
versus round-1 10/23 and 15/31. It was rejected; no augmentation code enters
the training path. These reused boot checks are now model-selection validation,
not an untouched held-out estimate.

The `reference-jump` source-only recipe instead adds actual visible boot
interiors from Chun-Li frame54 (36 points) and Zangief frame187 (28 points).
Exact normalized-pose hashes bind all coordinates. It preserves the original
`reference` recipe and the same forest algorithm. Two new distinct evaluation
poses (frame4 for each fighter) check 13 Chun-Li face and 20 Zangief shoulder
skin points; neither pose is used for training.

| Checks | Approved-seed baseline | Round 1 | With actual jump marks |
|---|---:|---:|---:|
| Chun-Li boot, 23 validation points | 12 wrong | 10 wrong | 4 wrong |
| Zangief boot, 31 validation points | 16 wrong | 15 wrong | 15 wrong |
| New skin controls, 33 points | 0 wrong | not measured | 0 wrong |

Within the original boot checks, six additional Chun-Li errors were fixed and
no formerly correct checks regressed. Zangief did not improve further. These
87 checked points do not certify the full top-20 sheets, whole-pose masks, new
actions or game runtime. No CTB2 table was promoted. The saved Saturn reference
state and source ROM are unchanged.

```sh
python tools/mock/review_round.py CHUNLI_CAPTURE.json chunli reference-jump work/chunli-jump-round
python tools/mock/review_round.py ZANGIEF_CAPTURE.json zangief reference-jump work/zangief-jump-round
```

Both connected runs produced before/after top-20 sheets and per-point reports.
Training sizes are 779 Chun-Li and 1315 Zangief pixels (three poses each).
Three split/tie tests pass; the six existing CTB2 format/assembly tests also
pass on the engine branch. The engine review separately found first-call
ownership dependent on uninitialized FIGHT: with equal staging/old 2bpp but
an invalid 4bpp mirror, nonzero FIGHT skips conversion. This was reproduced
using actual assembled cphook, reported on PR #27, and is not a claim of an
observed retail-game failure. Engine initialization and lifetime proof remain
Claude's open work; this PR changes only offline review data/metadata.
