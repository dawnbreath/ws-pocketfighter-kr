# T13: local Saturn reference inspection

`tools/saturn_pac.py` reads a locally extracted Pocket Fighter `PLxx.PAC`.
It validates the big-endian chunk table and each payload's bounds, then writes
chunk offsets, sizes and SHA-256 hashes to `manifest.json`. Chunks 0x102 and
0x105 are rendered as 16-column RGB555 palette swatches when their lengths
are whole palette rows. No engine or ROM code is changed.

```sh
python tools/saturn_pac.py /local/path/PL02.PAC --out work/saturn/PL02
python -m unittest discover -s tests -p test_saturn_pac.py -v
```

Requires Python 3.11 and Pillow (already used by the project). Output must be a
new directory. Keep inputs and outputs outside git or under ignored `work/`;
the swatches and manifests contain derived game data. No sample game data or
palette values are included in this change.

## Actual input verification

The owner's `Pocket Fighter (Japan).7z` was downloaded completely (527,700,106
bytes). The data track and cue were extracted successfully with py7zr. Track 01
has raw 2352-byte sectors; its ISO9660 volume descriptor is at sector 16 with
2048-byte user data starting at offset 16. Walking that directory yielded 35
`PL*.PAC` files, including E/F variants. `PL06.PAC` was not present; PL06E/F
were present. Do not interpret file count as complete animation coverage.

All 35 files passed the inspector: six chunks each, payloads within the file,
header total equal to physical length in every sample, 70 palette sheets
written. Main palette row counts range **71–159**, variant row counts **12–15**.
Thus the earlier estimates “80–100 main palettes” and “12 variant palettes”
are not valid for all files. The parser records the header total without
assuming its semantics for untested files.

Four synthetic unit tests pass: alignment, truncated/oversized tables and
payloads, RGB channel ordering/report creation/no overwrite, incomplete rows.
PL02's main swatch sheet was also visually inspected; it includes several
families of ramps. The assumption that every palette assigns indices 1–7 to
skin and 8–15 to clothing is **not validated** by swatches alone.

## Deliberate limits

No sprite decompressor is implemented. A short 0x101 prefix does not identify
a codec reliably; no public decoder/spec has been confirmed. The report says
`NOT IMPLEMENTED` explicitly. Bit 15 is not interpreted as alpha in swatches;
RGB channels use bits 0–4, 5–9, 10–14 of big-endian words.

Saturn and WS sprites are different drawings. These swatches are reference
material, not verified WS region labels or a production palette assignment.
A future frame decoder would still require correspondence and visual checks;
it must not automatically transfer masks to WS tiles. T12 remains the WS-native
capture/region work, with character provenance, inverse flips, active OAM,
occlusion and unresolved conflicts tracked separately.
