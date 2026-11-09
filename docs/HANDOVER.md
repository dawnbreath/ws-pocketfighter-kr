# HANDOVER: Claude → Codex (owner instruction: "GPT에게 인수인계")

Written by Claude at the owner's request. From now on Codex is the primary engineer for this repository; Claude is not running
unless the owner starts it again. No game data (ROM/saves/graphics/extracted text/palettes taken from game files) is in this repo or in this
document. Read `AGENTS.md`, `docs/4bpp-plan.md` (long, chronological), `docs/project-decisions.md`, `docs/copy-routines.md` first.

## 0. Rules that still apply (and one open question for the owner)
- No game data in git; one branch per task; PRs say task id / what / verification / not done. The owner never relays messages.
- AGENTS.md rule 2 says the *other* agent reviews and merges. With Claude gone nobody can review Codex's PRs. **Owner decision needed:**
  allow Codex to self-merge after its own tests + a documented checklist, or keep merging manual. Until the owner says so, do not self-merge.

## 1. What the owner wants (quality bar, in the owner's words, translated)
- Korean patch (done, see §6) **plus colourisation of the WonderSwan Pocket Fighter for Color WonderSwan at Saturn-Pocket-Fighter level**:
  characters distinguished by *parts* exactly like the Saturn version (e.g. Zangief: only trunks, boots and wristbands red, everything else bare
  skin; Chun-Li: only the top blue, bare arms/hands, brown trousers, white boots/buns). A single colour per character or band/rectangle
  methods were rejected repeatedly. Backgrounds (6 stages seen) must be multi-coloured per object, and the HUD (bars, timer, gem gauges)
  must use Saturn colours. Owner approval of one pose each of Chun-Li and Zangief exists (see §5); everything else is unreviewed.
- Latest owner feedback: the right side of the body (front arm/torso) looked mottled brown vs the left; fixed by a softer skin ramp (§5.4).
  Owner also said automatic painting still has wrong parts, and asked Codex (T19) to find the wrong parts instead of marking poses.
- Second game (Makai Mura WS) is untouched.
- Owner style preference for chat: warm, calm Korean (여보/자기/당신), no metaphors; sources + dates when researching.

## 2. PR / issue map and suggested merge order
| id | state | note |
|---|---|---|
| PR #27 `claude/T17-hybrid-proto` | open | **contains all engine work**; already includes Codex #29/#30/#32/#34/#35 merged locally. Review and merge first (default build is byte-identical to v007, see §3). |
| PR #17 `claude/T04b-sprite-transparency` | open | docs/diag source (OAMTEST, bench), VRAM/CPU analyses, owner decisions |
| PR #19 `claude/T14-mock-tools` | open | direction-only mock scripts (fighter/background); no game data |
| PR #13 `claude/T12-region-pipeline` | open | older plan + `tools/region_mock.py` |
| PR #10 `codex/T05-frame-tools` | draft | superseded by later T12/T15 tooling; close if unneeded |
| issues #31 (T18/T19), #24 (T16), #20 (T15), #14, #12, #8, #4, #3, #1 | open | #31 is the live work thread; others are mostly delivered, close with a comment when appropriate |

## 3. Build identity and commands (reproducible, no game data in git)
Inputs you supply: `orig/pf.ws` (SHA-256 `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`), OFL fonts in `fonts/` (see BUILD.md).
```
python tools/extract.py && python tools/gen_labels.py && python tools/design.py
sh tools/ko_build_all.sh build/pf.ws                       # default build: SHA-256 1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279 (= v007)
PF_HYBRID=1 sh tools/ko_build_all.sh build/hybrid.ws        # 4bpp prototype (no class table: fighters keep plain colours)
PF_HYBRID=1 PF_CLASS_TABLE=work/table.ctb2 sh tools/ko_build_all.sh build/hybrid_ctab.ws   # + per-pixel fighter colours from a CTB2 table
```
Every change so far was verified to leave the default build byte-identical; keep doing that (`%ifdef HYBRID/CTAB`, env switches in `tools/build.py`).

