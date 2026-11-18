# T46: Zangief walking drawings and an observed transition

Completion items: (1) capture/classify compatible drawings and compare Saturn
materials, (2) integrate their colours and prove native output, (3) check retained
output and preserve restart data. All three are complete as a review candidate.
Owner art approval, full animation coverage and the last drawing's exact motion
identity remain open; it is explicitly an observed late-forward transition.

## Source and materials

Four coherent step drawings are grouped by actual input while Zangief faces
right: backward/left edf5d1e6518c1d82e730660e36da1b83 and
0ce1c596239944b85ecf69468ba56ab2; forward/right
17ece493fd2fc86f91c2a224d7f08b0e and bc0c17f07da6642035c689f7fade1f41.
The late right-hold drawing5f7e6f558f359512ba60ee52a941d42b is retained and
coloured separately, without claiming a fully identified command/motion.
These are not opposite-facing coverage or all walking frames.

The400-frame settle probe still shows the FIGHT introduction and only existing
idle drawings. It is not used as walking evidence. At600 frames, the first
12-sample cohort has only two exact RAM/screenshot matches; none of the other
ten is relabelled passing. Moving the sampling holds by one frame produces12/12
coherent samples and the five selected drawings. Unseen/mixed source drawings
are unverified, not declared unused. Preparation records pose hashes, source
provenance, capacity and retained-tile overlap before export/ROM insertion.

Actual Saturn P1 Zangief/P2 Ken training footage, held right in six four-frame
steps from the T44 fight state, supplies walking/limb/material reference. Red
wristbands and boots use the existing first red ramp; trunks use the second.
Hands, exposed legs and body retain skin; hair/beard retain dark skin shading.
No gold trim, palette change or broad T19/T20 mask propagation is introduced.
Cross-port pixels/frames are not claimed identical. Rasterization reuses the
existing wrist_fixes.selection helper. The two-pixel toe at walking crop24,40/41
shares one retained source tile: its existing index11 is also dark red for
Zangief, so that output is preserved exactly instead of recolouring old art.

## Integration and native output

The existing exporter gains a Zangief walking family. Accepted protocols are
explicit600-frame settle or zero settle from an own-ROM ready state. The latter
saves the same600-frame prefix once to avoid replaying it for every sample;
its ROM/parent-state hashes and step receipt are retained. No capture-matching
criterion is weakened. The verifier stores recipe/character pairs together,
removing the growing per-family character conditional; Chun-Li defaults remain.
No assembly, IRQ fix, runtime check, bank switch, VRAM or text change is made.

The table grows819->942 records,123 added, all819 old outputs byte-identical.
Its47,170 bytes leave9,662 bytes free in the same bank. Both palette catalogues,
footer and the entire atomic copier are unchanged. All added outputs preserve
source transparency and shade low bits. ROM changes are confined to CTB3 and
checksum; original ROM preservation, readback/checksum and IPS round-trip pass.

Fresh own-ROM cold boots and ready/sample states accompany the candidate.
In24 walking runtime samples,14 are coherent and ten remain excluded. The four
step drawings match4285 representative visible/4bpp RAM pixels; the transition
matches1037, total5322. Every target pixel is visible, with no opponent occlusion
or offscreen portion. The new-ROM re-export reproduces the exact942-record table.
Four idle samples additionally verify the two prior breathing drawings/2514
pixels, and the retained basic pose independently matches1269 pixels.

## Retained output and frame-boundary diagnosis

Both selection, initial-fight and saved-start screens are identical to T45:
six fullscreens, including the repaired NO MERCY banner. Eleven same-source/
same-position walking pairs also have exact pixels outside P1's opaque mask.
One right-hold23 pair differs by123 Ken-area pixels and is explicitly excluded
from identical regression counts. A direct own-base/settle600 control reproduces
it, so it is not blamed on the ready-state optimization. The first permissive
diagnostic is superseded; the final comparison reports11 passes/one exclusion.

