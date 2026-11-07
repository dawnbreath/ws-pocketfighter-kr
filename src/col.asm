; WSC colorizer (runs from the VBlank hook). Lives in a switched ROM bank mapped at CS=0x2000.
; far-call 2000:0000. Clobbers all regs except sp/ss/cs. Returns with ds=0x1000.
; Scene = the mono words of palettes 0 and 1 (matched against the scene list). Unknown sets use the default table.
bits 16
cpu 186
org 0x0000
%define SLIST  0x0600            ; scene list: 8-byte entries {2 words key (p0,p1), word table offset}; key0=0xFFFF ends
%define DEFT   0x0C00            ; default ramp table: 16 palettes x 8 shades x RGB444
%define IMG    0xFD00            ; LUT(4)+palette(32) of ports 0x1C..0x3F
%define CACHE  0xFD80
%define V_P    0xFD60
%define V_K    0xFD62
%define V_W    0xFD64
%define V_S    0xFD66
%define V_T    0xFD68            ; current scene table offset
%define V_M    0xFD6A            ; magic
%define V_PT   0xFD6E            ; table pointer of the palette being converted
%define FLAG   0xFD70            ; 1 = character bands were applied to the sprite table this frame
%define BT     0x0D00            ; band tables: 4 palettes (8..11) x 8 shades x RGB444
%define V_B1   0xFD72
%define V_B2   0xFD74
%define PL1    0x0D40            ; P1 name-hash list {hash, body row offset}, hash 0 ends
%define PL2    0x0D80            ; P2 name-hash list
%define OAMCNT 0xFD5A
%define OAMBAK 0xFD4A
%define GA     0xFD30
%define GB     0xFD40
%define C3     0xFD4F
%define FLA    0xFD58
%define FLB    0xFD59
%define TMIN   0xFD5C
%define TH     0xFD5D
%define C1     0xFD5E
%define C2     0xFD5F
%define M1     0xFD50
%define M2     0xFD51
%define M3     0xFD52
%define M4     0xFD53
%define T1A    0xFD54
%define T2A    0xFD55
%define T1B    0xFD56
%define T2B    0xFD57
entry:
    cld
%ifdef BPP4
    mov al,0xC0
%else
    mov al,0x80
%endif
    out 0x60,al
    xor ax,ax
    mov es,ax
    mov ds,ax
    cmp word [V_M],0xA55A
    je .init
    mov word [V_M],0xA55A
    mov word [V_T],DEFT
.init:
    mov di,IMG
    mov dx,0x1C
    mov cx,18
.rd: in ax,dx
    stosw
    add dx,2
    loop .rd
    mov ax,[FLAG]
    mov [IMG+36],ax
    or ax,ax
    jz .nh
    mov si,0x3620             ; P1 name tiles (4 tiles) -> hash
    mov cx,32
    xor bx,bx
.h1:lodsw
    rol bx,3
    xor bx,ax
    loop .h1
    mov [IMG+38],bx
    mov si,0x36B0             ; P2 name tiles (7 tiles) -> hash
    mov cx,56
    xor bx,bx
.h2:lodsw
    rol bx,3
    xor bx,ax
    loop .h2
    mov [IMG+40],bx
    jmp .hd
.nh:mov word [IMG+38],0
    mov word [IMG+40],0
.hd:mov si,IMG
    mov di,CACHE
    mov cx,21
    repe cmpsw
    jne .changed
    jmp done
.changed:
    mov si,IMG
    mov di,CACHE
    mov cx,21
    rep movsw

    mov word [V_B1],0
    mov word [V_B2],0
    cmp word [FLAG],0
    je .nb0
    mov si,PL1
.l1h:mov ax,[cs:si]
    or ax,ax
    jz .l1e
    cmp ax,[IMG+38]
    je .l1m
    add si,4
    jmp .l1h
.l1m:mov ax,[cs:si+2]
    mov [V_B1],ax
.l1e:mov si,PL2
.l2h:mov ax,[cs:si]
    or ax,ax
    jz .nb0
    cmp ax,[IMG+40]
    je .l2m
    add si,4
    jmp .l2h
