; WSC colorizer (runs from the VBlank hook). Lives in a switched ROM bank mapped at CS=0x2000.
; far-call 2000:0000. Clobbers all regs except sp/ss/cs. Returns with ds=0x1000.
; Scene = the mono words of palettes 0 and 1 (matched against the scene list). Unknown sets use the default table.
bits 16
cpu 186
org 0x0000
%ifdef HYBRID
%define SLIST  0x0800            ; HYBRID: scene list moved up for code room (build.py passes slist=0x800)
%else
%define SLIST  0x0600
%endif
; scene list: 8-byte entries {2 words key (p0,p1), word table offset}; key0=0xFFFF ends
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
%ifdef FULLTILE
%define CTSTRIDE 50
%else
%define CTSTRIDE 34
%endif
%define CTABA  0x8000            ; class table inside the colour bank (CS=0x2000); distinct from the VRAM flag array at DS:0x8000
%define RSY    0x8200            ; HYBRID prototype: frames left of the rolling 2bpp->4bpp resync
%define FIGHT  0x8204            ; HYBRID: >0 while the fighter-tile copier hook is active (slots 0x180-0x1FF are owned by cphook)
%define FORCE  0x8205            ; HYBRID: 1 = cphook converts every staging tile on this call (first call after it did not own the slots)
%define RSC    0x8202            ; HYBRID prototype: next tile index to resync
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
%ifdef HYBRID
    mov byte [RSY],255         ; first use: establish the prototype's state (RAM is not assumed zeroed)
    mov word [RSC],0
    mov word [FIGHT],0         ; FIGHT/FORCE start unowned; scratch RAM need not be zero
%endif
.init:
%ifdef HYBRID
    call rsyn                  ; after the state is initialised
%endif
    mov di,IMG
    mov dx,0x1C
    mov cx,18
.rd: in ax,dx
    stosw
    add dx,2
    loop .rd
%ifdef FPAL
    cmp byte [FIGHT],1
    sbb ax,ax
    inc ax                    ; normalized 0/1: counter decay must not invalidate the name cache
%else
    mov ax,[FLAG]
%endif
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
%ifdef HYBRID
    mov byte [RSY],255
%endif
    mov si,IMG
    mov di,CACHE
    mov cx,21
    rep movsw

%ifdef FPAL
    xor ax,ax
    mov [V_B1],ax
    mov [V_B2],ax
%else
    mov word [V_B1],0
    mov word [V_B2],0
%endif
%ifdef FPAL
    cmp word [IMG+36],0
%else
    cmp word [FLAG],0
%endif
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
%ifdef HYBRID
    mov ax,[di-8]             ; 4bpp: opaque copy of entry 0 at index 4 (BG tiles whose shade 0 was opaque in 2bpp)
    mov [di],ax
%endif
    add di,24
    inc word [V_P]
    cmp word [V_P],16
    jb .p
%ifdef FPAL
    call fighter_palettes       ; only after a colour/name cache change, not per tile
%endif
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
%ifdef CTAB
    retf                    ; HYBRID+CTAB: fighters use per-pixel 4bpp classes, no band hack
%endif
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

%ifdef HYBRID
; ---- PROTOTYPE (T17): rolling resync of the 512 game tiles into 4bpp, map-aware for colour 0.
; In 2bpp, BOTH screens use palette bit 2: 0-3/8-11 opaque, 4-7/12-15 transparent at shade 0.
; In 4bpp zero is transparent for all palettes. Tiles with opaque-only map references expand zero -> 4; others keep zero.
; OAM uses are not scanned here: map-only classification is not a complete ownership/conflict proof.
; Tile flags (1 byte/tile) live at 0000:8000..81FF (prototype reservation; all-mode lifetime safety unproven): bit0 = referenced opaque, bit1 = referenced transparent.
; Runs from the VBlank colour hook while RSY>0 (set on every scene/palette change): 32 tiles per call, cursor wraps over 0..511;
; the map scan runs on the call that starts a round. Needs ds=es=0, DF=0. Clobbers ax,bx,cx,dx,si,di,bp.
rsyn:
    cmp byte [FIGHT],0
    je .nf
    dec byte [FIGHT]
