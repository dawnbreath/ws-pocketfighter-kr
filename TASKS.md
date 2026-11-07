# TASKS

| id | task | owner | status | branch / PR | blockers |
|---|---|---|---|---|---|
| T01 | Finish Korean image labels: continue screen (GAMEを再開/終了), composite label 127, fix clipped 통신대전 | Claude | open | – | needs emulator run |
| T02 | Script QA: glossary consistency, line-width lint over `text/ko/*`, spelling/spacing pass (names: 장기에프, 춘리, 사쿠라…) | Codex | open | – | – |
| T03 | Release packaging script (xdelta3 + IPS, CRC/SHA of base and patched, README) | Codex | open | – | final ROM |
| T04 | 4bpp feasibility gate (see docs/4bpp-plan.md §Feasibility) | Claude | gate 1 passed (mode works, ~10 copy routines, VRAM free); prototype pending T05 | claude/T04-4bpp-gate | T05 |
| T05 | Fighter frame dump + region-mask generator (phase 1) | Codex | open | – | user ROM at orig/pf.ws |
| T06 | Per-character palette design sheets for 12 fighters | Codex | open | – | T05 sample |
| T07 | Full-screen regression harness (emucap scripted playthrough → screenshot diff) | Codex | open | – | emucap install per README |
| T08 | Makai Mura WS: structure analysis (text encoding, fonts, VRAM free areas) | Claude | open | – | ROM |
| T09 | Makai Mura WS: translation + colour | both | blocked | – | T08 |

Update this table in the PR that changes a task’s state.
