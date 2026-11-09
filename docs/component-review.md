# Local component and pixel review

Run from the repository root; Python 3.11, NumPy and Pillow are already used by
the pipeline. Output contains game-derived pixels and stays under ignored work/.

```sh
python tools/component_marks.py work/chunli/capture.json work/chunli-review --frames 8 40
# Copy marks-template.json to a new local marks file, set reviewer, add marks.
python tools/segment_frames.py work/chunli/capture.json data/rules/chunli.json \
  work/chunli-marked --marks work/chunli-marks.json
```

`components.json` lists local component IDs, pixel area, bounding box and a
content fingerprint. The box is diagnostic metadata; marking a component
paints only its actual flood-filled pixels. The numbered view is 4× nearest
neighbor; coordinates for pixel marks use the original 224×144 frame. Use the
plain `-source.png` view for thin details obscured by numbers.

Within a frame's `marks` list, examples using deliberately synthetic values:

```json
{"kind":"component","component":2,"component_sha256":"copy exact fingerprint from catalogue","label":"white_trim"}
```

```json
{"kind":"pixels","pixels":[[10,20],[11,20]],"label":"wristband"}
```

Labels are explicit names from the exported legend. No meaning is inferred
from paint color or from an earlier conversation. Component hashes and frame
hashes prevent applying marks to another pose. A pixel mark can select opaque
shade-3 outline pixels, e.g. `cloth_outline`; transparent pixels are rejected.
Conflicting marks are errors. If one component mixes skin and wristband, mark
separate pixel subsets instead of assigning the entire component to skin and
then issuing a contradictory wristband mark. Use `unknown` to abstain locally.

The output records mark-file hash, reviewer and marked-frame count. It stays
`engine_ready=false`. Marks override automatic suggestions for that frame;
cross-frame contradictions still become unknown rather than being overwritten.
Semantic labels are not hardware palette indices.

## Verification

Four new synthetic tests verify actual component boundaries, thin pixel marks,
colored outlines, contradictory/mismatched marks, inverse-flip propagation into
the final tile mask, provenance/reviewer checks and the twelve-character part
schema. The existing nine segmentation tests also pass.

Real original-ROM captures: exported frames 8/40 of Chun-Li (36/23 components)
and 8/88 of Zangief (37/19 components). Codex visually inspected Chun-Li frame 8
and labelled component 2's 44-pixel hair-bun interior as white_trim. This is a
Codex review sample, not owner approval or complete character labelling.
The full 256-frame export succeeded: 640 tile hashes, 76 conflicting tiles,
841 conflicting pixels. The additional 44 conflicts against old automatic
priors are retained deliberately, not described as corrected universal masks.
Unmarked Zangief remained at 652 hashes, 30 conflicting tiles and 394 pixels;
all old mask/conflict/unobserved entries were compared for equality.

No new ROM or saves are produced. Capture files remain unchanged and retain
their provenance; existing elapsed_frames metadata has the release-frame
qualification recorded in PR #18 and must not be used as a precise timing
benchmark.

New Ryu/Ken captures use `requested_frames` to make this limitation explicit.
See [route evidence and remaining label coverage](ryu-ken-captures.md).
