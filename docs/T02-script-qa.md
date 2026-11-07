# T02 Korean script QA

Run `PF_FONT_DIR=/path/to/galmuri/dist python scripts/lint_ko.py --report work/lint.json`.
The font directory can also be repository-local `fonts/`. Requires Pillow, numpy and fonttools.
No ROM is needed. Add `--master text/master.json` to validate local WG byte budgets.
Font SHA-256 used: `e24256f42e43713d2ea086a1e1669d78b968f5b3cc547e5c157f0606ffa5def1` (Galmuri11, 12px).

Verification: 723 canonical records (274 story, 341 fixed, 108 WG), 0 hard errors;
WG byte budgets also passed with locally extracted original metadata. Three focused tests passed.
20 spacing candidates and 77 draft/canonical differences were reported. Regex candidates are
not automatic edits or complete Korean linguistic review. Canonical JSON is the actual build input;
Python drafts are parsed with AST, never executed or silently reapplied.

No canonical string was changed, so no ROM regression claim is made. Suggested edits below
need source/context review and build/runtime verification before application. The linter reuses
build.KR and build.wrap, including per-run 8px rounding, hard SJIS cells and column markers.
Image labels, contextual meaning, control equivalence to Japanese source and full-game coverage
are outside this static lint result. Glyph font identity is recorded for reproducibility.

## Spacing review candidates

| ID | Before | Suggested |
|---|---|---|
| S11#7 | 「(그런데…여름방학이 끝나면 / 정말 돌아가 줄까)」 | 「(그런데… 여름방학이 끝나면 / 정말 돌아가 줄까)」 |
| S19#2 | 「영화라…짐작 가는 데가 없진 않지. | 「영화라… 짐작 가는 데가 없진 않지. |
| S29#0 | 「아야야…알았어요. | 「아야야… 알았어요. |
| S35#0 | 「아야야…사정을 모르는 사람이네. | 「아야야… 사정을 모르는 사람이네. |
| F1_077 | 어린애 같은 분위기에 가슴 파인 / 옷…이 갭이 좋은 걸까… | 어린애 같은 분위기에 가슴 파인 / 옷… 이 갭이 좋은 걸까… |
| F1_078 | 영화 스타? 그것도 좋네 / 산더미 같은 선물…멋져 | 영화 스타? 그것도 좋네 / 산더미 같은 선물… 멋져 |

Leading ellipses (e.g. S02#0) are intentionally left for context review;
a regex flag does not establish that a space is required.

## Draft drift IDs

- `wg.py` / `W02fae0`
- `wg.py` / `W02fb12`
- `wg.py` / `W02fb3e`
- `wg.py` / `W02fbb8`
- `wg.py` / `W02fc54`
- `wg.py` / `W02fc7e`
- `wg.py` / `W02fd74`
- `wg.py` / `W02fdaa`
- `wg.py` / `W02fe32`
- `wg.py` / `W02fe66`
- `wg.py` / `W02fec8`
- `wg.py` / `W02ff0c`
- `wg.py` / `W02ff40`
- `wg.py` / `W02ff80`
- `wg.py` / `W06fe50`
- `wg.py` / `W08f880`
- `wg.py` / `W08f8d8`
- `wg.py` / `W08f95a`
- `wg.py` / `W08fad0`
- `wg.py` / `W08fafc`
- `wg.py` / `W08fb3c`
- `wg.py` / `W08fb6e`
- `wg.py` / `W08fbe4`
- `wg.py` / `W08fcb8`
- `wg.py` / `W08fd00`
- `wg.py` / `W08fd93`
- `wg.py` / `W09feb0`
- `wg.py` / `W0afea0`
- `wg.py` / `W0aff24`
- `wg.py` / `W0bf700`
- `wg.py` / `W0bf730`
- `wg.py` / `W0bf760`
- `wg.py` / `W0bf79c`
- `wg.py` / `W0bf7d6`
- `wg.py` / `W0bf81e`
- `wg.py` / `W0bf8a0`
- `wg.py` / `W0bf8ec`
- `wg.py` / `W0bf92a`
- `wg.py` / `W0bf9b6`
- `wg.py` / `W0bfa02`
- `wg.py` / `W0bfa54`
- `wg.py` / `W0bfaa8`
- `wg.py` / `W0bfacf`
- `wg.py` / `W0bfb48`
- `wg.py` / `W0bfb81`
- `wg.py` / `W0bfba8`
- `wg.py` / `W0cf518`
- `wg.py` / `W0cf792`
- `wg.py` / `W0cf832`
- `wg.py` / `W0cf8d6`
- `wg.py` / `W0cf944`
- `wg.py` / `W0cf9ce`
- `wg.py` / `W0cfa28`
- `wg.py` / `W0cfa7c`
- `wg.py` / `W0cfada`
- `wg.py` / `W0cfb42`
- `wg.py` / `W0cfb86`
- `wg.py` / `W0cfbfc`
- `wg.py` / `W0cfc60`
- `wg.py` / `W0cfcaa`
- `wg.py` / `W0cfd92`
- `wg.py` / `W0cfe08`
- `wg.py` / `W0dfe90`
- `wg.py` / `W0dfefa`
- `wg_fix.py` / `W0afea0`
- `wg_fix.py` / `W0aff24`
- `wg_fix.py` / `W0cf518`
- `wg_fix.py` / `W0cf792`
- `wg_fix.py` / `W0cf832`
- `wg_fix.py` / `W0cf9ce`
- `wg_fix.py` / `W0cfa28`
- `wg_fix.py` / `W0cfa7c`
- `wg_fix.py` / `W0cfada`
- `wg_fix.py` / `W0cfcaa`
- `wg_fix.py` / `W0cfd92`
- `wg_fix.py` / `W0dfe90`
- `wg_fix.py` / `W0dfefa`
