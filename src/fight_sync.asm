; HYBRID only. The original fight loop publishes OAM, waits one VBlank
; (4000:00D7), then calls the fighter copier (4000:02A4). Only a full
; background scan can span an entire frame on the observed transition.
; At that boundary, arm a transfer and reset the original counter atomically.
; The interrupt runs the existing copier once before its background work.
; Entry CX=1, IF set. Return AX=32, CX=0, DX=entry SP-6 and successful
; wait comparison flags. Preserve the remaining registers, stack, IF and DF.
bits 16
cpu 186
%include "colour_layout.inc"
org 0xFD22
    push bp
    mov bp,sp
    push ds
    pushf
    cli
    xor ax,ax
    mov ds,ax
    cmp byte [RESYNC_LEFT],0
    je .ordinary
    cmp word [RESYNC_CURSOR],0
    jne .ordinary
    or byte [FIGHT_ACTIVITY],0x80
    mov ax,0x1000
    mov ds,ax
    mov word [0x1020],0
    popf
.wait:
    cmp word [0x1020],cx    ; CX=1 from the original caller
    jb .wait
    mov word [0x106A],0     ; original wait epilogue
    mov ax,32
    mov cx,0
    lea dx,[bp-4]           ; copier returns DX=far-call entry SP-6
    pop ds
    pop bp
    retf                    ; keep PSW from the successful wait comparison

.ordinary:
    popf
    pop ds
    pop bp
    call 0x4000:0x00D7      ; original wait preserves AX, CX and the caller's DS
    jmp 0x4000:0x02A4       ; copier owns the caller's original far return
