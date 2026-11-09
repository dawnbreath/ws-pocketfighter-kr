[map symbols kr_stubs.map]
; Korean text engine stubs - placed in free tail of ROM bank 0x15 (CPU 5000:FF34)
bits 16
cpu 186
%ifndef KRFONT_BANK
%define KRFONT_BANK 0xC0
%endif
%ifndef STORY_BANK
%define STORY_BANK 0xC1
%endif
org 0xFF34

; --- called from 5000:AFBA (inside SJIS->glyph converter, after push ds/si/cx/dx)
; in: bx = 2-byte code (bl=lead). Korean lead A0..FE -> bh=page(2..), bl=idx, return to caller of AFB6
krchk:
    cmp bl,0xA0
    jae .kr
    mov ax,0xC000
    mov ds,ax
    retf
.kr:
    sub bl,0x9E
    xchg bl,bh
    add sp,4            ; drop return into AFB6
    pop dx
    pop cx
    pop si
    pop ds
    retf                ; return to AFB6's caller

; --- replaces glyph page select block in 5000:AEB4 and 9000:ABF9
; in: ah = page. out: ds:si = glyph sheet base. clobbers ax
fontsel:
    cmp ah,2
    jae .kr
    mov si,0xBBDC
    cmp ah,1
    jne .p0
    mov si,0xCB9C
.p0:
    mov ax,0xE000
    mov ds,ax
    retf
.kr:
    sub ah,2
    mov al,ah
    shr al,3
    add al,KRFONT_BANK
    and ah,7
    shl ah,5
    mov si,ax
    and si,0xFF00
    xor ah,ah
    mov ds,ax           ; ds<0x100 marks Korean bank number
    retf

; --- replaces lcall 4000:8F40 in both glyph emitters
glyphcopy:
    push ax
    mov ax,ds
    cmp ax,0x100
    pop ax
    jb .kr
    jmp 0x4000:0x8F40
.kr:
    pusha
    push ds
    push es
    pushf
    mov ax,ds
    push bx
    mov bh,0xC3
    mov bl,al
    call 0x9000:0x96DB
    pop bx
    jmp 0x4000:0x8F4B

%ifdef HYBRID
; compact variant (saves 3 bytes of the bank-0x15 tail for the copier trampoline); same behaviour as the original pair below
stmap:
    push bx
    mov bx,0xC300|STORY_BANK
    call 0x9000:0x96DB
    pop bx
    ret
storyseg:
    call stmap
    call 0x9000:0x976B
    retf
storymap:
    call stmap
    retf
%else
; --- story script bank (replaces mov ax,0x2000 / lcall 9000:9760 at 9000:C80F)
storyseg:
    push bx
    mov bx,0xC300|STORY_BANK
    call 0x9000:0x96DB
    pop bx
    call 0x9000:0x976B
    retf
; --- (replaces mov ax,0x2000 / lcall 9000:974C at 9000:CA0A)
storymap:
    push bx
    mov bx,0xC300|STORY_BANK
    call 0x9000:0x96DB
    pop bx
    retf
%endif
end_stubs:
; --- VBlank colour hook (replaces mov ax,0x1000 / mov ds,ax at 4000:03C4). returns with ds=0x1000.
%ifndef COL_BANK
%define COL_BANK 0xCD
%endif
colstub:
    push ax
    in al,0xC2
    push ax
    mov al,COL_BANK
    out 0xC2,al
    call 0x2000:0x0000
    pop ax
    out 0xC2,al
    pop ax
    retf
; --- sprite-band hook (replaces mov ch,[103c]/mov cl,[103d] at 4000:028D, after the OAM is composed)
oamstub:
    mov ch,[0x103c]
    mov cl,[0x103d]
    pusha
    push ds
    push es
    in al,0xC2
    push ax
    mov al,COL_BANK
    out 0xC2,al
    call 0x2000:0x0240
    pop ax
    out 0xC2,al
    pop es
    pop ds
    popa
    retf
end_col:
%ifdef HYBRID
; --- T17 prototype: trampoline for the RAM copier entry (4000:02A4 originally `jmp far 0000:0120`, 5 bytes -> `jmp far 5000:cpstub`).
; Runs the colour-bank hook (convert changed fighter tiles to 4bpp) and then continues into the original copier unchanged.
cpstub:
    pusha
    in al,0xC2
    push ax
    mov al,COL_BANK
    out 0xC2,al
    call 0x2000:0x0500      ; saves/restores ds/es itself
    pop ax
    out 0xC2,al
    popa
    jmp 0x0000:0x0120
%endif
