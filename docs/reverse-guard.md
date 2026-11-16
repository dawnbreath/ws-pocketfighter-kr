# T43: opposite-facing guard and Saturn guard/hit calibration

Completion items: (1) capture and verify the missing reflected WS guard,
(2) obtain an actual Saturn standing-guard counterpart with a hit control,
(3) preserve the stable build, input routes and restart/reference evidence.
All are complete for the cases below. No ROM artwork or palette is changed;
owner art approval and remaining gameplay coverage are still open.

## WS opposite-facing guard

The original T41 ROM and its own hit state are reused. Immediate backward input
mostly observes recovery/walking. The accepted state after120 left frames,
work/T43-normal-guard/left-05.mcs, supplies a deterministic continuation. Holding
left for60/80/100 more frames produces the reflected version of the existing
standing-guard source b108911b2cdd4c2ebdac88e996ed9df4. Its reflected source hash
is ee3d4a13e4d616ca2225357405a885af; no new source/colour records are needed.

All three accepted guard samples match604 opaque4bpp buffer pixels each and
all their visible screenshot pixels. Their unsigned OAM origin250 is six pixels
before the LCD edge. The T42 cyclic-source and exact-reflection path verifies
the entire known drawing while keeping offscreen evidence separate.

| Further left hold | Buffer pixels | Visible pixels | Offscreen | Behind Ken |
|---|---:|---:|---:|---:|
|60|604|347|81|176|
|80|604|357|81|166|
|100|604|523|81|0|

The best sample is523 visible pixels plus81 checked from the output buffer.
It is not a604-pixel unoccluded screenshot. Two nonreflected standing-hit samples
from the same continuation supply a direction/input control. In this12-sample
capture,7 are coherent:5 defence samples pass and2 are different drawings;
5 incoherent samples are retained as excluded. A closer-position seed probe is
also retained but yields no accepted reflected guard and is not counted.

The shared mirror-only check additionally reuses T42's three reflected-hit
samples from the identical ROM, connecting both reflected defence drawings:
1323 representative buffer pixels/933 visible pixels in6 samples. These include
three newly captured guard samples and three previously captured hit samples,
not six new live guard captures. No checker or game-code change is necessary.

```
python tools/capture_walk.py work/ball.ws work/ball-states/hit.mcs \
  work/ball-final-table/full.ctb3 data/palettes/wrist-fixes.json work/T43-normal-guard \
  --motion walk --settle-frames 0 --frames 20 40 60 80 100 120 \
  --read-colour-buffer --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/capture_walk.py work/ball.ws work/T43-normal-guard/left-05.mcs \
  work/ball-final-table/full.ctb3 data/palettes/wrist-fixes.json work/T43-back-guard \
  --motion walk --settle-frames 0 --frames 20 40 60 80 100 120 \
  --read-colour-buffer --emucap-mcp EMUCAP --mednafen MEDNAFEN
python tools/verify_contact_output.py work/T43-checked work/T43-back-guard \
  --family defence --wrapped-source --orientation either
python tools/verify_contact_output.py work/T43-mirror-checked \
  work/T43-back-guard work/T42-mirrored-hit \
  --family defence --wrapped-source --orientation mirror
```

## Saturn reference: separate the first hit from subsequent guard

The old first-punch reference is retained as a hit, not relabelled as a guard
merely because the training rules display GUARD ON. A first-party manual scan
for the PlayStation edition describes guard behaviour after damage:
https://manualzz.com/doc/9779157/capcom-pocket-fighter-user-manual . This was a
lead; Saturn behaviour is established by the controlled replay below, without
assuming identical mechanics or frame IDs between ports.

Both cases begin from the same owned Saturn rule-setting state with P1 Ken,
P2 Chun-Li, CPU ACT STAND. One case retains GUARD ON; the other changes just
that setting to OFF. UI screenshots record the values. The initial short Start
probe stays in the settings UI and is rejected as gameplay evidence. The accepted
route releases for16 frames, holds Start16/release16, moves up twice8/release8
and confirms TRAINING START with A8/release120, then steps1200+1000 frames.
The parent selection and battle HUD are visually checked; this uses supported
port0 inputs and changes no game/emulator binary. Ken then walks right100.

The ON/OFF contact screenshots are pixel-identical, and their first A8 reaction
at sample02 is also pixel-identical. Those first-punch images do not establish
a guard. From each saved contact state, repeat A8/release12,20,28 or36, then A8
and sample after0/4/8/12 further frames. All four matched ON/OFF pairs differ.
ON shows the blue guard effect/standing defensive posture; OFF shows the hit
burst/hurt posture. The clear ON gap36 frame2 is the standing-guard anatomy
reference; the gap12 pair provides a visible guard-effect/hit-effect control.
An independent menu check confirms the OFF setting persists after the round.
A long-gap follow-up probe did not isolate the guard and remains diagnostic.

This supplies the previously missing Saturn standing-guard counterpart for T36
and supports comparing the same hands, cuffs, shoulder/tunic, trousers, boots
and hair ornaments. The user's established skin hands, black cuffs/white studs
and other colours are retained. Port proportions/frame artwork differ; pixel
identity or synchronized frame IDs are not asserted, and final art approval is
not inferred from the comparison. Existing first-strike HIT labels stay correct.

Accepted reference: work/saturn-reference/T43-combo-guard/ with the recorded
contact-state hashes/events, backed by T43-guard-control-final/ UI and first-hit
controls. T43-reference-status.json explicitly classifies the rejected menu
attempts, the long-gap diagnostic and the actual OFF persistence check. In
particular the earlier follow-up's persisted-rules.png is a button-config page,
not evidence of rule persistence; T43-off-persistence/05.png is the real check.
Replay scripts, raw screenshots and all source/result states are private assets.

## Completion evidence and handoff

1. Reflected guard:3 accepted samples/604 buffer pixels per sample, up to523
   visible;81 offscreen pixels separately checked. Existing direction control
   and reflected-hit coverage connect through the unchanged T42 checker.
2. Saturn counterpart: UI-confirmed ON/OFF cases, identical first-strike controls
   and4 distinct subsequent-strike pairs establish the guard/hit distinction.
   Screenshots are manually reviewed reference evidence, not automatic art
   approval. No new unit tests or assembly suites are added for this evidence/
   documentation change; actual capture/checker runs and unchanged file hashes
   provide the relevant validation. Markdown/diff checks pass.
3. Original/T41 builds, states and data remain preserved. The763-record ROM/table
   hashes below are unchanged. Own-ROM base and accepted sample states, all
   Saturn probe/source/result states, captured reports and stop receipts accompany
   the stable ROM/IPS and replay scripts in the private backup. Saturn states
   are solid-compressed in a nested reference tar.xz with every member's SHA256
   verified; the outer ZIP CRC and Drive size/parent metadata are checked. No
   game data or private backup link is committed to Git.

ROM SHA256:45afd4ac98950a9c6263d4dcfc8ada77b5ff1cc5e2126274595b05b8655a6125.
CTB3 SHA256:5b403bfa69ed0ac37cdf21d8d04258fe4457fc0e0b2417aca638e05d0f2622a4.

Primary evidence: work/T43-verification.json, T43-checked/, T43-mirror-checked/,
T43-guard-comparison.png, T43-saturn-combo-compare.png and the classified Saturn
reference bundle. Full visibility of offscreen/occluded art, owner visual review,
unobserved actions/fighters, prior translation limits, VRAM font residency and
full-population timing remain open. Sol/Medium remained sufficient; no model
escalation was needed.
