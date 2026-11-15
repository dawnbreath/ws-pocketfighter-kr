# T39: correct Chun-Li roll materials against Saturn gameplay

Completion items: (1) resolve the material ambiguity with a suitable Saturn
motion, (2) integrate the bounded correction and verify actual output, (3)
preserve unchanged output and a restart backup. This is a visual review candidate,
not owner approval or a claim that the ports have identical animation frames.

## Reference and correction

The previous hammer reference flattened Chun-Li and then showed her rising;
it did not establish the inverted roll anatomy. Two-frame capture of that
recovery and a crouching kick confirms these are different motions. A close
forward+C throw, however, produces clear inverted/rotating Chun-Li footage.
P1 Ken transforms into a bull; P2 Chun-Li remains the comparison subject.
No controller-port workaround or game-data modification is needed.

Starting from the saved training contact state, hold right+C8, then release and
step2 frames60 times. Screens42/43 show folded arms, black cuffs, blue shoulder
puffs, skin fists and white hair ornaments. They provide anatomical counterparts
for the WS roll drawings. The sprites differ between ports; this is manual
material comparison, not a claim of synchronized time or identical frame IDs.
Other reference sequences and their original state/event hashes remain retained.

The original WS material polygons are corrected in place, with no second pass,
nearest-label transfer, palette change or runtime exception. In Roll A, the
rounded shoulder was mistaken for trousers; it is blue, while the adjoining
forearm is skin. In Roll B, a shoulder and fist were mistaken for white trim;
they become blue and skin, and the near cuff boundary follows the wrist.

| Source drawing | Changed opaque pixels |
|---|---:|
|4221c2788e85fc1618ab339e08a3ee6a (Roll A)|73|
|b1f44f9bcd965ea2e3d7a030ee64e151 (Roll B)|74|
|Prone/sitting/rising|0|

Exactly10 of707 CTB3 records change;697 outputs remain byte-identical, including
all637 pre-T38 records. Record keys, palettes and transparency remain identical.
No assembly, bank layout, VRAM, fonts, text or sound changes. Full-ROM comparison
finds86 changed bytes, all in CTB3 or the checksum. Table readback/checksum pass.
This does not complete unobserved hit/contact/KO/combo drawings or other fighters.

## Reproduction

Use the T38 local/Drive source inputs; game images and binary data stay outside
Git. Build with the existing tools, then cold-boot the candidate and create its
own guard state; do not import an older ROM's snapshot.

```
python tools/mock/walk_table.py work/damage-late/capture.json \
  work/defence-preview-table/full.ctb3 work/roll-refined-table --motion damage
PF_HYBRID=1 PF_CLASS_TABLE=work/roll-refined-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/roll-refined.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/capture_walk.py work/roll-refined.ws work/roll-refined-states/guard.mcs \
  work/roll-refined-table/full.ctb3 data/palettes/wrist-fixes.json work/roll-refined-runtime \
  --motion idle --settle-frames 600 --frames 2 36 38 40 74 82 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_reverse_actions.py work/reverse-standing work/reverse-walk \
  work/roll-refined-checked --damage work/roll-refined-runtime
```

NASM must be on PATH. Historical standing/walk captures remain separately
attributed in the shared checker's report; they do not represent new-ROM runs.
Only its damage family is new runtime evidence. The backup retains the concrete
cold-boot/state creation and static verification scripts.

## Results for the completion items

1. Suitable Saturn rotating footage and source-bound edits are complete. All147
   changed source pixels belong to the two roll drawings. The other three damage
   recipes are byte-identical. Geometry/range/transparency checks pass.
2. All5 drawings/2752 representative pixels match in6/6 actual samples, each
   at zero registration offset. Runtime re-export reproduces the exact candidate
   table. Selection and3 full battle screenshots (prone/sitting/rising) are
   pixel-identical to T38. Paired roll screenshots differ at exactly73+74 pixels,
   matching the authored change masks with zero changes outside them. Actual
   runtime results are in work/roll-refined-checked/report.json; combined evidence
   is in work/roll-refined-verification.json. No unrelated assembly suite is repeated for this
   material-only change; Black, py_compile and diff checks cover affected code.
3. Original/T38 ROMs and saves are preserved. Own-ROM restart states, accepted
   sample states, screenshots, reports and stop receipts accompany the new ROM,
   original-ROM IPS and source recipe. IPS round-trip passes; ZIP integrity and
   private Drive upload metadata are checked. No assets or backup links are
   published through the public repository.

ROM SHA256:f96e32a02ef3732fd22a77b2e7a4bcc7187f0cd5ad1d4a4eaea248c6e4327027.
CTB3 SHA256:10dd1cae7e94f98100696bb138549d63d52fd6336fcb21e7080b3faf04ea2bd7.
Previous ROM SHA256:58756b2618db3f81acfa3dd7cb207affd13fd7ef01c8041a249f9ea2bd1df72c.

Owner art approval remains open. T36 standing-guard reference, unobserved moves,
other fighters, prior translation limitations and general VRAM font-residency
proof remain open. Sol/Medium was sufficient; no escalation was needed.
