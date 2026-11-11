# T19: actual Saturn comparison and rejected seed colours

The owner rejected the Chun-Li and Zangief results on 2026-11-11 and preferred
Claude's earlier attempt. The previous seed labels, palette and runtime screenshots
must not be described as visually approved. Exact CTB2/VRAM agreement only proves
that the engine rendered the supplied data, not that those data depict the fighter correctly.

## Evidence and bounded correction

Compared actual Saturn Training gameplay (default Chun-Li versus Zangief,
local `reference/saturn-run/fighters.png`) with both WS seed-pose screenshots.
This is gameplay, not promotional art. Different resolutions and poses make a
cross-platform pixel equality test inappropriate.

Historical source: `adfa9dd`, `tools/mock/fighter_mock.py`, skin ramp
(246,213,164), (230,148,98), (131,49,0). The rejected catalogue instead used
RGB444 `eda,eb8,d85`: its darkest skin colour was bright orange. Eyes, beard and
contours assigned skin consequently disappeared into the body. Restore the early
ramp, quantised to `fda,e96,830`. Restore the historical hair rectangle rule:
only shade 3 is hair; lighter pixels remain skin. No assembly or memory layout changes.

This is a contrast restoration trial, NOT a full reconstruction of the lost original
Claude artefact and NOT a Saturn-matched approved palette. Current four-group mapping
still merges hair with brown clothing and silver with white; the historical mock
had independent ramps. Recolouring every skin shade-3 pixel dark also increases
arm/body mottling, so it does not solve semantic segmentation.

## Visual differences still open

- Chun-Li: the eye and face contour are readable again, but the right arm has excessive
  dark segmentation. Hair, bracelets, blue fabric edges and white highlights need
  separate region review. Do not propagate this seed as approved ground truth.
- Zangief: beard/eye contrast returns, but beard and skin creases still share a ramp.
  Saturn's yellow wristband/boot/trunks trim is absent from the mask. Uniformly
  darkening skin cannot recover it; the part labels need correction.
- Both: only one source-bound pose per fighter is connected. Other animations remain
  unapproved; neither a full colour patch nor all-pose accuracy is claimed.

## Reproduction and validation

Regenerate with `tools/mock/seed_table.py` and build with `PF_HYBRID=1`,
`PF_CLASS_TABLE=<out>/seed.ctb2`,
`PF_FIGHTER_PALETTES=data/palettes/ctab-fighters.json`.
Use the existing Korean/image build arguments from `docs/seed-table.md`.
Local output: `work/saturn-contrast-table` (46 exact-source records),
`work/saturn-contrast.ws`, `work/saturn-contrast-runtime-{chunli,zangief}`.
Each runtime directory retains screenshot, savestate, original frame and report.
Comparison: `work/saturn-contrast-comparison.png`, columns actual Saturn / rejected WS /
restoration trial. Crops are enlarged with nearest-neighbour scaling; image data stay local.

Both real-game seed poses were found: Chun-Li 18/18 and Zangief 28/28 active tiles
matched the new table in VRAM. Three exporter tests pass. Default build remains
SHA256 `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`;
original ROM unchanged. Trial SHA256
`dd2c663d20f7988b72a2349da8ba0812e52f196c6d2e5e0e62c82ccc4f993735`.
The six existing unaffected captures (title, menus, three story screens and the
Ryu/Ibuki fight) are pixel-identical to the previous trial using `tools/regress.py`.
This does not certify the corrected fighters' visual quality.
