# T18: review-only few-shot proposal loop

One command connects pose inventory, explicit seed marks, feature training,
per-pixel vote scores, prioritized review sheets, temporal disagreement records
and source-oriented conflict-preserving masks. NumPy/Pillow only; no new ML
runtime dependency. This is an uncalibrated nearest-neighbor baseline, not a
claim that every pose can be colored correctly from twelve seeds.

```sh
# Without marks: select diverse poses and export numbered review sheets/template.
python tools/propagate_labels.py work/chunli/capture.json work/chunli-seeds
# Fill explicit component/pixel marks with reviewer and existing fingerprints.
OPENBLAS_NUM_THREADS=1 python tools/propagate_labels.py work/chunli/capture.json \
  work/chunli-proposals --marks work/chunli-marks.json --seed-count 12
# After review, rerun to a new output directory with updated marks.
python tools/export_group_masks.py work/chunli/capture.json \
  work/chunli-proposals/masks.json work/explicit-group-map.json work/chunli-pgmd
```

Original capture and saves are untouched. Outputs contain game-derived pixels
and remain in ignored work/. Missing/one-class marks return SEEDS_REQUIRED;
no fabricated all-class labels or one-class certainty. Fingerprints and named
reviewer are mandatory. Explicit `unknown` marks remain abstentions.

## What the model does and does not know

Features: 5×5 shade patch divided by 3, plus x/y within the selected-side bbox.
Up to five nearest labelled pixels vote with inverse mean-squared distance.
Default acceptance: vote >=0.9 and nearest-feature MSE <=0.04. Those constants
are diagnostic thresholds, not calibrated error bounds. Unseen semantic
classes cannot be learned, and a confident answer can still be wrong.

No whole-component majority filter or arbitrary outline inheritance is used.
Thin features require explicit pixel labels; connected components can span
several body parts. Sprite grouping may include effects. Position-normalized
shape grouping is not pose semantics, action recognition or an all-moves census.

- `seed-review/`: translation-invariant unique poses, first representative plus
  greedy diverse 16×16 shape thumbnails; up to 12 candidate frames by default.
- `seed-comparison.png`: source | explicit seed | proposal. This is an inspection
  view, not an independent evaluation of training pixels.
- `least-confident.png`, `uncertain-review/`: distinct poses ranked by rejected
  fraction then mean vote score, with frame IDs and fingerprint-bound templates.
- `probabilities/*.npz`: xy, learned class IDs, normalized votes, nearest MSE,
  final accepted/unknown labels. Scores are not correctness probabilities.
- `report.json`: provenance, seed IDs, timing, rejection counts, same-source-pixel
  label disagreements in consecutive samples. This is not screen-space motion
  tracking. Zero disagreement with sparse predictions does not prove stability.
- `masks.json`: every selected tile key, inverse flips resolved using the same
  projection as segment_frames; contradictory predictions stay unknown. The
  existing exporter omits any tile with unresolved opaque pixels.

`heldout_*` counts exclude ALL translation-equivalent seed poses, not just seed
frame numbers. They measure rejection, not accuracy: there are no reference
labels for those poses. PGMD/1 remains unchanged and has no confidence field;
the bound report/NPZ files carry confidence separately. Do not claim PGMD covers
all observed tiles just because masks.json lists every tile hash.

## Seed recommendation and current evidence

Start by reviewing 12 diverse proposals per fighter, then choose additional
poses by uncertainty. Reviewers should ensure idle, walking, crouching, jumping,
punch/kick, hit/KO and special contexts are represented IF those actions exist
in the capture; the tool does not assign those meanings from frame numbers.
A fixed 8–15-pose count cannot guarantee coverage or thin-feature quality.

On the existing 256-sample original-ROM captures:

| | Chun-Li | Zangief |
|---|---|---|
| Unique translation-normalized poses | 76 | 80 |
| Suggested frame IDs | 0,218,209,199,217,147,151,153,59,206,159,173 | 0,218,214,139,143,114,134,231,189,213,222,208 |
| Local partial seed | frame8 components2 white_trim /4 skin | frame8 components2 skin /36 boots |
| Explicit labelled pixels | 116 | 222 |
| Non-seed-pose opaque pixel observations | 171477 | 272037 |
| Rejected observations | 163575 (95.4%) | 239469 (88.0%) |
| Non-seed-pose frames with rejected pixels | 249 | 224 |
| Tile keys / contradictory tile keys | 640 / 0 | 652 / 1 |
| Runtime (single BLAS thread, this host) | 5.57s | 9.29s |
| Complete PGMD records / omitted | 0 / 640 | 1 / 651 |

These were deliberately **partial Codex visual seeds, not owner-approved full
poses**. Most classes were absent. The sparse outputs are not useful full-body
colors and do not establish few-shot quality. Neutral all-group-zero mapping
was used only to check the existing PGMD export connection. No final engine
palette or ROM was generated. Before/after artifacts for these partial seeds
were inspected locally; no comparison against the unseen approved idle masks
is claimed.

## Acceptance and dependency

Completed: connected executable review/training/projection/export path; actual
Chun-Li/Zangief inventories and uncertainty sheets; runtime/rejection reports;
three new synthetic tests plus nine projection and four marking tests pass.
Tests cover translation dedup, uncertain/distant queries, one-class rejection,
provenance, explicit abstention, source projection and exclusion of translated
seed poses from held-out counts.

Blocked acceptance: issue #31 requests comparison to owner-approved idle seeds
and full-part quality. Those seed pixel masks are currently only in Claude's
local workspace. A private artifact locator with capture/marks provenance or a
reproducible recipe was requested on #31; no owner relay requested and no game
assets should enter git. After those arrive, train with the verified seeds,
inspect held-out poses, add targeted seeds and measure review quality. Until
then this PR delivers tooling, not T18's final visual-quality acceptance.
