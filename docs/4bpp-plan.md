# 4bpp conversion plan (goal: Saturn-level character colouring)

## Why
In WSC 2bpp mode only sprite palettes 12-15 are transparent and each tile has 4 colours; the original character art
encodes no skin/cloth distinction. Current result (v006): per-character vertical bands + horizontal limits, two
palettes per fighter. Target: per-pixel regions (skin / cloth / boots / hair …) with 16-colour palettes, like WS Final Fantasy.

## Hard facts already established (do not re-derive)
- ROM 2 MiB, mono; we expand to 4 MiB (original at +0x200000). Tools: `tools/build.py`.
- Text all goes through `5000:AFB6`; glyph emitters `5000:AEB4`, `9000:ABF9`. Korean already done via hooks in `src/kr_stubs.asm`.
- Sprites: scripts of commands (`04 base bank 00` / `05 ff ptr`) give piece lists; tiles are copied from ROM to VRAM per piece
  (`4000:E61C`, 16 bytes/tile). OAM is composed in `4000:022C`; our hook at `4000:028D` runs after composition.
- Palettes in mono ports 0x20-0x3F are re-synthesised each VBlank into colour RAM 0xFE00 by `src/col.asm`.
- Fighter identity: hash of HUD name tiles (VRAM 0x3620 P1, 0x36B0 P2) → per-character rows (see `design.py` CHARS).
- 4bpp mode = port 0x60 bits 7+6 (+bit5 packed). Tiles become 32 bytes; BG/sprite tile numbering and VRAM map change (0x4000+ holds tiles 512-1023).

## Phases
1. **Region data (offline, Codex)**: dump every fighter sprite frame (piece lists + 2bpp tiles → composited frames) from the user's ROM; produce a per-frame label mask (skin / cloth / boots / hair / outline) using shade values + geometry heuristics, then human-check sheets. Output = masks keyed by (character, ROM tile address), *not* committed if they embed game graphics; commit the generator + a tiny sample.
2. **Format & palette design (Codex, Claude review)**: per-character 16-colour palettes (reference: Saturn Pocket Fighter as remembered / supplied screenshots).
3. **Engine hooks (Claude)**: intercept the tile copy routines so selected tiles are expanded 2bpp → 4bpp using the masks; add VRAM layout changes; keep text/BG paths unchanged where possible (BG stays 2bpp-compatible by expansion with palette-only colour).
4. **Colourizer rewrite (Claude)**: 4bpp palettes, remove the band/OAM hack, keep scene tables.
5. **QA (both)**: full-screen pixel regression vs v006 for non-character screens; sprite regression per character.

## Feasibility gate
Before phase 3, Claude must prove in a throw-away ROM that one fighter's tiles can be expanded to 4bpp on the fly with correct transparency and no VRAM overlap. If the VRAM budget (BG 0x2000 + 0x4000+ free) forbids it, stop and report; fall back to improving the band method.

