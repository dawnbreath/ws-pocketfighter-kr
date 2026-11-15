# T37: reclaim unused colour-bank space

The637-record colour table left848 bytes in its former reserved half-bank.
Completion items: relocate existing data without adding hot-path work, prove
format/address boundaries, verify the current runtime and preserve a restart
backup. All are complete for the current637-record build.

## Shared layout

These are offsets inside ROM colour bank0D, NOT VRAM addresses. VRAM, glyph
streaming, text hooks and the mapped bank number are unchanged.

| Region | Before | After |
|---|---:|---:|
| Actual deduplicated scene palettes |1000..15FF|1000..15FF|
| Fighter palette catalogue |7000..7FFF reserved|2000..21FF reserved|
| CTB2/CTB3 reserved region |8000..FFFF|2200..FFFF|
|637-record table bytes |31920|31920|
| Free table bytes |848|24912|
| Maximum CTB3 records |653|1135|

The catalogue currently uses96 bytes (fallback and two registered fighters).
Fallback plus all12 fighters would use416 of the512 reserved bytes. Scene data
must end before2000 when the catalogue is enabled; a separate data-limit check
also prevents scene/table overlap without a fighter catalogue. A synthetic test
covers that previously independent path.

src/colour_layout.inc is the single source for NASM and Python. asm.py adds the
source include path; colour_layout.py reads only the static integer definitions.
Builders, validators and runtime fixtures share those offsets. The unchanged
lookup/copy code now addresses the relocated table; the neutral palette uses the
relocated catalogue. In the actual hybrid/CTB3/FPAL build, only five instruction
bytes change: four80->22 address bytes and one70->20 neutral-palette byte.
Instruction lengths/control flow and bank switching remain unchanged. DS:8000
ownership flags and RAM7000 sprite mirrors retain their original meanings.

Existing CTB3 files require no conversion. The exact637-record blob and palette
contents are unchanged (SHA256 below). The ROM must be rebuilt with matching
code/data offsets; use the new ROM's own states, not cross-ROM snapshot loading.

## Boundary and compatibility evidence

18 relevant tests pass: class-table format/legacy lookup6, full-colour runtime6,
fighter catalogue4 and layout2. They execute the assembled code with Unicorn,
including exact-source hash collisions, missing-source fallback, register/source
preservation and footer palettes. The new maximum-size1135-record test places
the target beyond a signed16-bit multiplication result, checks all128 copied
tiles and footer palette, then rejects1136 records. The low16 bits are valid:
address additions remain below10000 and no branch consumes IMUL overflow flags.
Full-roster catalogue placement fits; catalogue overflow rejects before mutation.

Default (no hybrid/class-table/catalogue flags) builds before and after are
byte-identical, MD5 67a9c2f7893e78d7f6ca046e25144b3c. The production candidate
uses the same637 records; whole-ROM comparison permits differences only in
colour bank0D and header checksum. Scene palettes, existing palette values,
body-row data other than catalogue pointers, and the table blob retain their
contents. ROM readback at D2200 and checksum pass.

Fresh Mednafen/emucap1.1.0 cold boots produce this ROM's own restart states.
Actual Chun-Li guard/hit screenshots match all1323 representative pixels.
Zangief's known base pose is observed in three samples: all28 tiles/1269 pixels
match existing output. Unregistered Ken still uses the neutral palette; generic
catalogue tests additionally exercise registered/unknown identity changes.
Character-selection screenshots are pixel-identical to the previous build.
This proves the relocated current data, not whole-game performance at1135 records.

```
PATH=NASM_DIR:$PATH PYTHONPATH=UNICORN_DIR python -m unittest discover -s tests -p test_class_table.py
PATH=NASM_DIR:$PATH PYTHONPATH=UNICORN_DIR python -m unittest discover -s tests -p test_full_colour_table.py
PATH=NASM_DIR:$PATH PYTHONPATH=UNICORN_DIR python -m unittest discover -s tests -p test_fighter_palettes.py
python -m unittest discover -s tests -p test_colour_layout.py
PF_HYBRID=1 PF_CLASS_TABLE=work/defence-preview-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/layout.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
```

ROM SHA256:d3c46b4526aa74f042a2951c07fe9ed638ffc2ad79d968c6e4a7df96ff0de16f.
Unchanged CTB3 SHA256:02a592c186ccde75f27ee432b0a3fffcb12245d501edb1bb1b92ba8bda7f7d81.
Original SHA256:b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e.

Local evidence: work/T37-default-{before,after}.ws, layout-boot/,
layout-zangief-boot/, layout-states/, layout-{guard,hit}-runtime/,
layout-zangief-check/, layout-verification.json. Black checks for the affected
formatted/new files, py_compile and diff checks pass. No unrelated graphics,
sound or text test suite was added. IPS round-trip and ZIP CRC are verified;
previous ROMs/states remain preserved, with new backup under the approved Drive
folder. Game assets remain outside Git.

Next data additions can use498 further full records in this layout. This does
not complete the remaining poses/fighters or prove general VRAM font residency.
T36's exact same-pose Saturn standing-guard reference and final visual approval
remain open. No model escalation was needed for this bounded address relocation.
