; Called only on changed palette inputs; DS=ES=0. Preserve C2; the caller
; restores registers at VBlank exit. The first display map word identifies
; converted stage cells, even while they scroll. Only rows 0..3 are replaced.
bits 16
cpu 186
%include "stage_layout.inc"
cmp word [STAGE_MAGIC_CACHE],STAGE_MAGIC
jne .done
in al,7
and al,15
cmp al,2
jne .done
test byte [0x1001],0x20
jz .done
mov dx,[0xfd04]
xor bp,bp
mov cx,4
.shade:
mov bx,dx
and bx,7
shr bx,1
mov al,[bx+0xfd00]
jnc .even
shr al,4
.even:
and ax,15
add bp,ax
shr dx,4
loop .shade
mov ax,60
sub ax,bp
shr ax,2
shl ax,7
add ax,[STAGE_BLOCK_CACHE]
mov si,ax
in al,0xc2
push ax
mov al,[STAGE_BANK_CACHE]
out 0xc2,al
push ds
mov ax,0x2000
mov ds,ax
mov di,0xfe00
mov cx,64
rep movsw
pop ds
pop ax
out 0xc2,al
.done:
retf
