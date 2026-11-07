# Reproducible build (no game data in git)

Inputs you must supply: `orig/pf.ws` — original dump, 2 MiB, SHA-256 `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
Fonts (OFL-1.1, not committed): Galmuri 2.40.3 (npm `galmuri@2.40.3`: Galmuri9/11/14.ttf from `package/dist`) and Neo둥근모 0.5.0 (npm `@kfonts/neodgm@0.5.0`: `package/src/neodgm.ttf`) in `fonts/` or `PF_FONT_DIR`.
Tools: Python 3.11+, Pillow, numpy, fonttools, nasm.

```
python tools/extract.py            # text/master.json (git-ignored Japanese text DB)
python tools/gen_labels.py         # text/labels_all.json, labels_raw.json (git-ignored)
python tools/design.py             # text/color_spec.json from tools/design.py
tools/ko_build_all.sh build/pf_kr.ws
```
Colour mode needs no save/state import. The build is deterministic.

## Build identities (Claude's local builds from the same sources)
| build | contents | SHA-256 |
|---|---|---|
| v006 | colour + Korean + image labels + character regions | `bb956d1f76eeff43d88f0b0e8520dd3d23ac6395f8df39a2bfe5596050d870d0` |
| v007 (T01 candidate) | v006 + Korean pause menu + clipped-label fix | `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279` |

## Regression evidence (T07 harness, emucap 1.0.0 + Mednafen, cold boots)
`tools/regress.py capture/compare` with a 14-step route (boot, title, menu, battle select, player select, story ×2, fight, pause open/closed, later fight): v006 vs v007 → 10 of 11 screens pixel-identical; `pause_open` differs (2803 px, bbox 57,50-168,101) as intended. Scope: captured screens only; not full gameplay QA. Machine-readable result: `docs/regression/v006-v007.json`.

## Saves
No save/state was ever supplied. Builds keep the original SRAM layout (the header save-type byte is unchanged); `.sav` files produced by the owner's earlier runs are copied beside each build by `tools/handoff.py`. Save compatibility has not been tested beyond booting.

## Reproduction check (Claude, branch claude/T01-pause-menu)
A fresh `git worktree` of this branch with `orig/pf.ws` + OFL fonts, running `extract.py → gen_labels.py → design.py → ko_build_all.sh`, produced a ROM with SHA-256 `1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279` — identical to the v007 build above. (v006 is not rebuilt by this branch.)
