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


## Revised region pipeline (T12) — supersedes the "animation roots" idea in phase 1
Finding (mock on captured frames, not committed): segmenting a fighter frame into connected components of the non-outline pixels (outline = 2bpp index 3) gives 25-45 regions per frame that follow the real art outlines. Classifying each component by simple per-character geometry (centroid height/offset from the sprite centre) and colouring per pixel already reproduces "bare skin + red trunks + red boots" (Zangief) and "blue dress + skin + white boots" (Chun-Li) — i.e. the Saturn-style separation the tile-band method cannot do.
Pipeline (no animation-script reverse engineering needed):
1. **Runtime capture** (emucap/Mednafen, scripted bot input per character, thousands of frames): per frame read OAM + VRAM, rebuild each fighter's pixel frame. Dedupe by *tile content hash* (16 bytes → hash).
2. **Segment + classify** per frame (outline flood fill + per-character rules in `data/rules/<char>.json`, rules reviewed on contact sheets).
3. **Mask table**: tile-content-hash → per-pixel class map (a pixel gets the class that wins over all frames where the tile appears; conflicts reported, fall back to the current band method for unmapped tiles).
4. **Engine (Claude)**: convert at the ~10 tile-copy sites (T10): 2bpp tile → 4bpp, class → palette-index offset; per-character 16-colour palettes in `design.py`.
5. **QA**: per-character contact sheets + pixel regression on non-fighter screens.
Coverage risk: poses never captured fall back to bands; capture scripts must cover specials/throws/KO.
