# T40: Chun-Li occluded squash and rotation drawings

Completion items: (1) author the four previously identified body drawings,
(2) integrate and distinguish visible-screen proof from hidden-output proof,
(3) preserve old output and a restart backup. All are complete as a review
candidate; hidden regions still lack an unoccluded gameplay screenshot and owner
art approval remains open.

## Source scope and material choices

Targeted400/600-frame passive probes show four known full body drawings remaining
partly covered by Ken. Finer timing does not remove that occlusion. The original
2bpp source tiles remain readable; authoring now uses player-palette composition
without opponent occluders. This is an offline source view, NOT a gameplay change
or screenshot evidence. Ordinary compose() and screenshot masks keep opponent
occlusion by default. Palette grouping alone does not prove general actor
ownership: only the four exact-source body hashes below are accepted. Three
shared trim/outline pixels retain their pre-existing outputs.

| Drawing | Full source MD5 | Opaque pixels | Representative visible | Hidden |
|---|---|---:|---:|---:|
| Squashed body |6df89aa84bdfb0673fae05a2364a9a84|588|358|230|
| Flattened body |4b390e9e7b5ba2f5d42adc289b19f18b|348|254|94|
| Rotation |2965b35a65f6edc9f4b8bf33666ab249|521|142|379|
| Seated transition |52bfb03bf87d089228fa305e65991a3b|546|326|220|
| Representative total | |2003|1080|923|

The same skin hands, black cuffs/white studs, blue sleeves/tunic, brown trousers/
hair and white boots/buns are used. Saturn hammer/throw/recovery references from
T38/T39 supply material/anatomy context; port frame identity is not asserted.
Unoccluded round14x14 crops b4e93ee55ac29afbebf42560fb307223 and
7aede331348673fbd40fa83914848868 have uncertain identity and receive no new
colour assignments. They are retained as unresolved, not labelled unused.
An additional full standing crop c27b64da4b65521177dec2c0230d3bdd consists of
already-coloured tiles and needs no record addition.

## Output verification and shared tooling

The existing exporter gains a contact family using isolated source composition,
restricted to these exact hashes and the actual no-input400/600 protocols. It
still rejects unobserved/conflicting tile cells and any old-record change.
Existing exporter families retain their visible-source behavior.

capture_walk.py --read-colour-buffer optionally reads4096 bytes at7000..7FFF,
the existing128-tile 4bpp fighter mirror (col.asm cphook). It writes nothing to
RAM or ROM and is absent from ordinary captures. verify_contact_output.py reads
that actual buffer with OAM flips, validates transparent/opaque pixels and
compares all opaque source pixels with the recipe. Separately, it compares only
the visible player pixels against the real screenshot at exact coordinates.
All captures must identify the same ROM and have successful stop receipts.
The figure labels distinguish occluded screenshots from RAM reconstructions.
A reconstruction is never reported as an unoccluded screenshot.

Two synthetic tests prove default opponent priority and isolated source
transparency/original OAM rank. Five existing capture-registration tests pass.
A negative runtime check flips one hidden colour-buffer bit while preserving the
original2bpp source and screenshot: verification rejects it at the buffer check.
This establishes that the hidden-pixel check does not simply accept visible
screen agreement. No extra runtime instructions, bank switches, text checks,
font/VRAM allocations or unrelated game paths are introduced.

```
python tools/mock/walk_table.py work/damage-gap-flat/capture.json \
  work/roll-refined-table/full.ctb3 work/contact-table --motion contact \
  --additional-capture work/damage-gap-roll/capture.json
PF_HYBRID=1 PF_CLASS_TABLE=work/contact-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/contact.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/capture_walk.py work/contact.ws work/contact-states/guard.mcs \
  work/contact-table/full.ctb3 data/palettes/wrist-fixes.json work/contact-flat-runtime \
  --motion idle --settle-frames 400 --frames 10 18 --read-colour-buffer \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_contact_output.py work/contact-final-check \
  work/contact-flat-runtime work/contact-roll-runtime work/contact-flat-fine
python -m unittest discover -s tests -p test_contact_composition.py
python -m unittest discover -s tests -p test_capture_alignment.py
```

The roll capture uses the same command with settle600, durations50/58; the fine
flat capture uses settle400, durations6/8/12/14. Use the candidate's own cold-boot
state. A source pose occurs earlier than in T39, so same-duration battle timing
is not asserted. Tool binaries/state/ROM hashes remain in capture provenance.

## Results for the completion items

1. Four source-bound recipes add52 records,707->759. All707 previous outputs,
   palette footer and original transparency remain unchanged. Table size38020,
   free bytes18812 at colour-bank offset2200. Ambiguous round crops stay pending.
2. Eight actual samples cover all four drawings. Representative proof is2003
   buffer pixels and1080 visible screenshot pixels, as separated above. Runtime
   re-export reproduces the exact759-record table. Full-ROM changes32917 bytes
   stay within CTB3/checksum; table readback, checksum and selection-screen pixel
   equality pass. Seven relevant tests, hidden-corruption rejection, Black,
   py_compile and diff checks pass. Unchanged assembly suites are not repeated.
3. Original/T39 ROMs and states remain preserved. Own-ROM restart states,
   accepted sample states, reports, screenshots and successful stop receipts
   accompany the ROM/IPS/source tools in the private restart backup. Original-ROM
   IPS round-trip and ZIP CRC pass; uploaded file size/parent metadata are checked.
   No game assets or private backup links are committed to the public repository.

ROM SHA256:b376572082c7cd5052205a0517a059ce186981a47a1d709b9c249c706a785f1a.
CTB3 SHA256:a6a59565776e8dcf98834278d6add04b4dbf9548929a9af219d4165a40a91bf7.
Previous ROM SHA256:f96e32a02ef3732fd22a77b2e7a4bcc7187f0cd5ad1d4a4eaea248c6e4327027.

Local evidence: work/contact-{static-verification,hidden-negative}.json,
contact-final-check/, contact-reproduced/, contact-{flat,roll}-runtime/,
contact-flat-fine/, contact-boot/, contact-states/, damage-gap-{flat,roll,opposite}/.
Hidden art visibility/owner review, ambiguous round forms, other moves/fighters,
T36 standing-guard reference, prior translation limits, font VRAM residency and
full-population performance remain open. Sol/Medium remained sufficient.
