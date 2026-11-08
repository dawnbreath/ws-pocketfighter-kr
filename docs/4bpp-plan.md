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
The user asked to verify the lower 2/3 of VRAM (0x4000-0xFDFF) and use it for Korean font storage. Actual design: Korean glyphs are **streamed from ROM at draw time** (hooked glyph emitters), so no resident Korean font lives in VRAM; this was reported to the user at the time. Measured ranges today: tile VRAM 0x2000-0x3FFF (game), 0x4000-0xFCFF unused by the game (2bpp watch), colour state 0xFD00-0xFDA7 + palette RAM 0xFE00-0xFFFF (ours). If 4bpp is adopted, 0x4000-0xBFFF becomes tile storage; Korean glyph tiles would then also need 4bpp expansion. Claude records the owner's streamed-font/4bpp decision below; VRAM lifetime and overlap verification remain required.

## Coverage note
Background Japanese signs inside stage art were set aside by Claude, not by the user. They are **not** excluded: inventory them (T11) before claiming image-text coverage.

## T04b result: sprite colour-0 transparency in 4bpp (Claude, diagnostic build, local only)
Test: diagnostic ROM (whole-game 4bpp via per-frame tile mirror) plus `OAMTEST`: every P1/P2 fighter sprite's palette field rewritten to 0/1 (palettes 8/9; in 2bpp mode these are *opaque* for colour 0). Cold boot in Mednafen via emucap, scripted navigation to a fight, screenshot at 4x.
Result: both fighters render as shape-accurate silhouettes with **no rectangular opaque boxes**; stage background stays visible inside each sprite's 8x8 cells. => in 4bpp, sprite colour 0 is transparent for palette fields 0/1 as well as field 4 (previous test). Fields 2/3 are not individually tested (same mechanism assumed, to be covered by the production regression).
Not covered: other game modes and screens (the diagnostic mirror breaks non-fight screens by design), real per-pixel masks, VRAM budget with Korean glyph tiles. Decision recorded by the owner: proceed with 4bpp; keep Korean glyphs streamed from ROM (expand glyph tiles to 4bpp at the copy sites, no resident font in lower VRAM).

