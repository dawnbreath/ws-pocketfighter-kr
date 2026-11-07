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

## Feasibility gate result (T04, Claude)
Measured on the user's ROM with Mednafen/emucap (v007 build, `PF_BPP4=1 python3 tools/build.py ...` sets port 0x60 = 0xC0):
- **4bpp mode works** in the emulator: a 4bpp planar tile written to VRAM 0x4000 + index*32 and referenced from the FG map renders with 16-colour indices (test pattern shown as vertical stripes); the game's own 2bpp tiles at 0x2000 disappear, as expected — every tile must be mirrored as 4bpp.
- **Tile writers**: a write watch over VRAM 0x2000-0x3FFF through title → menus → story → fight → pause found **30 PCs but only ~10 routines**: the unrolled RAM copier (RAM 0x138-0x164, fed from the stack queue by `4000:02C0`), `5000:AE2E`, `5000:AEA6`, `4000:8F68` (glyph copy, already hooked), `4000:05DD`, `4000:900C`, `4000:916D`, `4000:8FE0`, `4000:8BD8`, `4000:9090`. The unrolled copier alone moved ~4.8k writes in the sample → it is the hot path; per-frame full mirroring (512 tiles × expand) is far too slow (~77k cycles/frame), so mirroring must happen at the copy sites.
- **VRAM budget**: 4bpp tiles live at 0x4000-0xBFFF (tiles 0-1023); this region is unused by the game (verified earlier by write watch), so no overlap — only our colour variables at 0xFD00-0xFDA7 and palette RAM 0xFE00 remain.
- **Still unproven**: (1) BG map entries referencing tiles ≥ 512 (attribute bit 13) are not needed if tile numbers stay < 512; (2) sprite transparency in 4bpp (colour 0 should be transparent for all 16 palettes — to confirm with an OAM test); (3) the mirror hooks must expand using per-tile region masks that do not exist yet (T05).
**Verdict: GO for a prototype, not yet GO for the full conversion.** Next gate = T05 masks for one fighter + hooks for the unrolled copier and 5000:AE2E/AEA6 only, proving one fighter renders with 3+ regions without touching other screens.
