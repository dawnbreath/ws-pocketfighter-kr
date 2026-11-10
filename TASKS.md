# TASKS

| id | task | owner | status | branch / PR | blockers |
|---|---|---|---|---|---|
| T01 | Korean image labels: pause menu DONE (PR #6), clipped 통신대전 fix DONE, composite label 127 + icons 15/17/18/20/142/172 still JP, stage-art background signs not inventoried | Codex | review (regression v006→v007: 10/11 screens identical, pause_open differs as intended) | claude/T01-pause-menu | – |
| T02 | Script QA: glossary consistency, line-width lint over `text/ko/*`, spelling/spacing pass (names: 장기에프, 춘리, 사쿠라…) | Codex | lint verified; editorial review pending | codex/T02-script-qa | full translation/context review remains |
| T03 | Release packaging script (xdelta3 + IPS, CRC/SHA of base and patched, README) | Codex | tooling verified; merged (PR #5) | codex/T03-release | final canonical ROM/runtime approval pending |
| T04 | 4bpp feasibility gate (see docs/4bpp-plan.md) | Codex | PROTOTYPE PENDING: 4bpp mode renders; FG palette-1 colour-0 transparency reported; VRAM safety, SPRITE transparency and one-fighter expansion UNPROVEN | claude/T04-4bpp-gate | diagnostic tile mapping |
| T05 | Fighter frame dump + region-mask generator (phase 1) | Codex | open | – | user ROM at orig/pf.ws |
| T06 | Per-character palette design sheets for 12 fighters | Codex | open | – | T05 sample |
| T07 | Full-screen regression harness (emucap scripted playthrough → screenshot diff) | Codex | harness verified on original; patched regression blocked | codex/T07-regression | needs reproducible v006/candidate and save provenance |
| T08 | Makai Mura WS: structure analysis (text encoding, fonts, VRAM free areas) | Codex | open | – | ROM |
| T09 | Makai Mura WS: translation + colour | both | blocked | – | T08 |

| T13 | Saturn PAC reference inspector | Codex | tool verified on 35 local PACs; review pending | codex/T13-saturn-reference | sprite compression unconfirmed; no frame decoder |

| T10 | Original-ROM tile-copy catalogue | Codex | requested sites catalogued; RAM relocation confirmed; reviewed+merged by Claude | codex/T10-copy-routines | full dynamic ownership/lifetimes and production conversion unproven |
| T12 | Runtime fighter capture → region proposals → conflict masks | Codex | tools verified on Chun-Li/Zangief, 256 samples each; conflict evidence + exact ROM candidate mapping verified; semantic masks NOT engine-ready | codex/T12-runtime-regions | pose review and unresolved pixels; production engine integration remains |

| T15 | Architecture consultation + component/pixel review workflow | Codex | six questions answered; marks connected and verified; 12 reference part lists | codex/T12-component-marks | all-pose/stage coverage, final palettes and VRAM lifetime proof pending |

Update this table in the PR that changes a task’s state.
| T17 | 4bpp hybrid prototype: rolling resync + map-aware opaque expansion + copier hook + class table (PF_HYBRID=1 [PF_CLASS_TABLE], default build unchanged) | Codex | Codex: optional per-fighter CTB2 palette selection connected; startup fix verified; all-mode safety still open | codex/T17-fighter-palettes | class tables for all poses (T18), layer isolation, calibrated cost |

| T19 | Saturn-reference proposal QA | Codex | in progress: actual jump seeds integrated (#36): boot validation 28→19; skin controls 0/33 | codex/T17-takeover | full semantic review/table export and runtime validation pending; spot metrics are not full-pose accuracy |
| HANDOVER | Claude → Codex: Codex is primary engineer (see docs/codex-takeover.md) | Codex | handed over | codex/T17-takeover (based on PR #27) | no branch-work blocker; main merge policy unchanged |
