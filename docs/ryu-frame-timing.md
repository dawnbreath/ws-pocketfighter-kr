# Ryu’s split frame during the Ibuki fight

T63 fixes the T60 transition on the T62 colour cartridge. The two games receive identical controller input from cold boot. On left hold 23 both screens show the preceding complete drawing. T62 shows split halves at hold 24. T63 shows the following complete drawing, pixel-identical across the entire 224 × 144 LCD to T62 hold 25. T63 hold 25 matches as well.

## Transfer order

At 4000:20AE the fight loop has published its next OAM and requests a one-VBlank wait followed by a fighter copy. When the active rolling resync cursor is zero, the interrupt will scan both complete background maps. Only at that boundary the wrapper sets the request bit in the existing fighter lease and resets the original counter with interrupts masked. At IRQ entry the handler consumes the request and runs the existing bank-saving fighter converter and atomic copier once, before classifying the maps. Normal waits continue through the original wait and synchronous copier. The ordinary caller and IRQ register contracts are covered by the trampoline and wait tests.

The opacity classifier, tile budget, font placement, palette table and colour recipes are unchanged. Both builds ended the target update with 512 opacity flags equal to an independent classification of the current two maps. The full 2 KiB monochrome fighter mirror equalled staging on return in both builds.

## Native timing

| Same Ryu–Ibuki update | T62 | T63 |
| --- | ---: | ---: |
| VBlank entry, scanline | 144 | 144 |
| Fighter conversion starts, scanline | 34 after wrap | 144 |
| Monochrome copier starts, scanline | 121 | 72 |
| IRQ entry to IRET, emulated clocks | 53,257 | 78,981 |
| IRQ entry to game resuming, emulated clocks | 78,988 | 79,020 |
| Game resumes, scanline | 134 | 134 |

One LCD period is 40,704 clocks. The affected interrupt remains active for longer, while the original game loop resumes 32 clocks later on the same scanline. Both intervals span the same following VBlank edge. These are captured emulator timings for this update. Other interrupt loads and physical hardware timing remain open.

## Reproduction and controls

Cold boot each ROM independently. From startup wait 400 frames. Tap Start for 4 frames and release for 150, Start for 4 and release for 120, A for 3 and release for 90, then A for 3 and release for 120. Select Ryu with A for 3 and release for 150. Repeat A for 3 and release for 50 thirty times. Advance 80 frames, then 500 frames and save a state for that cartridge. Reload its own state for each run, hold left for 4, release for 4, then hold left for 1 through 40 frames.

* On the corrected screen, both fighters match their native 4bpp output at the original positions, including all 711 Ryu and 807 Ibuki pixels. Ryu’s staging and monochrome drawing both hash to `5afaf9326fb4e1a14d686fbaf13ed2de`. The split `67afb1445223b4972d973413f651ccf6` is not a drawable pose. A RAM-only sample at hold 23 can still combine upcoming OAM with old tiles while the LCD shows the complete previous body.
* Of 40 full-screen pairs, 36 are exact. Apart from the target, holds 7 and 8 show the opponent at another point in its update. Both T63 fighters match the native buffers on those screens. Hold 33 differs by seven pixels while the sampled OAM, staging, fighter mirrors, maps and palettes agree. The next screen is exact.
* The ten cold and follow-up screens match T62. Seven retained Chun-Li and Zangief drawings match 6,504 visible pixels. All six T62 Tabasa drawings match 7,001 representative pixels in 29 samples. Three older Tabasa drawings also pass. The Saturn material comparison remains the one recorded in T62.
* Build with the T62 sharded tables and roster palette. The focused suites for the atomic copier, trampoline, map classifier, hybrid startup, context and shards pass 29 tests. Applying the original-to-T63 IPS or the T62-to-T63 IPS to its respective source reproduces SHA-256 `24401b2cee1fcb716873feabe08a8d6a0f626a4701c90fc9c3259effccb405d0`. A second build reproduces those bytes. Six Tabasa and two Ryu state files restore in a separate run. The Ryu input state reproduces the full corrected screenshot.