.nf:cmp byte [RSY],0
    je .rd
    dec byte [RSY]
    mov bx,[RSC]
    and bx,0x1E0            ; invariant: cursor is a multiple of 32 in 0..480, so a batch never leaves tiles 0..511
    jnz .go
    push bx
    call scanop             ; scanop/scanmap clobber bx
    pop bx
.go:cmp bx,0x180
    jb .cv
    cmp byte [FIGHT],0
    jne .skip               ; fighter slots 0x180-0x1FF belong to cphook while a fight copier is active
.cv:mov si,bx
    shl si,4
    add si,0x2000
    mov di,bx
    shl di,5
    add di,0x4000
    mov cx,32
.t: mov al,[bx+0x8000]
    cmp al,1
    je .opq
    mov dx,8                ; transparent / conflict: index = shade
.r: lodsw
    stosw
    xor ax,ax
    stosw
    dec dx
    jnz .r
    jmp .nx
.opq:
    mov dx,8                ; opaque: shade 0 -> index 4 (plane 2 = NOT(p0|p1))
.q: lodsw
    stosw
    or al,ah
    not al
    xor ah,ah
    stosw
    dec dx
    jnz .q
.nx:inc bx
    loop .t
    and bx,511
    mov [RSC],bx
.rd:ret
.skip:add bx,32
    and bx,511
    mov [RSC],bx
    ret
scanop:
    push di
    mov di,0x8000
    mov cx,256
    xor ax,ax
    rep stosw
    in al,7
    xor ah,ah
    mov bp,ax               ; port 7: SCR1 map base nibble | SCR2 map base nibble << 4
    and al,15
    mov ah,al
    xor al,al
    shl ax,3                ; nibble * 0x800
    mov si,ax
    call scanmap
    mov ax,bp
    shr al,4
    mov ah,al
    xor al,al
    shl ax,3
    mov si,ax
    call scanmap
    pop di
    ret
scanmap:
    mov cx,1024
.s: lodsw
    mov bx,ax
    and bx,0x1FF
    shr ax,9
    test al,4               ; palette bit 2, identical for SCR1/SCR2; palette 8/9 are opaque
    jnz .tr
.op:mov al,1
    jmp .o
.tr:mov al,2
.o: or [bx+0x8000],al
    loop .s
    ret

; ---- PROTOTYPE (T17): copier hook. Entered (far call from the stub in bank 0x15) right before the RAM-resident copier at 0000:0120
; overwrites VRAM 0x3800-0x3FFF (tile slots 0x180-0x1FF = fighter tiles) with the staging buffer SS:0500-0CFF (128 tiles).
; Per tile: compare staging with the still-old VRAM tile; only changed tiles are expanded (class 0: index = 2bpp shade) to the
; 4bpp mirror at 0x4000 + (0x180 + i)*32 = 0x7000 + i*32. Saves ds/es; the stub saves the general registers. Fixed address 0x0500.
times 0x500-($-$$) db 0xFF
cphook:
    push ds
    push es
    cld
    mov ax,ss
    mov ds,ax               ; staging lives at SS:0500 (SS=0 observed)
    xor ax,ax
    mov es,ax
    mov byte [es:FORCE],0
    cmp word [es:V_M],0xA55A ; copier may precede the colour hook: ownership is not valid yet
    jne .force
    cmp byte [es:FIGHT],0
    jne .own
.force:
    mov byte [es:FORCE],1   ; first call after cphook did not own the slots: do not trust the equal-source skip
.own:mov byte [es:FIGHT],90
    xor bx,bx               ; tile index 0..127
    mov si,0x0500
.t: mov di,bx
    shl di,4
    add di,0x3800
    cmp byte [es:FORCE],0
    jne .chg
    push si
    mov cx,8
    repe cmpsw              ; ds:si (new) vs es:di (old 2bpp tile)
    pop si
    je .same
.chg:
%ifdef CTAB
    push si                 ; changed tile: 16-bit content hash (rol 3 / xor over 8 words)
    xor dx,dx
    mov cx,8
.h: lodsw
    rol dx,3
    xor dx,ax
    loop .h
    pop si
