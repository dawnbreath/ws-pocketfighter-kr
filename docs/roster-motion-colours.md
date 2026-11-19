# T52 — observed roster walking and standing attacks

This batch extends T51 with source-bound material regions for ten fighters.
It is a review candidate, not completion of every move or owner art approval.
The runtime, all twelve palettes and the prior colour outputs remain unchanged.
No ROM, mask, screenshot, extracted source or savestate is stored in Git.

## Completion checklist

1. Connect the compatible observed motion drawings as one batch: 57 drawings
   across ten fighters, through the existing sixteen hash partitions.
2. Preserve the earlier 1,476 explicit outputs, 490 fallback references, runtime
   code, palettes and unaffected native selection/representative idle output.
3. Verify every registered new drawing against actual 4bpp buffers and
   zero-offset screenshots from independently created candidate-ROM states.
4. Retain original/candidate ROMs, IPS, source/QA captures, matching states,
   references and rebuild inputs in a private restart archive; open a draft PR.

| Fighter | New registered drawings | Observed scope |
| --- | ---: | --- |
| Ryu | 8 | kick preparation, extended punch, steps |
| Ken | 4 | kick preparation and steps |
| Dan | 6 | observed standing kick/punch sequence |
| Sakura | 5 | preparation, punch and a step |
| Gouki | 13 | kick/punch transitions and steps |
| Morrigan | 3 | preparation and extended/retracting attack |
| Lei-Lei | 2 | large kick and punch |
| Felicia | 5 | kick/punch and observed transitions |
| Tabasa | 3 | body-only standing attack sequence |
| Ibuki | 8 | standing kick/punch and movement |

Input names alone do not establish action identity. The first T52 cohort was
captured before controls became active: all four input sequences reproduced the
same entry drawings. That cohort is a negative control, not motion evidence.
Later captures use fighter-specific points in the actual fight. A backwards
input may guard when the opponent is close; this is not labelled universal
backwards walking.

## Source and material limits

The retained actual Saturn selection portraits and animated full-body miniatures
provide material references. They are not frame-identical attack references.
WS silhouettes, alpha and original shade patterns are retained. Only exact
registered cropped-source hashes enable a recipe; unregistered drawings are
rejected offline rather than guessed at runtime.

The exporter retains previous tile outputs and resolves new identical-source
votes in explicit manifest order. `--accept-reference-tiles` is required when
those constraints disagree with initial material polygons. The final NPZ labels,
not the initial polygons, describe the inserted table's actual output. Constraint
counts and adjusted pixels are retained in the private export report. Native
agreement with those labels proves integration, not artistic correctness.

Six initially selected source composites have unobserved opaque tile pixels:
Ryu high kick; Ken high kick and three extended punch variants; Sakura high kick.
They are not certified or filled with guessed hidden pixels. An additional
Gouki punch and two steps share source cells whose material votes conflict with
Ryu's red glove group. Those three drawings are also outside this certification.
Holding a recipe does not freeze a whole unregistered pose: global identical
source tiles can be shared with other poses. Per-fighter material disambiguation
is still needed before these conflicts can be considered solved. No added
runtime character checks or bank switches are introduced in T52.

Tabasa's familiar-bearing drawings, Ibuki's hit flashes, remaining effects,
unobserved strengths, combos, crouch/air/reverse-facing and other moves remain
pending. Earlier translation, font-VRAM residency and hardware timing limits
remain open. A failed interrupted capture is retained separately as aborted;
it does not contribute a verification pass.

## Reproduction

All `work/` inputs below are private and included in the restart archive.

```sh
python tools/mock/roster_table.py work/T52-source-manifest.json \
  work/T51-table work/T51-table/fallback work/T51.ws \
  work/T52-review-table --family motions --accept-reference-tiles
PF_HYBRID=1 PF_CLASS_SHARDS=work/T52-review-table \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
python tools/build.py work/T52-review.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python work/T52_review_static.py
python work/T52_review_native.py
python work/T52_review_preserve.py
```

The existing `basics` family remains the default for both tools. `motions`
selects the new registry; capture ROM identity, fighter HUD identity, strict
registration, hidden-pixel rejection and immutable old outputs keep their
existing checks. No second exporter or verifier was forked.

## Evidence

- Final candidate `work/T52-review.ws`:
  SHA-256 `21b6562085e015580127eae97c831f9ef8d949d69a16cf79cd54d122f82f0cdd`.
  It contains 2,424 stored records and 726 cumulative fallback references.
- The first build passed all 57 drawings: 47,291 representative visible/RAM
  pixels in 166 strict zero-offset samples. 279 incoherent/offset samples
  were excluded; other drawings are not silently counted as covered actions.
- Enlarged art inspection then corrected 241 Morrigan stocking/hair pixels
  across three drawings. Those three drawings were checked again in the final
  ROM from a fresh cold boot and its own states: 2,965 representative pixels
  in 16 matching samples. The other 54 NPZ files and every P1 tile output in
  their 160 retained native samples (1,136 distinct sources) remain identical.
  The final ROM has therefore **not** been recaptured through every earlier
  sample. The initial and final ROMs, labels and capture hashes remain separate.
- All 1,476 T51 stored outputs and 490 protected fallback outputs, the twelve
  palettes and runtime code in every bank are byte-preserved in the final ROM.
  Initial-build regressions cover four old Chun-Li and three old Zangief idle
  drawings/6,504 pixels and ten pixel-identical selection screens. The final
  Morrigan selection screen is also pixel-identical.
- Final table/fallback/labels/provenance re-export is byte-identical across
  92 files. Original-to-final IPS round trip and checksum/palette/bank readback
  pass. The default basics exporter still reproduces 67 original data files,
  and its retained native replay covers all 35 prior basics.
- Four palette tests and four occlusion tests pass. Contact verification keeps
  its isolated-source default, including hidden pixels. Roster verification
  explicitly retains opponent occlusion, matching how its labels were authored;
  it does not claim those hidden pixels as certified art.

Full initial-build capture reproduction uses the private
`T52_native_complete.py`, `T52_capture_followup.py`,
`T52_capture_old_followup.py`, `T52_capture_last.py` and `T52_verify.py`.
`T52-initial-recipe.py` exactly preserves that initial recipe's hash; use it
with the exporter API to reproduce the initial data. The current public motion
recipe produces the final review table. Capture helpers require fresh output
directories; retain the archived evidence when making a new capture run.

The private restart archive retains the original, both evidence ROMs, final IPS,
matching states, initial/final labels, source/native captures, actual Saturn
references, translations, fonts, scripts and per-member hash manifest. It is
kept in the owner's existing Drive folder; no private URL or game asset is
published in the draft PR. Owner art approval and the specific source/material
limits above remain pending.