.l2m:mov ax,[cs:si+2]
    mov [V_B2],ax
.nb0:
    mov word [V_T],DEFT       ; not sticky: unknown palette sets use the default table
    mov si,SLIST
.f: mov ax,[cs:si]
    cmp ax,0xFFFF
    je .conv
    cmp ax,[IMG+4]
    jne .next
    mov ax,[cs:si+2]
    cmp ax,[IMG+6]
    jne .next
    mov ax,[cs:si+4]
    mov [V_T],ax
    jmp .conv
.next:
    add si,6
    jmp .f
.nomatch:
.conv:
    mov word [V_P],0
    mov di,0xFE00
.p: mov bx,[V_P]
    mov cx,bx
    shl cx,4
    add cx,[V_T]
    mov [V_PT],cx
    shl bx,1
    cmp word [FLAG],0
    je .nb
    mov ax,[V_P]
    cmp ax,14
    jne .c12
    mov word [V_PT],BT
    mov bx,24
    jmp .nb
.c12:cmp ax,12
    jne .c13
    mov ax,[V_B1]
    or ax,ax
    jz .nb
    mov [V_PT],ax
    jmp .nb
.c13:cmp ax,13
    jne .nb
    mov ax,[V_B2]
    or ax,ax
    jz .nb
    mov [V_PT],ax
.nb:mov ax,[bx+IMG+4]
    mov [V_W],ax
    mov word [V_K],0
.k: mov cl,[V_K]
    shl cl,2
    mov ax,[V_W]
    shr ax,cl
    and ax,7
    mov [V_S],ax
    mov bx,ax
    shl bx,1
    add bx,[V_PT]
    mov dx,[cs:bx]            ; base colour
    mov bx,[V_S]
    mov cx,bx
    shr cx,1
    mov si,IMG
    add si,cx
    mov al,[si]
    test bl,1
    jz .lo
    shr al,4
.lo:and al,15
    mov ah,15
    sub ah,al                 ; ah = L
    mov al,[cs:ntab+bx]       ; al = N
    cmp ah,al
    je .st
    call fade
.st:mov ax,dx
    stosw
    inc word [V_K]
    cmp word [V_K],4
    jb .k
    add di,24
    inc word [V_P]
    cmp word [V_P],16
    jb .p
done:
    mov ax,0x1000
    mov ds,ax
    retf
; fade: dx=colour, ah=L(current luma), al=N(nominal luma) -> dx
fade:
    mov bp,dx
    mov bl,al
    mov bh,ah
    xor si,si
    xor cl,cl
.c: mov ax,bp
    shr ax,cl
    and al,15
    mov dl,al
    cmp bh,bl
    jb .dark
    mov al,bh
    sub al,bl
    mov ah,15
    sub ah,dl
    mul ah
    mov ch,15
    sub ch,bl
    div ch
    add al,dl
    jmp .m
.dark:
    mov al,dl
    mul bh
    div bl
.m: mov ah,0
    shl ax,cl
    or si,ax
    add cl,4
    cmp cl,12
    jb .c
    mov dx,si
    ret
ntab: db 15,13,11,9,7,5,3,0
%if ($-$$)>0x240
%error main code too big
%endif
times 0x240-($-$$) db 0xFF
; ---- character bands: far-called from the OAM builder (4000:028D) once the sprite table is composed.
; P1 sprites (palette field 4) / P2 (5): top part -> palette 8 / 10, bottom part -> 9 / 11, middle unchanged.
; cx = ch:start index, cl:count (from the caller). Preserves nothing (caller saves).
oam:
    cld
    xor ax,ax
    mov ds,ax
    mov word [FLAG],0
    in al,4
    mov ah,al
    xor al,al
    shl ax,1
    mov bp,ax
    mov al,ch
    xor ah,ah
    shl ax,2
    add bp,ax
    xor ch,ch
    or cx,cx
    jnz .go
    retf
.go:
    mov [OAMCNT],cx
    mov [OAMBAK],cx
    mov bx,GA
    call ginit
    mov bx,GB
    call ginit
    mov si,bp
