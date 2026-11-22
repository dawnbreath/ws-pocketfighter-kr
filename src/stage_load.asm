; Replaces MOV word [1126h],0 after the eight stage descriptors are dispatched.
; DS is game SRAM. Preserve flags, all registers and C2 across the one-time copy.
bits 16
cpu 186
%include "stage_layout.inc"
mov word [0x1126],0
pushf
pusha
push ds
push es
cld
mov bx,[0x3000]
mov ax,bx
shr ax,2
add al,STAGE_ROM_BANK
and bx,3
shl bx,14
xor dx,dx
mov es,dx
mov [es:STAGE_BANK_CACHE],al
mov [es:STAGE_BLOCK_CACHE],bx
mov ah,al
in al,0xc2
push ax
mov al,ah
out 0xc2,al
mov dx,0x2000
mov ds,dx
mov si,bx
add si,[bx+STAGE_LUT_BYTES+2]
mov di,0xfe00
mov cx,64
rep movsw
mov cx,[bx+STAGE_LUT_BYTES]
lea si,[bx+STAGE_LUT_BYTES+4]
mov di,STAGE_TILE_RAM
rep movsw
mov word [es:STAGE_MAGIC_CACHE],STAGE_MAGIC
pop ax
out 0xc2,al
pop es
pop ds
popa
popf
retf
