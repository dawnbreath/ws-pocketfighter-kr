# AGENTS.md — two-agent protocol (Claude Code ⇄ ChatGPT/Codex)

Both agents work **only through this repository**. The human owner does not relay messages.

**Active ownership (2026-11-09, owner instruction): Codex is the primary engineer for
engine hooks, colour data, Korean patch integration and verification. Claude is inactive
unless the owner starts it again. The division table below is historical default ownership;
follow this transfer. Work can continue on task branches without waiting for Claude.**
Read this file, `docs/4bpp-plan.md` and `TASKS.md` before doing anything.

## Hard rules
1. **No game data in git**: no ROM/`.ws`/`.sav`/`.sn1`/savestates, no extracted Japanese text (`text/master.json`, `jp_*.tsv`, `labels_*.json`). `.gitignore` enforces this; never `git add -f` them.
2. Never edit `main` directly. One branch per task: `claude/<task-id>-<slug>` or `codex/<task-id>-<slug>`. Open a PR; the *other* agent reviews and merges. If the other agent is unavailable, leave the PR open (do not self-merge).
3. A PR must say: task id, what changed, how it was verified (commands + result), and what is *not* done.
4. Do not widen scope. Write new findings into `TASKS.md` (or an issue) instead of silently adding work.
5. Keep text hooks narrow: Korean-text code runs only on text paths; colour/OAM code runs only in the VBlank/OAM hooks. Do not add checks to graphics/sound/battle paths.
6. Verification is mandatory for any ROM-affecting change: build, run in Mednafen/emucap, compare against the previous build for unaffected screens (pixel-identical regression), save a short log in the PR.

## Hand-off mechanics
- Task state lives in `TASKS.md` (table: id, owner, status, branch/PR, blockers). Update it in the same PR that does the work.
- To ask the other agent for something: open a GitHub issue labelled `for:claude` or `for:codex` using the issue template, with inputs/outputs/acceptance criteria. The other agent picks it up on its next run (the owner starts each agent; no copy/paste needed).
- Large artefacts (tool outputs, region masks, sprite sheets) go under `data/` **only if derived data is not a copy of game graphics**; otherwise describe how to regenerate them with a script.

## Division of labour (default)
| Area | Owner |
|---|---|
| ROM structure, 68-style V30MZ asm hooks, emulator-driven verification (emucap/Mednafen) | Claude |
| Korean script QA, glossary, line-width/lint scripts, CI checks | Codex |
| 4bpp pipeline tooling (sprite-frame dump, region segmentation, palette authoring) | Codex (tools) + Claude (engine hooks) |
| Release packaging (xdelta/IPS, hashes, README) | Codex |
| Game #2 (Makai Mura WS) analysis | split per `TASKS.md` |

## Conventions
- Python 3.11+, black-style formatting, type hints for new code, no new heavy dependencies without noting them in the PR.
- Assembly: NASM 16-bit, `cpu 186`, comments for every hook explaining the replaced instructions and the register contract.
- Korean text: names per `docs/glossary.md`; 장기에프 (not 자기에프).
