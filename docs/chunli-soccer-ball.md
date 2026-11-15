# T41: identify and colour Chun-Li's soccer-ball transformation

Completion items: (1) identify both round drawings from actual Saturn/WS
sequences, (2) integrate and verify their colours without recolouring retained
output, (3) preserve old builds/states and a restart backup. All are complete
as a review candidate; owner art approval and unrelated coverage remain open.

## Identity and reference

The previously ambiguous14x14 shapes are the soccer ball that Ken transforms
his opponent into during his soccer throw. They are not normal Chun-Li heads.
WS palette-group inspection follows the squashed body into the round shape,
then its kick/flight; Ken and gem/effect sprites remain distinct groups. Both
ball drawings occupy the first four fighter source slots384..387. Palette or
slot membership alone was not used to infer identity.

A contemporary firsthand move list by Mike Corbitt describes Ken's soccer
throw and its command: https://otakuworld.com/games/psx/pktft-m.htm . It was a
lead, then confirmed through actual Saturn gameplay using the owner's disc.
From the saved training contact state (P1 Ken/P2 Chun-Li), hold left2, down-left2,
down2, down-right2, then right+P+K4; release and step4 frames45 times. Ken grabs
and squeezes Chun-Li, changes to soccer clothing, then kicks the ball. Captures
17/23 show white/black panels with gold edges. A separate charged-hammer probe
shows a different flattening/recovery and is retained as a rejected identity
reference. No game bytes or controller-port restrictions were bypassed.

The original WS drawings are b4e93ee55ac29afbebf42560fb307223 and
7aede331348673fbd40fa83914848868, both14x14/148 opaque pixels. They share four
raw tiles through flipping/rearrangement, so only four CTB3 records are added.
An exact-source lookup maps source shade1 to white13, shade2 to gold12 and
shade3 to opaque black4; source zero remains transparent. There is no positional
ROM exception, whole-body recolouring or redraw.

## Palette compatibility and shared tools

Index12 was unreferenced by every one of the759 retained output records.
Only that swatch changes from000 tofd0 in both registered fighter catalogues
(Chun-Li and Zangief), and the CTB3 footer is synchronized. Updating both handles
the shared ball tile pattern consistently without changing their existing body
colours. Fallback and all other swatches remain identical. The background resync
only expands ordinary2bpp shades to0..4; it does not introduce index12.

walk_table.py gains a ball family and an optional --palettes footer update,
reusing fighter_palettes.encode. A footer update checks every index used by the
baseline outputs against both fighter palettes before creating output. Recolouring
a used swatch is rejected; ball export requires the palette option so the gold
footer/catalogue cannot silently diverge. Old family defaults preserve their
previous footer behavior.

verify_contact_output.py gains an explicit recipe-family selection; contact
remains its default. Source/screenshot-incoherent samples are now listed as
excluded, matching the exporter's existing coherence rule. Buffer corruption
in coherent samples still fails verification. The two ball poses are fully
visible; RAM reconstruction is still labelled separately from screenshots.
The existing contact inputs retain all eight accepted samples with the same
2003 buffer/1080 representative visible pixels after the shared-tool change.
Two palette tests accept unused gold and reject used-white changes separately
for both registered fighters. No assembly/hooks, bank layout, text path or VRAM
allocation changes; this does not prove all-mode or full-population performance.

## Reproduction

NASM must be on PATH. Source inputs and states are private local/Drive artifacts;
ROM-derived images, tile bytes and private backup links stay outside Git.

```
python tools/mock/walk_table.py work/damage-gap-flat/capture.json \
  work/contact-table/full.ctb3 work/ball-final-table --motion ball \
  --palettes data/palettes/wrist-fixes.json
PF_HYBRID=1 PF_CLASS_TABLE=work/ball-final-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/ball.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/capture_walk.py work/ball.ws work/ball-states/guard.mcs \
  work/ball-final-table/full.ctb3 data/palettes/wrist-fixes.json work/ball-runtime \
  --motion idle --settle-frames 400 --frames 26 42 58 66 --read-colour-buffer \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_contact_output.py work/ball-final-check work/ball-runtime --family ball
python -m unittest discover -s tests -p test_palette_compatibility.py
```

## Results for the completion items

1. Actual Saturn soccer-throw footage and WS sprite lifecycle resolve both
   previously ambiguous shapes. Four records are added,759->763; all759 prior
   outputs remain byte-identical. Every previously referenced RGB remains the
   same for both registered fighters. Table size38220,free bytes18612.
2. Both ball poses match all296 representative opaque pixels in real screenshots
   and the actual4bpp buffer across three accepted samples; none are hidden.
   The fourth sample (duration66) has39 source/screenshot mismatched pixels and
   is explicitly excluded, not counted as passing. Runtime export reproduces the
   exact763-record table. Zangief's old base pose matches all28 tiles/1269 pixels
   in three actual samples. Selection screens are pixel-identical to T40.
   ROM readback/checksum and IPS round-trip pass. All13924 changed ROM bytes lie
   in CTB3, the four gold catalogue bytes (D2038/D2039/D2058/D2059), or checksum.
   Two palette tests, shared contact-artifact regression, Black, py_compile and
   diff checks pass; unchanged assembly suites are not repeated.
3. Original/T40 builds and states remain preserved. Own-ROM restart and accepted
   sample states, Saturn source/result states, screenshots, raw captures, reports,
   palette compatibility evidence and successful stop receipts accompany ROM/IPS
   and source tools in the private backup. ZIP CRC and upload size/parent metadata
   are verified. No ROM, state, game image or extracted game text is in Git.

ROM SHA256:45afd4ac98950a9c6263d4dcfc8ada77b5ff1cc5e2126274595b05b8655a6125.
CTB3 SHA256:5b403bfa69ed0ac37cdf21d8d04258fe4457fc0e0b2417aca638e05d0f2622a4.
Previous ROM SHA256:b376572082c7cd5052205a0517a059ce186981a47a1d709b9c249c706a785f1a.

Evidence: work/ball-{verification,static-verification}.json, ball-final-check/,
ball-reproduced/, ball-runtime/, ball-zangief-{boot,check}/, T40-wrist-fixes.json,
round-all-palettes.png, soccer-reference-detail.png, saturn-reference/soccer-throw/.
T40 hidden-region visibility/owner art review, other moves/fighters, T36 exact
standing-guard reference, earlier translation limits, font VRAM residency and
full-population timing remain open. Sol/Medium remained sufficient.
