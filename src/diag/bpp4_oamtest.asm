; src/diag/bpp4_oamtest.asm -- DIAGNOSTIC ONLY (T04/T04b). NOT included by the normal build.
; How to use (local experiment, never ship): in src/col.asm
;   1. in `oam:` right after `mov ds,ax` add:   %ifdef BPP4DIAG / call mirror4 / %endif
;   2. append `%include "diag/bpp4_oamtest.asm"` at the end of col.asm (inside the bank, before the size check);
;   3. build with defines BPP4=1, BPP4DIAG=1 (and OAMTEST=1 for the palette-field-0/1 sprite transparency test).
; The game runs slowly in this build (full 4bpp tile mirror every frame); it is a measurement tool.
; OAMTEST writes a debug record at 0000:FD60: [0]=changed active entries, [1]=first changed ACTIVE index (0xFF none),
; [2..3]=its OAM word after the change, [4]=SpriteStart (port 5), [5]=SpriteCount (port 6). Read it with emucap `read_memory`.
; Scope: only entries inside SpriteStart..SpriteStart+SpriteCount are touched (earlier version scanned all 128 entries).
%ifdef BPP4DIAG
; ---- DIAGNOSTIC ONLY (T04): mirror all 512 2bpp tiles (VRAM 0x2000) to 4bpp (0x4000+n*32), then give the first P1 fighter
; sprite tile a second colour region (right half uses palette indices 5..7) to prove sub-tile 4bpp colouring + transparency.
; Costs ~100k cycles per frame: the game runs slowly in this build, which is acceptable for a diagnostic.
mirror4:
    push bp
    xor ax,ax
    mov es,ax
    mov si,0x2000
    mov di,0x4000
    mov cx,512
.t: mov dx,8
.r: lodsw
    stosw
    xor ax,ax
    stosw
    dec dx
    jnz .r
    loop .t
    pop bp
    ; find the first palette-field-4 sprite
    in al,4
    mov ah,al
    xor al,al
    shl ax,1
    mov si,ax
    mov cx,128
.f: mov ax,[si]
    mov bx,ax
    shr bx,9
    and bl,7
    cmp bl,4
    je .got
    add si,4
    loop .f
    ret
.got:
    and ax,0x1FF
    shl ax,5
    add ax,0x4000
    mov di,ax
    mov cx,8
.rw:mov al,[di]
    or al,[di+1]
    and al,0x0F          ; pixels of the right half that are non-zero
    mov [di+2],al        ; plane 2 -> index +4
    add di,4
    loop .rw
%ifdef OAMTEST
    ; T04b rerun: restrict to ACTIVE OAM entries (SpriteStart=port 5, SpriteCount=port 6). Fighter sprites with palette field 4/5 are
    ; moved to fields 0/1 (palettes 8/9; colour 0 is OPAQUE there in 2bpp). Debug record at 0xFD60: [0]=changed count, [1]=first
    ; changed active index, [2..3]=its tile word, [4]=start, [5]=count.
    in al,4
    mov ah,al
    xor al,al
    shl ax,1
    mov bp,ax              ; OAM base
    in al,5
    mov [0xFD64],al
    xor ah,ah
    shl ax,2
    add bp,ax              ; first active entry
    in al,6
    mov [0xFD65],al
    xor ch,ch
    mov cl,al
    mov byte [0xFD60],0
    mov byte [0xFD61],0xFF
    xor dl,dl              ; active index
    mov si,bp
    or cx,cx
    jz .od
.o: mov ax,[si]
    mov bx,ax
    shr bx,9
    and bl,7
    cmp bl,4
    jne .o5
    and ax,0xF1FF
    jmp .oc
.o5:cmp bl,5
    jne .on
    and ax,0xF1FF
    or ax,0x0200
.oc:mov [si],ax
    inc byte [0xFD60]
    cmp byte [0xFD61],0xFF
    jne .on
    mov [0xFD61],dl
    mov [0xFD62],ax
.on:add si,4
    inc dl
    loop .o
.od:
%endif
    ; colours for palette 12 (sprite field 4) indices 5..7: orange / yellow / dark red
    mov word [0xFE00+12*32+5*2],0x0F70
    mov word [0xFE00+12*32+6*2],0x0FE0
    mov word [0xFE00+12*32+7*2],0x0600
    ret
%endif
