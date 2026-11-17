# T44: Zangief breathing colour candidate

T45 update: the banner blocker below is diagnosed and repaired in
[the atomic copier change](atomic-copier.md). The original T44 results below
remain historical evidence; corrected T45 retains the exact819-record table.

Completion items: (1) identify compatible drawings and compare actual Saturn
materials, (2) connect them to the ROM and verify native output while preserving
existing art, (3) record regression results and preserve restart data. The two
new drawings are integrated and verified; regression has a documented transient
banner difference, so this is a review candidate, not full compatibility approval.

## Drawings and scope

The retained basic pose is d6c38a439bca04684b9f7124e41d052e. Its1269 opaque
pixels, both red wristbands and all existing tile outputs remain unchanged.
Two additional breathing drawings are d31dac2508219dad2b407c584af9ae7d
(46x43,1266 opaque pixels) and d1539bf006207f456e951bd13ea41084
(45x42,1248 opaque pixels). Both are exact source-hash recipes, not automatic
pose propagation or a reapplication of rejected T19/T20 masks.

An actual Saturn training sequence selects P1 Zangief and P2 Ken, then starts
training. The fight/idle04/08/12 screenshots show red wristbands and boots with
red trunks. The WS candidate uses the existing two red ramps: group1 for bands
and boots, group2 for trunks. Hair and beard retain dark skin shading; group2
must not be treated as brown hair. No gold trim or new palette entry is added.
Cross-port frames and pixel shapes are not claimed identical; owner art review
remains pending. Actual screenshots are retained privately, not embedded in Git.

A16-sample source idle capture contains13 coherent samples. Three mixed-tile
transition samples are excluded. The preliminary left/right hold capture still
shows pre-combat breathing; it is not evidence of walking coverage. Walking,
reverse orientation, attacks and further animation drawings remain unverified.

## Integration and actual output

capture_walk.py now selects the named fighter's palette and records its actual
character argument; the default stays Chun-Li. The existing exporter and native
RAM/screenshot verifier gain a Zangief breathing family. No duplicate renderer,
runtime character check, assembly hook, bank switch or VRAM allocation is added.

The CTB3 table grows763->819 records:56 added, all763 old source/output pairs
byte-identical. The41,020-byte table has15,812 bytes free. Both fighter palette
catalogues and the table footer are unchanged. ROM differences are confined to
CTB3 and checksum; original-ROM IPS round-trip and checksum pass. Re-export from
new-ROM runtime captures produces the exact same819-record table.

New-ROM cold boots create their own states; old-ROM states are never loaded into
the new ROM. In13 runtime samples,9 are coherent:8 accepted new-drawing samples
(three1266-pixel and five1248-pixel samples) plus one unchanged1269-pixel basic
pose. Four incoherent transition samples remain excluded. Both new drawings
match every opaque4bpp RAM index and all2514 representative visible screenshot
pixels. No target pixel is hidden, offscreen or opponent-occluded. Exact base
comparison independently matches all1269 old-pose RAM/screen pixels.

## Regression result and its limit

Both selection screens, both saved-start battle screens and Zangief's initial
fight screen are pixel-identical to T41:five complete screens. Chun-Li's initial
fight screenshot differs by237 pixels, only at x88..135/y56..63 in the animated
NO MERCY banner. Repeating the old-ROM cold boot reproduces its old screenshot.
An old/new diagnostic cold boot and four following frames reproduce the delta.
This screenshot is not counted as an identical regression pass.

Native RAM identifies six foreground map entries at row7/columns11..16,
palette7, source slots405..410. Their original staging/2bpp source differs by78
bytes. In both ROMs none matches any CTB3 record; the actual4bpp mirror is the
exact ordinary2bpp expansion, and all240(old)/264(new) opaque banner pixels
match their own source and unchanged palette exactly. This rules out accidental
application of a new Zangief material to the observed strip. It does not measure
or prove identical animation phase/cycle cost; the cause of that source-phase
difference and full-population performance remain open. No unrelated bypass or
hook is added to hide it. T41 remains the stable reference ROM; T44 is separate.

Relevant checks:15 shared capture-registration, recipe-orientation, palette,
composition and cyclic-crop tests pass. Black, py_compile and git diff checks
pass. ROM readback, scope/checksum, table preservation, runtime re-export and IPS
round-trip pass. Unchanged assembly and all-game suites are not repeated.

## Reproduction and restart

Private input artifacts use these paths; executables are environment-specific.
NASM must be on PATH. Existing sources/fonts and original ROM are required.

```
python tools/capture_walk.py work/ball.ws work/ball-zangief-boot/base.mcs \
  work/ball-final-table/full.ctb3 data/palettes/wrist-fixes.json work/T44-idle-source \
  --character zangief --motion idle --settle-frames 240 \
  --frames 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 \
  --read-colour-buffer --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/mock/walk_table.py work/T44-idle-source/capture.json \
  work/ball-final-table/full.ctb3 work/T44-idle-table --motion zangief-idle
PF_HYBRID=1 PF_CLASS_TABLE=work/T44-idle-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T44-zangief.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

Use work/T44_boot.py to create own-ROM Zangief/Chun-Li bases. With the Zangief
base, capture idle/settle240 durations2,4,8,12,20,24,32 into T44-idle-runtime and
34,36,38,40,42,44 into T44-idle-runtime-more, using the new table and ROM.

```
python tools/verify_contact_output.py work/T44-final-checked \
  work/T44-idle-runtime work/T44-idle-runtime-more --family zangief-idle
python tools/mock/walk_table.py work/T44-idle-runtime/capture.json \
  work/ball-final-table/full.ctb3 work/T44-reproduced --motion zangief-idle \
  --additional-capture work/T44-idle-runtime-more/capture.json
python -m unittest tests.test_capture_alignment tests.test_recipe_orientation \
  tests.test_palette_compatibility tests.test_contact_composition tests.test_cyclic_source
```

ROM SHA256:d05169818d907a1828af5a7b0e96daefefc910a324eb9b1d3bbd320c824de7b2.
Table SHA256:95368cf96735e90023351324876a3c00e1ece2ac8b0eaf8c685b4176d09a52de.

Evidence: work/T44-{static-verification,base-qa,banner-qa,screen-regression}.json,
T44-final-checked/, T44-reproduced/, T44-idle-{source,runtime,runtime-more}/,
T44-{chunli,zangief,baseline-chunli}-boot/, T44-banner-{old,new}/ and
saturn-reference/T44-*/. Private restart backup includes original/stable/candidate
ROMs, IPS, tables, fonts/source, own bases and accepted sample states, raw captures,
replay scripts, Saturn source/result states, reports and stop receipts. Saturn
reference states are solid-compressed and member-hash verified; outer ZIP CRC
and uploaded size/parent metadata are verified before handoff. No private backup
links, game graphics, ROM, state or extracted Japanese source are published.

Completion status: items1 and2 complete as a visual candidate; item3's preservation
is complete, but exact transient-banner regression and its phase/cycle explanation
remain open. Owner art approval, genuine walking/reverse/attack coverage, previous
translation limits, font VRAM residency and all-population timing remain open.
Sol/Medium was sufficient; no model escalation.
