# T17: character-keyed CTB2 palettes

The legacy CTB2 footer supplied two fixed palettes: changing the selected
fighter could leave Chun-Li's palette on another character. Optional
`PF_FIGHTER_PALETTES` now selects each side's palette from the existing HUD-name
lookup. It requires `PF_HYBRID=1` and `PF_CLASS_TABLE`; legacy builds keep their
original CTB2 footer behaviour.

```sh
PF_HYBRID=1 PF_CLASS_TABLE=work/table.ctb2 \
PF_FIGHTER_PALETTES=data/palettes/ctab-fighters.json \
python tools/build.py work/fighter-palettes.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

The committed palette catalogue contains design colours for Chun-Li and
Zangief from the handover's already-used soft skin ramp, quantized to RGB444.
It is not a new owner approval of every colour. Other recognized fighters use
the neutral fallback until their part groups/palettes are reviewed. An unknown
side also falls back when the other HUD name is recognized. If neither HUD is
recognized, the routine preserves the scene palette path instead of treating
arbitrary tile data as a fight. Catalogue names and RGB444 lengths/ranges are
validated, and ambiguous HUD hashes reject the optional build.

## Integration and storage

No new RAM/VRAM reservation, tile-copy hook or per-pixel check is added. Existing
`V_B1/V_B2` hold character-row pointers from the name lookup. In this optional
mode a normalized FIGHT-active value enables the existing name hashing/cache
path (the old band hook is bypassed under CTB2). Normalization prevents the
counter's decay from invalidating the cache every call.

The unused word at ROM character-row offset 22 points to that character's
32-byte palette. The fallback starts at colour-bank CS:7000, followed by named
palettes; this is ROM, not VRAM address 7000. The catalogue must end before
CS:8000, where CTB2 begins, and scene tables must end before CS:7000. The existing
24-byte row stride and fixed hook entry addresses are retained.

After the existing scene/name colour cache changes, the colour hook installs
the two selected 16-colour palettes at RAM FF80/FFA0 (palettes 12/13). The optional
mode removes the old per-copier-call fixed-palette rewrite. The footer remains
in CTB2 for binary compatibility but is not used for palette choice in this
mode. Tile mask lookup/format and exact-source collision checks are unchanged.

## Validation and scope

Three focused tests validate catalogue rejection without mutation and execute
the actual assembled colour entry: both side assignments, character swaps,
missing/unregistered names, unchanged-name cache reuse, and neither-name-known
scene preservation. The existing six CTB2 and two startup tests also pass.
Default build SHA-256 remains
`1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`.

Fresh emucap/Mednafen before/after captures: five title/menu/story screenshots
are pixel-identical. Fight changes 1536 pixels within (32,84)..(194,123), with
all pixels outside that rectangle unchanged. The captured Ryu/Ibuki use neutral
fallbacks; the test table is a local diagnostic table, not reviewed full-body
colour masks. This verifies palette selection, not completed colourisation.

Per-character palette selection does not fix missing/wrong class masks or
resolve same-source semantic conflicts between fighters. Full reviewed tables,
remaining fighters, fades/all-mode lifecycle and final colour QA remain open.

Direct runtime palette-RAM verification also passed for P1 Chun-Li and P1
Zangief: all 16 words matched their catalogue palettes; P2 Ken selected the
neutral fallback. Cached row pointers were E30/E18 and ED8/E18 respectively.
The first Zangief observation was still the fighter-entry intro (FIGHT=0,
no fighter sprites), so no character override was expected. Loading its saved
state and advancing 120 frames reached active combat and the correct palette.
Selection/fight screenshots, raw palette reads, launch/stop receipts and saves
are retained locally. All three probe emulator generations were stopped.
This uses ordinary input and saved-state continuation, not HUD/RAM edits.
