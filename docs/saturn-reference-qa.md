# T19: direct Saturn reference and proposal QA

This is reference evidence and an offline classifier fix, not a completed colour patch.

## Reference provenance

The owner supplied the Pocket Fighter (Japan) disc archive and a 512 KiB
`Sega Saturn BIOS v1.01 (Multi Region)(J).bin`. The disc identifies itself as
`T-1230G`, `POCKET FIGHTER`, region `JT`; Mednafen selects the 4 MiB expansion cart.
Archive SHA-256: `0d371c7fff54cdf7b704531cca0091e826ace335c2fe8e1d76a3d0e1033fd03f`.
BIOS SHA-256: `785c67183e8934f46929171b576648f50ce38f19e151e48d193c08bb32cd15e2`.
Emulator: emucap 1.0.0 Mednafen package, upstream 1.32.1;
binary SHA-256 `920e59a239f2fcd5610cf67d135a67ab5adff65e0fdce6a15e7b6ca98a80b328`.

The supplied multiregion BIOS differs from Mednafen's expected stock BIOS hash.
Only the isolated Saturn reference profile uses `ss.bios_sanity 0`; the BIOS
bytes were not patched. All 35 tracks are extracted from the supplied archive,
and the original CUE is loaded through emucap's reviewed media manifest.
Fresh internal RAM was selected; this does not overwrite any existing save.
ROM, BIOS, screenshots, model seeds, masks and savestates remain local.

Cold-boot route: choose internal RAM, wait through initial loading, Start,
Battle Select → Training (Down three times, A). At Player Select, Down/Left
from Ryu selects Chun-Li; A selects her default colour. From opponent Ken,
Down twice selects Zangief; A selects his default colour. After loading, confirm Training Start with A.
Emulator frame-step requests and screenshot receipts are retained locally;
they do not establish matching animation frames across the two platforms.

## How the reference is used

Compare semantic regions in a matching action/default costume before RGB.
Saturn and WonderSwan differ in sprite geometry, resolution and available
palette groups; screenshots must not be treated as pixel-aligned masks.
Transformation costumes, hit flashes, effects and alternate colours need their
own references. Printed box screenshots and promotional illustrations are
secondary references, not direct Saturn framebuffer captures.

Local Codex proposal sheets contain the 20 most frequent captured poses each:
Chun-Li 192/256 samples, Zangief 182/256. These are flat semantic proposals
trained with partial provisional Codex marks, not Claude's unseen approved
seed/prediction files and not final shaded ROM screenshots. Missing semantic
classes cannot be recovered simply by increasing classifier confidence.

## Concrete classifier correction

`predict_proba(...).argmax(1)` returns a column index, not the original class ID.
When seeds contain classes 2 and 8, the old prediction path saves 0 and 1.
The corrected path indexes `clf.classes_`, retaining 2 and 8. A real random
forest regression test exercises the prediction helper used by the CLI.
This fixes corrupted class identities; it does not fix semantic misclassification.

Verification: `python -m unittest discover -s tests -p test_proto_class_ids.py`
passes (one test). No ROM code or production table changed.

Remaining: top-20 per-pixel reviewed error records, corrected training marks,
held-out before/after measurements, broader action captures, exact-source-safe
engine table integration and runtime colour regression. No T19 acceptance or
4bpp/VRAM safety gate is claimed here.

## Direct framebuffer comparison (first spot checks)

Captured both fighters together in Saturn Training, then Chun-Li jumping and
attacking. Default costume confirms bare hands/arms and brown trousers for
Chun-Li; bare fists/thighs and red trunks/boots/wristbands for Zangief.
The local WonderSwan proposals have four explicitly reviewed incorrect points:
Chun-Li frame 0 hand and trouser leg predicted cloth (votes .765/.565), and
Zangief frame 1 thigh and fist predicted trunks (votes .965/.525).
These are Codex's partial-seed reproduction, not an assertion about Claude's
unseen 661-tile table. Vote confidence is demonstrably not correctness.

Four fingerprint-bound pixel marks were applied through `apply_marks`; all
four now have the expected class and all other label pixels remain unchanged.
This is a spot correction, NOT a retrained model or held-out convergence result.
Exact coordinates, pose fingerprints, before/after arrays, errors and marks
remain in ignored `work/{chunli,zangief}-qa/reference-*.json` locally.
The Saturn idle savestate and capture receipts remain with the local reference
runtime; they are not interchangeable with WonderSwan saves.
