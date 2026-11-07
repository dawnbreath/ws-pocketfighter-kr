# Pocket Fighter (WonderSwan) — Korean patch + colour

Fan translation / colourisation tooling. **No game data is stored here.**
Supply your own dump at `orig/pf.ws` (2 MiB, SHA-256 `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`)
and run `tools/extract.py` once to regenerate the (git-ignored) Japanese text database.

Build: `tools/ko_build_all.sh build/pf_kr.ws` (needs nasm, Python 3, Pillow, numpy, fonttools, the OFL fonts Galmuri / Neo둥근모 in `fonts/`).

See `AGENTS.md` for how Claude and ChatGPT/Codex split the work, and `docs/`.
