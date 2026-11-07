# T05 candidate extraction and mask proposals

`python tools/frames_dump.py --rom orig/pf.ws --out work/frames-v1`

Requires Pillow and the documented original ROM SHA-256. ROM data, sheets,
per-pixel masks and manifest stay under ignored work/. Do not commit them.
`python -m unittest discover -s tests -v` passes 5 synthetic tests for planar
decoding, signed coordinates, both flips, shared tiles, bounded lists and reads.

On the supplied original: 332 command-pattern matches, 324 bounded candidates,
8 rejected lists, 192 conflicting per-source-tile mask proposals. Six contact
sheets were generated. Sheet 0 visually contains menu/HUD/label art. Therefore
these are NOT 324 verified fighter animation frames. Static matching cannot
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

## Review correction after Claude supplied gen_labels.py

The piece list uses the script command bank (`command >> 16`), whereas pixel
tiles use the bank operand of command 04. The earlier draft incorrectly used
the graphics bank for both. The split-bank synthetic test now exercises the
actual extraction function. The earlier 329/3/227 counts are superseded.

Bounded readers now live in pieces_checked.py; the existing pieces.py API stays
compatible with gen_labels.py, whose discovery order is also the label ID map.
Do not replace the established label inventory with this stricter candidate scan:
it rejects eight cross-bank candidates pending runtime address semantics, and
does not deduplicate aliases. Neither rejection proves that an asset is unused.
