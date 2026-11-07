# T03 release packaging

`python tools/release.py orig/pf.ws build/pf_kr.ws work/release-vNNN --xdelta3 /path/to/xdelta3`

The output directory must not already exist. It contains only patch.ips,
patch.xdelta, manifest.json and README.txt. Both patches are applied back to a fresh
base and compared byte for byte before publication. Hashes include CRC32, MD5,
SHA-1 and SHA-256 for base, target and patch files. xdelta uses `-e -9 -S none -A`.
IPS supports expansion and truncation (the latter requires IPS truncation support).
No source filenames are embedded in the xdelta application header.

Verification: `XDELTA3=/path/to/xdelta3 python -m unittest discover -s tests -v`
passed 4 tests with xdelta3 3.0.11: synthetic 2→4 MiB expansion, Unicode paths,
IPS 65535-byte record splitting, reserved EOF offset, truncation, zero extension,
RLE decoding, malformed records, preserving existing output and package allowlist.

This is tooling validation. No final game package was created or published.
The release owner must supply the exact canonical ROM after runtime QA and finish
the generated README's version/credits/known-issues/save-compatibility fields.
