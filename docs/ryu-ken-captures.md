# T12: Ryu and Ken capture coverage

Original ROM SHA-256:
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
Both fresh Mednafen/emucap runs completed 256 samples with no imported save,
verified the original hash after capture, and confirmed their own launch stopped.
Selection portraits and fight HUDs were visually inspected: RYU vs CHUN-LI on
the urban stage; KEN vs CHUN-LI on the snow stage. Final sample-0224 images still
show those identities. This confirms two routes, not all moves or modes.

At the initial selector Ryu needs no direction; Ken needs one right tap.
Existing Chun-Li and Zangief routes are unchanged. Capture command:

```sh
python tools/capture_frames.py orig/pf.ws work/ryu --character ryu --samples 256 \
  --emucap-mcp /path/to/emucap-mcp --mednafen /path/to/mednafen
# Repeat with work/ken and --character ken.
python tools/segment_frames.py work/ryu/capture.json data/rules/ryu.json work/ryu-masks
python tools/component_marks.py work/ryu/capture.json work/ryu-review --frames 8 40 88
python tools/map_region_sources.py orig/pf.ws work/ryu/capture.json \
  work/ryu-masks/masks.json work/ryu-sources.json
# Repeat those three commands for Ken.
```

Local capture digests (run-specific provenance, not reproducibility expectations):

- Ryu: `996e6be4eda6e9cfe022e22b84f914db00cf832d8ab2869aa1f5b079b7eb432a`
- Ken: `909f34b62524500e6ac4e32e99b2ead55a56da37ad8ae72c6ebd6dbce916ede6`

| Measurement | Ryu | Ken |
|---|---:|---:|
| Samples / empty samples | 256 / 0 | 256 / 0 |
| Distinct selected-side source tile hashes | 880 | 785 |
| Hashes outside slots 180–1FF | 0 | 0 |
| Referenced slots / slots with multiple contents | 51 / 47 | 49 / 47 |
| Exact ROM match: one candidate | 586 | 617 |
| Exact ROM match: multiple candidates | 294 | 168 |
| No exact ROM match | 0 | 0 |
| Unknown source-mask pixels | 18377 | 19032 |
| Components in review frames 8 / 40 / 88 | 32 / 35 / 31 | 23 / 20 / 37 |

Slot counts use profile_tile_slots.py from PR #25. ROM matches are candidates,
not proven runtime copy origins. Reused slots across time are normal animation,
not proof of simultaneous conflicts. Active palette-field grouping can include
effects; the totals are not a certified inventory of pure body graphics.

## Visual review limits

The current Ryu/Ken rules intentionally contain no whole-body geometric priors.
Consequently zero conflicting labels is **not** evidence of correct body colors:
most interior pixels remain unlabelled. Existing masks stay engine_ready=false.
Do not use those empty priors to manufacture complete color masks.

Ryu frame 8 component 4 spans [37,90,57,116] (156 pixels), across upper-body
regions. Ken frame 8 component 1 spans [39,86,57,104] (185 pixels), including the
hair/face vicinity. Numbered component and plain-source images were inspected.
Such components require explicit pixel subsets; one component label cannot be
assumed to separate gloves from bare forearm, or hair from face. No complete
hand/arm annotation or owner approval is claimed. Local images and review
fingerprints are retained in work/; no game-derived graphics enter git.

## Timing metadata correction

New frames use `requested_frames` instead of the misleading `elapsed_frames`.
It sums requested press/after durations, excluding backend release frames. It
is not an emulator frame counter and must not be used for per-frame timing
budgets. Existing captures remain immutable, with their earlier warning.
In-repository tools select frames by index and do not consume elapsed_frames;
no segmentation or mask coordinates changed.

No ROM patches or saves were produced. Remaining work includes reviewed
pixel-level glove/forearm labels, the other fighters, scene/mode writer tracing,
and engine/palette integration after the pending contract review.