%endif
    mov di,bx
    shl di,5
    add di,0x7000
%ifdef CTAB
    push bx                  ; Exact-source records sorted by hash16; build selects CTB2/CTB3 stride.
    xor ax,ax                ; lower-bound binary search on the hash: ax = lo, cx = hi (record indices)
    mov cx,[cs:CTABA+4]
.lb:cmp ax,cx
    jae .lbd
    mov bp,ax
    add bp,cx
    shr bp,1                 ; mid index
%ifdef FULLTILE
    imul bx,bp,50
%else
    mov bx,bp
    shl bx,5
    add bx,bp
    add bx,bp
%endif                ; bx = mid*record stride
    cmp [cs:bx+CTABA+6],dx
    jb .lbl
    mov cx,bp                ; record.hash >= dx -> hi = mid
    jmp .lb
.lbl:lea ax,[bp+1]           ; record.hash < dx -> lo = mid+1
    jmp .lb
.lbd:mov bp,ax               ; first record with hash >= dx; verify the equal-hash run against the exact source bytes
%ifdef FULLTILE
    imul bx,bp,50
%else
    mov bx,bp
    shl bx,5
    add bx,bp
    add bx,bp
%endif
    lea bp,[bx+CTABA+6]      ; absolute pointer of that record
    mov bx,[cs:CTABA+4]      ; bx = remaining records (count - index)
    sub bx,ax
    mov cx,bx
    pop bx                   ; restore tile index (bx was only a temporary above)
    jcxz .plain
.s: cmp dx,[cs:bp]
    jne .plain               ; sorted: the first non-equal hash ends the run
    push es
    push si
    push di
    push cx
    push cs
    pop es
    lea di,[bp+2]
    mov cx,8
    repe cmpsw
    pop cx
    pop di
    pop si
    pop es
    je .found
    add bp,CTSTRIDE
    loop .s
%endif
.plain:
    mov cx,8
.r: lodsw
    stosw
    xor ax,ax
    stosw
    loop .r
    jmp .n
%ifdef CTAB
.found:
    add bp,18
%ifdef FULLTILE
    ; Matched exact source: copy precomputed 4bpp. Advance original staging tile.
    add si,16
    mov cx,16
.m: mov ax,[cs:bp]
    add bp,2
    stosw
    loop .m
%else
    mov cx,8
.m: lodsw
    stosw                   ; p0,p1 unchanged
    or al,ah
    mov ah,al               ; non-zero pixel mask
    and al,[cs:bp]          ; plane 2 = group bit 0
    and ah,[cs:bp+1]        ; plane 3 = group bit 1
    add bp,2
    stosw
    loop .m
%endif
    jmp .n
%endif
.same:
    add si,16
.n: inc bx
    cmp bx,128
    jb .t
%ifdef CTAB
%ifndef FPAL
    mov ax,[cs:CTABA+4]      ; fighter palettes 12 and 13 (16 colours each) follow the entries
    mov bx,CTSTRIDE
    mul bx
    add ax,CTABA+6
    mov si,ax
    mov di,0xFE00+12*32
    mov cx,32
.pw:mov ax,[cs:si]
    stosw
    add si,2
    loop .pw
%endif
%endif
    pop es
    pop ds
    retf
%ifdef FPAL
; V_B1/V_B2 reuse the existing cached HUD-name lookup; row+22 is a ROM palette pointer.
fighter_palettes:
    cmp word [IMG+36],0
    jne .active
    ret
.active:
    mov ax,[V_B1]
    or ax,[V_B2]
    jnz .known
    ret                        ; no recognized HUD: leave non-fight scene palettes alone
.known:
    mov bx,[V_B1]
    mov di,0xFF80
    call .side
    mov bx,[V_B2]
.side:
    mov si,0x7000             ; neutral palette for unknown/unregistered character
    or bx,bx
    jz .copy
    mov ax,[cs:bx+22]
    or ax,ax
    jz .copy
    mov si,ax
.copy:
    mov cx,16
.word:
    mov ax,[cs:si]
    stosw
    add si,2
    loop .word
    ret
%endif
%endif
