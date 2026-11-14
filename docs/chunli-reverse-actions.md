# T34: opposite-facing Chun-Li walking and standing attacks

Completion items: verify six mirrored standing-attack drawings, verify four
mirrored walking drawings, and preserve the recovered runtime/restart evidence.
All three items are complete for this bounded batch. No ROM, palette or source
material recipe was edited.

## Inputs and verification

The recovered T32 ROM is SHA256
4a5241020bed175a90d3829a3e2548e346b2c8de220e01c287b35e795da7c861;
CTB3 remains the historical602-record SHA256
abfe2f5129c1cb2bc273a9a90f02ba4aabe2dd85ded978fa7a7f4ecc5648e06a.
The pinned state is T33's work/restored-T32-reverse2/03.mcs: P1 is to the right
of the opponent and facing left. Each independent sample reloads this state.
It is already playable, so no additional settle is requested. Default settle
behavior remains unchanged; the new optional --settle-frames records its override
in capture metadata and input_protocol. Zero does not send an invalid step0.

```
python tools/capture_walk.py ROM REVERSE_STATE CTB3 PALETTES STANDING \
  --motion attack --settle-frames 0 --frames 2 4 6 8 10 12 16 20 24 32 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/capture_walk.py ROM REVERSE_STATE CTB3 PALETTES WALK \
  --motion walk --settle-frames 0 --frames 2 4 6 8 10 12 16 20 24 32 \
  --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_reverse_actions.py STANDING WALK OUT
```

The checker reverses the original cropped shade drawing, requires an exact known
source hash, authors its established indices and mirrors those indices back to
compare with the real screenshot. It reuses the existing exact registration
helper. Standing attacks require zero offset. Walking allows a unique exact
horizontal registration within6 pixels; the observed nonzero offsets are +1/+2.
Screenshots are never altered. Every selected opaque pixel must match. The
original capture flags are preserved and retained beside the separate registration
result, rather than rewriting raw capture evidence. The checker fails if any of
the ten required source drawings is absent.

## Results

1. Standing attacks: all6 drawings, 4422 representative pixels; 10 matching
   action samples at zero offset. Of20 source samples,17 have coherent generic
   table rendering. Other drawings/contact/recovery samples are not counted as
   verified attack drawings.
2. Walking: all4 drawings, 2689 representative pixels; 7 matching action samples.
   Three need horizontal registration (indices5,7,8: +2,+1,+1); four match at zero.
   Of20 source samples,15 pass the original generic render check. Holding the
   away direction encounters a guard drawing in this state; this batch does not
   claim a complete backwards-walking route or guard colouring.
3. Preservation: ROM and CTB3 hashes above remain unchanged. Successful emulator
   stop receipts, original captures, pinned reverse state and captured per-sample
   states remain local. Registered walking samples rejected by the original
   capture check use the pinned state plus recorded input for replay; no state
   is fabricated for them. Five alignment tests, Black, py_compile and diff checks
   pass. The new checker passes on both completed captures.

Local evidence: work/reverse-standing/, work/reverse-walk/,
work/reverse-final-checked/{report.json,detail.png}. A local backup bundles this
report, screenshots, captured states and the original pinned state. None of this
game data is committed. The PR contains only tools, task status and this report.

Opposite-facing dash, crouch/jump attacks, contact/combos/damage and other fighters
remain open. T33's reacquired-font and historical full-ROM equality limitations
still apply. Sol/Medium remained sufficient; no model escalation was needed.
