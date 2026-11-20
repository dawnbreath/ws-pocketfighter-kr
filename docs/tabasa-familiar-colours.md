# T57: Tabasa's toothed familiar form, compared with Saturn

The previously unidentified aircraft-like WS composite is a toothed violet form
seen directly in actual Saturn training footage. T57 connects its one completely
observed source: dark violet body, golden eyes, white teeth and the visible robe.
The other related partial composites are not promoted into completed drawings.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Identify source and materials | Actual Saturn training selection, low-attack sequence and moved-left followup show the same toothed form. The selected WS source has zero unobserved required opaque pixels. | Two related sources still have ten unobserved source tiles; the separate T56 Tabasa appendage remains unidentified. Material identification alone does not close those source-visibility limits. |
| Connect the familiar colours | One registered exact hash; 31 canonical records added. Existing CTB4 runtime, palettes, text/font bytes and ROM size unchanged. | Final visual approval; no claim of frame-identical port geometry. |
| Verify actual insertion and regression | 1250 representative actual 4bpp+visible pixels in one zero-offset native sample; missing[]. Existing 180 registered drawings / 591 samples retain actual P1 outputs offline in 14,116 tile comparisons (3511 context/source pairs). | Twenty-five incoherent/offset samples excluded. Other unregistered forms are not certified. |
| Retain own-ROM states/restart backup and draft PR | Original/candidate, IPS, source/native captures, matching WS/Saturn states, reference shots and hashes retained privately; draft PR targets T56. | Original Saturn disc remains separate; no game assets/private storage links in Git and no self-merge. |

The source key is `9447fa3e4bd0ae5a2d65c897ebcc14be`. Actual Saturn low-attack
screens show the toothed body, slanted golden eyes and white tooth row. The WS
shade pattern, alpha and silhouette are retained; no image is resized into ROM
tiles. The existing Tabasa palette supplies violet shades, gold shades, white
and opaque black. This is colour integration, not a translation/title edit.

Only that exact hash enables `tools/mock/tabasa_familiar_colours.py`. Immutable
old outputs and explicit exact-source donors constrain the final NPZ label.
Native label agreement proves insertion, not final artistic correctness. Related
unregistered composites can share some newly coloured tiles, but their full
output and unseen opaque pixels are not certified or described as untouched.

Final table: 4513 records (4338 canonical, 175 unchanged Gouki variants), with
1244 protected fallback references. All 4307 parent canonical outputs, all 1244
fallback references and all 175 variants are preserved. Largest partition is
307/1091. No new runtime branch, VRAM allocation or bank-switch instruction.

## Native and reference evidence

The candidate is cold-booted into its own states. Its registered familiar drawing
passes actual 4bpp buffer and zero-offset screenshot checks: 1250 representative
pixels in one matching sample. Old Chun-Li four and Zangief three idle drawings
also pass, 6504 representative pixels. Three relevant selection screens and all
ten cold/initial-battle/followup screenshots are exact against T56, with all
sampled battle buffers equal. This pair has no new screenshot exclusion; prior
T56-specific changes/exclusions remain documented in their own evidence.

The Saturn reference uses the original matching cue graph, firmware and saved
selection state, followed by ordinary training inputs. The moved-left sequence
shows the form clear of the central treasure-chest graphics. Both successful
reference runs stop normally. An initial disk-full launch failed before a game
started and is retained as incomplete, not reference evidence. Space was recovered
only from stopped emulator disc copies whose bytes matched preserved originals.

This closes one previously held T54 source: that observed 101-hash cohort now has
95 registered drawings and six remaining holds. It does not complete Tabasa's
moves, all related familiar frames, physical hardware timing, all-mode RAM,
Gouki P2 native, remaining translation or lower-two-thirds font-VRAM requirements.

## Reproduction from the private restart archive

The source capture belongs to T54; native candidate states belong to T57.
Never cross-load states. Use fresh output directories and adapt emulator/NASM
paths on the restoring machine:

```sh
python tools/mock/roster_table.py work/T57-source-manifest.json \
  work/T56-table work/T56-table/fallback work/T54.ws work/T57-new \
  --family familiar --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T57-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T57-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_sharded_colour_table test_fighter_palettes test_contact_composition
```

Candidate SHA-256:
`e05845023a43769875dc479021741ab92aca7f3da3e84272c8f434408c911ffe`.
Thirteen focused tests and the exact-source hash/alpha/index check pass; unknown
sources reject. Re-export reproduces all 36 table/fallback/label/provenance
files; rebuilt ROM equals the native candidate. Original IPS roundtrip,
checksum and replicated-bank checks pass. Private harnesses retain actual
inputs, stop receipts, report hashes and separate visibility scopes.
