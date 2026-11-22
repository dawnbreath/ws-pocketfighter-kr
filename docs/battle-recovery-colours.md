# T73 battle recovery colours

The twelve-fighter replay extends the T72 A+B sampling to holds 37, 41, 46, 52 and 60. Nine additional native drawings have uncovered colour data. Four come from the previous release's intermediate frames and five from the later holds. All nine have matching staged and displayed source pixels, visible P1 tiles and zero LCD offset.

| Fighter | Native input | Hold in frames |
| --- | --- | --- |
| Dan | A+B, after one settling frame | 17 |
| Gouki | A+B | 12, 60 |
| Ken | A+B | 1, 46 |
| Lei-Lei | Quarter-circle A | 45 |
| Lei-Lei | A+B | 37 |
| Ryu | A+B | 46, 52 |

Ken and Gouki reuse their existing stance material regions for one registered hash each. On their turning poses, Ken and Ryu share the garment boundaries and retain their own belt, head and glove colours. Thirty Japanese Saturn game captures show the five fighters' costume colours at six points per input. Animation and input timing differ between the two releases.

## Reproduction

Start with the T72 stage 4 catalogue. Run `tools/mock/roster_table.py --family battle-recovery --accept-reference-tiles` in contexts 0, 1 and 4 with the registered native inputs and relevant previous manifests through T72. All opaque cells in newly authored tiles had visible donors. Set `PF_CLASS_SHARDS` to the resulting stage 4 and `PF_HYBRID=1`. Build using `PF_FIGHTER_PALETTES=data/palettes/roster.json`, `tools/build.py --img` and the three existing Korean JSON inputs. Use `tools/verify_roster_output.py --family battle-recovery` to compare actual LCD and native colour buffers to the reconciled labels.

## Results

- 58 matching native samples. The nine representatives cover 7,141 visible P1 pixels, including 4,331 changes from T72. All nine representative comparisons match outside P1.
- All 328 previous registered drawings retained their tile outputs across 1,489 samples and 37,329 tile uses. The patch adds 139 canonical mappings and 20 Gouki and 34 Ken variants. The final table contains 8,603 entries.
- Ten cold LCD captures and all five graphics-memory samples matched T72. Dan hold 16 and Lei-Lei holds 41 and 43 also matched T72 across the full screen. All 457 changed pixels at Dan hold 18 belong to his newly coloured P1 drawing.
- Gouki's fixed-input A+B replay also samples holds 56–64. Outside P1, holds 58, 59 and 63 match T72. Holds 60, 62 and 64 match the preceding T72 frame outside the union of the compared P1 silhouettes. Holds 56, 57 and 61 have residual differences, including 113 pixels at hold 61 with a different opposing silhouette. The maximum equal-hold difference was 795 pixels.
- Verified twelve roster controls, the seven previous wrist drawings, five Ryu dash drawings and the restored Ryu input replay. Reloaded all 22 supplied states in a fresh emulator. Two independent exports/builds, original-ROM and T72 IPS/xdelta round trips and the private reconstruction all produced `9bd51ab658ece871f3b2e0c6821fcd0c155cf7a841455786378e4adc04fa25f5`. All 103 unit tests passed.

This batch covers the registered P1 drawings. Further moves and opponents, final art approval and real-device timing remain open.
