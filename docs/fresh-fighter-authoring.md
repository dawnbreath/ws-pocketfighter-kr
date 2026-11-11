# T20: fresh Chun-Li and Zangief material authoring

The owner requested a restart after rejecting both Codex's colours and Claude's
historical masks. `tools/mock/fresh_fighters.py` does not import the historical seed
recipe, component labels, random-forest model or registration proposals. It authors
material polygons directly against each original WS monochrome pose. The poses are
identified by source hash, not by an assumed reusable component number.

The completed unit here is two new basic-pose candidates, exported into the existing
4bpp engine and checked in the game. This is not a complete animation colour patch
or a claim of owner approval. Other poses must not inherit these coordinates.

## Visual basis and choices

Reference: actual Saturn Training screenshots under local
`reference/saturn-run/`, default Chun-Li versus Zangief. The source screenshot includes
cream skin, dark brown facial features, blue/white/brown Chun-Li clothing with yellow
trim, and red Zangief equipment with yellow trim. Different poses and resolutions
preclude pixel-equivalence with Saturn.

- Chun-Li: author the bun and hanging white ribbon separately from skin, then blue
  sleeve/apron, brown trousers, wrist detail and boots. Existing dark eye pixels and
  silhouette use brown; internal skin creases use the lighter skin shadow.
- Zangief: separate hair, beard and facial features from body creases. Author trunks,
  boots and both wristbands independently; trace gold trim along selected seams.
- Keep all original source shades and transparent pixels. No geometry is redrawn.
  Polygons assign materials to existing pixels only.
- Four groups remain available for each source shade. For Chun-Li, white material's
  darkest shade uses the blue shadow; its otherwise unused group-3 shade-3 colour
  supplies yellow trim. This is deliberate palette allocation, not a new engine
  check. Zangief has separate skin, red, brown and gold groups.
- Black/dark contours are not applied to every skin crease. The source silhouette
  and face features remain distinct from interior body shading.

This is a new hand-authored interpretation at WS resolution. Small bracelet details,
trim placement and pose-specific material borders still warrant visual review.
No classification accuracy claim is based on the engine merely matching its input.

## Regeneration

```
python tools/mock/fresh_fighters.py CHUNLI_CAPTURE.json ZANGIEF_CAPTURE.json \
  data/palettes/fresh-fighters.json work/fresh-fighters
PF_HYBRID=1 PF_CLASS_TABLE=work/fresh-fighters/fresh.ctb2 \
PF_FIGHTER_PALETTES=data/palettes/fresh-fighters.json \
python tools/build.py work/fresh-fighters.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

The authoring output directory must be new. Local outputs include source,
material and group arrays, preview images, CTB2 and hash-bound report. Never commit them.

The existing exact-source projection handles OAM flips and visibility. Conflicting or
unobserved source pixels omit the entire tile. Its shared record encoder now lives
in `tools/class_table.py`; both the historical exporter and this authoring tool use
it. There are no new assembly branches, RAM allocations or runtime bank switches.

## Local validation and handoff

- Original capture sets: Chun-Li 22 occurrences and Zangief 17 occurrences of the
  respective basic pose. Export: 46 exact-source records, zero omitted tiles.
- Source pose mutation is rejected; generated materials/groups are deterministic.
- Existing exporter/projection/CTB2 tests: 3 + 9 + 6 pass, including emitted assembly
  checks with Unicorn/NASM. The first class-table run skipped 3 checks without those
  dependencies; the full dependency-enabled run passed all 6.
- Trial ROM SHA256: `630568b46af8ae5d02bf2e0bb9af4baab88f283345402a3beae600a4e551198b`.
- Default Korean build SHA256 remains
  `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`;
  original ROM remains `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
- Local files: `work/fresh-fighters-final/`, `work/fresh-fighters.ws`,
  `work/fresh-runtime-chunli/` and `work/fresh-runtime-zangief/`. Runtime directories
  retain actual frame dumps, screenshots, savestates and stop receipts. Earlier trials
  and saves are preserved. No ROM, screenshot, sprite mask or savestate is uploaded.

Actual-game verification: all 18 Chun-Li and 28 Zangief active tiles matched the
exported table. The rendered screenshots matched the independently generated palette
preview on all 677 Chun-Li and 1269 Zangief opaque pixels (zero differences). This
checks integration, not subjective Saturn likeness. Comparison: `work/fresh-comparison.png`.

Regeneration after extracting the shared encoder and formatting the final palette:
`work/fresh-fighters-repro/fresh.ctb2` is byte-identical to the built trial table;
its report binds the final palette file hash. Historical palette/recipe files remain
available for their own earlier trials.

`tools/regress.py capture/compare`: title, menus, story1/2/3 and the unaffected
Ryu/Ibuki fight are pixel-identical to the preceding trial (six screens, zero changed
pixels). This covers the captured route, not all game modes.
