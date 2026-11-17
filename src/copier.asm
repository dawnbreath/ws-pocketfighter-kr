; RAM-resident fighter copier, relocated by original 4000:02A9 to 0000:0120.
; HYBRID replacement for the original 84-byte template at ROM 1402C0.
; The original borrows SP to POP 1024 words from SS:0500..0CFF into SS:3800.
; A VBlank during that window otherwise pushes interrupt/hook frames into the
; source pixels. Mask interrupts before borrowing SP; restore the caller's PSW
; only after the real stack is back. No per-tile checks or extra bank changes.
; Contract: preserve DS,DI,BX,SI,BP,ES,SS,SP and caller IF/DF; AX=0020,CX=0,
; DX=entry SP-6 (original scratch), far return to the original caller.
bits 16
cpu 186
org 0x0120
entry:
    pushf
    cli
    push ds
    push di
    mov dx,sp
    mov sp,0x0500
    mov ax,ss
    mov ds,ax
    mov di,0x3800
    mov cx,64
    mov ax,32
.copy:
%assign offset 0
%rep 16
    pop word [di+offset]
%assign offset offset+2
%endrep
    add di,ax
    loop .copy
    mov sp,dx
    pop di
    pop ds
    popf
    retf
    times 84-($-$$) nop
