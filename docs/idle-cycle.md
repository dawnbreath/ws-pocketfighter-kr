# T28: four-pose Chun-Li idle colouring

T27 covered the base and its nearest breathing neighbour. The two remaining
source drawings (`e9120a9d…`, `177ef003…`) have the upper/middle body displaced
horizontally and lower rows displaced vertically. They are mapped from the T27
neighbour, not from arbitrary animation frames.

`idle_neighbor.author` now validates the exact source/target pair and selects the
matching geometry: source x+1 for target rows0..28, source y-1 for rows29 onward.
It keeps material shading and explicit black/white indices as before. For each new
pose, four newly exposed contour pixels were inspected against the original drawing:
left arm edge, two lower cuff-edge pixels, and trousers/boot junction. Those receive
explicit indices; unresolved or conflicting pixels still fail export. This is a
bounded interpretation of the four original idle drawings, not a general classifier.

`full_colour_table.py --idle-cycle` includes all four Chun-Li poses and the existing
Zangief base pose. All 56 T27 records are byte-identical; 17 new records bring the
CTB3 to 73 records (3720 bytes). No palette, runtime code or VRAM layout changes.
`--idle-neighbor` still generates the exact T27 table, verified byte-for-byte.

```
python tools/mock/full_colour_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  work/cuff-table data/palettes/wrist-fixes.json work/idle-cycle-table --idle-cycle
PF_HYBRID=1 PF_CLASS_TABLE=work/idle-cycle-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/idle-cycle.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

Local preview: `work/idle-cycle-comparison.png`. Runtime captures, transitions,
source frames, per-pose restart savestates and stop receipts:
`work/idle-cycle-runtime-chunli/`. Candidate SHA256:
`ef414d3e227320e4ae6ce6facb471115f6b73409a1e676f7a6de0e1f593d4223`.
Game data are not committed. Walking, attacks, damage poses and other fighters are
not covered by this completion; original saves and earlier candidates remain preserved.
Visual review is not replaced by a table/mirror match.

Real-game cycle observed: 1→2→3→4→3→2→1→2→3, all transition mirrors match.
The four poses use 18/18/16/16 active tiles and all 2721 opaque screenshot pixels
match the intended colours. Both previous pose screenshots, initial base and title
are pixel-identical. Reports: `work/idle-cycle-pixel-verification.json` and runtime
`report.json`; local animation: `work/idle-cycle-game.gif`.
