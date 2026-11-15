# T36: Chun-Li standing guard and standing hit reaction

Completion items: (1) add two source-bound defence drawings, (2) integrate and
verify their actual output, (3) preserve old colours and restart/package evidence.
All three are complete as a review candidate. Exact same-pose Saturn standing-
guard comparison remains open; this is not a final visual approval.

## Source and reference decisions

The guard source is b108911b2cdd4c2ebdac88e996ed9df4 (37x27,604 opaque pixels),
facing left; its mirrored canonical hash is ee3d4a13e4d616ca2225357405a885af.
The standing-hit source is e6f4022073d25082efc088a4d40d383d (37x31,719 pixels),
facing right. A neutral-input probe initially showed fragmentary hit crops:
1713adeb... and6daf97af... . Reconstructing P1 alone confirms both are the same
full hit drawing obscured by the opponent (412/226 occluded pixels). They are
not labelled as separate poses or treated as unused. Full, unoccluded captures
supply the export instead; unobserved/conflicting tile cells still fail export.

Original shade grids define material polygons in tools/mock/defence_colours.py:
skin hands, opaque black cuffs/white studs, blue tunic, brown trousers and white
boots/buns. Source pixels and transparency are preserved. No nearest-label
propagation, positional ROM exception or palette adjustment is used.

The previously supplied Saturn disc and BIOS were reacquired from the owner's
Drive links. The Drive connector rejected the527700106-byte archive because of
its256MiB response limit; the same shared file was downloaded directly, extracted
and run locally. All35 tracks and the CUE remain local. emucap/Mednafen1.1.0
uses the supplied multi-region BIOS with ss.bios_sanity0 in an isolated reference
launcher; neither the BIOS nor game bytes were edited. The runtime accepts only
controller port0, so training P1 Ken/P2 Chun-Li supplies actual hit references;
CPU arcade and low-guard probes supply further posture/material observations.
Same-pose standing-guard footage was not isolated; opponent overlap/low attacks
prevented a clean match. Guard anatomy is authored from the original WS pixels
with the established material palette, and exact Saturn guard/visual review
remains explicitly pending. Reference screenshots are evidence, not approval.

## Shared tools and integration

capture_walk.py --motion idle adds a real no-input step for passive hit/contact
probes; existing motion defaults remain unchanged. The exporter adds --motion
defence and repeatable --additional-capture arguments. Each input is validated
against the requested protocol individually. Frame references retain capture
indices and original frame numbers, plus source paths/hashes/protocols. Votes,
exact transparency, conflicts and old-record checks reuse the existing path.

The shared screenshot checker adds --defence for these direction-bound recipes;
existing reverse families retain their normalization. No duplicate renderer or
new ROM hook is added. Optional horizontal registration remains exact and unique;
all23 verified defence samples actually use offset0.

```
python tools/mock/walk_table.py work/reverse-walk/capture.json \
  work/reconstruction-low-air/full.ctb3 work/defence-preview-table \
  --motion defence --additional-capture work/recovered-walk-source/capture.json
PF_HYBRID=1 PF_CLASS_TABLE=work/defence-preview-table/full.ctb3 \
PF_FIGHTER_PALETTES=data/palettes/wrist-fixes.json \
python tools/build.py work/defence.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
python tools/verify_reverse_actions.py work/reverse-standing work/reverse-walk \
  work/defence-checked --defence work/defence-guard-runtime work/defence-hit-runtime
```

## Results for the completion items

1. Two drawings add35 records: all602 former outputs and both palette blocks
   remain byte-identical. CTB3 is637 records/31920 bytes, leaving848 bytes
   (at most16 further full records) in the reserved half-bank. Future additions
   must address this measured capacity before insertion. No assembly, glyph,
   VRAM allocation, translation or unrelated graphics path changed. The existing
   copier's classification scope remains the fighter slots at3800..3FFF.
2. Fresh cold boot creates this ROM's own states. Guard captures reload the
   reversed playable state with settle0; hit captures reload a normal state with
   settle180. Across44 samples,28 pass the generic table render check. Of those,
   all9 guard and14 full hit samples match authored colours at zero offset.
   Representative totals are604+719=1323 pixels. Runtime export reproduces the
   exact built table. Full-ROM differences from T33 are confined to CTB3 and the
   two checksum bytes; readback/checksum pass. Selection screenshots are identical.
3. Previous builds/states and the original ROM are preserved. New start states,
   accepted per-sample states and successful emulator stop receipts are retained.
   IPS round-trip recreates the new ROM exactly. A local backup contains the ROM,
   IPS, baseline/new tables, source/runtime captures, scripts and restart states.
   Saturn comparison evidence/states are separate from game images; no ROM, state,
   screenshot, extracted Japanese text or tile data is committed to Git.

ROM SHA256:9508d40aa939ce5b0b64164cd3d6b3d4bbeca9e2bd077a7147ba2fea4dad7b47.
CTB3 SHA256:02a592c186ccde75f27ee432b0a3fffcb12245d501edb1bb1b92ba8bda7f7d81.
Original SHA256:b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e.

Validation also reproduces the historical331-record standing-attack table with
its unchanged SHA25670a52b75ead7a03e8c0acb4fe2e0b76224509008a496e2dc6077cff0f8a07852;
a wrong additional protocol is rejected before output creation. Five alignment
tests, Black, py_compile and git diff checks pass. No unchanged assembly suite
was repeated. Local evidence: work/defence-checked/, defence-verification.json,
defence-guard-runtime/, defence-hit-runtime/, defence-runtime-reproduced/ and
saturn-reference/. Final art review, exact Saturn standing-guard reference,
other defence/damage/knockdown/contact/combo poses and other fighters remain open.
T33's font/historical-ROM limitations persist. Sol/Medium remained sufficient.