## Feasibility gate result (T04, Claude) — PROTOTYPE PENDING
What was measured (user's ROM, Mednafen via emucap, `PF_BPP4=1` test ROM; builds are test-only):
- 4bpp mode (port 0x60 = 0xC0) renders a 4bpp planar tile written at VRAM 0x4000 + index*32 and referenced from the FG map with 16-colour indices (one test tile, stripes). The game's 2bpp tiles at 0x2000 stop being displayed.
- A write watch on VRAM 0x2000-0x3FFF (title → menus → story → fight → pause) hit 30 PCs ≈ 10 routines: RAM copier 0x138-0x164 (fed by `4000:02C0`), `5000:AE2E`, `5000:AEA6`, `4000:8F68` (hooked), `4000:05DD`, `4000:900C`, `4000:916D`, `4000:8FE0`, `4000:8BD8`, `4000:9090`. Write watches only show *writers*, not readers/lifetimes.
Additional measurement (this PR): with `PF_BPP4=1`, an FG-layer tile using **palette 1** (opaque-colour-0 in 2bpp) with pixel value 0 shows the BG layer through it (green BG visible between red FG stripes, colour 0 itself was set to blue) → in 4bpp colour 0 is transparent for a palette that is opaque in 2bpp. This was tested on the FG layer through map writes, NOT on sprites.
NOT proven (do not treat as safe): absence of reads/overlaps in 0x4000-0xBFFF after the mode switch; sprite (OAM) transparency in 4bpp; one fighter expanded with correct regions; BG paths; performance of the expanding copy hooks. The earlier "free VRAM" statement was a 2bpp measurement only.
Next gate (decoupled from T05, per Codex review): apply an explicit diagnostic mask to ONE confirmed fighter tile, prove copy path + transparency + layout under 4bpp, then hand that tile mapping to T05.

## VRAM reconciliation (user requirement vs current design)
The user asked to verify the lower 2/3 of VRAM (0x4000-0xFDFF) and use it for Korean font storage. Actual design: Korean glyphs are **streamed from ROM at draw time** (hooked glyph emitters), so no resident Korean font lives in VRAM; this was reported to the user at the time. Measured ranges today: tile VRAM 0x2000-0x3FFF (game), 0x4000-0xFCFF unused by the game (2bpp watch), colour state 0xFD00-0xFDA7 + palette RAM 0xFE00-0xFFFF (ours). If 4bpp is adopted, 0x4000-0xBFFF becomes tile storage; Korean glyph tiles would then also need 4bpp expansion. This needs the owner's decision before any 4bpp commit.

## Coverage note
Background Japanese signs inside stage art were set aside by Claude, not by the user. They are **not** excluded: inventory them (T11) before claiming image-text coverage.

## T17 hybrid prototype result (Claude; branch claude/T17-hybrid-proto, `PF_HYBRID=1`, throw-away)
Prototype: in the VBlank colour hook, a **rolling 2bpp→4bpp resync** (32 tiles per call, cursor over 0..511, class 0 = index equals the 2bpp shade, runs for 255 frames after every scene/palette change); no copier hook yet. Default build (no `PF_HYBRID`) is byte-identical to v007 (SHA-256 1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279, checked after the change).
Route: T07 14-step route, base v007 vs prototype, cold boots (screens kept local):
- Mechanism works: boot pixel-identical; title, battle select, player select, story text, HUD render in 4bpp; no crashes.
- **Finding 1 — BG colour 0 becomes transparent in 4bpp.** Tiles whose 2bpp shade 0 was an *opaque* BG colour (story border tiles: blue in 2bpp) show the **backdrop colour** instead (brown) after expansion. Hence the expansion cannot map shade 0 → index 0 for BG tiles. Proposed fix: map-aware expansion — tiles referenced by the BG/FG maps (not OAM) expand shade 0 → an opaque index (e.g. 4) whose palette entry duplicates entry 0; sprite tiles keep 0. Needs a map scan at resync (1024 words ≈ 20k cycles, scene change only) and the colourizer to mirror entry 0 into index 4 for BG palettes. Tiles shared between BG and OAM remain a conflict to detect.
- **Finding 2 — fight sprites glitch** (white outline pixels) because slots 0x180–0x1FF are refreshed only by the rolling cursor; the copier hook (every second frame) is required, as predicted.
- **Finding 3 — the opponent/stage differed between the two cold boots** (stairs stage vs ghost-town stage), so fight screens cannot be pixel-compared unless the route pins the opponent.
- Differences by screen (changed pixels): title_press 306, title_menu 224, battle_select 4247, player_select 1721, story 9.5-9.8k, fight/pause ~14-20k.
Not done: copier hook, map-aware BG expansion, palette mirroring, per-frame cost calibration.

### T17 update: map-aware opaque expansion (iterations 2-5, Claude)

**Superseded interpretation:** the layer-specific 2bpp transparency rule below was incorrect. Both SCR1/SCR2 use palette bit 2; palettes 8/9 are opaque. The cited tile-382 references therefore do not prove a mixed-transparency conflict. See [T17 correction and evidence](t17-transparency-review.md). Historical measurements below are retained as observations, not accepted causal explanations.
Changes: (a) palette entry 4 mirrors entry 0 (`.p` loop), (b) tile flag array at 0000:8000 (RSY/RSC variables moved to 0x8200/0x8202 because **0xFDB0-FDB3 is clobbered by the game's stack/RAM use** — the first attempt there corrupted the cursor), (c) map scan at the start of each rolling round (SCR1 refs always opaque, SCR2 refs opaque only for palette attr 0-3 — in 2bpp colour 0 is transparent on SCR2/sprites only for palettes 4-7, never on SCR1), (d) bug found and fixed: `scanop` clobbered `bx` (cursor). Default build still byte-identical to v007.
Route result v007 vs prototype (changed pixels): title_press 528 (bbox: the PRESS START text row), title_menu 753, player_select 942 → 2777 after the layer rule, battle_select 6713, story ~9.3k, fights/pause ~17-24k (copier not hooked).
Analysis of the remaining differences:
1. **battle_select 6713**: colour pairs are symmetric (A→B and B→A in equal counts) = the scrolling wallpaper is at a different animation phase between the two cold boots; not a conversion error. Pixel regression on animated screens needs a pinned frame (same savestate / same frame counter), not just the same input script.
2. **Story border ≈ 9.1k px blue/brown**: cause identified from VRAM: **blank tile 382 (all shade 0) is used as solid fill in SCR1 (attr 9, opaque, brown) *and* as transparent filler in SCR2 (attr 8/9)**. Flag = 2/3 → expanded transparent → the SCR1 fill shows the backdrop instead. This is exactly the shared-tile conflict Codex warned about (T15 §1). One tile slot cannot be opaque and transparent at the same time in 4bpp.
3. Player-select: 1792 px (255,255,255)→(85,34,17): another blank-tile case (white fill via opaque shade 0) — same class of conflict.
Options for conflicts (not implemented): (A) **tile aliasing**: copy the tile into a free slot, expanded opaque, and rewrite the SCR1 map entries to the alias (needs free-slot discovery and breaks if the game rewrites the map later); (B) set the backdrop colour so the transparent result equals the intended fill (only works for one fill colour per scene); (C) per-scene patch of the game's map data. (A) is the general answer; cost ≈ one extra map pass at resync plus the risk of stale maps.
Also found: text tiles drawn after the rolling window expired are stale (story page text partly garbled) → continuous dirty-check resync or a hook at the glyph copy is required.

### T17 review follow-ups (Codex review of 63cbc51, accepted)
- Fixed: `rsyn` was called before the first-use block initialised the prototype state, and RSC was never initialised; the cursor could be arbitrary (Codex's synthetic execution: RSC=511 writes [7FE0,83E0), RSC=FFFF writes [3FE0,43E0) = original tile VRAM). Now: init (RSY=255, RSC=0) happens in the first-use block, `rsyn` is called after it, and the cursor is masked to a multiple of 32 in 0..480 on every call (batch stays inside tiles 0..511).
- Memory contract of the prototype: 0000:8000-81FF tile flags, 0000:8200 RSY, 0000:8202 RSC (0x4000-0x7FFF = 4bpp tile mirror). 0xFDB0-0xFDB3 is **not** safe scratch (observed clobbered); FDA8-FDAD is the diagnostic record of the OAM test only.
- Corrected wording: RSY counts colour-hook invocations, not proven video frames, and the re-arm condition (cache incl. FLAG and HUD hashes) is broader than "scene/palette change"; it is a heuristic, **not a proven scene-load-complete signal**.
- Finding 1 (BG colour 0 / blank-tile conflict) stays a *measured visual discrepancy with a candidate explanation* (tile 382 referenced by SCR1 attr 9 and SCR2 attr 8/9 with opposite transparency needs); layer isolation via DispControl/layer-enable bits and per-layer screenshots is still to be done before the aliasing design is committed.
- The "blanket remap to opaque 4" is applied only per tile with opaque-only references (flag==1); tiles with mixed use are left transparent (flag 2/3), which is exactly where the discrepancy shows.

### T17 update 3: copier hook (Claude)
Added (HYBRID only): the 5-byte far jump at 4000:02A4 (to the RAM copier at 0000:0120) now goes to `cpstub` in the bank-0x15 tail (22 bytes; the story-bank stubs are compacted under HYBRID to make room: 203/204 bytes), which maps the colour bank, calls `cphook` (colour bank 2000:0500, fixed address) and then jumps to the original copier unchanged. `cphook` compares each of the 128 staging tiles (SS:0500+16i) with the still-old VRAM tile (0x3800+16i) and expands only changed tiles (class 0) to the 4bpp mirror at 0x7000+32i (= slots 0x180-0x1FF). Default build rebuilt: SHA-256 1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279 (unchanged).
Result (T07-style route, cold boot, local screenshots): fights, pause menu and later fight frames render correctly in 4bpp — both fighters complete, no white-outline glitches seen earlier; HUD OK. (Stage/opponent still differ between cold boots, so pixel diffs on fight screens are not meaningful; the visual check is the evidence.) Not measured: cycles of the hook (still the unreliable timer), calls during other modes, interaction with the rolling resync when both write the same slots.
Open: shared blank-tile conflict (story border), late-drawn text tiles, stage-start loading order, BG index-0 aliasing, real class masks (Codex PGMD tables), per-pixel palettes.

### T17 update 4: first real-ROM per-pixel fighter colouring (Claude, local test; table not committed)
Pipeline now complete end to end in a test ROM (`PF_HYBRID=1 PF_CLASS_TABLE=<file>`): `cphook` hashes every *changed* staging tile (16-bit rol3/xor), searches the class table in the colour bank (CS=0x2000:8000: count word, entries {hash16, 16 mask bytes = per row m2,m3}, then two 16-colour palettes for palette 12/13), expands to 4bpp with plane 2/3 = `nonzero-pixel mask & m2/m3` (group g → palette index 4g+shade), and writes the two palettes. With a class table the band hack in `oam:` is bypassed (fighters stay on fields 4/5). Default build SHA unchanged (1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279; the CTAB flag and address macros are distinct).
Test data: a 46-tile table derived from the owner-approved Chun-Li/Zangief mock frames (one idle pose each; no conflicts among their pieces); stays local (game-derived).
Result: running the real game, P1 = Chun-Li shows the approved mock in that pose: white hair buns, skin face/arms, blue chest and skirt panel, brown side parts, white boots. Other poses fall back to group 0 (all skin colour) because their tiles are not in the table — this is the expected coverage limit, not a bug. P2 (Ken, palette 13 with Zangief colours) is all skin-coloured for the same reason.
Still open: (1) real tables for all poses/fighters (Codex PGMD + owner-reviewed marks); (2) per-character palette selection by the existing name-hash lookup instead of the fixed 12=Chun-Li/13=Zangief test palettes; (3) binary search / table size (linear scan today); (4) cost calibration; (5) BG/HUD classes; (6) blank-tile conflict and late-drawn tiles.

### T18 findings: coverage and few-shot propagation (Claude, local data; nothing game-derived committed)
- Fresh Chun-Li capture (`tools/capture_frames.py`, 256 samples): **76 distinct poses** when composed frames are compared translation-invariantly (189 if position counts). Tile-hash inheritance from the one approved idle pose covers ~3 % of tiles.
- Random forest (7×7 shade patch + relative x/y) trained on the **one** approved pose (677 px) colours the other poses plausibly at the layout level (white buns/boots, blue panel, brown trousers, skin face/arms) but with clear errors: patchy blue, brown/skin confusion on legs in jump/kick poses, speckle, stray pieces from effects/other sprites in the selected-side composite. Idle variants (#1-#4) are fair, motion poses poor.
- **Per-outline-component majority smoothing made it worse** (components span several parts, e.g. hair+buns+arm), so it must not be used as a blanket post-process.
- Decoding the Saturn `PLxx.PAC` sprite stream was attempted for ~15 min: chunk 0x100 holds 12-byte records only in its first part (offset u16, w, h in tiles, …) and the rest is other tables; the 0x101 codec is not obvious. Dropped; Codex had reached the same conclusion.
- Conclusion: a first-pass auto-colour needs more seed poses per fighter and a review loop; ~76 poses/fighter (more with specials) is reviewable by number. Labelling a pose by components costs several reasoning/review steps; 12 fighters × all poses by hand is not feasible, so tiering is needed (owner-validated main poses first). Tooling requested from Codex in issue #31.

### T18 update: auto-coloured table in the real ROM (Claude, local)
Table format v2 (CTAB): count word, then `count` entries of **32 bytes** `{hash16, 16 mask bytes, 14 pad}` **sorted by hash16** (binary search in `cphook`, ~10 steps instead of a linear scan), then two 16-colour palettes (12, 13). A 661-entry table for Chun-Li (633 tiles from random-forest predictions over the 256 captured samples, 18 approved-pose entries overriding, Zangief's approved pose appended) = 21.2 KB at bank+0x8000. Default build SHA unchanged (1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279).
In-game result (P1 = Chun-Li vs Ken, five frames): idle/walk-like poses show the white buns, blue chest/skirt panel, brown trousers and white boots; a frame with an attack/knock-down shows plain skin colour for tiles that were not in the captured samples (unmatched tiles fall back to group 0). Ken (P2) has no table → skin colour. Remaining coverage problem = poses not present in the capture + classifier errors, not the engine path.
Next: broader/longer captures (more moves) per fighter; a smarter fallback than group 0 for unknown tiles is impossible at runtime without the table, so exhaustive offline coverage is required.
