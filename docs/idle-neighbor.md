The remaining two idle poses are continued in [T28](idle-cycle.md).

# T27: one additional Chun-Li breathing pose

Continue from the owner's preferred T26 hand/cuff colours without redesigning the
base pose. The next source pose is `09b8001e109c1602f4b3d47951121a04` (39x27).
Unlike a uniform sprite translation, its upper/middle body shifts up one row while
the lower rows stay fixed. `idle_neighbor.py` is bound to this exact pair of hashes.
It maps body rows16..28 to source row+1, keeps other rows in place, preserves explicit
black/white exceptional indices, and otherwise retains material while using the new
source shade. Strict same-shade registration handles gaps; eight newly exposed
arm/neck/blue-shoulder pixels were explicitly classified after visual inspection.
Unresolved pixels fail export rather than inventing a label. This mapping is not
a general propagation rule for arbitrary animations.

`full_colour_table.py --idle-neighbor` includes that pose with the original two
fighter poses. Projection retains exact source identity, flips and conflicts.
46 previous records are byte-identical; 10 new records extend the table to 56.
There are no unresolved/conflicting exported pixels. Zangief and the base Chun-Li
pose are unchanged; no palette/runtime code changes.

```
python tools/mock/full_colour_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  work/cuff-table data/palettes/wrist-fixes.json work/idle-next-table --idle-neighbor
PF_HYBRID=1 PF_CLASS_TABLE=work/idle-next-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/idle-next.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

Local preview: `work/idle-next-comparison.png`; runtime evidence and save:
`work/idle-next-runtime-chunli/`. ROM SHA256:
`ab73770f67de4672d838173518fa647da7d7d0c008a853ea4d553aa4a84fc37b`.
The remaining idle drawings have horizontal and vertical changes not covered by
this mapping. They remain unverified, as do walking/attacks. This is not a complete
idle-loop colour patch or owner approval of the new pose.

Real game verification: the next pose was reached through normal frame stepping;
all 18 active tile mirrors and all 679 opaque pixels match. The initial base-pose
screenshot and title are pixel-identical to T26. Save/frame/stop receipts are retained.
Report: `work/idle-next-runtime-verification.json`.

Without `--idle-neighbor`, regenerated CTB3 is byte-identical to T26.
