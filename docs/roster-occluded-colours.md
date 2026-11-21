# T58: recover complete P1 drawings from occluded roster composites

Eight held Ken/Sakura composites reduce to four complete P1 source drawings.
Three further Ken/Ibuki/Morrigan composites match previously registered complete
bodies exactly. Opponent sprites and Ibuki's separate afterimage sprites account
for the differing visible outlines; they are not new body geometry to repaint.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Classify source drawings and required pixels | Four exact complete-source keys; zero missing required opaque pixels and zero offscreen pixels. The authoring captures all belong to T54. Three old exact identities remain controls, not new colour drawings. | Eight original composites remain held: two internally hidden Tabasa sources, Ibuki's streak composite, three Morrigan effects, an unexplained Ryu partial source and Tabasa's unidentified appendage. |
| Connect compatible colours without changing old outputs | Four drawings, 67 new canonical records; all 4338 parent canonical outputs, 1244 fallback references and 175 Gouki variants retained. | Final art approval. Unregistered forms can share new tile outputs; their complete appearance is not certified. |
| Verify native insertion and relevant regression | All four drawings / 3111 representative RAM pixels / ten samples. Separately, 2312 representative visible pixels and 799 hidden pixels; hidden corruption rejects. Old controls and cold regression are detailed below. | 71 source-coherence/offset exclusions; hidden pixels have no unobscured screenshot claim. Five initial battle pixels excluded with identical sampled buffers. |
| Retain own-ROM states/restart backup and draft PR | Original/candidate/IPS, source manifests, native captures, matching states, reference shots and hashes retained privately. Draft stacks on T57; source only in Git. | No self-merge. Prior unobserved moves, P2, hardware timing, text and lower-two-thirds font-VRAM requirements remain open. |

`roster_occluded_colours.py` registers isolated P1 sources explicitly with
`VISIBLE_SOURCE = False`. The manifest must agree. Existing families retain
their visible-source default; a T57 legacy export remains byte-identical across
35 data/label files. The exporter uses its existing exact-source donor path,
without relaxing the requirement to observe every new opaque tile pixel.
Protection manifests also carry their own source-visibility policy.

The native roster verifier passes the family policy to the existing contact
verifier. That verifier checks the actual 4bpp buffer for the complete P1 body
and compares screenshots only where P1 is visible. The comparison sheet labels
the actual screenshot and RAM reconstruction separately. No new compositor,
runtime branch, bank-switch instruction, palette or VRAM allocation is added.

The four registered complete drawings are:

| Fighter | Complete source key |
| --- | --- |
| Sakura | `e2eb9cc0b63934da7e60d778d3c1c1ef` |
| Ken | `81eb8d8eb388ed28b8f52f906d5857f4` |
| Sakura | `d7a496c3794fe905394b98405b1d2660` |
| Sakura | `eb4a6b4dddf770f8ea007ff8ec061cf7` |

## Native evidence and limits

The candidate is cold-booted into its own matching states. Ken's new body
includes a 525-pixel opponent-occluded sample; Sakura also has hidden body
regions. Flipping a class-plane bit in an opaque, hidden Ken pixel causes the
verifier to reject the actual buffer. Ibuki's previously registered body passes
with 465 pixels hidden by separate sprites. Ken/Morrigan's other known-body
controls are observed fully visible; their historical occlusion is not described
as freshly reproduced. The three known controls cover 2418 representative RAM
pixels in 14 samples and add no new colour drawings.

The fourth Sakura drawing did not reproduce at the old 500-frame state offset.
A bounded followup at own-ROM offsets 498/499/501/502 finds two zero-offset
matching samples at 501 and 502. Earlier missing/incoherent samples are retained,
not promoted into successful output evidence.

Old Chun-Li four and Zangief three idle drawings pass native buffer/screen
checks, 6504 representative pixels. Six selection screens, five cold screens
and four post-battle screenshots match the baseline exactly. The initial battle
screenshot differs by five pixels and is excluded; OAM, 2bpp source, staging,
4bpp output, palettes and active sprite range match at that snapshot and at
the following 1/2/4/8-frame snapshots. This is bounded scanout evidence, not
a claim that the initial screenshot is identical or that timing is calibrated.

The previously certified 181 drawings / 592 samples retain all actual P1 tile
outputs offline: 14,149 tile comparisons, 3542 distinct context/source pairs.
This is not a fresh replay of every previous move. Runtime, text/font bytes,
all twelve palettes, ROM size and existing context variants remain unchanged.

Final table: 4580 records (4405 canonical, 175 variants), 1255 fallback references;
largest partition 311/1091. Fifteen focused shard/palette/contact tests pass,
plus four recipe hash/alpha/index checks and hidden-corruption rejection.
All 39 re-export files and the rebuilt ROM match; checksum and original IPS
roundtrip pass. Original ROM SHA-256 remains
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.

The old 101-hash crouch/air cohort has 95 earlier registered visible drawings,
four held outlines now explained through complete-body identities, and two
remaining Tabasa holds. These four outlines are not four additional painted
bodies. Seven of the thirteen T56 held outlines are similarly explained; six
remain held. Neither accounting completes a character's moves.

## Reproduction from the private restart archive

Source captures/states belong to T54; native candidate states belong to T58.
Never cross-load states. Use fresh output directories and adapt tool paths:

```sh
python tools/mock/roster_table.py work/T58-source-manifest.json \
  work/T57-table work/T57-table/fallback work/T54.ws work/T58-new \
  --family occluded --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T58-new \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T58-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_sharded_colour_table test_palette_compatibility \
  test_fighter_palettes test_contact_composition
```

Candidate SHA-256:
`e54e8ee87e3ceeb9981c34a21934269a3f0a411e5cb142cf5f8bfedc52870c57`.
