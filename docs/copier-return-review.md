# T17 copier tail-transfer correction

At ROM 1402A4 the original EA 20 01 00 00 is JMP FAR 0000:0120. It
preserves the far caller's return frame. The a219db2 prototype instead used
the existing far() helper, which emits 9A (CALL). cpstub eventually jumps to
the unchanged RAM copier, so the copier's RETF consumes the newly introduced
return frame and resumes at 4000:02A9 rather than the original caller.

02A9 is the startup relocation routine: PUSHA, copy 84 bytes from CS:02C0
to 0000:0120, POPA, RETF. It eventually returns to the original caller but
unnecessarily reinstalls the copier and sets DS=4000/ES=0. This is not an
unbounded stack leak; it is a wrong return path and segment side effect.

The fix reuses far() with an explicit keyword-only opcode, retaining 9A as
the default for every existing call site. Only the copier tail-transfer asks
for EA. No new per-tile checks, assembly instructions or bank transitions.

## Synthetic assembled contract test

`tests/test_copier_jump.py` obtains the actual patched bytes through
build.apply_engine, assembles the real cpstub and cphook, and runs a synthetic
far caller. A RETF sentinel substitutes for the original copier to isolate the
return-frame contract. Both changed and equal tile cases must reach the
sentinel then the original caller, never 02A9. They also check:

- Original SP, CS, DS, ES and general registers restored; C2 bank restored.
- Staging and old 2bpp VRAM unchanged by the pre-copy hook.
- Changed tiles produce the expected 4bpp plane layout.
- Equal source tiles leave the 4bpp destination untouched (existing behavior,
  not a claim that dirty-equal implies initialized/context-correct output).

Both tests pass after correction and fail with the former 9A opcode, which
returns to 02A9. Unicorn checks memory/control flow, not WS cycle timing or
hardware I/O. The real copier body and its stack-switched transfer are not
reimplemented by the test. Requires existing build dependencies plus optional
Unicorn and NASM in PATH; no game fixtures.

## Scope and pending issues

This patch is based on a219db2 and does not include the separate palette-rule
fix #29. The two fixes touch separate code. It does not approve the entire
prototype: dirty-output initialization/context invalidation, OAM/map ownership,
late glyph output, per-mode VRAM lifetime and calibrated timing remain open.
No save was imported/modified; no save-format or production compatibility pass
is claimed. Local ROMs/screenshots stay in ignored work/.

## Build and runtime evidence

Full build flags: `--img --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json`,
existing pinned v007 local fonts/master/labels. Default SHA-256 remains
`1493264631a1316cc8e0e4cb32abb5e9637f7bbce27cf06ef87cd01c2ec8a279`.
HYBRID=1 corrected SHA-256:
`4604a74daa73162aa2086d9018e33a5ada3f28a67a98a84afd314918dbdb4042`.
Both were rebuilt after the helper refactor and compared byte-for-byte.

For a controlled old-opcode baseline, the corrected ROM was copied locally,
1402A4 (expanded offset 3402A4) changed back EA→9A, and the ROM checksum
recomputed. Baseline SHA-256:
`778373f990b9d446726af995cca3ebde69631c00c394f5ff466561842a9699b6`.
No other ROM payload changed. This baseline construction is explicitly a local
comparison artifact, not a claim to have reproduced a separately supplied ROM.

Two fresh emucap/Mednafen runs used tools/regress.py's default SEQ. Both reached
an actual RYU vs IBUKI fight on the bar stage (visually confirmed), then stopped
their exact launch IDs. All six captured screens — title, menus, story1/2/3,
fight — were pixel-identical between old-opcode baseline and corrected ROM.
Story3 still shows existing prototype text artifacts; equality is not a claim
that those artifacts were fixed. The narrow change preserves observed output
while the synthetic control-flow test proves the corrected return contract.
No timing, whole-mode, save-load, or final colorization pass is inferred.
