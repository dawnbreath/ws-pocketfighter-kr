# Colour mock-ups (direction only, NOT the engine)
Throw-away scripts used to show the owner what Saturn-style colouring should look like. They read **local captures** (screenshots / `sprdump.json` under `$PF_WORK`, default `work/`, git-ignored) and write PNGs there. No game data is stored here.
- `fighter_mock.py`: per-region colouring of two captured fighter frames (component ids are specific to one capture; production must derive regions by rules — see docs/4bpp-plan.md T12).
- `bgpack_mock.py`: hand-defined regions (polygons) + 5-step ramps for six stage backgrounds and a recoloured HUD (see T14). Polygons are rough by design.
Colour values were designed by looking at public Saturn/official art, not extracted from game files.
