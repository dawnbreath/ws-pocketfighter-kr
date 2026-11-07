# TASKS

| id | task | owner | status | branch / PR | blockers |
|---|---|---|---|---|---|
| T01 | Korean image labels: pause menu DONE (PR #6), clipped 통신대전 fix DONE, composite label 127 + icons 15/17/18/20/142/172 still JP, stage-art background signs not inventoried | Claude | review (regression v006→v007: 10/11 screens identical, pause_open differs as intended) | claude/T01-pause-menu | – |
| T02 | Script QA: glossary consistency, line-width lint over `text/ko/*`, spelling/spacing pass (names: 장기에프, 춘리, 사쿠라…) | Codex | lint verified; editorial review pending | codex/T02-script-qa | full translation/context review remains |
| T03 | Release packaging script (xdelta3 + IPS, CRC/SHA of base and patched, README) | Codex | tooling verified; merged (PR #5) | codex/T03-release | final canonical ROM/runtime approval pending |
| T04 | 4bpp feasibility gate (see docs/4bpp-plan.md §Feasibility) | Claude | open | – | – |
| T05 | Fighter frame dump + region-mask generator (phase 1) | Codex | open | – | user ROM at orig/pf.ws |
| T06 | Per-character palette design sheets for 12 fighters | Codex | open | – | T05 sample |
| T07 | Full-screen regression harness (emucap scripted playthrough → screenshot diff) | Codex | harness verified on original; patched regression blocked | codex/T07-regression | needs reproducible v006/candidate and save provenance |
| T08 | Makai Mura WS: structure analysis (text encoding, fonts, VRAM free areas) | Claude | open | – | ROM |
| T09 | Makai Mura WS: translation + colour | both | blocked | – | T08 |

Update this table in the PR that changes a task’s state.
