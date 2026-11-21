# T60: paused for frame-transition analysis

T60 is **not complete** and has no new colour ROM. The last verified candidate
remains T59, source commit `5f9ed9d471dbdf6e9db5e97ca81fc7350cf49961`,
ROM SHA-256 `c296654460af1182cc80505f09a4760b1c944be2dbdc9e4aec34a2880490fdec`.

The owner requested a stop when a higher model/reasoning setting is needed.
The next call-path/timing analysis is recommended for Astra / High. This is
not a recommendation to raise routine colour authoring to that setting.

## Unchanged completion checklist

| Unit | Evidence now | Unfinished |
| --- | --- | --- |
| Classify source drawings and required pixels | Five original composites remain. Ten unobserved raw tiles all belong to two internally occluded Tabasa sources. Ibuki/Tabasa source probes and actual Saturn reference are retained. | Ryu transition cause; exact Tabasa appendage anatomy/material identity; two Tabasa internal-visibility holds. |
| Connect compatible colours without changing old outputs | T59 remains unchanged; an Ibuki polygon proposal is private and uninserted. | No T60 recipe, table, palette or ROM insertion is complete. |
| Verify native insertion and relevant regression | Read-only own-ROM transition captures and a separately cold-booted unmodified run completed with normal stops. | No T60 native insertion or regression claim. |
| Retain own-ROM states/restart backup and draft PR | T54 source states, original-ROM states, Saturn references and hashes retained privately; no game data in Git. | Resume after model change; do not treat this analysis handoff as a finished feature. |

## Concrete Ryu evidence

The held source key is `67afb1445223b4972d973413f651ccf6`. Restoring its own
T54 state reproduces the split drawing in the actual screenshot. All twenty
P1 tile byte strings equal the preceding complete drawing, while their OAM
positions/layout have changed. The staging buffer already contains the next
complete P1 drawing. Combining that staging with the current OAM yields
`5afaf9326fb4e1a14d686fbaf13ed2de`, which is also the next frame's mirror key.

At the split snapshot, CPU PC is `2000:03D4`, the `scanmap` flags-OR instruction.
The existing call path is `entry -> rsyn -> scanop -> scanmap`. At the start of
a rolling-resync round it scans 1024 words in each of the two background maps.
The source is held as a transition, rather than painted as another body pose.

This demonstrates an observed ordering/timing state; it does **not** yet prove
that this scan causes the visible artifact, establish its cycle cost, or prove
that an analogous transition never occurs in the original game. The unmodified
ROM run contains fifteen backward-input samples, but selects a different
opponent/simulation state and does not reproduce this exact hash. It is a
limited control, not an aligned absence proof.

The unresolved dependency is the order and time budget of OAM publication,
staging-to-mirror copying and the colour hook, including the map-opacity flags.
A repair must preserve BG colour-zero semantics, the atomic borrowed-SP copier,
existing actor contexts, reserved RAM boundaries and unrelated game paths.
Skipping background work during fights or painting the mixed drawing does not
resolve those requirements. Do not change the ROM based only on the PC snapshot.

The next higher-model task is to trace the corresponding caller/IRQ paths and
measure the relevant work, then select and verify one bounded repair if the
patch is causal. High is recommended because these coupled invariants remain
unresolved; Extra High is not automatic. After the path is settled and relevant
native regressions pass, return to Medium for the repeat author/insert/check work.

## Other retained evidence

Ibuki's held dash key is `d26b0bdba5c7d5ae4234078b94d35844`. Its P1 staging
composition matches the mirror despite differences elsewhere in the 2048-byte
buffer. Actual Saturn dash 08/12 reference is retained. A blanket whole-buffer
staging-equality gate would incorrectly reject this source.

Tabasa key `11b524ab63adec26666d27b861ee5a20` matches staging and persists
through the following eight frames. Its source is usable, but the appendage
material identity remains open. Actual Saturn backward movement and Ken-versus-
Tabasa Guard-ON reference are retained. A 36-frame post-hit gap produces a blue
guard effect; earlier menu-only and first-hit shots remain diagnostics, not
guard proof. No ambiguous anatomy is promoted into completed colouring.

Private evidence: `T60-Ryu-transition-evidence.json`, the three `T60-*-transition`
reports, `T60-original-Ryu`, `T60-original-comparison-limit.json`,
`T60-remaining-material-evidence.json`, `T60-preparation.json`, and the two
T60 Saturn reference folders. Never load these states into another ROM.
