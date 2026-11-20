# T53: character-specific shared-tile colours

An identical 2bpp source tile can represent Ryu's red glove and Gouki's bare
hand. A global CTB3 output cannot distinguish those materials. T53 adds a
character selector to the existing exact-source lookup and connects three
previously deferred Gouki drawings: one back-view punch and two steps.
The current candidate is for review; it does not complete every fighter's moves.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Context lookup and OAM ownership | Existing OAM hook publishes a 128-byte owner map; existing copier recolours unchanged sources when owner changes. 35 focused tests pass, including P2, wrapping, collision and restoration cases. | Physical hardware, calibrated timing and all-mode RAM lifetime remain unproven. |
| Three Gouki drawings | 37 context-specific records; all 2424 previous stored and 726 fallback outputs preserved, 271 retained Gouki sources frozen. All twelve palettes unchanged. | Art approval, other actions, strengths, facing and effects remain. |
| Integrated native regression | 60 drawings / 49,550 representative visible and RAM pixels / 290 matching samples. Three new drawings independently require actual context 1: 2259 pixels / 11 samples. Old Chun-Li four and Zangief three drawings: 6504 pixels. Twelve selection screens and five cold screens identical; pause/resume five coherent samples and nine shared sources with distinct actual Ryu/Gouki outputs verified. | 385 registration/timing samples excluded from drawing proof. Initial battle scanout has eight different pixels despite identical buffers; next 1, 2, 4 and 8-frame screens are identical. |
| Reproducible handoff | Original, candidate, matching states, tables, IPS, sources, reports and per-member hashes retained in the private restart archive. Draft PR targets the T52 task branch. | No self-merge; game assets stay outside Git. |

## Representation and runtime

CTB4 header is `<4sH>` (`CTB4`, count). Records are 52 bytes:
`<H16sBB32s>` = hash, exact source, selector, reserved zero, 4bpp output.
Selector 255 is the mandatory canonical fallback for each source; 1 selects
Gouki. The representation reserves 1..15, but the current builder rejects
unassigned selectors. Records sort by hash/source/selector, specific before
fallback. Validators reject duplicates, missing canonical rows, invalid hashes,
reserved bytes, alpha and ordering. Capacity is 1091 records per existing hash
partition (sixteen banks); the candidate's largest partition contains 175.

Fighter row byte 21 supplies the selector, reusing cached row pointers. Existing
OAM publication runs before the copier and supplies the new start/count. The
map is keyed by the actual sprite tile slot, not a fixed player range. Low four
bits hold context and bit 7 marks an owner change. The unchanged-source shortcut
then forces only those changed owners through the existing conversion. The
lookup checks the selector within its existing exact-source equal-hash run.
There is no additional bank-switch instruction per converted tile. Scene gate
and map initialisation run outside the tile loop; leaving context restores
canonical outputs. Legacy assembly builds remain byte-identical.

The map occupies RAM 0x8300..0x837F. Baseline read/write watches found no accesses
in 24 pinned states over 90 frames each, and a cold title/menu/story/fight route.
This is bounded runtime evidence, not proof of all-mode lifetime. It does not
establish the user's separate lower-two-thirds font VRAM reservation.
Of 1145 historical OAM tables, no simultaneous cross-player slot alias occurred;
34 slots changed side between frames. New native captures checked 34,474 slot
owners with zero mismatches/aliases. Gouki was exercised as P1; P2 Gouki remains
native-unverified despite emitted-code P2/wrap tests. Simultaneous aliases are
not a solved general case.

The shard reader selects an effective context view; default remains canonical.
Both ordinary roster and walking exporters retain inherited context variants,
including canonical rows needed after compaction. Three real append controls
preserved all sixteen candidate shard blobs. Single-file CTB4 walking export
is rejected instead of silently flattening the variants.

## Reproduction from the private archive

Use the archive's source commit, NASM and Python with numpy/Pillow/fontTools.
Keep own-ROM states with the recorded ROM; never load a T51/T52 state into T53.
Source captures for the recipes belong to T51, protection manifests also retain
older captures. They are offline authoring inputs, not candidate runtime proof.
Use fresh output directories:

```sh
python tools/mock/roster_table.py work/T53-source-manifest.json \
  work/T52-review-table work/T52-review-table/fallback work/T51.ws work/T53-table-new \
  --family gouki-context --context 1 \
  --protect-manifest work/T51-source-manifest.json \
  --protect-manifest work/T52-source-manifest.json --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T53-table-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T53-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_class_table test_full_colour_table test_sharded_colour_table \
  test_fighter_palettes test_context_colour_table test_contact_composition
```

Candidate SHA-256:
`324b0f5a21d8c685e980d6f9561010256e58812c7f7f51452d244ea16749fcd2`.
CTB4 stores 2484 records: 2447 canonical (including mandatory identity rows)
and 37 variants, with 753 protected canonical fallback references. Original IPS
roundtrip, checksum, replicated code and unchanged original game/text bytes pass.
Rebuilt candidate equals the native-tested ROM; non-context build equals T52.

Private native harnesses `work/T53_native.py`, `T53_verify.py`, `T53_static.py`,
`T53_old_qa.py`, `T53_post_pause.py` and `T53_shared_proof.py` retain commands,
stops and actual-RAM evidence. Adapt local emulator paths before a rerun.
The comparison PNG uses visible screenshot pixels only; obscured pixels are
omitted. Saturn is a material reference in a different pose, not frame identity.
The initial eight-pixel cold-battle exclusion is documented by
`T53-tail-regression.json`; it is not counted as a fully identical screen.
English/title, remaining translation, font VRAM and previous art/timing limits
are unchanged. No claim of full move coverage or final visual approval is made.
