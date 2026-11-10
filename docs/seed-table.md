# T19: seed poses connected to CTB2 and the real game

`tools/mock/seed_table.py` regenerates a bounded trial table from Claude's
source-bound seed recipes and the local original-ROM captures. The default
uses only the known Chun-Li/Zangief seed pose hashes; it does not export the
random-forest proposals as reviewed game data.

```sh
python tools/mock/seed_table.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  data/palettes/ctab-fighters.json work/seed-table
PF_HYBRID=1 PF_CLASS_TABLE=work/seed-table/seed.ctb2 \
PF_FIGHTER_PALETTES=data/palettes/ctab-fighters.json \
python tools/build.py work/seed-palette.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

The output directory must be new and local/ignored: CTB2, labels, source crops,
reports and resulting ROMs contain game-derived data. None is committed.
Reports bind capture, palette and table hashes, selected frames and group maps.

## Projection and export policy

Reuse the existing `segment_frames` source-pixel projection, extracted as
`project_labels` without changing its semantics. OAM flips are undone; clipping
and occlusion remain unobserved; source identity is preserved. Merge observed
group assignments across occurrences, retaining disagreements. A tile is
exported only when every source pixel has one observed group; a conflict or
unobserved pixel excludes the whole tile. No majority vote or guessed fill.
`class_table.pack_table` supplies sorted, exact-source-verified CTB2 records.

Groups: Chun-Li skin0, blue1, brown/hair2, white/silver3; Zangief skin0, red1,
pants2. Mapping hair to the brown group and silver to the white group is an
explicit four-group design reduction, not a fifth palette group or a claim
of exact reproduction of every original mock colour. The recipe's own known
approximation/tie policy remains documented in the earlier handover.

## Local results

Default: 22 occurrences of Chun-Li's one seed pose and 17 occurrences of
Zangief's one seed pose give 46 unique source tiles, 1634 CTB2 bytes; no omitted
source tiles within this bounded set. This recreates the scale of Claude's
lost 46-tile initial experiment, not an assertion of byte identity with it.

Optional `--include-idle-proposals`: direct strict geometric transfer from the
seed to three explicitly identified Chun-Li idle poses, no nearest-label fill.
It gives 50 complete tiles/1770 bytes and excludes 23 tiles with unobserved
pixels. These additional four records are diagnostic proposals; this larger
table was NOT promoted into the runtime test. Source/pose identity alone does
not certify semantic labels, especially across other actions or characters.

## Runtime verification

The default 46-record table was built with the character-keyed palette mode.
Two independent cold boots selected Chun-Li and Zangief with ordinary inputs.
The verifier waited for each exact seed pose hash, read active OAM, original
2bpp VRAM, 4bpp mirror and palette RAM, then compared every selected-side tile's
32 bytes against its source plus exported class planes. Result:

- Chun-Li: 18/18 active tiles hit the table and matched the 4bpp mirror.
- Zangief: 28/28 active tiles hit the table and matched the 4bpp mirror.

Chun-Li matched at the initial fight observation; Zangief required 230 additional
requested step frames after that route's intro. Screenshots show the blue/brown/
white Chun-Li parts and red Zangief trunks/boots/wristbands. Screenshots, raw
frame records, receipts and restart savestates remain local. Both managed
emulator generations were stopped. No HUD, palette or tile RAM was edited to
force the result. Pixel/pose matches are scoped to those observed seed poses.

Three export tests cover plane encoding, unknown/conflict omission and invalid
source/group rejection; nine existing segmentation tests pass after the shared
projection extraction. The default Korean build remains v007 SHA-256
`1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`; the original
ROM hash is unchanged. Full semantic review, other poses/fighters, BG/HUD,
all-mode lifetime/save/timing checks and final packaging remain unfinished.

Six-shot regression against the preceding per-fighter-palette diagnostic build
(PR39): title, menus, story1/2/3 and the Ryu/Ibuki neutral-palette fight are all
pixel-identical (zero changed pixels). This is compatible with the new masks:
all four fallback groups share the same neutral ramp. It does not replace the
separate Chun-Li/Zangief seed-pose checks above. The regression emulator was
also stopped by the harness.

Test ROM SHA-256:
`1fde86e055627e0b8a8fa8ba150b922e314192f2151a3f59e739b8386111be4e`.
Default seed-table SHA-256:
`32d9020038b14d96bbebf8a4aa64987eb8382e5634d2e17378287cacc1c04c50`.
A second regeneration using the finalized tool produced the same table bytes.
