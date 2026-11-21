# Ibuki’s dash and the Ryu timing trace

T61 connects Ibuki’s 84 × 33 dash drawing to 27 new canonical tile records using the existing fighter palette. The separate Saturn dash capture supplies the cream clothing and brown hair and face-covering reference. Three proposed pixels inherit their existing shared-tile colours. The engine, actor selectors, font and palette bytes are identical to T59.

## Native output

The T61 cartridge was cold-booted to its own Ibuki save. Rightward holds of 12 and 16 frames both reproduce source d26b0bdba5c7d5ae4234078b94d35844. Each capture matches all 758 visible body pixels against the 4bpp buffer and the LCD screenshot at zero offset. A second cold boot of T59 provides the matched before image. The Ibuki selection screen is identical.

Against T59, nine of ten cold and follow-up screenshots match exactly. Eight pixels in one row of the first battle screenshot differ. OAM, staging, source VRAM, colour VRAM and palettes match at all five sampled battle boundaries. The first screenshot remains an open scanout difference. The 188 previously registered drawings retained their output across 605 stored samples and 14,441 fighter tile checks. This comparison used recorded captures.

The T61 SHA-256 is `77176a35df331a1720f23cdd23afc87525fa01d50f9d1fc63b9a8a0d45fc646b`. The IPS reproduces the ROM byte for byte from the original. The authoring and native verification commands both accept `--family ibuki-streak`. Include the T59 table and fallback catalogue on export and the T61 table labels on verification.

## Ryu’s original wait and the colour interrupt

Independent 21–25 frame holds from the same T54 Ryu save give matching breakpoint prefixes. The original fight main loop calls the OAM builder at 4000:20A8, waits one VBlank at 4000:20AE and calls the fighter copier at 4000:20B3. The interrupt stack records 4000:00EB inside that wait on both interrupt entry and return.

On the observed path the OAM hook runs on LCD line 20. The interrupt enters on line 144. The two-map scan is still running at the next frame boundary. It returns on line 6 of the following display cycle, and the IRQ returns on line 34. The fighter conversion starts on line 34 and the original RAM copier enters on line 120. At holds 23 and 24 the new layout uses the previous body tiles. At hold 25 the mirror agrees with staging. These measurements are for the retained T54 state and its emulator. A matched original-game control and a validated scheduling repair remain open. T61 adds no timing change.

## Four remaining source cases

Ryu’s mixed transition remains excluded from pose authoring. Tabasa has three remaining shapes. On the two internally occluded sources, both original snapshots have matching P1 staging and mirror. A targeted search of 170 coherent Tabasa samples found separate views of all 234 previously unseen opaque cells across ten tiles. The captured raw cells alone do not determine their colours. The third shape still needs an anatomical match for its front appendage. Saturn and WonderSwan poses need separate verification.
