# T32: Chun-Li crouching and airborne basic attacks

Completion items: (1) source-bound colours for the observed crouch/jump attack
family, (2) actual game output and saved states, (3) preservation of the previous
build. This batch adds 15 drawings; it does not claim every animation frame or
finish combos, contact, damage, opposite facing or the other fighters.

## Sources and material decisions

Independent samples reload the same fight-start state, settle 240 frames, then
use down12 followed by down plus the optional attack button, or up4/release8
followed by the optional attack button. WS A is kick and B is punch; the actual
Saturn captures use B for kick and A for punch. Saturn reference screenshots are
local at `/workspace/work/reference/saturn-low-air/`.

The seven low drawings cover crouch idle, sweep preparation/rotation/extension/
return and crouching punch preparation/extension. The eight air drawings cover
four jump drawings and preparation/extension of kick and punch. Geometry in
`tools/mock/low_air_colours.py` is bound to exact original crop hashes. Skin hands,
opaque black cuffs, white studs, blue tunic, brown trousers and white boots/buns
use the existing palette. Transparency is unchanged. User visual approval remains
pending; matching a mask in the emulator does not itself approve its appearance.

Shared source tiles have one output, irrespective of position: hair contour
`68fbfef9...(23,9)` retains old index3; the air-kick hair edge at x13..18,y0
shares a three-pixel tile with the air-punch skirt edge and retains index3 too.
The exporter rejects unknown/conflicting cells and changes to old records.
There are 271 additional records, 602 total, 30,170 bytes. All331 existing records
and both palette blocks are byte-identical. Only 2,598 bytes remain in the reserved
32KB half-bank; future additions must measure capacity before insertion.

## Capture and integration

`capture_walk.py --motion low-air` reuses the existing runner. Only airborne
captures may register a unique exact vertical offset within ±8 pixels. No image
is recoloured, warped or filtered; any colour difference rejects the match.
Existing standing/walk checks and dash-only horizontal registration retain their
behavior. Focused tests cover opt-in vertical alignment, a changed pixel and
ambiguous offsets, along with the existing horizontal tests.

Source captures used durations2,6,10,14,20 for all six actions, plus
12,16,24,32,40,48 for sweep and three airborne routes. Original captures remain
untouched. Derived alignment and combined evidence retain parent capture hashes
and original frame indices in `work/low-air-combined.json`.

```
python tools/mock/walk_table.py work/low-air-combined.json \
  work/attack-table/full.ctb3 work/low-air-table --motion low-air
PF_HYBRID=1 PF_CLASS_TABLE=work/low-air-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/low-air.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/capture_walk.py ROM SAME_ROM_IDLE_STATE CTB3 PALETTES OUT \
  --motion low-air --frames 2 6 10 14 20 24 32 48 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
```

Engine code, text hooks, VRAM allocation and bank switching are unchanged.
Full-ROM comparison against T31 allows differences only in the CTB3 span at
`0xD8000` and checksum bytes `0x3FFFFE..0x3FFFFF`; table readback and checksum pass.
Original ROM SHA256 remains
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
Candidate SHA256:
`7926e3ca853fa801f87fbda739d798976af67c68d159a0500eb5e0586a569849`.
Table SHA256:
`abfe2f5129c1cb2bc273a9a90f02ba4aabe2dd85ded978fa7a7f4ecc5648e06a`.

## Evidence

1. **Colours:** all15 source-bound drawings are integrated; original source
   geometry/transparency and all331 existing tile outputs are preserved. The
   final runtime capture reproduces the exact CTB3 SHA256 above.
2. **Actual output:** cold boot and the four-pose idle return cycle passed. All15
   representative action screenshots match all10,322 opaque pixels. Of48 samples,
   41 match the contemporaneous OAM (including exact vertical registration for
   airborne sprites). The other7 transition screenshots match known coherent
   drawings exactly, but their OAM snapshots are not used as mask/export evidence.
   The analogous10 rejected source snapshots also match known drawings in their
   screenshots. These cross-pose checks are saved separately; they are not counted
   as coherent OAM samples. Crouch attacks return to crouch idle, air attacks to
   standing idle; holding up through48 frames starts the next jump.
3. **Preservation:** six standing-attack drawings' actual opaque pixels equal
   T31 in six regression samples. Six pinned fullscreens (title, fight start,
   four idle drawings) are pixel-identical. Existing walking/dash/Zangief records
   are statically unchanged; those paths were not recaptured in this batch.
   Previous builds and saves remain intact. New per-sample states, four idle
   states and successful emulator stop receipts are kept with the captures.

Validation commands include `python -m unittest discover -s tests -p
 test_capture_alignment.py` (5 pass), `python work/verify_low_air_pixels.py`,
`python tools/mock/walk_table.py work/low-air-runtime/capture.json
 work/attack-table/full.ctb3 REPRODUCED --motion low-air`, Black, py_compile and
`git diff --check`. Local `work/low-air-runtime-transients.json` records the seven
separate screenshot identifications; `work/low-air-transients.json` records the
source equivalents.
Local evidence: `work/low-air-idle-chunli/`, `work/low-air-runtime/`,
`work/low-air-standing-regression/`, `work/low-air-verification.json`,
`work/low-air-rom-diff.json`, `work/low-air-game-detail.png`. Game assets, ROMs,
screenshots, extracted sources and states remain local and are not committed.

Sol/Medium remained sufficient for the bounded source masks and existing engine;
no model escalation was needed. General VRAM lifetime/font-residency proof,
performance measurement, contact/combos/damage/opposite facing and the remaining
fighters/localisation items stay open. English and title text remain deferred.