.l1:mov ax,[si]
    mov bx,ax
    shr bx,9
    and bl,7
    cmp bl,4
    jne .q5
    mov bx,GA
    jmp .up
.q5:cmp bl,5
    jne .nx
    mov bx,GB
.up:mov dl,[si+2]
    mov dh,[si+3]
    cmp dl,[bx]
    jae .y1
    mov [bx],dl
.y1:cmp dl,[bx+1]
    jbe .y2
    mov [bx+1],dl
.y2:cmp dh,[bx+2]
    jae .x1
    mov [bx+2],dh
.x1:cmp dh,[bx+3]
    jbe .nx
    mov [bx+3],dh
.nx:add si,4
    dec word [OAMCNT]
    jnz .l1
    mov bx,GA
    mov di,[V_B1]
    call gcalc
    mov bx,GB
    mov di,[V_B2]
    call gcalc
    mov al,[GA+7]
    and al,[GB+7]
    cmp al,0xFF
    je .end
    mov word [FLAG],1
    mov cx,[OAMBAK]
    mov [OAMCNT],cx
    mov si,bp
.l2:mov ax,[si]
    mov bx,ax
    shr bx,9
    and bl,7
    cmp bl,4
    jne .r5
    mov bx,GA
    jmp .ch
.r5:cmp bl,5
    jne .nx2
    mov bx,GB
.ch:mov dh,[bx+7]
    cmp dh,0xFF
    je .nx2
    mov dl,[si+2]
    mov al,1                      ; band 0..3 by y
    cmp dl,[bx+4]
    jbe .bd
    mov al,2
    cmp dl,[bx+5]
    jbe .bd
    mov al,4
    cmp dl,[bx+6]
    jbe .bd
    mov al,8
.bd:test dh,al
    jz .skin                      ; band is skin
    mov ah,[bx+8]                 ; cloth: optional horizontal limit around the sprite centre
    or ah,ah
    jz .nx2
    mov al,[si+3]
    sub al,[bx+9]
    jnb .ab
    neg al
.ab:cmp al,ah
    jbe .nx2
.skin:
    mov ax,[si]
    and ax,0xF1FF
    or ax,0x0C00
    mov [si],ax
.nx2:add si,4
    dec word [OAMCNT]
    jnz .l2
.end:
    retf
ginit:
    mov byte [bx],0xFF
    mov byte [bx+1],0
    mov byte [bx+2],0xFF
    mov byte [bx+3],0
    mov byte [bx+7],0xFF
    ret
; gcalc: bx=group, di=row ptr (0 = default). fills T1..T3, flags, xr, centre; flags=0xFF if the group is absent/small
gcalc:
    mov al,[bx+1]
    sub al,[bx]
    jb .abs
    cmp al,16
    jb .abs
    mov [TH],al
    mov al,[bx]
    mov [TMIN],al
    mov byte [C1],45
    mov byte [C2],100
    mov byte [C3],100
    mov byte [bx+7],6
    mov byte [bx+8],0
    or di,di
    jz .cut
    mov al,[cs:di+16]
    mov [C1],al
    mov al,[cs:di+17]
    mov [C2],al
    mov al,[cs:di+18]
    mov [C3],al
    mov al,[cs:di+19]
    mov [bx+7],al
    mov al,[cs:di+20]
    mov [bx+8],al
.cut:
    mov al,[TH]
    mov ah,[C1]
    call pct
    add al,[TMIN]
    mov [bx+4],al
    mov al,[TH]
    mov ah,[C2]
    call pct
    add al,[TMIN]
    mov [bx+5],al
    mov al,[TH]
    mov ah,[C3]
    call pct
    add al,[TMIN]
    mov [bx+6],al
    mov al,[bx+2]
    add al,[bx+3]
    shr al,1
    mov [bx+9],al
    ret
.abs:
    mov byte [bx+7],0xFF
    ret
; al = al*ah/100
pct:
    push bx
    mul ah
    mov bl,100
    div bl
    xor ah,ah
    pop bx
    ret
