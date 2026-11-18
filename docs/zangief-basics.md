# T47: standing Zangief kick/punch and a shared walking step

Completion items: (1) classify the former transition and prepare compatible
basic drawings with Saturn reference, (2) integrate/native-verify them,
(3) check retained output and preserve restart data. All three are complete
as a review candidate; owner art review and unobserved actions remain open.

## Classification and reference

The formerly provisional5f7e6f558f359512ba60ee52a941d42b repeats in held-right
walking from an earlier ready state, with43 horizontal pixels between fighters,
no attack inputs and no opponent contact. Matched neutral27/35-frame samples
remain ordinary breathing; the basic-attack cohort does not contain that key.
It is now classified as an observed forward walking phase. This is gameplay
classification, not an exclusive ROM animation/command-ID mapping.

The new basic drawings are standing A-kick windup/lift/extension
65989721d7cd23dedeb183ab309439ea,09e8aaa366a030a339fb253bd62208c3,
1c1d0c478b8fcab6826dc75602907bb1; standing B-punch preparation/extension
e3d09ab5964d42c079be7aa225a96654,6451863b7a5ab82fa3fa3604cb7b97d0;
and5cfd48d768091d52c40bc378a616943b, a shared later movement drawing seen
under held left and right. No combo/strength/opposite-facing completeness is
inferred from these samples.

Own-ROM ready states at base+500 keep Ken farther away. All18 attack and10
movement source samples are coherent. Actual Saturn standing punch/kick footage
uses Saturn A=punch/B=kick; WS A/B have the opposite observed mapping here.
The material reference supports skin hands/exposed legs and red bands/boots/
trunks. Existing palette ramps and dark skin hair/beard shading are retained;
no gold trim, broad rejected masks, new outlines or bitmap reshaping is added.
Source hashes bind all geometry. Three retained source tiles are respected,
including the sparse toe's existing dark-red index11.

## Integration and native proof

The existing exporter/verifier gain one Zangief basic family, accepting explicit
zero-settle attack/walk captures from a pinned ready state. The older walking
recipe's provisional constant is renamed without changing its five outputs.
Rasterization uses the existing selection helper. A64-pixel-wide kick exposed
an overlap in the checker's old fixed300-pixel gallery cells; cells now derive
from actual pane dimensions. Before/after gallery JSON reports are byte-identical.
Only the offline layout changes; verification criteria and game code do not.

The table grows942->1116 records,174 added, with every prior output preserved.
55,870 bytes leave962 bytes/19 record slots free. Both catalogues, footer, atomic
copier, font/text data and all code are unchanged. Added outputs retain source
transparency/shade bits. Changed ROM bytes are confined to CTB3 and checksum.
Readback/checksum, unchanged original hash and original-ROM IPS round-trip pass.

Fresh own-ROM boots and500-frame ready states precede new runtime capture.
Six new drawings match7845 representative visible and4bpp RAM pixels across20
samples:4058 kick,2537 punch and1250 movement pixels. No target pixel is hidden
or offscreen. Runtime re-export produces the exact1116-record table. Eight prior
drawings independently match9105 pixels:three breathing/basic poses and five
walking phases. Source/screenshot matching is exact; no offset rule is weakened.

## Retained-screen results and phase exclusions

Five original fullscreens are identical to T46. The initial Chun-Li fight
sample differs by five skin/background pixels, only at x48..52/y98. Diagnostic
cold boots show identical P1 OAM, palette12 and all16 native P1 colour tiles.
The next four fullscreens are exact, giving nine identical fullscreens in the
bounded regression. The initial sample is excluded from identical counts.

Twenty-one paired battle/movement captures have exact pixels outside P1's
unchanged source/position mask. Seven original pairs differ in Ken's area and
are excluded. Their Ken OAM and all19/20 native RGBA tile outputs are identical
under the unchanged repeated grayscale fallback; actual palette13 in both
native intro probes equals that fallback. Replaying each own-ROM snapshot and
stepping neutrally clears six ROI differences by the next frame and the last
by frame two. These results bound observed frame/raster update phase differences;
they are not reported as identical original pairs or a cycle-perfect benchmark.
No ROM bypass is added to conceal them.

Six relevant orientation/palette/composition tests pass, plus Black, py_compile
and diff checks. The retained walking recipe also reproduces its old14-sample
native results. Unchanged assembly/all-game suites are not repeated. The actual
comparison poster uses six new WS screenshots, two Saturn references and the
retained now-classified walking phase; these nine panels are not nine features.

## Reproduction and restart

Private artifacts retain original/T46/candidate ROMs, tables, source, fonts,
raw captures, own ready/sample states and successful stop receipts. Adapt NASM,
emucap and Mednafen executable paths; numpy/Pillow/fontTools are required.

```
python tools/mock/walk_table.py work/T47-attack-source/capture.json \
  work/T46-walk-table/full.ctb3 work/T47-basic-table --motion zangief-basic \
  --additional-capture work/T47-far-walk-control/capture.json
PF_HYBRID=1 PF_CLASS_TABLE=work/T47-basic-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T47-zangief.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/verify_contact_output.py work/T47-basic-final-checked \
  work/T47-attack-runtime work/T47-walk-runtime --family zangief-basic
python tools/mock/walk_table.py work/T47-attack-runtime/capture.json \
  work/T46-walk-table/full.ctb3 work/T47-reproduced --motion zangief-basic \
  --additional-capture work/T47-walk-runtime/capture.json
python work/T47_static.py
python work/T47_compare.py
python work/T47_finish_verification.py
```

T47_create_states.py creates the old-ROM source ready state at500 frames;
T47_prepare_runtime.py creates the candidate's own ready state. Capture attack
A/B holds3,5,7,9,11,15,19,23,27 and left/right holds3,11,19,27,35 with
capture_walk.py --character zangief --settle-frames 0 --read-colour-buffer.
Idle regression uses own boot+240 and holds2,4,12,34,36. Never cross-load another
ROM version's state. Old pre-layout gallery reports are retained as history;
use T47-basic-final-checked for the corrected comparison gallery.

ROM SHA256:fab37eb8a262921253a5f0c31b7312e7c6b3a1dbdc265e66322d83429af8c425.
Table SHA256:3bfdd90948d17087e29f808ac22c760b1cf74021b8cdda738ec6f0d88dbc6be1.

Evidence:work/T47-{classification,preparation,static-verification,regression,
dynamic-boundary,verification}.json; T47-basic-final-checked/;
T47-boundary-followup/; T47-{before,after}-probe/; T47-*-runtime/ and
saturn-reference/T47-zangief-basics/. The solid-compressed Saturn source/result
archive has verified member hashes. The approved private Drive backup includes
ROM/IPS/tables, original inputs/fonts, own states, raw captures/screenshots,
replay helpers, reports and stop receipts; ZIP CRC/member hashes and uploaded
size/parent metadata are verified. No game assets/private backup links in Git.

Results for items1/2/3:classification/reference, actual integration/output,
and bounded regression/restart preservation complete. Owner art approval,
unobserved frames/strengths/combos/opposite-facing/other fighters, earlier
translation/font-VRAM limits and full-population timing remain open. Only19
record slots remain; any later additions require their actual capacity check.
Sol/Medium sufficed; no escalation was required.
