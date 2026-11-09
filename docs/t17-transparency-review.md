# T17: correct the 2bpp palette predicate

The screen index does not decide whether 2bpp shade zero is transparent.
For BOTH SCR1 and SCR2, palette bit 2 decides:

| 2bpp palette | Shade zero |
|---|---|
| 0–3, 8–11 | Opaque |
| 4–7, 12–15 | Transparent |

In 4bpp, zero is transparent for every palette. Sprite palette fields are 0–7,
selecting hardware palettes 8–15, so their field bit 2 uses the same predicate.

Sources inspected 2026-11-09:

- [WSdev palette documentation](https://ws.nesdev.org/wiki/Display/Palette),
  “Palette transparency”: explicitly lists both ranges and the 4bpp rule.
- [Beetle/Mednafen renderer](https://github.com/libretro/beetle-wswan-libretro/blob/4b01295838ea89e3f1355bbe4cb5cf98aa6108cd/mednafen/wswan/gfx.c#L350):
  BG and FG 2bpp paths both use `pixel || !(palette & 4)`; their 4bpp paths
  require nonzero pixel. This is corroborating implementation evidence,
  not a new physical-hardware measurement or a pin of our emucap binary.

## Correction

The f327ba8 prototype made SCR1 always opaque and treated every SCR2 palette
>=4 as transparent. Thus it wrongly classified SCR1 palettes 4–7/12–15 and
SCR2 palettes 8–11. Replace both branches with one shared `test al,4` predicate.
The existing per-tile flag union and expansion routines remain unchanged.
Removing the layer discriminator also avoids unnecessary register setup.

The reported story tile 382 with SCR1 palette 9 and SCR2 palettes 8/9 does
**not** prove opposite transparency requirements: all those references are
opaque in 2bpp. The observed screenshot discrepancy remains real, but that
specific aliasing rationale is invalid. Genuine mixed uses can exist, for
example palette 0 versus 12, or a map use versus a transparent sprite use.
Do not allocate alias slots based on the erroneous >=4 classification.

The scanner still does not incorporate active OAM or visibility/window/layer
state, so flag==1 means opaque-only among scanned map references, not among
all live users. This patch fixes the predicate; it does not certify the
prototype's map/OAM ownership, alias allocation or memory lifetimes.

## Scratch and initial state

f327ba8 moves initialization before rsyn and masks the incoming cursor to
0..480 in multiples of 32, addressing the earlier out-of-range batch report.
The shared V_M magic still does not establish migration from older saved state.

Claude reports FDB0–FDB3 was clobbered. No exact write-event trace/PC/SS:SP was
provided here, so the cause cannot independently be identified as the game's
stack. Observing corruption is sufficient to withhold a safe-scratch claim;
it does not establish the replacement 8000–8203 region's all-mode safety.
Request reproducible write-watch evidence and reader/lifetime coverage before
production use. The source comment no longer claims the game never writes the
entire range. scanop uses BP; the clobber contract now includes it.

## Verification

NASM/Unicorn executes the actual scanmap body against synthetic maps, covering
all 16 palette values with both old layer flags, palettes 8/9 sharing a tile,
and a real opaque/transparent conflict. Both tests pass on the correction;
the old source fails both tests (three failing subcases). This tests assembled
memory behavior, not WonderSwan timing.

```sh
NASM=/path/to/nasm python -m unittest discover -s tests -p test_hybrid_map.py -v
```

Build and runtime evidence is recorded in the PR. Diagnostic game data remains
in ignored work/. No production gate or all-game colorization pass is claimed.

### Local build/runtime results

Built with pinned existing v007 fonts/master/labels and `--img --ko
text/ko/story.json text/ko/fixed.json text/ko/wg.json`:

- Default SHA-256: `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`
  (byte-identical to the established v007).
- f327ba8 prototype, PF_HYBRID=1:
  `4fe4faae69a0a8c19091cf4d0dc2fe8a02943259d87df5e845009a842b5d09b4`.
- Corrected prototype, PF_HYBRID=1:
  `31671d1f1da2bd9038680eaa3a893ea55cea126060b0b7691e64979e4c6094a9`.

Three fresh emucap runs used the same short input sequence, no imported save:
wait400; title screenshot; start4+150; start4+120; menus screenshot;
a3+90; a3+120; select screenshot; a3+150; wait60; last screenshot.
All three captures completed and stopped their exact launch IDs.

Corrected vs prior prototype: title and menus identical; select differs only
in the bottom 224×8 strip (1792 pixels), previously brown and now matching the
default image there. All pixels outside that strip match the prior prototype.
The last checkpoint is also identical between prototypes, **but visually still
shows the faded PLAYER SELECT screen**. Its script label `story` is not stage
identity. Thus this run does not validate story borders, later text or fights.

Default comparison: select mismatch drops from 2805 to 1013 pixels, with the
remaining differences outside the repaired strip; menu mismatch remains 553.
Title is identical. Animation/phase mismatch is not isolated here; these are
not whole-screen visual passes. No unrelated prototype rendering defect is
claimed fixed. The corrected map predicate and isolated intended strip change
support this narrow patch, not adoption of the full rolling-resync prototype.
