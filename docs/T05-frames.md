# T05 candidate extraction and mask proposals

`python tools/frames_dump.py --rom orig/pf.ws --out work/frames-v1`

Requires Pillow and the documented original ROM SHA-256. ROM data, sheets,
per-pixel masks and manifest stay under ignored work/. Do not commit them.
`python -m unittest discover -s tests -v` passes 4 synthetic tests for planar
decoding, signed coordinates, both flips, shared tiles, bounded lists and reads.

On the supplied original: 332 command-pattern matches, 329 bounded candidates,
3 rejected lists, 227 conflicting per-source-tile mask proposals. Six contact
sheets were generated. Sheet 0 visually contains menu/HUD/label art. Therefore
these are NOT 329 verified fighter animation frames. Static matching cannot
prove script reachability or exhaustive traversal. This task remains blocked
for full fighter coverage until Claude provides animation roots/interpreter
semantics or runtime tile-copy/OAM traces. See issue #3.

The optional mapping JSON has `rom_sha256` and `commands` keyed by six-digit hex
command address; each entry needs `character` and `evidence`. Names are never
inferred from HUD positions. The output tracks command address, bank/base,
piece pointer, signed origin, flip bits and original ROM tile address.

Mask values: 0 unknown, 1 skin, 2 cloth, 3 boots, 4 hair, 5 outline. These are
shade/geometry guesses, not approved segmentation or confirmed transparency.
Per-piece labels are inverse-flipped into source tile orientation. Repeated
source addresses with different proposals are reported rather than overwritten.
Overlapping pieces and runtime palette semantics need review before masks can be
used by engine hooks; `engine_ready` deliberately remains false.

No ROM was modified. T04's 4bpp feasibility and VRAM lifetime proof are still
Claude's engine task. T06 palette design awaits genuine mapped fighter samples.
