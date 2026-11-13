# T33: recover T32 after workspace replacement

The replacement environment retained the original Pocket Fighter ROM and repository
access, but no former build, CTB3, captures or states. Recovery used the original
ROM (SHA256 b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e)
and unchanged T32 source at c2c037619d6679e7f6f34c356824c33a41ea4248.

Completion items: recover the colour table; build and verify a new runtime;
recover restart states and check the opposite-facing idle pose.

## Results

1. **Exact colour data recovered.** Fresh original-game captures regenerate the
   two basic poses and four Chun-Li idle drawings using seed_table --wrist-fixes
   and full_colour_table --idle-cycle (73 records). Further captures supply the
   existing walk/dash/attack/low-air recipes. Each run retains its actual input
   protocol, events, source-frame indices and stop receipt; mixed capture evidence
   is identified explicitly, never relabelled as a different single input route.
   The existing projection, conflict, transparency and old-record checks are reused.
   Result: 139 -> 211 -> 331 -> 602 records. Both the 331-record attack table and
   final602 table match their historical SHA256 exactly. Final table:
   abfe2f5129c1cb2bc273a9a90f02ba4aabe2dd85ded978fa7a7f4ecc5648e06a.
2. **New runtime verified.** Fresh T32 cold boot and own states drive 20 standing
   attack and48 low/air captures. All6 standing drawings match4422 representative
   opaque pixels (13 coherent samples); all15 low/air drawings match10322 pixels
   (41 coherent samples). Unmatched snapshots are excluded from pixel proof.
   Selection screenshots match the recovery idle-only build exactly. Fight-start
   screenshots differ in animation phase and are NOT accepted as full-screen
   regression evidence. The complete ROM differs from that same-font idle build
   only in CTB3 and checksum; table readback, checksum and original-ROM hash pass.
3. **Restart and reverse idle recovered.** Input right20, up+right44/release4,
   after settle240 from the recovered early state crosses the opponent. Five
   samples show Chun-Li to the right, facing left: all18 tiles are horizontally
   flipped, known and screenshot-exact. The drawing is mirrored base91f38eef...
   (677 opaque pixels). Per-sample states are retained. Earlier jump/contact
   samples contain unknown tiles and do not prove their colouring.

## Build identity and limitations

New ROM SHA256:
4a5241020bed175a90d3829a3e2548e346b2c8de220e01c287b35e795da7c861.
It is NOT byte-identical to the lost historical T32 ROM. Fonts were reacquired
from quiple/galmuri commit71e1cacf1437a11220307120e63e30bc275312d4; NASM2.16.03
was built locally. emucap/Mednafen1.1.0 supplies fresh runtime evidence, replacing
historical1.0.0 evidence rather than assuming it remains applicable. No engine,
translation, palette or geometry recipe was modified. Historical text-image
pixel equivalence remains unverified because the old build/fonts are absent.

The recovery source scripts, captured data and reports remain local under work/:
reconstruction-capture.json (parent hashes and actual protocols),
reconstruction-{walk,dash,attack,low-air}/, restored-T32.ws,
restored-T32-boot/, restored-T32-{attack,low-air}/,
restored-T32-reverse2/, restored-T32-verification.json.
Recovery attempts before control became available or after AI interference are
retained but unsupported drawings never enter the table. Five alignment tests pass.
An IPS patch round-trip reproduces the new ROM exactly. Private local backup
includes ROM, CTB3, restart states, provenance and reports; none are in Git.

Opposite-facing attacks/movement, unobserved frames, contact, combos, damage,
other fighters and general VRAM/font-residency/performance proof remain open.
Sol/Medium remained sufficient; no model escalation was required.
