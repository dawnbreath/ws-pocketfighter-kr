# T15 / issue #20: architecture and labelling decisions

This answers the six consultation questions and the two follow-up comments in
issue #20. It does not certify production 4bpp conversion or all-character
semantic accuracy. Following the owner's 2026-11-09 handover instruction, Codex owns engine changes,
capture, annotation, export, integration and verification. Historical split notes
below describe the earlier two-agent workflow.

## 1. Lookup architecture

Compute content hashes offline. Hot copy paths should use a bounded lookup
based on proven source identity and actor/stage/layer context, with no hashing
of every byte on every repeated copy. A content hash is an equality key, not
an anatomical identity. Identical source pixels can be a glove, bare hand,
background object or a shared blank; inverse flips before exporting masks.

A canonical key `(character or stage, layer, tile-content hash, source pixel)`
collects proposals and conflicts. It cannot resolve two simultaneous uses of
the same tile that need different colors. Use separately allocated tile slots
or palette/map context when proven; otherwise retain an explicit unknown or
reviewed neutral fallback. Never silently select the majority label. ROM
candidate matches from T12 help tracing but do not establish copy paths.

Scene-load map attribute changes or updates limited to dirty map cells remain
possible alternatives to scanning all 1024 map cells every VBlank. A costly
full-map rewrite does not rule out those approaches. Compare real hook timing
and tile duplication costs before choosing. See `copy-routines.md` for copy,
staging, clear and compaction contracts; do not patch every writer identically.

## 2. Conditional VRAM budget

| Item | Calculation | Conclusion |
|---|---|---|
| Original logical tile slots | 512 × 16 = 8192 bytes | Shared by game graphics and streamed glyph destinations |
| Same slots expanded | 512 × 32 = 16384 bytes | Diagnostic mapping 4000–7FFF requires 16 KiB |
| Reported one-scene BG/HUD | 294 + 48 = 342, if disjoint | Leaves at most 170 slots in that allocation for other disjoint live tiles |
| Palette RAM | FE00–FFFF = 512 bytes | Not available for tiles |
| Patch state | FD00 region | Must preserve its actual allocation/lifetime |
| Palette-only 2bpp expansion | Still 32 bytes per tile in 4bpp | Does not save tile VRAM |

A snapshot's unique content hashes over time are not simultaneous occupancy.
Fighters, BG, HUD and streamed Korean glyphs may reuse the same slots. Neither
the 342 estimate nor two fighter captures proves the worst-case live union.
The entire 4000–FFFF range is not free memory. Do not count a second bank as
sprite capacity without checking the hardware addressing and map/OAM rules.

The conditional 16-KiB budget is plausible for preserving original slots,
but memory readers, state/work areas, glyph copies, mode changes and all writer
paths still need runtime lifetime checks. T10 revealed additional writers;
there is **no safe-fit verdict yet**. Retain the user's chosen streamed-font
approach as reported by Claude, and verify glyph tiles in the real allocation.

## 3. Capture split and coverage

Codex: original/candidate captures, component proposals, local review marks,
context-aware conflict tables, contact sheets and regressions. Claude: source
copy hooks, palette allocation, assembly, VRAM lifetime/timing proof and build
integration. Both review the other's PRs; no self-merge.

Existing evidence: Chun-Li and Zangief each have 256 samples, not exhaustive
move coverage. The other ten fighters have reference part inventories, not
runtime animation coverage. All-stage BG/FG capture remains pending. Six
reported WS stages are evidence of six observations, not proof of total roster
or Saturn stage parity. Do not infer a PLxx character ordering from the PAC
container. Tabasa/Tessa is not Donovan.

For each future stage capture, record scene/opponent identity, build hash,
start/scroll position, BG/FG maps, tile banks, palette interpretation and window/
scroll registers. Capture at stage start plus changed/animated/scrolling states.
Preserve glyph/name overlays separately so text is not classified as scenery.
A coverage matrix must explicitly include story, card battle, gallery and ending.

## 4. Annotation schema and connected implementation

Implemented in `component_marks.py` and `segment_frames.py --marks`:

- Export numbered outline-connected components and a plain source frame.
- Bind a local mark file to capture SHA-256, character and exact frame content.
- Assign a semantic name to a component with a checked component fingerprint.
- For merged parts, use explicit pixel coordinates for thin boundaries, gloves,
  wristbands, belts and colored outlines. An outline pixel can have
  `cloth_outline`; no forced universal black outline.