## T14: stage backgrounds + HUD in Saturn-style colour (owner request)
Measured on a v007 fight (stage with stairs; local capture, nothing committed): BG layer map at 0x1000 uses palette attr 0 for 880/1024 entries (the stage art), palettes 2/3/4 for ~140 entries (props at the edges); 294 distinct BG tiles. The HUD (bars, timer gem, power gauges, names) is the FG layer map at 0x1800, 48 distinct tiles, **all** palette 4. Today every BG pixel goes through one 4-colour ramp per scene -> monochrome tint; every HUD pixel through one teal ramp.
Rewriting map palette attributes per frame is too expensive (>~30k cycles for 1024 words vs ~4k cycles of VBlank). Therefore: bake the colour class into the tile at the 4bpp copy sites (same mechanism as fighters, T12): `tile content hash -> class (0..3 groups x 4 shades in palette 0 / 16-colour palettes)`; per-stage tables built offline from the 12 stage captures; HUD tiles get a fixed class table (health bar yellow, timer gem violet, gem gauges pink/yellow/blue like the Saturn HUD).
Needs from Codex (extension of issue #14): capture every stage's BG/FG tile set (stage = opponent's character: 6 distinct stages seen), classify tiles into 4 groups per stage by position/brightness rules + contact-sheet review.
A screenshot-recolour mock (not an implementation) was shown to the owner for direction only.

**Caveat from Codex review (accepted):** the diagnostic scans all 128 OAM entries (not only `SpriteStart/SpriteCount`), so it may also rewrite stale inactive entries; the screenshot shows both fighters as silhouettes without boxes, which supports but does not *prove* the claim for active sprites only. The claim stays "measured, weakly supported" until the OAMTEST diagnostic is rerun restricted to the active range and reporting selected index/tile. The diagnostic source currently lives in the owner-side working tree, not in the repo.

**Reported T04b rerun and reproducibility correction:** Claude reported 47 of 60 active entries changed, first relative index 13, OAM word 0x4180, with silhouettes and no opaque boxes. However, the published source at c274259 still read ports 5/6, scanned all 128 entries for the first diagnostic tile, and clobbered caller registers under its documented bare-call wiring. Its FD60–FD65 record also overlaps col.asm's V_P/V_K/V_W scratch variables. The reported owner-side run cannot therefore be treated as a reproduction of that published source.

The corrected diagnostic now uses caller CH/CL, selects and rewrites only active entries, wraps within the 128-entry table, preserves the caller, and requires an explicitly reserved DIAG_RECORD. Five isolated NASM/Unicorn synthetic-memory tests pass (the previous code failed all five). These tests establish the routine's memory/register behavior, **not WonderSwan rendering, transparency, timing or VRAM lifetimes**. A reproducible game build, exact route, source/build hashes and a new active-OAM/debug capture are still required before accepting the transparency gate. See docs/diagnostic-review.md.

## VRAM capacity analysis for 4bpp (Claude; reasoning + prior measurements, CPU cost still an ESTIMATE)
- Tile references are **9-bit indices (0-511)** for BG, FG and sprites in this game. In 4bpp each index selects 32 bytes at 0x4000 + index*32, so the full tile set needs exactly **0x4000-0x7FFF (512 tiles)**. The 2bpp area 0x2000-0x3FFF is no longer displayed (kept only as the staging source the game still writes).
- 0x4000-0xFCFF had **0 game writes** in all watched modes (2bpp watch; see §Reconciliation), and the diagnostic ROM that mirrors all 512 tiles to 0x4000-0x7FFF rendered the whole game in 4bpp. => the existing 512-slot payload is **16 KiB**, but free-space/read-lifetime safety and additional slot allocations are not established by a no-write watch: fighters, BG, HUD and Korean glyph tiles all live inside the same 512 indices as today, expanded in place; no extra tile numbers are needed.
- What *does* limit: (a) **index conflicts** — one tile index referenced by two parts with different colour classes cannot hold two different expansions (the 73/30 Codex counts are cross-frame semantic conflicts by content hash, NOT measured simultaneous VRAM-index collisions); resolve by masks that agree, or by giving the part its own index when the game has a free slot (needs T10 slot tables); (b) **CPU**: expanding 2bpp->4bpp at the copy sites. Diagnostic full-mirror = 512 tiles/frame, far too slow; per-tile cost is estimated ~150-250 cycles, i.e. 64 tiles/frame ~ 10-16k of the ~39k cycles per frame. **To be measured** per copy site (count tiles written per frame in fight/story/card-battle) before claiming feasibility; (c) palettes: sprites use palettes 8-15 in 4bpp (16 colours each), BG 0-15 -> enough for P1/P2/effects/HUD, but stage BG needs several class groups in one palette (see T14).
- Korean glyphs: still streamed from ROM into the same tile slots; expansion adds the 4bpp conversion at `glyphcopy`; text is 2-colour, so a fixed 2bpp->4bpp nibble expansion (colour 1 -> index 15, colour 0 -> 0) is enough.
- Gate to close this item: per-frame tile-write counts per mode + cycle measurement of the expanding copy on one real site.

## CPU cost of the expanding copy (measurement attempt, Claude)
Routine tested (`src/diag/bpp4_bench.asm`): per tile, 8 rows of `lodsw` (p0,p1) + per-pixel class bytes (m2,m3 from a ROM mask table) -> `p2 = nz & m2`, `p3 = nz & m3`, `stosw` ×2. 512 tiles with interrupts masked; time from the HBlank timer (1 tick = 1 line = 256 cycles).
- One valid sample (title/early boot): **440 lines ≈ 112,640 cycles for 512 tiles ≈ 220 cycles/tile** for the per-pixel path — consistent with my earlier 150-250 estimate.
- The uniform-class path and the empty-loop reference returned 0-1 lines under the same method, i.e. the timer read is **not reliable** under `cli` in this emulator; those two numbers are NOT valid. Do not use them. (A calibrated method, e.g. counting emulated instructions or a known-delay loop check first, is still needed.)
- Budget: 3.072 MHz / 75.47 fps ≈ 40.7k cycles per frame. At ~220 cycles/tile, allowing 25% of a frame (~10k cycles) ≈ **~45 tiles/frame**; 64 tiles ≈ 14k cycles (35%). Whether this suffices depends on measured tiles written per frame per mode (asked of Codex in issue #20).

**Correction (after Codex review of PR #23):** the first OAMTEST run (47/60 changed) used debug bytes at 0000:FD60..66 that alias `col.asm` scratch (V_P/V_K/V_W) and a call that clobbered caller registers, so that run's *record* is not trustworthy; the silhouette screenshot is only supporting evidence. The corrected diagnostic (`src/diag/bpp4_oamtest.asm` from #23, reserved `DIAG_RECORD`) must be wired into a reproducible experiment and the active-sprite capture rerun before the transparency claim is used as a gate. `src/diag/bpp4_bench.asm` also writes FD70..78 without reservation: treat its 220 cycles/tile as one unreliable sample.

## T04b rerun with Codex's corrected diagnostic (Claude, owner-side build)
Build: owner-side tree with `src/diag/bpp4_oamtest.asm` from PR #23 (`%define DIAG_RECORD 0xFDA8`, `%include`, near `call mirror4` right after `mov ds,ax` in `oam`), defines BPP4=1 BPP4DIAG=1 OAMTEST=1, `tools/build.py ... --img --ko story/fixed/wg`; ROM SHA-256 `088427ba5bf04551928810d03c733a330cc9614cd8222f872693e91aaff96cc6` (derived from the owner's ROM; not committed). Route: cold boot, 900 frames, `start`×3 + `a` taps, 40× `a`, +400 frames (fight). Record at 0000:FDA8 read with emucap each frame for 14 frames; the routine takes >1 frame, so a snapshot may fall mid-call (changed=0 with a stale first/word) — only snapshots after a completed call count:
- count=60 (active entries), start=0: changed=47, first relative active index=13, word 0x4180 (tile 0x180, field 0, H-flip).
- count=58: changed=47, first=11. count=51: changed=39, first=12 (one snapshot mid-call).
Screenshot: both fighters as shape-accurate silhouettes without opaque boxes (fields 0/1 via active sprites). The earlier 47/60 number is thereby reproduced with the corrected source, with DIAG_RECORD not aliasing `col.asm` scratch (FDA8..AD: no `col.asm` define uses it; runtime lifetime of that address in the game is still not proven). => sprite colour-0 transparency for palette fields 0/1 on active sprites: **measured with the corrected diagnostic**; fields 2/3, other modes, VRAM safety, timing remain unproven (no gate pass).