## 4. Architecture of the 4bpp colour path (all behind `PF_HYBRID=1`)
Facts (measured, see 4bpp-plan.md): game tile indices are 9-bit; 4bpp mode (port 0x60=0xC0) reads tile `i` at `0x4000+32*i`; colour index 0 is
transparent for palettes 4-7/12-15 on both layers and sprites (Codex #29, WSdev + Mednafen); the whole game renders with a 4bpp mirror.
In a fight every VRAM tile write comes from the RAM-resident copier (0000:0120..0164, called every second frame, 128 tiles from `SS:0500` to VRAM
0x3800..3FFF = slots 0x180-0x1FF = fighter tiles). Other scenes write tiles in bursts at scene start (writers in `docs/copy-routines.md`).
Pieces (files `src/col.asm`, `src/kr_stubs.asm`, `tools/build.py`, `tools/colorlib.py`, `tools/class_table.py`):
1. **Rolling resync `rsyn`** (called from the VBlank colour hook after init): while `RSY>0` (re-armed on every colour-hook cache change) converts 32 tiles/call of the
   2bpp VRAM into the 4bpp mirror (class 0 = index equals shade). Map-aware opaque expansion: tiles referenced only by opaque palette attrs (0-3/8-11) expand shade 0 → index 4
   (palette entry 4 mirrors entry 0 in the `.p` loop). Tile flags at 0000:8000-81FF, RSY 0x8200, RSC 0x8202, FIGHT 0x8204, FORCE 0x8205. `FDB0-FDB3` is NOT safe scratch.
2. **Copier hook**: `4000:02A4` (originally `jmp far 0000:0120`) → `jmp far 5000:cpstub` (bank-0x15 tail, 22 bytes; story stubs compacted under HYBRID to make room) →
   colour-bank `cphook` at 2000:0500 (fixed) → original copier. `cphook` compares staging vs still-old VRAM per tile, converts only changed tiles (all tiles on the first call:
   `FORCE`) into `0x7000+32*i`; `FIGHT` makes `rsyn` skip slots 0x180-0x1FF while a fight is active. Codex #30 fixed my CALL FAR→JMP FAR bug.
3. **Class table CTB2** (`tools/class_table.py`, Codex #32): magic `CTB2`, count, records `{hash16 (rol3/xor over 8 LE words), exact source16, mask16}` sorted by (hash16, source),
   then two 16-colour RGB444 palettes (12 then 13). In the colour bank at CS:8000 (HYBRID moves the scene list to bank 0x800). `cphook` binary-searches hash16, verifies the equal-hash run
   byte-for-byte, then expands: plane2 = nonzero-pixel & mask-plane2, plane3 likewise → group g gives palette index `4g+shade` (shade 1-3). With a table, the old band hack in `oam:` is bypassed.
   Fighters use OAM fields 4/5 = palettes 12/13 (P1/P2). **Currently the two palettes are fixed test palettes (12 = Chun-Li, 13 = Zangief); choosing them per fighter (name-HUD hash lookup already exists
   in `col.asm` for the band method) is not implemented.**
4. Diagnostics (not in the build): `src/diag/bpp4_oamtest.asm` (Codex-corrected), `src/diag/bpp4_bench.asm` (timer samples are unreliable).

## 5. Colour data pipeline and what is known
### 5.1 Capture and poses
`tools/capture_frames.py` (256 samples/fighter: Chun-Li = down,left; Zangief = down,down,right; Ryu default; Ken right) → `segment_frames.compose` composes the selected side;
translation-normalised unique poses: Chun-Li 76, Zangief 80 in 256 samples (189 if position counts). Top-10 poses ≈ 59 % of samples, top-20 ≈ 75 %. Poses are numbered by capture order
(`tools/mock/propagate_proto.poses`). Specials/throws/hit/KO are not covered by the current route.
### 5.2 Owner-approved seeds (source-only recipe)
`tools/mock/seed_recipe.py` regenerates the approved Chun-Li (pose md5 `91f38eef…`) and Zangief (`d6c38a43…`) masks from a local capture (rules in code; deterministic after Codex #35's tie-order fix).
Class names/ramps: see `tools/mock/fighter_mock.py`.
### 5.3 Propagation techniques tried (T18)
- **Registration transfer** (`tools/mock/register_transfer.py`): excellent between near-identical animation frames (Chun-Li idle variants 1-4: exact looking), useless between different drawings.
- Random forest on one seed (`tools/mock/propagate_proto.py`): plausible layout, material errors on motion poses. Outline-component majority smoothing made results worse (do not use).
- Codex's NumPy nearest-neighbour proposals (`tools/propagate_labels.py`, #33) + `tools/mock/review_round.py` (#35): corrections give small gains; not promoted into tables.
- Saturn art: the `PLxx.PAC` container/palettes are parsed (`tools/saturn_pac.py`); the 0x101 sprite codec was not identified; Saturn pixels are not geometrically registerable to WS tiles. Owner supplied disc + BIOS; Codex captured direct Saturn references (`docs/saturn-reference-qa.md`).
**Conclusion**: quality needs *reviewed seeds per animation cluster* + registration transfer inside clusters + a classifier only as a low-confidence first pass; labelling cost is the real bottleneck.
### 5.4 Palette decisions (values are design choices from public Saturn art, not extracted)
Skin ramp (WS shade 1/2/3): `(246,213,164) (246,184,136) (222,132,88)` — softened so interior shade-3 texture stops looking like dark brown speckle (an alternative `(250,222,176) (244,190,146) (206,120,80)` is equally fine).
Others used in the test table: red `(246,0,0) (180,0,0) (100,0,0)`, pants `(246,0,0) (200,20,20) (115,0,0)`, blue `(131,213,246) (0,98,246) (0,16,148)`, brown `(180,82,49) (131,49,16) (82,32,0)`, white `(246,246,246) (213,213,246) (82,82,197)`.
Group layout per fighter palette: g0 skin(+hair outline), g1 blue/red, g2 brown/pants, g3 white; idx0 transparent. Only 4 groups × 3 shades fit (planes 2/3); a fifth part class cannot be expressed without a format change (e.g. a separate face vs limb skin).
### 5.5 Owner-approved targets (verbatim intent)
Zangief: bare skin; red trunks *groin area only* (thighs skin); red boots; red wristband bands (not the arm beside them). Chun-Li: blue chest/skirt panel with blue outline, bare arms/hands/fists
(incl. upper-right "sleeve" area = skin), brown trousers on the legs, white boots, white hair buns; head-top circles white. Ryu/Ken: gloves/wristbands must be separate from forearm skin.

## 6. Done / not done (condensed)
Done: Korean text (story, fixed records, WONDER GATE), Korean image labels (except label 127 and icons 15/17/18/20/142/172), pause menu, title buttons, colour mode with scene tables (v007), reproducible build,
regression harness (Codex), release packaging tool (Codex), Saturn PAC inspector, 4bpp prototype with copier hook and per-pixel fighter colouring proven in the real game for Chun-Li poses in the table.
Not done / open (priority order):
1. Reviewed fighter tables for all 12 fighters × all poses (T18/T19) and **per-fighter palette selection** (§4.3); poses missing from captures; Ryu/Ken glove separation.
2. 4bpp safety: other modes (story/card battle/gallery/ending), late-drawn text tiles (story page text), shared blank-tile conflict (one tile used opaque on SCR1 and transparent on SCR2 — tile aliasing idea),
   calibrated cycle cost (timer method unreliable), long-run stability, save compatibility (no save was ever supplied; original `.sav` handling in `tools/handoff.py`).
3. Backgrounds (6 stages seen: stairs/mansion, ski, beach-house/elephant, chinatown, bar, toy shop; Saturn also has castle/den/running battle — not confirmed in WS) and HUD colours (T14): plan = tile-hash → class baked at 4bpp copy sites; direction mocks only
   (`tools/mock/bgpack_mock.py`; outline-component method on BG art with per-component classes worked far better than polygons, bar stage proof in 4bpp-plan.md/#20).
4. Background Japanese signs (e.g. 元飯店) were never inventoried (T11).
5. Makai Mura WS (T08/T09) not started.
6. Final QA, release packaging with `.sav` hand-off, README.

## 7. Local artefacts that existed only in Claude's sandbox (gone; regenerate)
Captures (`/home/user/pf-cap/*`), the 661-record test CTB2, mock images, emulator helper scripts (`emud.py`, route/compare scripts), the older build tree `/home/user/pocketfighter`. Everything needed to regenerate them is in
this repo (capture/segment/seed/propagate/class_table tools + docs). Pixel regression between two cold boots of fights is not meaningful (opponent/stage differ, animated backgrounds): pin the opponent and the frame.
