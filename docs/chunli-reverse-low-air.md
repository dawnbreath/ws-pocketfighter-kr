# T35: opposite-facing Chun-Li dash, crouch and airborne attacks

Completion items: verify four mirrored dash/transition drawings, verify fifteen
mirrored crouch/jump/basic-attack drawings, and preserve the runtime and restart
evidence. These items are complete for the existing source-bound recipes; this
is not a claim of every animation frame or whole-game visual approval.

## Capture and comparison

The same recovered T32 ROM and CTB3 are retained byte-for-byte:
ROM SHA256 4a5241020bed175a90d3829a3e2548e346b2c8de220e01c287b35e795da7c861;
CTB3 SHA256 abfe2f5129c1cb2bc273a9a90f02ba4aabe2dd85ded978fa7a7f4ecc5648e06a.
No engine, palette or material recipe was edited. Original ROMs and existing
states remain intact.

Two pinned reverse states are used. The near state is T33's
work/restored-T32-reverse2/03.mcs. To make the far state, reload it, tap
up+right44/release12, then advance4 and save: work/reverse-far/01.mcs.
Its P1/P2 mean OAM x positions are167.33/100.0; all18 P1 tiles are known and
horizontally flipped. This gap avoids contact that interrupts the sweep return
and forward-dash transition in the near state. No RAM was edited to move fighters.
Each action sample reloads its pinned state with settle override0.

Per state: dash holds1,3,6,10,14,18,19,21,23,25,28,32 with the established
press4/release4 prefix; low/air holds2,6,10,14,20,24,32,48 with the established
crouch12 or jump4/release8 prefix. A final focused far-state sweep-return capture
uses down12 followed by down+A holds26,28,30 (three independent reloads). Its
actual protocol/events and original frame indices are retained in the capture.

The existing reverse checker now accepts optional --dash and --low-air lists of
capture directories. It merges evidence by the exact canonical mirrored source
hash, keeping each sample's source path, capture hash, state hash, protocol and
registration. Per-run provenance lives in the report's captures array. Standing/
walk-only invocation remains supported. Montage size follows requested families.
It reuses the same comparison path, not a second colour renderer or majority vote.

Dash uses unique exact horizontal registration within±6 pixels. Airborne frames
use the existing unique exact vertical registration within±8; crouching frames
require zero offset. Observed dash offsets range-4..+5, and air offsets are-1/0/+4.
Original screenshot pixels and capture flags are untouched. Each selected opaque
pixel must equal the mirrored established material recipe; unsupported/contact
or mismatched drawings are excluded. Any missing required drawing fails the check.

## Results

- Dash: all4 drawings,2704 representative pixels,30 matching action samples from
  48 captures (43 pass the generic capture render check).
- Low/air: all15 drawings,10322 representative pixels,64 matching action samples
  from99 captures (84 pass the generic capture render check). This includes the
  three sweep-return samples, not a missing-pose exemption.
- New total:19 drawings/13026 representative pixels. Combined with T34's unchanged
  six standing attacks/four walking drawings:29 drawings/20137 pixels. Combined
  verification reports no missing recipe in any requested family.

```
python tools/verify_reverse_actions.py work/reverse-standing work/reverse-walk \
  work/reverse-complete \
  --dash work/reverse-dash work/reverse-far-dash \
  --low-air work/reverse-low-air work/reverse-far-low-air work/reverse-sweep-return
```

The default two-family checker also passes against T34 captures. Five alignment
tests, Black, py_compile and git diff --check pass. Every emulator has a successful
stop receipt. States exist for samples accepted by the original capture checker;
other registered samples are replayable from the pinned state and recorded inputs.
The local evidence archive includes near/far pinned states, captured states,
original screenshots/captures and the combined report/montage. Game data are not
committed. Local evidence: work/reverse-complete/ and the capture roots above.

Visual approval, contact/combos/damage, unknown frames, other fighters and whole-
game VRAM/performance proof remain open. T33's reacquired-font/historical ROM
limitations remain. Sol/Medium was sufficient; no model escalation was needed.
