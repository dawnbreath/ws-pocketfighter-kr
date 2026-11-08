# T04b diagnostic: active OAM and caller contract

The routine is experiment-only and is not included in the normal build. This
change does not produce or modify a game ROM. It fixes the source published
in PR #17 so the engine owner can perform a reproducible runtime experiment.

## Reproduced problems in c274259

Synthetic input: caller start=10/count=2, stale ports start=0/count=128, inactive
slot 0 field=4, active slots 10/11 fields 4/5. The published code selected slot
0's tile and modified inactive OAM. A caller count of zero still modified slot
0. A start=126/count=4 test also modified inactive slot 10. The bare call
suggested in the source header clobbered registers (including CX needed by the
rest of the OAM hook). All five isolated tests failed against the old source.

The test precondition is DS=0 and DF=0, matching the documented OAM hook; the
failure does not depend on an invalid direction-flag setting. All memory,
tiles and ports are synthetic, with no game data or original ROM loaded.

The old debug record at FD60..FD65 aliases V_P, V_K and V_W in col.asm.
A later converter pass can overwrite it. Diagnostic records need a reserved
lifetime, not just an apparently unused address at one breakpoint.

## Corrected contract

Input CH=start, CL=count (valid 0..127 / 0..128); DS=0. Only port 4 is read
for the OAM base. Both first-tile selection and OAMTEST palette rewriting use
the caller range. Slot arithmetic wraps within the 128-entry table. Zero count
selects/modifies no sprite. General registers, ES and flags are preserved;
DS/SS are unchanged, with a near return.

OAMTEST requires DIAG_RECORD at assembly time. The record is six bytes: changed
count, first relative active index (FF for none), first rewritten word, caller
start, caller count. The synthetic test uses FDA8..FDAD, outside the current
named converter variables; this is **not** proof of its lifetime in a game.
The integrating diagnostic build must reserve/check that region explicitly.

The full mirror still expands 512 tiles per call and is deliberately slow.
It provides no evidence of feasible production conversion cost.

## Isolated verification

Optional development dependencies: NASM and Python `unicorn`; no new normal
build/runtime dependency. Tests explicitly skip if either is unavailable.

```sh
NASM=/path/to/nasm /path/to/python-with-unicorn -m unittest discover \
  -s tests -p test_oam_diag.py -v
```

Five tests pass with the fixed source: stale-port versus caller range, ring
wrap, empty range/debug initialization, field-5-only selection, caller register preservation with and
without OAMTEST. The empty-range test also verifies FD60..FD65 remain untouched.
Tests execute NASM's actual assembled instructions using Unicorn's generic
16-bit x86 engine. They do not simulate WonderSwan pixels, V30MZ cycles, port
latching or the full game. NASM `cpu 186` constrains the instruction set.

## Required owner-side rerun

Publish the complete diagnostic wiring/build flags (including DIAG_RECORD),
ROM SHA-256 and scripted route; reserve and watch the record's lifetime. Capture
caller start/count, selected active index/tile, rewritten OAM, frame output and
unchanged-region comparison. Recheck fields 0/1 and keep fields 2/3 and other
modes explicitly untested until measured. No rendering or production gate is
cleared by these isolated tests, and the earlier 47/60 claim is not silently
relabelled as a result of this corrected source.
