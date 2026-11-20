# T56: observed dash-protocol body colours

T56 adds 26 exact source-bound body drawings across eight fighters using the
existing CTB4 runtime and palettes. Ten fighters were sampled; the input protocol
also produces guard, airborne and hit/damage drawings, so this does not certify
complete dashing or all actions.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Classify source drawings and required pixels | 160 source samples across ten fighters; 39 new coherent hashes classified. The selected 26 have no missing required opaque pixels. | Thirteen held: seven partial composites, three ground-effect composites, two unseen-pixel Sakura drawings and one unidentified Tabasa appendage. No held drawing is declared unused. |
| Connect compatible colours without changing old outputs | 26 drawings connected; all 3873 parent canonical outputs, 1152 protected fallback references and 157 old Gouki variants preserved. Existing runtime, twelve palettes, text/font bytes and ROM size unchanged. | Global identical sources can also improve previously unregistered opponent pixels; one explicit eight-pixel change is documented below. |
| Verify native insertion and relevant regression | 26 drawings / 20,829 representative visible+RAM pixels / 66 zero-offset samples, missing[]. Existing 154 drawings' 525 certified samples preserve actual P1 outputs offline in 12,563 tile comparisons (2985 context/source pairs). | Offline preservation is not a fresh replay of every prior move. Final art and full timing remain open. |
| Retain own-ROM states/restart backup and draft PR | Original/candidate, IPS, matching states, source/native captures, references and report hashes retained privately; draft PR targets T55. | No assets/private storage links in Git; no self-merge. |

| Fighter | Registered new body drawings |
| --- | ---: |
| Ryu | 3 |
| Ken | 2 |
| Dan | 3 |
| Sakura | 4 |
| Gouki | 1 |
| Morrigan | 5 |
| Felicia | 1 |
| Ibuki | 7 |

Lei-Lei yielded no new coherent hash in this source sample, which is not complete
move coverage. Tabasa's newly observed drawing is held for material identity.
The initial 29 proposed bodies included two Sakura composites whose opaque
source pixels are unobserved, and a large Tabasa appendage lacking confirmed
material identification. Those three were separated before insertion. The
remaining seven partial and three effect-bearing composites were already held.

Only exact registered source hashes enable the proposals. Actual Saturn portraits
and animated miniatures provide different-pose material references. Source grids
separate exposed skin, clothes, gloves, hair/scarves, fur and tights. Old outputs
and explicitly ordered exact-source donors constrain final NPZ labels; native
agreement proves insertion, not final artistic approval. Gouki reuses context 1,
freezing 473 retained actor sources before adding 18 variants.

Final table: 4482 records (4307 canonical, 175 Gouki variants), with 1244 protected
fallback references; largest partition 306/1091. No engine hook or VRAM change.

## Native regression and the deliberate opponent change

All 26 new drawings pass. A Sakura-only, 22-sample neighbouring-duration followup
resolved two initial missing drawings without changing the ROM. Sixty-one
incoherent/offset samples are excluded. Gouki's new body separately requires
actual context 1: 842 pixels / three matching samples. Old Chun-Li four and
Zangief three idle drawings retain 6504 representative pixels in this candidate.
Ten relevant selection and five cold title/menu/story screens are exact.

Cold battle is **not** wholly pixel-identical. One newly registered shared source
is a shade-3 vertical column; the new group-2 output also applies to P2 Ibuki's
hair/tie edge (slot 483). Its eight pixels change from palette index 3 to 11.
Both ROMs' actual 32-byte tile buffers match their own expected catalogue output.
At the +1 screenshot, exactly those eight actual RGB pixels differ, matching
the preceding latched OAM sample; every other screenshot pixel is identical.
This is an intentional newly coloured source, not a timing-only difference.

The initial screenshot additionally has 23 Ryu scanout pixels excluded from
whole-screen equality. OAM, source VRAM, staging, palettes and sprite start/count
are identical; 4bpp buffers differ only by the eight expected class-plane bytes.
The +2, +4 and +8 screenshots and all sampled buffers are exact. The first and
+1 screenshots are not counted as identical regressions. Private
`T56-cold-regression.json` and `T56-cold-tile-investigation.json` retain the
source hash, actual buffers, RGB coordinates and separate scopes. No calibrated
hardware timing or complete opponent-art claim is made.

## Reproduction from the private archive

Source captures and their matching base states belong to T54; native test states
belong to the candidate T56. Never cross-load similar-named states. Use fresh
output directories and installed NASM/Python/numpy/Pillow/fontTools:

```sh
python tools/mock/roster_table.py work/T56-source-0.json \
  work/T55-table work/T55-table/fallback work/T54.ws work/T56-canonical-new \
  --family dash --accept-reference-tiles
python tools/mock/roster_table.py work/T56-source-1.json \
  work/T56-canonical-new work/T56-canonical-new/fallback work/T54.ws work/T56-new \
  --family dash --context 1 --accept-reference-tiles \
  --protect-manifest work/T51-source-manifest.json \
  --protect-manifest work/T52-source-manifest.json \
  --protect-manifest work/T53-source-manifest.json \
  --protect-manifest work/T54-source-manifest.json \
  --protect-manifest work/T55-source-manifest.json
cp work/T56-canonical-new/labels/*.npz work/T56-new/labels/
PF_HYBRID=1 PF_CLASS_SHARDS=work/T56-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T56-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_sharded_colour_table test_fighter_palettes test_contact_composition
```

Candidate SHA-256:
`f933dcd76fde05e3114d6457b8122b6c7167fd2b368050e998fb71677c14354e`.
Thirteen focused tests and 26 exact-hash/alpha/index checks pass; unknown drawings
reject. Re-export reproduces all 61 final table/fallback/label/provenance files,
and its rebuilt ROM equals the native candidate. Original IPS roundtrip and
checksum pass. Harness paths must be adapted to the restoring machine.

Remaining: held source/material cases, final art approval, unobserved actions,
strengths/facing/effects/modes, Gouki P2 native, simultaneous mixed-owner aliases,
all-mode RAM lifetime, physical hardware timing and earlier text/font-VRAM work.
The next Saturn material investigation is independent of these completed bodies.
