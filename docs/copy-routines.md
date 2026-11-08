# T10: original-ROM tile writers and their callers

Scope: the writer list in issue #8, checked against the owner's unmodified
2 MiB ROM, SHA-256
`b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e`.
This is a source/destination catalogue, not a production 4bpp implementation
or an exhaustive list of writers reached in every mode.

## Address and evidence conventions

Addresses below are CPU `segment:offset`, not file offsets. With the observed
ROMBBSLCT=0xF and this 32-bank ROM, CPU 4000 maps to ROM bank 0x14, 5000 to
0x15 and 9000 to 0x19. For example 4000:02C0 is file 0x1402C0, NOT 0x0402C0.
Switchable 2000/3000 windows require their bank register too. DS=1000 denotes
the cartridge/work area, not internal RAM at address zero; do not flatten it
away. Entry register values in formulas are those before the routine changes
them. Ranges are inclusive, assuming valid nonzero counts and no 16-bit wrap.

Evidence: local NASM 2.16.01 `ndisasm -b 16`, disassembly from the named entry
points, dispatch-table inspection and far-call operand searches. Caller examples
were checked in surrounding code. A byte-pattern scan is not proof of a complete
call graph; indirect calls and data can invalidate simplistic scan results.

## Relocated copier: the RAM mystery is resolved

- Startup call at **4000:008B → 4000:02A9**.
- 02A9 copies **0x2A words (84 bytes)** from CS:02C0 to 0000:0120.
- **4000:02A4** is a far jump to **0000:0120**, preserving the far caller's
  return frame. Example caller: 4000:19B7 after OAM composition at 19AC and
  a call to 4000:00D7. Other far-call encodings occur at ROM file offsets
  0x141BC7, 0x1420B3, 0x14A835, 0x14A960, 0x14B0C4, 0x14B1A8,
  0x14B2C2, 0x14B4D1, 0x14B57D, 0x14B9A8, 0x14F0C9,
  0x19E541, 0x19EB96, 0x19F0B4 and 0x19F32C (scan candidates).
- Entry saves DS/DI and the original SP in DX, changes SP to **0x0500**, sets
  DS=SS and DI=**0x3800**, then performs 16 POP-to-memory words per iteration,
  64 iterations, adding 32 to DI each time. It restores SP, DI, DS and RETFs.
- Transfer: **SS:0500–0CFF → SS:3800–3FFF**, 2048 bytes = **128 2bpp tiles**.
  Under observed SS=0 these are internal RAM staging and tile VRAM.
- ROM writer instructions **02D8–0304** relocate to **0138–0164**. The source
  is staging RAM consumed through the stack; it is NOT a ROM read at each POP.
  Hooking only ROM:02D8 after the template has been copied misses execution.
- The transfer itself carries no BG/sprite tag. Its example caller is adjacent
  to OAM composition, but the 16 call encodings are not proof of sprite-only use.

**Runtime confirmation:** official emucap/Mednafen 1.0.0, original ROM, fresh
runtime, cold boot frozen, advance 400 frames, read `ram` address 0x120 length
0x54. All 84 bytes equal original file `[0x1402C0:0x140314]`. State reported
ROMBBSLCT=15 and SS=0. No ROM or RAM was written by the inspection. The managed emulator was stopped successfully afterward.

To repeat the comparison, save the `read_memory` response as a local JSON:

```python
import json
from pathlib import Path
rom = Path('/local/pf.ws').read_bytes()
ram = bytes.fromhex(json.loads(Path('work/ram-copy.json').read_text())['hex'])
assert len(ram) == 84 and ram == rom[0x1402C0:0x140314]
```

An `exec` breakpoint requested at 0x138 returned CS=4000, IP=0138 in this
backend. That is **not** evidence of executing 0000:0138: inspect CS as well as
reported PC. A subsequent bounded write-watch did not establish a RAM-copier
hit in the tested interval. The runtime result claimed here is byte identity
of the installed routine; the entry/copy/return flow is statically established.

## Catalogue

