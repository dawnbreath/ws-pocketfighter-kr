; src/diag/bpp4_bench.asm -- BENCHMARK ONLY (T04), not part of the build. Needs defines BENCH4=1 BSEL=0|1|2 and a call site:
;   in `oam:` once after ~224 OAM builds:  call bench4   (see git history of the owner-side tree; the oam hook runs only when sprites exist,
;   so the benchmark must be triggered inside a fight).  Result word at 0000:FD70, marker 0xBEEF at FD78.
; CAVEAT: the HBlank-timer read (port 0xA8) gave one plausible sample (440 lines) and otherwise 0/1 line for shorter loops under `cli`;
; treat the number as ONE measurement, not a calibrated benchmark.

%ifdef BENCH4
; ---- BENCHMARK ONLY (T04): cycles of the 2bpp->4bpp expanding copy for 512 tiles, HBlank timer (1 tick = 1 scanline = 256 cycles).
; One section per build (BSEL=0 per-pixel mask path, 1 uniform-class path, 2 empty-loop reference). Result: word at 0000:FD70, marker FD78.
bench4:
    push bp
    push ds
    push es
    xor ax,ax
    mov ds,ax
    mov es,ax
    cli
    mov ax,0xFFFF
    out 0xA4,ax
    mov al,0x01
    out 0xA2,al
    in ax,0xA8
    mov [0xFD76],ax
    mov si,0x2000
    mov di,0x4000
    mov bx,bench4
    mov cx,512
%if BSEL==0
.t1:mov dx,8
.r1:lodsw
    mov bp,ax
    or al,ah
    mov ah,al
    and al,[cs:bx]
    and ah,[cs:bx+1]
    xchg ax,bp
    stosw
    mov ax,bp
    stosw
    add bx,2
    dec dx
    jnz .r1
    loop .t1
%elif BSEL==1
    mov bx,0xFF00
.t2:mov dx,8
.r2:lodsw
    mov bp,ax
    or al,ah
    mov ah,al
    and al,bl
    and ah,bh
    xchg ax,bp
    stosw
    mov ax,bp
    stosw
    dec dx
    jnz .r2
    loop .t2
%else
.t3:mov dx,8
.r3:dec dx
    jnz .r3
    loop .t3
%endif
    in ax,0xA8
    mov bx,[0xFD76]
    sub bx,ax
    mov [0xFD70],bx
    mov al,0
    out 0xA2,al
    mov word [0xFD78],0xBEEF
    sti
    pop es
    pop ds
    pop bp
    ret
%endif
