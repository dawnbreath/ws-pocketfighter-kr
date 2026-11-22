# TASKS

| id | task | owner | status | branch / PR | blockers |
|---|---|---|---|---|---|
| T01 | Korean image labels: pause menu DONE (PR #6), clipped 통신대전 fix DONE, composite label 127 + icons 15/17/18/20/142/172 still JP, stage-art background signs not inventoried | Codex | review (regression v006→v007: 10/11 screens identical, pause_open differs as intended) | claude/T01-pause-menu | – |
| T02 | Script QA: glossary consistency, line-width lint over `text/ko/*`, spelling/spacing pass (names: 장기에프, 춘리, 사쿠라…) | Codex | lint verified; editorial review pending | codex/T02-script-qa | full translation/context review remains |
| T03 | Release packaging script (xdelta3 + IPS, CRC/SHA of base and patched, README) | Codex | tooling verified; merged (PR #5) | codex/T03-release | final canonical ROM/runtime approval pending |
| T04 | 4bpp feasibility gate (see docs/4bpp-plan.md) | Codex | PROTOTYPE PENDING: 4bpp mode renders; FG palette-1 colour-0 transparency reported; VRAM safety, SPRITE transparency and one-fighter expansion UNPROVEN | claude/T04-4bpp-gate | diagnostic tile mapping |
| T05 | Fighter frame dump + region-mask generator (phase 1) | Codex | open | – | user ROM at orig/pf.ws |
| T06 | Per-character palette design sheets for 12 fighters | Codex | open | – | T05 sample |
| T07 | Full-screen regression harness (emucap scripted playthrough → screenshot diff) | Codex | harness verified on original; patched regression blocked | codex/T07-regression | needs reproducible v006/candidate and save provenance |
| T08 | Makai Mura WS: structure analysis (text encoding, fonts, VRAM free areas) | Codex | open | – | ROM |
| T09 | Makai Mura WS: translation + colour | both | blocked | – | T08 |

| T13 | Saturn PAC reference inspector | Codex | tool verified on 35 local PACs; review pending | codex/T13-saturn-reference | sprite compression unconfirmed; no frame decoder |

| T10 | Original-ROM tile-copy catalogue | Codex | requested sites catalogued; RAM relocation confirmed; reviewed+merged by Claude | codex/T10-copy-routines | full dynamic ownership/lifetimes and production conversion unproven |
| T12 | Runtime fighter capture → region proposals → conflict masks | Codex | tools verified on Chun-Li/Zangief, 256 samples each; conflict evidence + exact ROM candidate mapping verified; semantic masks NOT engine-ready | codex/T12-runtime-regions | pose review and unresolved pixels; production engine integration remains |

| T15 | Architecture consultation + component/pixel review workflow | Codex | issue #20 closed with measured tile-slot reuse for all 12 fighters; six answers, verified component marks and 12 reference part lists | codex/T12-component-marks | all-pose/stage coverage, final palettes and VRAM lifetime proof pending |

Update this table in the PR that changes a task’s state.
| T17 | 4bpp hybrid prototype: rolling resync + map-aware opaque expansion + copier hook + class table (PF_HYBRID=1 [PF_CLASS_TABLE], default build unchanged) | Codex | Codex: optional per-fighter CTB2 palette selection connected; startup fix verified; all-mode safety still open | codex/T17-fighter-palettes | class tables for all poses (T18), layer isolation, calibrated cost |

| T19 | Saturn-reference proposal QA | Codex | VISUAL REJECTED by owner: previous seed colours/masks are not approved; comparing early Claude palette with actual Saturn gameplay | codex/T19-saturn-contrast | contrast restoration is a trial; beard/hair/trim region correction and all-pose review remain |
| HANDOVER | Claude → Codex: Codex is primary engineer (see docs/codex-takeover.md) | Codex | handed over | codex/T17-takeover (based on PR #27) | no branch-work blocker; main merge policy unchanged |

| T20 | Re-author Chun-Li/Zangief from original WS pixels and actual Saturn gameplay | Codex | REJECTED by owner: broad redraw changed too much; return to middle-column #41 and apply T21 only | codex/T20-fresh-fighter-masks | visual review and remaining poses; no inherited seed approval |

| T21 | Middle-version local fixes: Zangief wristbands; Chun-Li below image-right hand | Codex | superseded by T22: upper Chun-Li patch overlaps hand; owner requests red-only Zangief wristbands | codex/T21-local-wrist-fixes | basic-pose visual review; other poses remain out of scope |

| T22 | Restore Chun-Li hand pixels; red-only Zangief wristbands | Codex | game verified: hand restored; lower trousers retained; red-only wristbands; zero out-of-region differences | codex/T22-hand-and-red-wrists | basic-pose visual review; other poses remain unverified |

| T23 | Separate Chun-Li hand from outer cuff | Codex | 10 outer-edge pixels revised; central hand and Zangief unchanged | codex/T23-separate-cuff | basic-pose visual review |

| T24 | Exact black cuff / white spikes / skin hand | Codex | CTB3 fixed and tested; actual black/white/skin output verified; 9 Chun-Li pixels change, Zangief identical | codex/T24-exact-cuff-colours | basic-pose visual review; remaining poses/modes unverified |

| T25 | Match inner Chun-Li cuff against Saturn | Codex | 13 inner-band pixels revised; lower hand and Zangief unchanged | codex/T25-inner-cuff | basic-pose visual review |

| T26 | Correct the cuff directly beneath Chun-Li hand | Codex | 16 lower-band pixels revised; hand, trousers and Zangief unchanged | codex/T26-lower-cuff | basic-pose visual review |

| T27 | Extend T26 colours to next Chun-Li breathing pose | Codex | game verified: next pose 679/679 pixels, base/title identical; 10 new records | codex/T27-chunli-idle-neighbor | idle cycle continued in T28; other actions and visual review |

| T28 | Complete four-pose Chun-Li idle colouring | Codex | all 4 poses connected and full return cycle observed; 2721/2721 pixels match; old poses/title identical | codex/T28-complete-idle | visual review; non-idle actions outside scope |

| T29 | Chun-Li forward/backward walking colours | Codex | four drawings integrated; 2689/2689 representative pixels, 14/14 runtime samples; six unaffected screens identical; 73 old records preserved | codex/T29-chunli-walk | visual review; dash/attacks/damage/opposite facing and performance coverage remain |

| T30 | Chun-Li dash/transition colours | Codex | four drawings connected; 2704/2704 representative pixels; 12/14 dash samples match; walking four poses and six pinned screens unchanged; all139 old records preserved | codex/T30-chunli-dash | visual review; 2 transient samples excluded from pixel proof; attacks/damage/opposite facing and performance remain |

| T31 | Chun-Li standing kick/punch colours | Codex | six drawings connected; 20/20 samples and 4422/4422 representative pixels match; idle6 screens and walk/dash8 drawings unchanged; all211 old records preserved | codex/T31-chunli-basic-attacks | visual review; combos/crouch/jump/contact/damage/opposite-facing and remaining fighters pending |

| T32 | Chun-Li crouching/jumping basic-attack colours | Codex | 15 drawings integrated; 10322 representative pixels; 41/48 coherent runtime samples plus7 separately identified transition screenshots; six standing attacks and six fullscreens unchanged; all331 old records preserved | codex/T32-chunli-low-air | visual review; unobserved frames/contact/combos/damage/opposite-facing and other fighters; table has2598 bytes free |

| T33 | Recover lost T32 colour data/runtime and reverse idle | Codex | exact602-record historical table recovered; new build21 drawings/14744 pixels verified; mirrored base idle5 samples verified; restart backup generated | codex/T33-recover-runtime | ROM differs due reacquired fonts; old text-image equivalence and other reverse actions remain unverified |

| T34 | Opposite-facing Chun-Li standing attacks and walking | Codex | 6 attack +4 walking drawings verified, 7111 representative pixels; unchanged recovered ROM/table; restart evidence bundled | codex/T34-reverse-actions | reverse dash/crouch/jump/contact/damage remain; away direction blocks in this state |

| T35 | Opposite-facing Chun-Li dash/crouch/air attacks | Codex | 4 dash +15 low/air drawings verified,13026 representative pixels; combined29 reverse drawings/20137 pixels; unchanged ROM/table and restart archive | codex/T35-reverse-low-air | visual approval; contact/combos/damage/unobserved frames and other fighters remain |

| T36 | Chun-Li standing guard/hit colours | Codex | review candidate:2 drawings/1323 pixels;9 guard+14 full hit samples;35 records added, all602 preserved;637-record table/IPS roundtrip and restart backup | codex/T36-chunli-guard-hit | standing-guard counterpart obtained T43; owner visual approval/other hit/contact/KO poses; former capacity limit superseded by T37 |

| T37 | Reclaim same-bank colour table capacity | Codex | data relocated to2200;free bytes848->24912,max CTB3 records1135;18 relevant tests;current637-record table unchanged;Chun-Li1323+Zangief1269 pixels verified;default build identical | codex/T37-colour-bank-layout | actual runtime tested at637 records;full-size performance/remaining fighter data and prior visual/VRAM items remain open |

| T38 | Chun-Li knockdown/roll/recovery colours | Codex | review candidate:5 drawings/2752 pixels in12 actual samples;70 records added,all637 preserved;707-record runtime re-export/IPS roundtrip/restart backup | codex/T38-chunli-damage | roll materials corrected against Saturn throw footage in T39; owner art review/unobserved damage/contact/KO/combo drawings and other fighters remain |

| T39 | Correct roll sleeves/hands against Saturn throw footage | Codex | review candidate:147 pixels/10 records corrected;all5 damage drawings/2752 pixels in6 actual samples;paired roll diff exactly147 pixels;selection+3 battle screens identical;697 outputs preserved;runtime re-export/IPS/restart backup | codex/T39-chunli-roll-reference | owner art approval; port frame identity not asserted; prior unobserved moves/fighters/VRAM items remain |

| T40 | Chun-Li occluded squash/rotation body colours | Codex | review candidate:4 drawings/52 records added;all707 preserved;759-record runtime re-export;2003 representative RAM pixels plus1080 visible screen pixels separately verified;8 samples/7 tests/hidden corruption rejection/IPS/restart backup | codex/T40-chunli-contact | hidden regions lack unoccluded screenshots/owner art review;round14x14 forms resolved in T41;remaining moves/fighters/VRAM/performance |

| T41 | Identify/colour soccer-ball transformation | Codex | review candidate:2 poses/296 fully visible pixels in3 samples;4 records added,all759 old outputs and used RGB preserved;763-record runtime re-export;Zangief1269 pixels/3 samples;gold uses previously unreferenced12;IPS/restart backup | codex/T41-chunli-soccer-ball | owner art approval;one incoherent sample excluded;T40 hidden regions and prior moves/fighters/VRAM/performance limits remain |

| T42 | Verify clipped/reflected Chun-Li hit and existing guard output | Codex | QA review:7 live defence samples;2042 representative buffer/1547 visible pixels across3 situations involving2 drawings;122 offscreen pixels separately checked;offscreen corruption rejected;8 tests and existing contact/ball regression;unchanged T41 ROM/763 records;restart backup | codex/T42-edge-defence-qa | opposite-facing guard verified T43;unobserved moves/offscreen and occluded art full visibility;prior visual/VRAM/performance items remain |

| T43 | Opposite-facing guard and Saturn guard/hit reference | Codex | evidence review:3 new mirrored-guard samples/604 RAM pixels/523 visible/81 offscreen;2 hit controls;mirror-only family connects T42 hit data;Saturn4 ON/OFF follow-up pairs isolate guard/hit;stable T41 ROM/763 records;states/reference backup | codex/T43-reverse-guard | owner art review;offscreen/occluded art full visibility;unobserved moves/fighters and prior translation/VRAM/performance limits |

| T44 | Zangief breathing colours with Saturn reference | Codex | review candidate:2 new drawings/2514 visible+RAM pixels in8 samples;old base1269 pixels unchanged;56 records added,all763 preserved;819-record runtime re-export/IPS and restart backup | codex/T44-zangief-motion | banner corruption diagnosed/fixed in T45;owner art review;genuine walking/reverse/other moves and prior VRAM/performance limits |

| T45 | Prevent IRQ stack corruption in borrowed-SP tile copier | Codex | review:existing84-byte RAM copier replaced;native IF1->0 while SP=0500;banner96 bytes match original;fixed763/819 seven fullscreens identical;five prior unaffected screens identical;819 colour records unchanged;Zangief3783+Chun-Li1323 representative RAM pixels;7 focused tests/own states/IPS/restart backup | codex/T45-atomic-copier | owner art review;unobserved modes/moves;precise interrupt delay/full-table timing and prior translation/font-VRAM limits |

| T46 | Zangief forward/back steps and observed transition | Codex | review candidate:4 steps+1 transition/5322 visible+RAM pixels in14 samples;all819 old outputs preserved,942 records;old3783 pixels/six fullscreens unchanged;11 dynamic outside-P1 pairs exact;one mid-copy Ken phase sample excluded,next4 Ken ROI frames exact;IPS/re-export/own states/restart backup | codex/T46-zangief-walk | owner art review;forward-walking classification confirmed T47;unobserved frames/opposite-facing/attacks;earlier translation/font-VRAM/full-population timing limits |

| T47 | Zangief standing kick/punch and shared movement | Codex | review candidate:5 attack+1 movement drawings/7845 visible+RAM pixels in20 samples;old8 drawings/9105 pixels retained;all942 outputs preserved,1116 records;former transition reproduces in far forward walking;9 fullscreens+21 outside-P1 pairs exact;phase exclusions bounded by native buffers/followups;IPS/re-export/own states/restart backup | codex/T47-zangief-basics | owner art review;19 record slots free;unobserved frames/strengths/combos/opposite-facing/other fighters;prior translation/font-VRAM/full-population timing limits |

| T48 | Reclaim colour table capacity | Codex | 265 redundant records removed, 284 slots free, all 1116 outputs preserved. 14 native Zangief drawings, nine matching fullscreens and protected re-export verified. | codex/T48-compact-colour-table | One seven-pixel intro sample excluded. Full timing and physical hardware pending. |

| T49 | Zangief crouch and air colour batch | Codex | review candidate:12 drawings/15035 visible+RAM pixels in40 zero-offset samples;all14 old drawings/16950 pixels retained;1116 effective outputs preserved;1013 records+436 protected fallback references;9 identical fullscreens;94 Ken RAM/46 Ken screenshot samples;IPS/native re-export/own states/private restart backup | codex/T49-zangief-low-air | owner art review;21 low-air phase/offset exclusions;2-pixel intro exclusion with identical buffers and next4 frames exact;48 Ken screenshot phase exclusions and13 nonidentical cross-build dynamic pairs;unobserved falling/landing/strengths/combos/opposite-facing/other fighters;prior translation/font-VRAM/hardware timing limits |

| T50 | Connect hash-partitioned tables for remaining roster | Codex | review candidate:16 code/data banks;1013 explicit+436 fallback outputs preserved;18160 aggregate capacity/1135 per partition;all26 Zangief drawings/31985 representative pixels;native re-export/legacy build equivalence/IPS/own states | codex/T50-sharded-colour-tables | remaining roster art not completed;two intro phase exclusions (162/228 pixels),followed by3 exact screens;per-partition distribution/full timing/real hardware;prior translation/font-VRAM limits |

| T51 | Basic colour batch for remaining ten fighters | Codex | review candidate:10 palettes+35 drawings/29442 native visible+RAM pixels in83 zero-offset samples;old1013+436 outputs and palettes preserved;1476 records+490 fallback references;oldChun-Li4/Zangief3 idle drawings/6504 pixels;10 exact selection screens;IPS/labels/table re-export/own states/private restart backup | codex/T51-roster-colour-basics | owner art review;48 timing exclusions and48 other off-family samples;remaining actions/strengths/facing/fighters' unobserved drawings;prior full timing/translation/font-VRAM limits |

| T52 | Observed walking/standing attacks for the other ten fighters | Codex | review candidate:57 drawings/47291 representative pixels;final Morrigan241px correction/3 drawings/2965 current-ROM pixels;54 labels+160 retained native samples' P1 outputs preserved;old1476+490 and12 palettes/runtime unchanged;IPS/re-export/private restart backup | codex/T52-roster-walk-attacks | owner art review;279 initial timing exclusions;hidden/effect/familiar drawings and globally shared material conflicts;other moves/strengths/facing and prior translation/font-VRAM/hardware timing limits |

| T53 | Resolve conflicting materials in globally shared source tiles | Codex | review candidate: CTB4 owner-sensitive lookup;3 Gouki drawings/37 variants;60 drawings/49550 pixels plus old7/6504;35 tests;canonical outputs and12 palettes preserved;IPS/own states/private restart backup | codex/T53-context-colours | owner art review;8-pixel initial scanout exclusion with identical buffers and next4 screens exact;P2 Gouki native/all-mode RAM/hardware timing and prior translation/font-VRAM limits |

| T54 | Observed crouch/air colours for the other ten fighters | Codex | review candidate:50 drawings/42996 native pixels/158 matching samples;Gouki8 context1/6536 pixels;oldChun-Li4/Zangief3/6504 pixels and60 prior drawings outputs preserved;13 tests;12 selection+5 cold+4 follow-up screens exact;IPS/re-export/own states/private restart backup | codex/T54-roster-low-air | owner art review;3 opaque-source visibility composites held;48 observed hashes unregistered;146 timing/offset exclusions and32-pixel initial battle scanout exclusion with identical buffers;prior moves/P2/hardware/text/font-VRAM limits |

| T55 | Remaining observed crouch/air follow-through colours | Codex | review candidate:44 registered drawings/35268 native pixels/77 matching samples (36 add colours,8 known-tile compositions);old110 drawings/448 samples outputs andChun-Li4/Zangief3/6504 native pixels retained;18 tests;8 selection+5 cold+4 follow-up screens exact;IPS/re-export/own states/private restart backup | codex/T55-roster-low-air-followthrough | owner art review;cohort94 registered+7 held of101 observed hashes;65 timing/offset exclusions and15-pixel initial battle scanout exclusion with identical buffers;prior unobserved moves/P2/hardware/text/font-VRAM limits |

| T56 | Observed dash-protocol body colours | Codex | review candidate:26 drawings/20829 native pixels/66 samples;Gouki1 context1/842 pixels;old154 drawings/525 samples outputs andChun-Li4/Zangief3/6504 native pixels preserved;13 tests;10 selection+5 cold+3 late battle screens exact;IPS/re-export/own states/private backup | codex/T56-roster-dash |13 partial/effect/source/material cases held;61 timing/offset exclusions;explicit8-pixel P2 Ibuki material change plus23 initial scanout pixels separately recorded;prior art/moves/P2/hardware/text/font-VRAM limits |

| T57 | Tabasa toothed familiar form matched to Saturn | Codex | review candidate:1 exact form/1250 native pixels;31 records added;old180 drawings/591 samples outputs andChun-Li4/Zangief3/6504 native pixels preserved;13 tests;3 selection+10 cold/battle screens exact;actual Saturn training reference/IPS/re-export/own states/private backup | codex/T57-tabasa-familiar | final art review;two related sources retain10 unseen source tiles;T54 cohort now95 registered+6 held;separate T56 appendage and prior unobserved moves/P2/hardware/text/font-VRAM limits |

| T58 | Recover complete bodies from occluded roster composites | Codex | review candidate:4 Ken/Sakura drawings/3111 RAM pixels (2312 visible+799 hidden)/10 samples;3 known-body controls/2418 pixels/14 samples;67 records added;old181 drawings/592 samples outputs andold7/6504 native pixels retained;15 tests+hidden corruption rejection;6 selection+9 cold/followup screens exact;IPS/re-export/own states/private backup | codex/T58-isolated-roster-sources | final art review;8 original composites held;71 coherence/offset exclusions;5 initial battle scanout pixels excluded with identical buffers;hidden pixels have no unobscured screenshot claim;prior moves/P2/hardware/text/font-VRAM limits |

| T59 | Morrigan body and neutral ground-puff proposal | Codex | review candidate:3 drawings/3071 RAM pixels (3021 visible+50 hidden)/3 samples;53 actor variants;oldMorrigan4/3835 andGouki8/6536 pixels plusold7/6504 native pixels retained;old185 drawings/602 samples outputs andRGB preserved offline;27 tests;4 selection+10 cold/battle screens exact;IPS/re-export/own states/private backup | codex/T59-roster-effects | final body/effect art review;neutral puff colours are a proposal, not matched Saturn effect timing;five original composites held;6 coherence exclusions;existing ownership loop now active for Morrigan, hardware timing uncalibrated;prior moves/P2/text/font-VRAM limits |

| T60 | Remaining composites and observed Ryu frame transition | Codex | PAUSED for Astra/High call-path/timing analysis per owner instruction;read-only transition/original/Saturn evidence retained;T59 is unchanged last verified ROM;no T60 insertion or completion claim | codex/T60-remaining-roster-composites | five source/material cases remain;Ryu new OAM/old mirror/new staging observed at scanmap PC2000:03D4;causality/cycle cost and aligned original comparison unresolved;see docs/roster-frame-transition-handoff.md |

| T61 | Ibuki dash streak and measured Ryu wait | Codex | 27 records, two native samples of 758 visible pixels, 188 previous drawings preserved offline, original fight wait and IRQ return traced | codex/T61-ibuki-dash-streak | Ryu scheduling and three Tabasa drawings open, first cold battle screen has an eight-pixel difference; see docs/ibuki-dash-streak.md |

| T62 | Tabasa familiar attacks and backstep | Codex | Six native drawings, 7,001 visible pixels over 29 samples, three older Tabasa and seven wrist controls, ten exact cold screens, reproducible IPS and six restored states | codex/T62-tabasa-attack-materials | Ryu transition remains open; Saturn familiar colour alternation, unsampled poses and hardware timing remain under review |

| T63 | Ryu–Ibuki split frame during map resync | Codex | Corrected full LCD matches T62 next intact frame; 1,518 fighter pixels, ten cold screens, seven wrist and nine Tabasa controls, 29 tests and eight restored states. See docs/ryu-frame-timing.md. | codex/T63-ryu-frame-timing | Target IRQ is longer; all-mode and physical hardware timing, unobserved actions and font VRAM coverage remain open. |

| T64 | Colour five complete Ryu poses after T63 and verify the roster | Codex | Five Ryu drawings, 3,475 representative pixels, five complete scene pairs equal outside Ryu. Twelve fighters checked on the candidate, 18 states restored and reproducible IPS. | codex/T64-ryu-movement-colours | One eight-pixel cold battle difference; later screens exact. Wider actions, hardware and prior font VRAM limits remain open. |

| T65 | Movement colours for Ken, Dan, Felicia, Lei-Lei, Gouki and Tabasa | Codex | 15 drawings, 44 native matches, 12,167 representative pixels. All twelve fighters checked, 28 own-ROM states restored, both IPS paths and rebuild verified. | codex/T65-roster-movement-colours | Five dynamic screen pairs differ outside P1 and one cold frame differs by five pixels. Additional actions and hardware timing remain open. |

| T66 | Standing attack colours for Ibuki, Sakura and Morrigan | Codex | 10 drawings, 44 native matches, 8,939 representative pixels. All ten screen pairs identical outside P1. Twelve fighters and seven wrist drawings checked. | codex/T66-roster-attacks | Additional move coverage and hardware timing open |

| T67 | Standing attacks and recovery across the eight remaining fighters | Codex | Eleven new drawings across five fighters, 95 native matches, 9,615 representative pixels. Nine cold screens exact; first battle differed by eight pixels. | codex/T67-roster-attacks | Additional move coverage and hardware timing open |

| T68 | Crouching and airborne attacks across the roster | Codex | Twelve new drawings across six fighters, 163 native matches and 25 restored states. Nine of ten cold screens exact. | codex/T68-crouching-attacks | Other moves and physical hardware timing open |

| T69 | Close-range attack inputs across the roster | Codex | Nine new drawings, 83 native matches. All nine pairs exact outside P1. Ten cold screenshots exact and 22 states restored. | codex/T69-close-attacks | Other moves and hardware timing open |

| T70 | Directional attacks across the roster | Codex | 31 drawings across 11 fighters, 163 native matches, 43 Zangief control screens and 44 restored states. Ten cold screens identical. | codex/T70-directional-attacks | See docs/roster-directional-attacks.md for Felicia timing and remaining move coverage. |

| T71 | Directional attack and dash follow-throughs | Codex | Nine additional drawings across six fighters, 59 native matches and 22 restored states. The cold-run changes were 23 Ryu headband pixels. | codex/T71-battle-followthrough | See docs/directional-attack-recovery.md for battle comparisons and remaining coverage. |

| T72 | Simultaneous attack colours across the roster | Codex | 31 drawings across twelve fighters, 223 native matches, 44 restored states and seven wrist controls. | codex/T72-simultaneous-attacks | See docs/simultaneous-attack-colours.md for the cold battle scanline, scene comparisons and remaining coverage. |

| T73 | Intermediate and late attack recovery | Codex | Nine further drawings across five fighters, 58 native matches and 22 restored states. All ten cold screens matched T72. | codex/T73-battle-recovery | See docs/battle-recovery-colours.md for timing comparisons and remaining coverage. |

| T74 | Gouki guard and changed-tile transfer timing | Codex | Two registered drawings, 19 native matches, 15 restored states and 11/13 fixed-input screens matching T73 outside P1. | codex/T74-gouki-transitions | See docs/gouki-guard-transfer.md for the two residual holds, first cold battle LCD and hardware coverage. |

| T75 | Fighter tile upload order | Codex | Both ends of the fighter slots refresh from the upper rows. No mixed opponent drawing in 15 Gouki holds, 12 fighters checked and 17 states restored. | codex/T75-battle-scanout | See docs/fighter-scanout.md for same-input timing differences and hardware coverage. |