| Observed writer → entry | Caller / dispatch evidence | Source and transfer size | Destination | Applicability |
|---|---|---|---|---|
| RAM 0138–0164 → 0000:0120 | 4000:02A4 far-jump trampoline; installed by 02A9 | SS:0500, 64 × 32 bytes | SS:3800–3FFF | Staging copier, no tile owner tag; see above |
| 5000:AE2E → AE0E | Far calls 5000:A69F, A799, A812 | 0000:0500, **0x3F8 words = 2032 bytes = 127 tiles** | 0000:3800–3FEF | Staging flush; differs by one tile from RAM copier |
| 5000:AEA6 → AE77 | 5000:A73C; CX/DX loaded from caller locals at A736/A739 | 0000:0500, 16 × entry CX bytes | 0000:3800 + 16 × entry DX | Partial staging flush; no internal BG/sprite discrimination |
| 4000:05DD → 05BE | Descriptor opcode 1; table word at CS:0524; indirect CALL AX at 0497 or 04FC | ES:SI descriptor: source segment +2, source offset +4, **byte count +6** | 0000:2000 + descriptor word +0 | General tile-load command; descriptor has no tile owner tag |
| 4000:8BD8 → 8BB1 | Stage-script opcode 4; table CS:8ACC; CALL AX at 8782 | Segment/offset stored at caller DS:[1104]/[1106], set by opcode 1 at 8AE3; 16 × word [ES:DI] bytes | 0000:2000 onward | Background/stage initialization path, not fighter-only |
| 4000:8F68 → 8F40 | Examples 5000:2019/207D/20E1/AF05 and 9000:AC4F/ACFA; many more far-call encodings | Bank-window source described below; each row 16 × entry DH bytes, entry DL rows; source row stride 0x100 | 0000:2000 + entry CX, contiguous output rows | General rectangular tile-sheet copy; includes caller at 5000:AF05; do not apply fighter masks globally |
| 4000:8FE0 → 8FC4 | Examples 9000:8FB9/C335/C444/C560/DE84; many other call encodings | Caller DS:(entry SI + 16 × entry BX + 0x100 × row), 16 × DH bytes per row, DL rows | 0000:2000 + entry CX, contiguous rows | General direct-segment rectangle copy; no bank change or owner test |
| 4000:900C → 8FF7 | 9000:B628/B95C; B628 sets BX=1040, CX=009D | **No source**: BX becomes zero; writes 8 × entry CX zero words | 0000:2000 + entry BX | Tile clear, not a copy. Example clears 0x3040–0x3A0F (157 tiles) |
| 4000:916D → 9036 | 9000:B7B7/BAE4; B7B7 path sets DS=1000, SI=6000 | Selected indices in 1000:3800 + 2i; source **1000:(entry SI + 16 × selected_index)**; eight words per selected tile | 0000:(2000 + entry CX + 16i) | Compacts selected workspace tiles. Selection is computed earlier in 9036 using 9000:8B12; not a direct ROM→VRAM bulk copier |
| 4000:9090 | **Rejected for this original ROM** | 908F is `mov dh,0x28`; 9090 is its immediate operand | None at this instruction | Need the original trace/build provenance; never patch 9090 as a writer |

The 05BE descriptor is eight bytes and advances SI by eight on return. Its
caller 046F uses scripts in segment 5000; 049D can load a script through a bank
window and handles an alternate script form before dispatch. Consequently the
handler address alone does not identify which scene or tile owner is involved.

The 8BB1 dispatcher starts at 876F and indexes the word table at 8AC4 by twice
the opcode. Script selection reads DS:[3000] and the table at 4000:8C50. This
establishes the stage-script path without treating nearby table bytes as code.

### Bank handling for 8F40

Before changing DS, 8F40 passes entry DS in AX to **9000:972D**. That helper
computes `0xE0 + (AX >> 12)` and invokes **9000:96DB** with selector port C3.
96DB saves the prior C3 mapping in the segment-1000 work area and writes the
new mapping. The copy then reads **3000:(entry SI + 16 × entry BX + 0x100 × row)**.
On this 2 MiB ROM the selected file bank is that value modulo 32. **9000:9776**
restores the saved selector. The sibling helper 974C uses 0xF0 rather than 0xE0.
Do not infer a ROM address from DS=3000 without retaining C3.

### 916D selection count and source lifetime

9036 first constructs the selected-index list in segment 1000 at 3800,
counting selections in its local `[BP+1E]`. The copy loop iterates that selected
count; DX is the compacted destination index. It reloads entry SI each pass,
adds selected_index×16, copies one tile and increments DX. The producer and
lifetime of the segment-1000 workspace are not proven for every caller by this
catalogue. Treat it as staged data, not a reason to color every matching ROM byte.

## Consequences for the engine work

1. Preserve staging writes and copy contracts. Whole/partial staging flushes,
   descriptor byte copies, rectangular source strides, indexed compaction and
   clears need distinct handling or a correctly parameterized shared routine.
2. Preserve the RAM copier's stack switching and far return. Patching the ROM
   template requires installation timing to be accounted for; patching only
   the currently executing ROM address is insufficient.
3. Derive sprite/background identity from a proven caller or descriptor context.
   A writer into shared tile VRAM and a matching content hash do not establish it.
4. Most writers assume valid counts; REP instructions can do zero work, whereas
   a bottom-tested LOOP/DEC path may wrap on zero. Do not change those contracts
   casually. 8F40/8FC4/916D explicitly clear DF; earlier small REP handlers rely
   on their calling context. Retain flags/register behavior when designing hooks.

Additional writers encountered while following these paths: **4000:8A0C**
(stage descriptor source + BP to 2000 + DI, CX bytes), **902F** (one 16-byte tile),
and **8FA8** (sibling banked rectangle copy with an absolute destination).
Their existence means the initial watch list is not an exhaustive conversion
inventory. 8FA8 must not be assumed to target tile VRAM on every call.

## Completion and remaining scope

Every requested address now has an entry/caller route, source/count/destination
formula or an explicit invalid-address finding. The RAM relocation is confirmed
in a running emulator. No game bytes, disassembly dumps, ROM or savestates are
committed. No ROM-affecting change was made, so a new patched-build pixel
regression is not applicable to this documentation change.

Still unproven: all-mode dynamic reachability, every caller's semantic owner,
workspace lifetimes, all additional writer paths, actual 4bpp VRAM allocation,
performance and production hooks. This catalogue does not clear the 4bpp gate.
