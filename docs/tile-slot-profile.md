# T15: captured slot reuse and engine handoff

Run `python tools/profile_tile_slots.py CAPTURE.json work/slots.json`.
The input is a complete schema-1 capture from capture_frames.py. Active OAM
start/count and selected palette field are honored; tile contents are read in
source orientation, so H/V flips do not create different hashes. Offscreen or
occluded references are included. This is reference occupancy, not visible-pixel
coverage or writer attribution. Outputs contain derived game data: keep in work/.

Existing original-ROM fight captures (256 samples each):

| Character | Unique hashes in slots 180–1FF | Outside | Referenced slots | Slots with multiple contents |
|---|---:|---:|---:|---:|
| Chun-Li | 640 | 0 | 43 | 41 |
| Zangief | 652 | 0 | 61 | 59 |

Reusing a slot across time is normal animation, not proof of a simultaneous
semantic collision. Nor does membership in 180–1FF prove which writer last
populated it. Other ten fighters, story/card/gallery and scene-load writer
attribution remain unmeasured. Do not extrapolate these fight captures.

## Requested compact mask layout needs an explicit contract

Current mask IDs have 14 values plus unknown (-1). An arbitrary 8×8 semantic
mask requires 64 four-bit values = **32 bytes**, with nibble 15 available for
unknown. Sixteen bytes can encode only two bits per pixel: four classes, not
all semantic IDs. Claude's two additional bitplane bytes per row instead encode
four *palette groups*, keeping original shade bits; this requires a reviewed
semantic-to-palette-group mapping first. It cannot faithfully encode arbitrary
semantic labels or an extra unknown value. Never silently truncate IDs.

Existing masks already undo flips through observations() and preserve conflicts
as unknown. They are unreviewed geometric proposals, not approved engine masks;
a uniform flag is valid only when every relevant opaque pixel is resolved and
agrees after an approved group mapping. A proposed binary format must specify
unknown fallback, transparent pixels, palette mapping and collision handling
before it becomes a production table.

A sorted hash32 table alone does not eliminate runtime hashing. The incoming
staging tile still needs a key; hashing offline only helps if a proven source
identity selects a precomputed key. Otherwise measure the runtime hash cost and
confirm the full 16 source bytes after a hash hit (collisions must not silently
select a different mask). No source identity has yet been proven for every
staged fighter tile. Content equality alone also does not establish semantic
identity: retain character/context and conflict handling.

## Review of PR #17 at 32e40f3

The corrected OAM diagnostic was accepted and Claude reports reproducing active
sprite transparency. This is reported owner-side evidence, not an independent
rebuild here. No production feasibility gate passes from it.

The new timing proposal mixes denominators: 15.7 changed tiles **per frame**
from 299 frame pairs is not 15 changed tiles **per copier call** when calls
happen every other frame. If windows and routes were comparable, that is about
31.4 changes/call, not 15. The windows differ, so measure both quantities in the
same run before deriving a budget. Include all 128 tile comparisons, lookup/key
cost, original copier work and worst-case changed tiles. The old 220-cycle
sample is uncalibrated and cannot settle feasibility.

A dirty comparison also needs a validity invariant: equal 2bpp bytes do not
imply a valid 4bpp destination at startup, or after a character/palette/mask
context change or another writer. Define initialization and invalidation at
scene/copy ownership transitions, avoiding broad checks on unrelated paths.

The benchmark is excluded from normal builds but is unsafe to wire unchanged:
it writes FD70–FD78 scratch without reservation, changes flags/registers and
unconditionally enables interrupts. It needs an explicit call contract and
reserved record before another measurement. Historical statements that the
mirror renders the whole game conflict with the stated non-fight breakage;
retain only the measured fight claim. Requested corrections sent on #17/#20.
