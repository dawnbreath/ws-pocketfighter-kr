# T07 emucap regression harness

Install the official emucap 1.0.0 core and Mednafen packages; verify their release
hashes and preserve their directory layouts. Python needs Pillow. This tool
speaks MCP stdio directly to the core; it does not need an external `emu.py`,
MCP registration, user input relaying or a desktop session.

```
python tools/regress.py capture orig/pf.ws work/base --emucap-mcp /path/to/emucap-mcp --mednafen /path/to/mednafen
python tools/regress.py capture build/pf_kr.ws work/candidate --emucap-mcp /path/to/emucap-mcp --mednafen /path/to/mednafen
python tools/regress.py compare work/base work/candidate work/comparison
```

Use two **patched** builds for unaffected-screen regression. The above base-vs-
patch example will intentionally report changed pixels. Exit 0 from compare
means identical; exit 1 means difference/error, with details in the report or
traceback. Missing/empty screens, changed screenshot hashes, differing input
sequences or emulator binaries are rejected. No regions are silently masked.

Each run owns a fresh emucap home under its output directory, cold-boots frozen,
records exact inputs, ROM/core/emulator hashes, identities, screenshots and stop
receipts. Only its own launch generation is stopped. Existing output directories
are never overwritten. No saves/states are imported. No user save files were
provided in this session, and save compatibility has NOT been tested. Runtime
homes, logs and captured files remain under ignored work/.

`--sequence file.json` supplies an array of `["wait",frames]`,
`["button",held_frames,after_frames]`, `["shot","unique_name"]` actions.
The default sequence adapts the inherited regress.py route. Visual inspection of
the original confirmed the actual checkpoint meanings (legacy names retained):

| Key | Actual image |
|---|---|
| title | CAPCOM boot logo, not game title |
| menus | Pocket Fighter title menu |
| story1 | Story fade/transition; not readable-dialogue proof |
| story2 | Ryu story with partially printed Japanese dialogue |
| story3 | Ryu story with partially printed Japanese dialogue |
| fight | Ryu vs Chun-Li battle, timer 99 |

These six samples do not establish all menus or complete text output coverage.
Add reviewed routes for changed screens to the same harness as needed.

## Verification performed

Two fresh cold boots of original SHA-256
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`:
all six screens IDENTICAL, zero changed pixels. Both managed generations stopped.
This proves this original-ROM route was reproducible in this environment, not
universal emulator determinism or Korean/4bpp regression safety.

- Core 1.0.0 executable SHA-256: `5defd4cd01dd3554fbc832c2354d79e4a52763df9c47ec0b98bc732269ce869f`
- Mednafen executable SHA-256: `920e59a239f2fcd5610cf67d135a67ab5adff65e0fdce6a15e7b6ca98a80b328`
- Official release: https://github.com/mcpads/emucap/releases/tag/1.0.0
- `python -m unittest discover -s tests -v`: two tests PASS, including identical,
  a single changed pixel, tampered PNG hashes and missing screenshot sets.

No previous v006 patch, reproducible full build assets, or save provenance was
handed over. Candidate-vs-v006 comparison and final Korean/color runtime QA
remain blocked pending Claude's engine handoff (issue #3). No final release was
created. No ROM or screenshot is committed.