Native own-ROM snapshot probes locate the new sample at CS0:0138, SP0CA2,
CX3, DI3FA0, IF0: the protected POP copier is partway through source tile506.
That2bpp shadow is consequently partial. Its staging source and4bpp low planes
both exactly match original ROM graphics at10160; the older sample has already
finished that tile. All20 Ken RGB tile buffers are identical between snapshots,
as is palette13's repeated grayscale ramp. Thus there is no new-material colour
leak or damaged staging pixel at this observed difference. Holding right for
one further frame four times yields zero Ken-ROI differences in all four
screens (ROI x96..143/y80..127). This bounds the observed frame/raster phase
sampling difference; it is not counted as a pixel-identical original pair or a
full-game timing proof. P1's own source/RAM/screenshot checks stay exact.

Six relevant orientation/palette/composition tests, Black, py_compile and diff
checks pass. Existing T45 Chun-Li guard/hit artifacts also retain their three
checker results after the offline family-registry change; this is a checker
regression, not a new-ROM combat claim. Unchanged assembly suites are not rerun.

## Reproduction and restart

Use private input artifacts and adapt EMUCAP/MEDNAFEN/NASM paths. Source files,
ROMs, graphics, extracted text and state data do not belong in public Git.

```
python tools/capture_walk.py work/T45-zangief.ws work/T45-zangief-boot/base.mcs \
  work/T44-idle-table/full.ctb3 data/palettes/wrist-fixes.json \
  work/T46-walk-offset-source --character zangief --motion walk \
  --settle-frames 600 --frames 3 7 11 15 19 23 --read-colour-buffer \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/mock/walk_table.py work/T46-walk-offset-source/capture.json \
  work/T44-idle-table/full.ctb3 work/T46-walk-table --motion zangief-walk \
  --additional-capture work/T46-walk-live-source/capture.json
PF_HYBRID=1 PF_CLASS_TABLE=work/T46-walk-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T46-zangief.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

work/T46_boot.py creates own-ROM Chun-Li/Zangief bases. T46_create_states.py
loads the own Zangief base, steps600, saves walk-ready.mcs; do not cross-load
another ROM version's states. From that ready state:

```
python tools/capture_walk.py work/T46-zangief.ws work/T46-states/walk-ready.mcs \
  work/T46-walk-table/full.ctb3 data/palettes/wrist-fixes.json work/T46-walk-runtime \
  --character zangief --motion walk --settle-frames 0 \
  --frames 2 3 6 7 10 11 14 15 18 19 22 23 --read-colour-buffer \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_contact_output.py work/T46-walk-checked \
  work/T46-walk-runtime --family zangief-walk
python tools/mock/walk_table.py work/T46-walk-runtime/capture.json \
  work/T44-idle-table/full.ctb3 work/T46-reproduced --motion zangief-walk
python work/T46_static.py
python work/T46_compare_walk.py
```

ROM SHA256:b5900024218410692916014ded0c0b46a4b647dfc55692a7745ca9edbec785fa.
Table SHA256:3f1b1ce1bf6b5a1ac6a0509511e78f4ef67201c0db46c48a339c05aaa6b50a4a.

Evidence: work/T46-{preparation,static-verification,verification,walk-regression,
direct23-regression}.json, T46-{walk,idle}-checked/, T46-opponent-{probe,followup}/,
T46-*source/, T46-states/, T46-*-boot/, T46-*-runtime/ and
saturn-reference/T46-zangief-walk/. The actual comparison image contains five WS
screenshots and a separate Saturn reference, not reconstructed art passed as
screenshots. Stop receipts accompany the native runs. A verified cleanup freed
only identical disc copies from two stopped emulator generations; original disc,
BIOS, ROMs, states and reports were retained.

The approved private Drive backup preserves original/T45/candidate ROMs, IPS,
tables, fonts/source, own states and accepted sample saves, raw captures, reports,
replay helpers and stop receipts. Saturn source/result states and screenshots
are solid-compressed with member hashes verified; outer ZIP CRC/member hashes
and uploaded size/parent metadata are checked. No private backup links or game
assets are published here. Completion1 reference/classification,2 integration/
native output and3 bounded regression/restart preservation are complete as a
review candidate. Owner art approval, unobserved frames/opposite-facing/attacks,
transition identity, earlier translation/font-VRAM limits and full-population
cycle timing remain open. Sol/Medium was sufficient; no escalation was needed.
