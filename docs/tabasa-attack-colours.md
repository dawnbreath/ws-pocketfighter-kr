# Tabasa’s attacks and backstep

T62 connects three standing attack drawings, two crouching attack drawings and one backstep. T61 already contains Ibuki’s dash streak. This closes the four colour-authoring holds in the T60 handoff. Ryu’s mixed transition still requires a timing repair and validation.

## Materials and source coverage

The T61 source captures reproduce all six drawings on one cartridge. Three standing poses expose all 234 previously hidden opaque cells in ten tiles shared with the two crouching poses. The exporter votes on identical 16-byte sources with sprite flips and priority resolved. All opaque source pixels have evidence or a protected previous output.

Actual Saturn backstep frames 8 and 12 show the pale sleeve beneath an arched plum cape, the gold cuff and the exposed hand. The pet attack footage shows a blue-grey familiar with red trim and a separate orange phase in the crouching sequence. T62 uses the blue-grey interpretation on the shared WonderSwan familiar tiles. The timing of the Saturn colour alternation on WonderSwan remains an art-review question.

## Colour integration

Tabasa uses selector 3 in the existing CTB4 actor table. A canonical-only export also matched a source used by Zangief. Actor ownership keeps that use intact. Tabasa’s previously unused palette slots 8 and 12 supply the coat and trim. The swatch check covers 227 retained Tabasa source tiles. The older familiar still uses opaque black at slot 4. No assembly instructions, font tiles or VRAM reservations were added.

The exporter retains 4,484 canonical records, 1,312 fallback references and the earlier Gouki and Morrigan variants. The new table has 4,972 records including 131 Tabasa variants. Use the `tabasa-attacks` family with context 3, the T61 base and fallback catalogues, and the retained actor manifests. Re-export from the same inputs produced byte-identical files and ROM.

## Native verification

The T62 cartridge was cold-booted to its own states. The six new drawings matched the actual 4bpp buffer, actor context and LCD screenshot over 29 zero-offset samples. Their representative visible area totals 7,001 pixels. All six matched states reloaded in a separate emulator launch. Fifty-nine samples outside registration or scanout agreement were excluded. The standing attack poses also appeared at different input durations in the two builds.

The older Tabasa controls passed on the new cartridge, including two low/air drawings and the toothed familiar. The four Chun-Li and three Zangief controls matched 6,504 body pixels. All ten cold and follow-up screens matched T61, as did the three checked character selection screens. For wider coverage, 14,511 prior P1 tile and RGB checks on 607 stored samples preserved the output of 189 registered drawings.

The 27 context, shard, composition and palette tests passed. The IPS applied to original SHA-256 `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e` reproduces the 4 MiB T62 ROM with SHA-256 `3d0ddd20de35dc3cbf9edd60fd0d0d6017153867dc24802962cf09826ea232b4`. Physical hardware timing and the lower VRAM font area remain unverified.
