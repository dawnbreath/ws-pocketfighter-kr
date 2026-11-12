# T30: Chun-Li dash colouring

The owner renewed the work rules in `작업시작지시문구.txt`: reuse established
structures, group authoring/integration/necessary checks, preserve originals and
saves, and stop if a model escalation becomes necessary. This batch follows the
existing T29 table and finishes the following scope together:

1. Compare dash hand/cuff boundaries against actual Saturn gameplay.
2. Connect the four new dash/transition drawings and verify the actual game.
3. Preserve existing idle, walking and Zangief colours, plus restart states.

No translation, English/title image, font residency or VRAM allocation is changed.
The general lower-VRAM safety/font-residency requirement remains unproven; this
batch does not claim to resolve it. Sol/Medium was sufficient for these bounded
source masks and existing table/capture paths; no model escalation was required.

## Drawings and input evidence

Actual Saturn references were captured from the existing training save with a
2-frame direction press, 2-frame release and a second directional hold. Local
reference directory: `/workspace/work/reference/saturn-dash/`. The back-dash
reference identifies the lifted front knee as brown trousers, not blue tunic;
the hands are skin, cuffs black, and studs white.

Four source-bound region recipes live in `tools/mock/dash_colours.py`:

| source crop MD5 | role | opaque pixels |
|---|---|---:|
| 5e0cd125b0a086105e98febe9295dde8 | back dash | 684 |
| 9a49607f57c9b91bba21ec22af5946f6 | forward dash | 729 |
| 139c4f7f1874a8b3b30cf32c31b90fe0 | forward transition | 612 |
| 4ff7cf95194eada31aa2b4b08cec90cf | recovery | 679 |

The first WS short double-tap probe from the pre-control state yielded walking,
not dash. A 240-frame settle followed by press4/release4/hold confirmed both dash
poses. The established repeated-2-frame-tap route after settle180 captures their
transitions and recovery as well. Both exact protocols are recorded, not inferred
from a direction label. Exported source capture: `work/dash-repeat-source/`.

A separate capture discrepancy was isolated: dash OAM position can be ahead of
the screenshot's latched position. The back-dash samples align at +3 or -1 pixels;
forward samples at -5. `capture_walk.match_render` first tests the exact position,
then for dash only accepts a unique *zero-error* horizontal match within ±6 pixels.
It records the offset and keeps screenshots untouched. This does not permit colour
errors, shape errors, approximate matches or vertical corrections. Tied offsets,
clipped registrations and mixed-transition samples stay unmatched. Walking keeps
its previous exact-position comparison. Three focused tests cover offset matching,
refusal of changed pixels and refusal of ambiguous registration.

The shared `walk_table.py --motion dash` exporter reuses the existing ownership,
flip, coverage and conflict logic. It rejects missing drawings, unobserved cells
and changes to existing source records. All 139 T29 records and palettes remain
byte-identical; 72 records bring the table to 211 records / 10620 bytes. Engine
assembly and runtime branches are unchanged. The default walk export still
reproduces the T29 table byte-for-byte.

## Reproduction and exact outputs

```
python tools/capture_walk.py BASE_ROM BASE_ROM_IDLE_STATE BASE_CTB3 PALETTES OUT \
  --motion dash-repeat --frames 10 14 18 22 24 26 28 30 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/mock/walk_table.py OUT/capture.json \
  work/walk-final-table/full.ctb3 work/dash-table --motion dash
PF_HYBRID=1 PF_CLASS_TABLE=work/dash-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/dash.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

Candidate SHA256:
`a428817a8b033df9b532304a780b56121a876657ea333d746b9c0c9996d9d6d2`.
Table SHA256:
`8b9fc88714f5a44d8a67a2739d3085df1ddbcefd1ac8fb537ebbdb6fe910b782`.
The complete table was read back from the final ROM at `0xD8000` and is identical.
Re-exporting from the final runtime capture also reproduces it byte-for-byte.
Original ROM SHA256 remains
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.

## Completion evidence for the three items

1. **Boundary comparison:** actual Saturn forward/back-dash screenshots and the
   original WS shade grids were inspected before insertion. Material polygons
   retain original transparency and distinguish hands/cuffs/knee. Visual approval
   by the owner remains open; numerical agreement is not artistic approval.
2. **Connection and output:** candidate was cold-booted and routed to Chun-Li.
   New candidate-ROM idle states then drove the dash samples. 12/14 samples match;
   the four representative drawings match all 2704 authored opaque pixels, each
   at offset `[0,0]`. The two unmatched transition samples (indices11/13) were
   visually inspected and excluded from pixel-proof/export; they are retained.
   This is not a claim that every transition frame or animation timing was proved.
3. **Preservation:** six pinned full screenshots (title, fight start, four idle
   drawings) are pixel-identical to T29. Eight walking samples match, and all four
   walking drawings' opaque screenshot pixels equal the prior build. All139 old
   table records, including Zangief, are unchanged. Earlier ROMs and saves remain;
   new per-sample states and stop receipts are stored with the captures.

Local evidence: `work/dash-idle-chunli/`, `work/dash-runtime/`,
`work/dash-walk-regression/`, `work/dash-verification.json`,
`work/dash-game-detail.png`. Nothing game-derived is committed.
Checks: build, actual Mednafen/emucap screenshots, final ROM readback, exact table
regeneration, `test_capture_alignment.py` (3 tests), Black, py_compile, diff check.

Attacks, damage, opposite facing, other fighters' remaining poses, calibrated
performance and general VRAM lifetime proof remain open. This is a review candidate,
not a complete Korean-patch release. The actual-pixel and runtime-evidence approach
uses the supplied `rom-art-and-fonts` and `rom-graphics-verification` guidance;
existing project structure is retained as the supplied template recommends.
