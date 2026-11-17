# T45: prevent interrupt stack writes into the fighter tile source

Completion items: (1) identify the T44 banner corruption, (2) integrate a bounded
fix into the existing copy path, (3) verify native output/regression and preserve
restart data. These items are complete for the tested routes. Owner art review,
unobserved game modes and full-population timing remain separate open items.

## Cause and scope

The T41/T44 NO MERCY difference was actual source-buffer corruption, not merely
an unmeasured animation phase. In the damaged six-tile strip, intact tile bytes
match original ROM graphics while damaged bytes contain code return addresses,
including the VBlank colour trampoline's return. The original RAM copier at
0000:0120 sets SP=0500 and uses1024 POP-memory operations to copy SS:0500..0CFF
to SS:3800..3FFF. Interrupt delivery while SP serves as that data pointer writes
hardware/handler stack frames into source pixels that later copies reuse.
Different lookup timing changes which source words are damaged.

Native execution breakpoints at the first POP show original CS=0,SP=0500,
PSW=F206 (IF enabled), versus repaired PSW=F046 (IF disabled). Two PC-filtered
write-watch probes reported no hits and are inconclusive; they are not counted
as direct interrupt-hit evidence. A controlled interrupt-request test reproduces
source damage in an unmasked negative control and preserves it with the fix.
Native old/new ROM graphics and repaired-buffer comparisons provide the actual
end-to-end evidence.

## Existing routine replacement

src/copier.asm replaces only the original84-byte relocation template at original
ROM offset1402C0 (expanded-ROM offset3402C0). The existing startup copies exactly
84 bytes to0000:0120 as before; the cphook trampoline and caller return path are
unchanged. The new routine saves PSW and masks interrupts before borrowing SP,
restores the real stack after the fixed2048-byte copy, then restores saved PSW.
Pending IRQ delivery can then use the real stack. It preserves entry IF and DF,
DS/DI and the original callee-preserved registers. AX/CX/DX remain scratch; the
saved-PSW word moves the scratch DX stack address down by two bytes. Call sites
do not use that address as a return value. No per-tile checks, new scratch RAM,
bank switches, character tests or text/sound/combat hooks are added.

The template uses a direct DI=3800 load instead of the original2000+1800 setup,
leaving room within the same84 bytes. tools/build.py verifies the original
opcode template and length before applying it, only when PF_HYBRID=1. Other
build paths retain their original copier. The only81 changed ROM bytes versus
T44 are inside this template and the checksum. The entire colour bank,819-record
table, all palettes, text and translations are byte-identical to T44.

## Verification

Seven focused NASM/Unicorn tests cover exact relocation length, pending IRQ
request/delivery after stack restore, disabled-entry IF and set DF restoration,
source/destination bounds, caller/register/far-return behavior, changed/equal
colour-source handling and HYBRID-only installation. The unmasked control damages
the source; the masked routine keeps source and destination exact. An existing
equal-source copier test lacked the ownership initialization required by FORCE;
its fixture now sets magic/FIGHT before testing that intended skip path. The
production FORCE/lookup routine is unchanged.

Cold boots create own-ROM states; old-ROM states are never imported into a new
ROM. Five T44 unaffected fullscreens remain pixel-identical: both selections,
both saved-start battle screens and Zangief's initial fight. Chun-Li's initial
fight differs by131 pixels, all in the repaired banner strip. Both fixed763 and
fixed819 builds now have identical selection, initial fight, saved-start battle
and four following screenshots:seven exact fullscreens. In both fixed builds,
all96 banner staging/2bpp VRAM bytes match original ROM graphics at13300C, and
the relocated84-byte RAM copier matches the patched template. The T44 blocker
is resolved; the formerly damaged banner is not used as an expected reference.

Zangief's two new breathing poses still match all2514 representative visible/RAM
pixels across eight samples. Its existing1269-pixel basic pose is independently
unchanged. Runtime re-export reproduces the exact819-record CTB3 table. Native
Chun-Li guard/hit checks additionally exercise battle-time copying:three accepted
samples,1323 representative RAM pixels and993 representative visible pixels,
including330 opponent-occluded hit pixels checked only through RAM. Exact sample
accounting is in work/T45-defence-final-checked/report.json. Source/screenshot-incoherent
samples remain excluded. ROM checksum/readback, original-ROM IPS round-trip,
Black for changed tests, py_compile and git diff checks pass. No unrelated
translation or assembly suites are repeated.

## Reproduction and restart

NASM must be on PATH; Unicorn is needed for the focused tests. Private ROM/font/
state inputs are in the restart archive, not Git. Adapt emulator binary paths.

```
PATH=NASM_DIR:$PATH PYTHONPATH=work/test-deps python -m unittest \
  tests.test_atomic_copier tests.test_copier_jump
PF_HYBRID=1 PF_CLASS_TABLE=work/T44-idle-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/T45-zangief.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/verify_contact_output.py work/T45-idle-checked \
  work/T45-idle-runtime --family zangief-idle
python tools/verify_contact_output.py work/T45-defence-final-checked \
  work/T45-defence-runtime work/T45-guard-early-runtime \
  --family defence --orientation either --wrapped-source
python work/T45_verify.py
```

work/T45_boot.py reproduces own-ROM Chun-Li/Zangief bases. The local
T45_banner_{new,baseline}.py cold boots record full RAM and four following
screens; T45_original_copy_entry.py/T45_fixed_copy_entry.py record native
first-POP IF evidence. T45_create_states.py creates new-ROM battle states.
The source/frame capture protocols remain those in docs/zangief-breathing.md.
Native stop receipts accompany the captures. All diagnostic probes are retained;
missing-guard preliminary reports are not the final two-pose check.

Candidate ROM SHA256:af7ad0cd4cb944e295259ada36373e3b68742d5b28b836fc1256b39640f23425.
Unchanged table SHA256:95368cf96735e90023351324876a3c00e1ece2ac8b0eaf8c685b4176d09a52de.

Original/T41/T44 builds, original and new own-ROM states, candidate ROM/IPS,
control ROM, unchanged tables, fonts/source, raw captures, screenshots, reports,
focused tests, replay scripts and stop receipts are preserved in the approved
private Drive backup. ZIP CRC/member hashes and uploaded size/parent metadata
are checked. No game assets or private backup links are published in Git.

Completion results:1 cause identified;2 existing copy path repaired;3 native
regression and restart preservation complete. This is not a full-mode or cycle
benchmark. The fixed copy contains a constant1024 POPs, with no added per-tile
branch/check; its precise interrupt delay and full-table timing are not measured.
Owner art approval, further moves/fighters and prior translation/font-VRAM limits
remain open. No model/reasoning escalation was needed.
