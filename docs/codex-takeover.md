# Codex takeover — 2026-11-09

The owner explicitly assigned Claude's remaining work to Codex. Handover commit
`79c7307` is received; Codex now owns the engine, colour data, Korean integration,
verification and eventual packaging. Claude's local 661-record table and old
sandbox artefacts are unavailable; available source recipes/captures are reused.
Task branches and public PRs preserve reviewability. Work does not wait for
Claude to restart. Original game data and local captures/saves stay out of git.

## Remaining completion criteria and current evidence

| Work | Evidence from this takeover | Still unfinished |
|---|---|---|
| Safe colour engine and integration | First-use FIGHT/FORCE initialization fixed in existing colour entry; copier arriving before entry forces refresh. Actual assembled code: two startup tests fail on old code and pass on fixed code; six CTB2 tests pass. | Per-fighter palette selection, all-mode VRAM/state lifetimes, late text, timing and long-run validation. This is not the 4bpp safety gate. |
| Reviewed character parts and tables | #36 actual-jump review recipe retained. Handover registration tool exercised on local poses; ambiguous equal-score labels now abstain and automatic nearest-label fill removed. | Full top-20 semantic review, all actions/12 fighters, Ryu/Ken gloves, validated collision-safe tables and runtime colour checks. |
| Korean image text, stage and HUD colours | Existing builds and source data preserved. | Label127/icons and stage-sign inventory remain open; background/HUD per-object colouring not complete. English/title-text deferral remains per owner. |
| Regression, saves and release | Default build is byte-identical to v007; before/after hybrid cold-boot route gives six identical screenshots. Original ROM and previously saved Saturn reference state preserved. | Other modes, save compatibility, final package and full output QA. Makai Mura remains unstarted. |

## Initialization change and limits

The existing `entry` first-use block clears the contiguous FIGHT/FORCE bytes.
`cphook` tests the existing initialization magic once on entry, before per-tile
processing; before the colour entry has initialized state, it does not trust
FIGHT or the equal-source shortcut. A copier-before-colour-entry call therefore
refreshes the 4bpp mirror even when staging equals the old 2bpp source. After
normal initialization, the existing dirty-tile path remains in use. No new
per-pixel/per-tile guard, ROM bank switch or unrelated subsystem hook was added.
This removes a dirty-initial-RAM dependency; no retail boot failure had been
claimed. Existing initialized-state magic semantics and the 90-call ownership
heuristic are not a proof of all-mode memory lifetimes.

Build hashes:

- Original: `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
- Default: `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279` (unchanged).
- Hybrid before: `852d62a34538bf48f6e0de8fd3899fab33e7eb84988e552eb007b3eae67f736d`.
- Hybrid after: `8adcf880a22da2cf888c834af0eb6cfddbbc70fb0702f9640cc291dafdfbfad3`.

`tools/regress.py` default six-shot route, emucap/Mednafen 1.0.0, separate fresh
runtime homes, cold boots: title/menus/story1/story2/story3/fight all zero changed
pixels. Fight was visually checked as Ryu vs Ibuki in the bar. These captures
use no class table and establish only this route's regression; class lookup
is additionally covered by the six existing format/assembly tests. Both managed
emulator generations were stopped by the harness. No owner save was supplied;
this does not claim existing-save compatibility.

## Registration handover audit

`register_transfer.transfer` previously resolved equal-score matches by loop
order even when semantic labels disagreed. Such ties now remain unknown; ties
agreeing on one label remain usable. The CLI no longer fills rejected/unmatched
pixels by nearest-label distance. Its output is explicitly partial proposals,
not full-pose approval. Two synthetic tests distinguish conflicting/agreed ties.
Self-transfer exactly reproduced both seed label dictionaries.

Strict transfer coverage from the seed to existing local nearby poses:
Chun-Li poses2/3/4: 546/679, 430/680, 440/685 pixels (80.4%, 63.2%, 64.2%);
Zangief poses2/4: 623/1266, 472/1248 (49.2%, 37.8%). These are coverage, not
correctness; they do not substantiate the handover's broader 80–96% claim for
our independent capture. Unmatched pixels remain explicit gaps.

## Corrections to historical handover claims

`docs/HANDOVER.md` is retained as historical handoff evidence. Its §4 sentence
mixes 2bpp and 4bpp transparency: in 2bpp, palette bit2 controls zero transparency
for the screens; in 4bpp, index0 is transparent irrespective of that old rule.
Its shared-blank-tile explanation is superseded by `t17-transparency-review.md`;
remaining visual issues require their actual layer/attribute evidence. Its
“Korean text done” wording does not close the pending editorial/image/sign QA
items recorded in TASKS. No unverified claim is promoted by accepting handover.

The updated registration CLI was also connected end-to-end on the first eight
existing Chun-Li samples (four normalized idle poses): seed recipe → strict BFS
selection → relaxed geometric matches → local proposals, with no nearest-label
fill. It produced labels for 677/677, 663/679, 653/680 and 662/685 visible pixels
in poses 1/2/3/4, at depths 0/1/3/2. Strict edge coverage along the selected chain
was 80.4%, 75.0%, 92.4% (rounded console values 80%, 75%, 92%); these are chained
proposal coverage, not independent semantic accuracy. Remaining holes persist
and chained labels require review before table export.