- Require a named reviewer. Tool acceptance is not owner approval. Contradictory
  marks fail; marks never silently replace other conflicting marks. A component
  spanning two parts must be split with pixel marks, not painted wholesale.
- Apply marks before inverse-flip tile projection and cross-frame conflict
  aggregation. Other poses can still conflict: one reviewed pose does not
  establish universal reuse. Unknown labels abstain, not a global blacklist.

Examples and verification: `component-review.md`. The existing centroid boxes
are only automatic suggestions. Manual markings operate on actual connected
pixels or explicit source coordinates; no new bounding rectangle is painted.

All twelve `data/rules/<character>.json` files now contain part IDs, semantic
labels, color intent, a ramp role, thin-feature review flags and reference
provenance. Reference inspected directly:
https://segaretro.org/File:Pocket_Fighter,_Characters.png

No image or extracted palette values are committed. The common slot plan is a
capacity proposal: transparent 0, skin 1–4, costume 5–8, secondary 9–11,
accent 12–14, outline 15. Parts sharing a role may need incompatible colors;
allocation/shade sharing must be solved per fighter before engine export.
It is not a claim that every part already fits those ranges. Owner-reported
Chun-Li/Zangief/Ryu/Ken targets are distinguished from reference proposals.

## Background follow-up: signatures, boundaries and colors

Darkest shade is palette-dependent: source index 0 must not be assumed darkest
for every BG tile, nor transparent. In 4bpp index 0 transparency requires
remapping formerly opaque dark pixels to an opaque slot. Capture original
palette semantics along with tile data before choosing barriers.

Two barrier thresholds are alternative segmentations for review. Their
component IDs are local to a capture. A scroll-stable key can retain canonical
map/tile coordinates plus tile-content and source-pixel identity; a hash alone
cannot identify semantic objects across repeated tiles. Record all conflicting
uses, and avoid nearest-neighbor inheritance when a dark boundary borders two
different classes. Explicit boundary marks or a neutral reviewed outline are
preferable to accidental color bleeding. Automatic geometry splits of snow or
sky remain proposals until reviewed. No auto-alignment to Saturn art is assumed.

Sixteen independent ramps cannot fit one 16-color palette. With transparent
index 0 and a shared opaque outline, `2 + 4*C <= 16` permits three classes
having four other shades each. If each class instead needs only three shades
plus the shared outline, `2 + 3*C <= 16` permits four. More semantic classes
can share actual colors, or use multiple palettes with a proven map allocation;
they do not each get a free independent ramp. These are capacity equations,
not final stage palettes.

BG/HUD segmentation and all-stage collection are the next capture implementation
work; this PR does not claim to implement `bg_segment.py` or all-stage labels.
The component mark protocol is reusable, but BG barrier/palette interpretation
must be implemented separately from the fighter shade-3 assumption.

## 5. Compatibility risks

Check Color-mode requirement and the advertised target hardware; bank remaps
and ROM expansion; old-save load/write round trips without layout changes;
working SRAM use; glyph/label copy destinations; active OAM limits and flips;
foreground transparency/windows; animated BG/map changes; audio cadence and
actual VBlank/CPU cost. Preserve original saves and record provenance rather
than replacing them with newly generated test data. No save/layout changes are
introduced by this tooling PR.

## 6. Gates and completion evidence

1. Source contracts and exact build identity; do not accept stale diagnostic
   code or unqualified PC offsets as a trace.
2. One confirmed active fighter tile: record SpriteStart/Count, selected index,
   tile, mask, transparency and destination; then broaden.
3. Reuse T07 for unchanged-region pixel equality. For intentional recoloring,
   verify geometry, transparency, expected palette/mask and reviewed parts;
   full-frame equality is inappropriate there.
4. Exercise standing, crouching, attack, jump, flip, overlap, effects and scene
   transitions per fighter; each named part must be checked at thin boundaries.
5. Add all modes, old-save compatibility and measured timing/audio gates before
   release. Do not equate test/tool count with completed game coverage.

Consultation answers and connected annotation workflow are delivered. Final
part accuracy, all-fighter/all-stage captures, BG implementation, palette
allocation and the production engine gate remain open implementation work.
