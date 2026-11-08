; DIAGNOSTIC ONLY: not included by the normal build, never ship this full mirror.
; Call mirror4 from col.asm oam immediately after mov ds,ax (DS must be zero).
; Define BPP4=1, BPP4DIAG=1; OAMTEST=1 additionally rewrites fighter fields 4/5
; to 0/1. Include this file before the bank-size check. No patched ROM is supplied.
; Input CH=start, CL=count from the caller (0..127, 0..128). Ports 5/6 can be stale
; here, so they MUST NOT supply the active range. Port 4 supplies the OAM base.
; Preserves all general registers, ES, flags; DS/SS unchanged; near return.
; DIAG_RECORD..+5 (OAMTEST only): changed count, first relative active index (FF=none),
; first changed OAM word, caller start, caller count. Diagnostics overwrite these
; bytes, so reserve them explicitly in the experiment before integration.
; OAMTEST requires DIAG_RECORD; do NOT use FD60..65 (V_P/V_K/V_W in col.asm).
; FDA8..AD is outside the current named color state, but its runtime lifetime
; still needs checking in the exact diagnostic build. Tests use synthetic memory.
; Full 512-tile expansion is deliberately slow and does not prove engine timing.
%ifdef BPP4DIAG
%ifdef OAMTEST
%ifndef DIAG_RECORD
%error OAMTEST requires an explicitly reserved DIAG_RECORD address
%endif
%endif
mirror4:
    pushf
    pusha
    push es
    push cx                 ; keep caller range across the mirror loop
    cld
    xor ax,ax
    mov es,ax
    mov si,0x2000
    mov di,0x4000
    mov cx,512
.tile:
    mov dx,8
.row:
    lodsw
    stosw
    xor ax,ax
    stosw
    dec dx
    jnz .row
    loop .tile
    pop dx                  ; DH=start, DL=count, from the caller
%ifdef OAMTEST
    mov [DIAG_RECORD+4],dh
    mov [DIAG_RECORD+5],dl
    mov byte [DIAG_RECORD],0
    mov byte [DIAG_RECORD+1],0xFF
    mov word [DIAG_RECORD+2],0
%endif
    in al,4
    mov ah,al
    xor al,al
    shl ax,1
    mov bp,ax               ; OAM table base
    xor bx,bx
    mov bl,dh
    and bx,0x7F             ; slot index, wraps within the 128-entry table
    xor cx,cx
    mov cl,dl
    xor dx,dx               ; relative active index
    xor di,di               ; whether a field-4 tile has been selected
    jcxz .done
.active:
    mov si,bx
    shl si,2
    add si,bp
    mov ax,[si]
    push bx
    mov bx,ax
    shr bx,9
    and bl,7
    cmp bl,4
    jne .field5
    or di,di
    jnz .field4
    ; Color only the first ACTIVE field-4 tile, preserving its OAM word.
    push ax
    push cx
    push si
    and ax,0x1FF
    shl ax,5
    add ax,0x4000
    mov si,ax
    mov cx,8
.region:
    mov al,[si]
    or al,[si+1]
    and al,0x0F
    mov [si+2],al
    add si,4
    loop .region
    pop si
    pop cx
    pop ax
    inc di
.field4:
%ifdef OAMTEST
    and ax,0xF1FF
    jmp .changed
%else
    jmp .next
%endif
.field5:
%ifdef OAMTEST
    cmp bl,5
    jne .next
    and ax,0xF1FF
    or ax,0x0200
.changed:
    mov [si],ax
    inc byte [DIAG_RECORD]
    cmp byte [DIAG_RECORD+1],0xFF
    jne .next
    mov [DIAG_RECORD+1],dl
    mov [DIAG_RECORD+2],ax
%endif
.next:
    pop bx
    inc bx
    and bx,0x7F
    inc dx
    loop .active
.done:
    mov word [0xFE00+12*32+5*2],0x0F70
    mov word [0xFE00+12*32+6*2],0x0FE0
    mov word [0xFE00+12*32+7*2],0x0600
    pop es
    popa
    popf
    ret
%endif
