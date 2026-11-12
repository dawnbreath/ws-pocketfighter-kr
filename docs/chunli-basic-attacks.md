# T31: Chun-Li standing kick and punch

This batch completes the three stated items together: basic-attack material
colouring, actual attack output verification, and preservation of existing idle
and movement colours. It covers the first standing attack from a single button
press/hold, including its preparation and return; combos, crouching/jumping
attacks and hit reactions are still pending.

## Source and material decisions

The same pinned fight-start state was allowed 240 frames before each independent
button hold. On WS, A produces the observed standing kick and B the punch. Actual
Saturn reference captures use B for the matching kick and A for the matching punch;
button letters were not assumed equivalent across platforms. References are local
at `/workspace/work/reference/saturn-attacks/` and
`work/saturn-attacks-sheet.png`, `work/saturn-punch-detail.png`.

Six exact source drawings are defined by `tools/mock/attack_colours.py`:

| source crop MD5 | role | opaque pixels |
|---|---|---:|
| da9950a7316768a434213bddb9e5d29c | kick preparation/return | 709 |
| 2f3fbff891144393268a98bedf93bcaf | raised leg | 677 |
| 04e879c18591883671038dd65079cefc | extended kick | 845 |
| a3a756f06beb783c320c9792dcdb0ef8 | punch preparation | 730 |
| 17516aefda8720731530dac523275d52 | punch wind-up/return | 648 |
| 3e9e0c29f78d37334d5b176fc9de7dda | extended punch | 813 |

The oversized punch wrist uses opaque black with white spikes above/below it;
these are cuff studs in the Saturn reference, not skin or a separate hit flash.
Original transparency and shades are retained for skin, blue tunic, brown trousers,
white boots/buns. The raised kicking boot is white beyond the brown leg.

A real source-tile reuse conflict was resolved before insertion: two dark pixels
at the extended boot edge `(37,7)/(38,7)` share their source tile with the trouser
contour `(16,32)/(15,32)` in the same kick drawing. Both uses retain the common dark
outline index3; no positional runtime exception was added. Punch contour `(7,28)`
also retains index3 because that exact tile already exists in T30. The exporter
then reports no unknown/conflicting cells and preserves all existing records.

## Integration

`capture_walk.py --motion attack` and `walk_table.py --motion attack` reuse the
existing capture, ownership/flip projection, table validation and conflict checks.
Attack verification uses exact positions, without the optional dash registration.
There are 120 new table records; all211 T30 records and the palette footer remain
byte-identical. Final CTB3: 331 records /16620 bytes, within the existing bank limit.
Engine assembly, glyph/text paths, VRAM layout and unrelated game assets are unchanged.
Comparing the complete final ROM to T30 finds differences only in the table span
and the two header checksum bytes at `0x3FFFFE..0x3FFFFF`.

```
python tools/capture_walk.py ROM SAME_ROM_IDLE_STATE CTB3 PALETTES OUT \
  --motion attack --frames 2 4 6 8 10 12 16 20 24 32 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/mock/walk_table.py OUT/capture.json \
  work/dash-table/full.ctb3 work/attack-table --motion attack
PF_HYBRID=1 PF_CLASS_TABLE=work/attack-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/attack.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

Candidate SHA256:
`798e270c63265b9d012f4da359f0df28e47284ccf8684e7239eab396bb1a0b09`.
Table SHA256:
`70a52b75ead7a03e8c0acb4fe2e0b76224509008a496e2dc6077cff0f8a07852`.

## Evidence for the completion items

1. **Basic-attack colouring:** all six source-bound masks were compared against
   original shade grids and actual Saturn attacks before insertion. Hand/cuff,
   boot/leg and the shared contour decisions are explicit above. User visual
   approval remains open; pixel agreement is not an approval of the art.
2. **Actual output:** the candidate was cold-booted through the existing selection
   route, then its newly generated base-pose state drove independent attack holds.
   All20/20 captures match. All4422 opaque pixels of the six representative attack
   screenshots equal the authored colours, at zero offset. Both attacks return to
   the already coloured idle drawing. Final ROM table readback at `0xD8000` matches;
   checksum is valid; exporting from final runtime capture reproduces the table.
3. **Preservation:** all four walking and four dash drawings' opaque screenshot
   pixels equal T30 (8 walking and 8 dash regression samples). Six pinned full
   screenshots—title, fight start and four idle drawings—are pixel-identical.
   All211 old table records, including Zangief, are unchanged. Original ROM SHA256
   remains `b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
   Earlier builds/saves remain; new per-sample states and stop receipts are saved.

Local evidence: `work/attack-idle-chunli/`, `work/attack-runtime/`,
`work/attack-walk-regression/`, `work/attack-dash-regression/`,
`work/attack-verification.json`, `work/attack-rom-diff.json`,
`work/attack-game-detail.png`. Game data are not committed. Black, py_compile and
`git diff --check` pass; no assembly change warranted repeating unrelated engine tests.

Sol/Medium remained sufficient; no escalation was needed. Remaining attack families,
contact/combo paths, damage, opposite facing, other fighters, calibrated performance
and general VRAM lifetime/font-residency proof are not completed by this batch.
English/title text remains deferred as requested. This is a review candidate, not
an entire localisation release.
