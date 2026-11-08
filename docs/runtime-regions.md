# T12: runtime capture and region proposals

This connects a cold-boot emucap route to local OAM/VRAM snapshots, outline
components, character-specific geometric rules, tile-content hashes and a
conflict-preserving mask table. It changes no game or engine code.

## Run

Python 3.11, Pillow and NumPy are required. Reuses `regress.MCP` for transport
and `wsgfx.tile2` for decoding. Use the original PF ROM (SHA-256
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`);
the route deliberately rejects other builds. Each output directory must be new.

```sh
python tools/capture_frames.py /local/pf.ws work/chunli --character chunli \
  --samples 256 --emucap-mcp /local/emucap-mcp --mednafen /local/mednafen
python tools/segment_frames.py work/chunli/capture.json \
  data/rules/chunli.json work/chunli-masks
python tools/capture_frames.py /local/pf.ws work/zangief --character zangief \
  --samples 256 --emucap-mcp /local/emucap-mcp --mednafen /local/mednafen
python tools/segment_frames.py work/zangief/capture.json \
  data/rules/zangief.json work/zangief-masks
python -m unittest discover -s tests -p test_segment_frames.py -v
```

Keep all captures, screenshots, masks and contact sheets in ignored `work/`.
The checked-in rules contain only heuristic boxes and semantic names, not game
pixels. The public repository must not receive generated output.

## Capture contract and observed verification

Fresh emucap home, original ROM, no imported save or savestate. OAM and VRAM
are read at a frozen frame boundary; a screenshot may represent the previous
latched frame, so it is an identity/scene check, not a pixel-equality oracle.
The report retains ROM/emulator hashes, actions, elapsed frame counts, graphics
registers, OAM base/start/count, raw memory and the exact managed-launch stop
receipt. Incomplete runs do not pass the segmentation input check.

Selection from the initial Ryu position: Chun-Li = down, left; Zangief = down,
down, right. Down alone selects Sakura: an initial probing run caught this
and was excluded. Both final selection portraits and battle HUDs were visually
checked. Sample 224 screenshots still show the corresponding fighters in battle.
Official emucap/Mednafen 1.0.0 was used. Both managed instances stopped cleanly.

| Character | Samples | Captured elapsed frames | Unique tile hashes | Empty samples | Conflicting tiles | Conflicting pixels | Pixels without a label observation |
|---|---:|---|---:|---:|---:|---:|---:|
| Chun-Li | 256 | 2671–3691, every 4 | 640 | 0 | 73 | 797 | 6049 |
| Zangief | 256 | 2688–3708, every 4 | 652 | 0 | 30 | 394 | 9611 |

The action loop samples idle, attacks, crouch, jump and movement. These are
**samples, not 256 unique poses and not all moves**. No percentage of total
animation coverage can be claimed from this route.

Nine synthetic tests pass (including conflict-source provenance): stale/empty OAM, active-table wrapping, coordinate
wrapping, priority across fighter sides, inverse horizontal/vertical flips,
outline components, conflict consensus, end-to-end output/character guard and
truncated memory (some tests cover multiple assertions).

## Mask contract

`masks.json` is scoped by character and input ROM. Each SHA-256 key identifies
16 bytes of 2bpp tile content, **not a ROM address**. A mask has 64 row-major
labels in the tile's original, unflipped orientation; the `labels` dictionary
specifies meanings. Transparent source pixels are label 0. Visible source
shade 3 is provisionally outline. Shades 1/2 form connected components;
component centroids are tested against normalized whole-silhouette rule boxes.
Large, overlapping-rule and screen-clipped components remain unknown.

Only active OAM entries contribute. Earlier entries own overlapping pixels,
including when a different fighter side occludes the selected fighter. Pixel
coordinates wrap modulo 256 and are clipped to the 224×144 LCD. Hidden source
pixels do not receive semantic votes. Multiple labels for one tile pixel are
recorded in `conflicts` and emitted as -1, never silently majority-voted.
Each conflicted pixel also has `conflict_evidence`: for every competing label,
`first_frame` identifies the first contributing capture frame and `sample_count`
counts sampled frames supporting that label. Repeated appearances of a tile in
one frame count once per label. Counts are diagnostic evidence, not confidence
or majority-vote permission. Resolve the frame index through `capture.json`;
the capture and rule hashes identify the exact inputs. Source-label references
were replayed against both real captures, and all existing masks/conflict lists
remained identical after adding this metadata.

`unobserved` means no label observation (including rejected geometry), not
necessarily that the source pixel never appeared onscreen.

`proposals.png` shows per-frame rule proposals **before cross-frame consensus**.
Magenta means unknown, gray transparent, near-black outline. The RGB colors
are debug categories, not production palettes; e.g. Zangief boots use the
shared debug boot color. Read `masks.json` for the conflict-filtered result.

## What is not complete

Both sheets were visually inspected. Standing samples show useful separated
regions, but many attack/jump components are unknown and some geometric
assignments are wrong for transformed poses. These are explicitly
`UNREVIEWED_GEOMETRIC_PROPOSALS`, `engine_ready: false`. Agreement among
heuristics is not proof of anatomical correctness. Manual review or additional
pose-specific evidence is needed before any engine consumption.

Palette-side groups can include effects. This is an OAM compositor, not a full
hardware renderer: BG priority, sprite windows and per-scanline limits are not
simulated. No claim of exhaustive visible-pixel attribution is made. Outline
shade interpretation and semantic labels still need per-pose review.

No ROM hooks, VRAM allocation, production 4bpp palette, font changes or new
save state are included. Source ROM remains unchanged; existing saves remain
untouched. This completes the requested capture-to-proposal tooling bundle,
not the final per-pixel colorization or the production 4bpp feasibility gate.

## Link captured content to ROM source candidates

```sh
python tools/map_region_sources.py /local/pf.ws work/chunli/capture.json \
  work/chunli-masks/masks.json work/chunli-sources.json
```

The capture hash, original ROM hash and character must match the mask report.
The tool searches the entire original ROM at **every byte offset**, including
unaligned and overlapping matches, for each selected-side tile's exact 16 bytes.
Output is local-only and exclusive-create. No alignment, bank or writer is guessed.

Verified on the existing 256-sample captures:

| Character | One candidate | Multiple candidates | No exact match |
|---|---:|---:|---:|
| Chun-Li | 607 | 33 | 0 |
| Zangief | 617 | 35 | 0 |

These are per-character counts. A single candidate is still only a byte match,
not proof of the runtime copy source; `copy_path_verified` and `engine_ready`
remain false. Multiple candidates stay unresolved. This provides offsets for
Claude's copy-site tracing without inserting unreviewed masks or picking an
arbitrary address. Semantic conflicts are not resolved by finding ROM offsets.

Two synthetic tests cover odd offsets, overlapping/repeated matches, no-match
inputs, invalid tile lengths, capture/ROM provenance and exclusive output.
All reported real candidates were re-read from the original ROM and checked
against their tile SHA-256. No ROM or captured pixels are included in git.
