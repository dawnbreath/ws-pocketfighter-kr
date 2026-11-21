# T59: Morrigan bodies and neutral ground-puff proposal

Three previously held Morrigan body/effect sources now use the existing CTB4
ownership path. The body colours are compared with actual Saturn training
footage. The WS ground-puff timing is not matched to a Saturn effect frame:
its neutral colours are explicitly an art proposal, not established port parity.

## Completion checklist

| Unit | Evidence | Remaining scope |
| --- | --- | --- |
| Classify source drawings and required pixels | Three exact complete P1 keys; zero missing required opaque pixels. Actual Saturn training confirms green hair, dark suit and pink tights. Neutral slots 4/8/12 have zero uses among all 497 retained actor source tiles. | The slot audit is bounded to observed sources, not all-mode palette safety. Ibuki's streak, Ryu's partial source, two internally hidden Tabasa sources and Tabasa's appendage remain held. |
| Connect compatible colours without changing old outputs | Shared build-time owner registry adds Morrigan selector 2 alongside Gouki 1. Fifty-three actor variants; canonical outputs, 175 Gouki variants and retained Morrigan RGB are preserved. | Ground-puff colours and final body art await visual approval. |
| Verify native insertion and relevant regression | All three drawings / 3071 representative RAM pixels (3021 visible + 50 hidden) / three samples, with actual selector 2 reads. Existing Morrigan/Gouki and Chun-Li/Zangief controls are detailed below. | Six incoherent/offset samples excluded. Hidden pixels are RAM evidence only. Hardware timing and unobserved moves remain open. |
| Retain own-ROM states/restart backup and draft PR | Original/candidate/IPS, source manifests, captures, matching WS/Saturn states and hashes retained privately. Source-only draft stacks on T58. | No self-merge; earlier P2/all-mode/text/font-VRAM requirements remain open. |

The previous tools independently hardcoded Gouki context 1. `fighter_contexts.py`
now supplies the build, exporter and capture tool with one ownership registry.
The build activates only selectors actually present in the table and rejects
unassigned IDs. The exporter still requires the assigned actor family and
retained-source manifests. Both export source-visibility policies are preserved.

No assembly instruction, bank-switch routine, RAM/VRAM allocation, Korean-text
path or ROM-size rule changes. Morrigan fights now activate the existing OAM
ownership loop, previously used for Gouki; zero additional execution cost is
not claimed. The two-owner emulator test distinguishes the same raw source
under Gouki 1 and Morrigan 2 simultaneously on opposite sides.

The three otherwise unreferenced Morrigan opaque swatches become `fff`, `aaa`
and `555`. Only that fighter's palette changes. Dust shade 1/2/3 maps to
4/8/12; source zero stays transparent. The other eleven palettes are identical.
The per-actor variant prevents the new neutral indices from replacing canonical
outputs used by other fighters. All 497 previously retained Morrigan sources
keep their earlier output and RGB. This does not prove that an unobserved move
could never reference those slots.

The exact source keys are `f70174b89f5aab6b1c2adc7a0d24e4f7`,
`a5cc6564ddd53f14825daecaebaffd27` and
`9b9ed3307f1ad992dc493227f06af79a`.

## Native and preservation evidence

The candidate is cold-booted into its own states. Three new drawings pass actual
4bpp buffer and visible-screenshot comparison: 3071 representative buffer pixels,
separately 3021 visible pixels and 50 opponent-hidden pixels. Each P1 slot's actual
context-map value is checked as 2, rather than inferred from labels.

Four previous Morrigan low/air drawings / 3835 pixels / 12 samples pass with
selector 2 and their old labels. Eight Gouki drawings / 6536 pixels / 21 samples
pass with selector 1. Old Chun-Li four and Zangief three idle drawings retain
6504 representative native pixels. Four selection and all ten cold/battle/
followup screenshots are exact against T58, with all sampled battle buffers equal.

Prior 185 drawings / 602 certified samples retain source output and actual RGB
offline: 14,360 P1 tile comparisons / 3633 context/source pairs. This is not a
fresh replay of every previous move. All 4405 old canonical records and 1255
fallback references are preserved. New canonical entries are identity fallbacks;
only the assigned actor gets the new variant.

Final table: 4685 records (4457 canonical, 175 Gouki variants, 53 Morrigan
variants), 1309 fallback references, largest partition 317/1091. Twenty-seven
focused context/shard/palette/contact tests pass, including both selectors on
the same source and rejection of an unassigned selector. Three recipe
hash/alpha/index checks pass. All 38 re-exported files and the rebuilt ROM match;
the legacy T58 build also remains byte-identical when using its previous palette.
Checksum and original IPS roundtrip pass. The original remains preserved.

The three former T56 Morrigan holds are now source-bound review candidates;
three T56 holds remain (Ibuki streak, Ryu partial source, Tabasa appendage).
Together with the two earlier Tabasa source-visibility holds, five original
composites remain unresolved. This is not complete move coverage or art approval.

## Reproduction from the private restart archive

Authoring captures belong to T54; new candidate states belong to T59. Never
cross-load states. Use fresh destinations and adapt emulator/NASM paths:

```sh
python work/T59_export.py
PF_HYBRID=1 PF_CLASS_SHARDS=work/T59-reexport \
PF_FIGHTER_PALETTES=data/palettes/roster.json \
  python tools/build.py work/T59-new.ws --img \
  --ko text/ko/story.json text/ko/fixed.json text/ko/wg.json
PYTHONPATH=tools:tools/mock:tests:work/test-deps python -m unittest \
  test_context_colour_table test_sharded_colour_table test_fighter_palettes \
  test_contact_composition test_palette_compatibility
```

Candidate SHA-256:
`c296654460af1182cc80505f09a4760b1c944be2dbdc9e4aec34a2880490fdec`.
