# T42: clipped and reflected Chun-Li defence output

Completion items: (1) connect clipped/reflected source drawings to existing
recipes, (2) integrate and run the corresponding RAM/screen checks, (3) preserve
the stable build and restart evidence. All are complete for the cases below.
This adds verified coverage and QA behavior, not new ROM artwork or colour data.

## Cause and bounded tool change

Historical normal-side hit captures placed Chun-Li at unsigned OAM x248, i.e.
eight pixels before the LCD's left edge. Cropping to224x144 first produced
truncated source hashes cf43d5.../dc035e... that could not match complete known
drawings. Composition on the256-coordinate OAM surface recovers the existing
standing-hit source e6f402... and an already-coloured idle source09b800... .
Other passive captures show an exact horizontal reflection of the same hit
source. There is no need to add colour-table records for these cases.

compose() gains an explicit viewport option; its default remains224x144 and
opponent priority/transparency are unchanged. cyclic_crop() takes the smallest
occupied rectangle on the256x256 surface using the largest empty gap per axis.
It handles ordinary, empty and fully occupied-axis inputs explicitly. The
existing source hash uses one-byte shape dimensions, so a whole-axis256 crop is
not admitted as an exact recipe. A palette group alone still does not establish
general actor identity; accepted drawings must match the existing recipe hash.

The existing RAM/screen checker gains --family defence, --wrapped-source and
--orientation source|mirror|either. Defaults preserve the old contact/ball
behavior. Reflection matches exact original source bytes after flipping and
reflects the authored labels back; there is no nearest-pose transfer. A shared
source-region/recipe resolver serves both verification and figures.

Actual4bpp pixels are read from the existing fighter mirror, including hidden
and off-LCD coordinates. Only the normal LCD composition supplies screenshot
pixels. Reports distinguish offscreen pixels from pixels covered by the
opponent. Grey in figures is an off-LCD placeholder, not generated screenshot
evidence. RAM reconstructions are labelled separately. Multiple input directions
now bind to direction-local screenshot numbers, matching capture_walk.py;
global capture frame indices remain in provenance, including excluded frames.
No ROM loop, hook, bank switch, text path, palette or VRAM allocation changes.

## Live completion evidence

The existing T41 ROM runs with its own hit/guard states. Three captures sample
16 inputs:8 are coherent,7 match the defence recipes and1 is a different drawing.
The8 incoherent inputs are retained as excluded, not reported as passing. All
accepted captures have explicit4096-byte colour-buffer reads and stop receipts.

| Verified situation | Representative RAM pixels | Visible screenshot pixels | Offscreen | Behind opponent |
|---|---:|---:|---:|---:|
| Standing hit at left edge |719|533|122|64|
| Reflected standing hit |719|410|0|309|
| Existing guard |604|604|0|0|
| Representative total across situations |2042|1547|122|373|

These are three situations involving two authored drawings, not three new poses.
The table selects the accepted sample with most visible pixels in each situation.
Two edge samples, three reflected hit samples and two guard samples pass. Full
hidden/offscreen art still does not have an unoccluded screenshot proof.

A negative check flips one colour-buffer bit at off-LCD coordinate254,89 while
preserving the original2bpp source and real screenshot. The buffer comparison
rejects it; screenshot agreement cannot mask offscreen corruption. Four new
cyclic-source tests cover wrapping across both axes, normal coordinates, empty
source and a fully occupied axis. Two reflection tests require explicit opt-in,
reflect labels, prefer a direct match and reject a similar nonmatching drawing.
Two existing composition tests also pass (8 total). Existing contact8-sample
and ball3-sample artifact checks retain their prior counts/results. Black,
py_compile and diff checks pass; no unrelated assembly suite is repeated.

```
python tools/capture_walk.py work/ball.ws work/ball-states/hit.mcs \
  work/ball-final-table/full.ctb3 data/palettes/wrist-fixes.json work/T42-edge-hit \
  --motion idle --settle-frames 400 --frames 10 18 26 42 --read-colour-buffer \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_contact_output.py work/T42-defence-final \
  work/T42-edge-hit work/T42-mirrored-hit work/T42-guard \
  --family defence --wrapped-source --orientation either
python -m unittest discover -s tests -p test_cyclic_source.py
python -m unittest discover -s tests -p test_recipe_orientation.py
python -m unittest discover -s tests -p test_contact_composition.py
```

Reflected-hit capture uses the same ROM/table/palette, guard.mcs, idle, settle0
and durations50/58/66/74/82/90. Guard capture uses guard.mcs, walk, settle0 and
2/6/10 (both directions). Preserve each original coherence flag; do not substitute
old-ROM captures as new-ROM runtime proof. Historical opposite captures are
only diagnostic inputs. One reflected hit has719 buffer pixels but only268
visible; the representative table above uses its later410-visible-pixel sample.

## Preserved build and handoff

ROM is unchanged T41, SHA256:
45afd4ac98950a9c6263d4dcfc8ada77b5ff1cc5e2126274595b05b8655a6125.
Unchanged763-record CTB3 SHA256:
5b403bfa69ed0ac37cdf21d8d04258fe4457fc0e0b2417aca638e05d0f2622a4.
The original-ROM IPS still reconstructs that exact ROM. No new ROM version is
claimed. Source snapshot, stable ROM/patch/table, original input, own-ROM base
states, accepted sample saves, capture reports, stop receipts, negative-test and
figure/summary scripts are retained in the private restart backup. ZIP CRC and
uploaded size/parent metadata are verified; no game data or private backup link
is committed to Git.

Local evidence: work/T42-verification.json, T42-defence-final/,
T42-{edge-hit,mirrored-hit,guard}/, T42-offscreen-negative.json,
T42-{contact,ball}-final-regression/, T42-case-detail.png. Opposite-facing guard
and unobserved damage/contact/KO/combo drawings remain unverified. T36's exact
Saturn standing-guard reference, owner art approval, other fighters, translation
limits, general VRAM font residency and full-population timing remain open.
The bounded source reconstruction and existing-recipe checks needed no model
escalation; Sol/Medium remained sufficient.
