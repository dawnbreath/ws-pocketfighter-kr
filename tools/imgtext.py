"""Korean replacement of the Japanese *image* labels (sprite-assembled): same pieces/tiles, new tile pixels."""
import sys, json, struct
sys.path.insert(0,'/home/user/pocketfighter/tools'); sys.path.insert(0,'/home/user/tools/py')
import numpy as np, wsgfx
from PIL import Image, ImageDraw, ImageFont
FD='/home/user/pocketfighter/fonts/'
ORIG='/home/user/pocketfighter/orig/pf.ws'
rom0=open(ORIG,'rb').read()
LABELS={x['idx']:x for x in json.load(open('/home/user/pocketfighter/text/labels_raw.json'))}
def tile_addr(x,w): return ((x['bank']&0x1f)<<16)+x['base']+((w&0x1ffe)>>1)*16
def canvas(x):
    pl=x['pieces']; xs=[p[2] for p in pl]; ys=[p[1] for p in pl]; x0,y0=min(xs),min(ys)
    W=max(xs)-x0+8; H=max(ys)-y0+8
    g=np.full((H,W),-1,np.int8)
    for w,y,xx in pl:
        p=wsgfx.tile2(rom0,tile_addr(x,w))
        for yy in range(8):
            for xx2 in range(8): g[y-y0+yy,xx-x0+xx2]=p[yy][xx2]
    return g,x0,y0
def ttf(name,size): return ImageFont.truetype(FD+name,size)
def text_bitmap(text,font,w,h,dx=0,dy=0):
    im=Image.new('1',(w,h),0); d=ImageDraw.Draw(im); d.fontmode='1'; d.text((dx,dy),text,font=font,fill=1)
    return np.array(im,dtype=bool)
def fit(text,maxw,maxh,fonts):
    """fonts: list of (file,size) largest first; returns font whose width<=maxw"""
    for f in fonts:
        ft=ttf(*f); w=int(ft.getlength(text))
        if w<=maxw: return ft,w,f
    ft=ttf(*fonts[-1]); return ft,int(ft.getlength(text)),fonts[-1]
FONTS16=[('Galmuri14.ttf',14),('Galmuri11.ttf',12),('Galmuri9.ttf',10)]
FONTSBIG=[('Galmuri14.ttf',21),('Galmuri14.ttf',18),('Galmuri14.ttf',14),('Galmuri11.ttf',12)]
def render_label(idx,text,style='dark',margin=0,fg=None,bg=None,align='center',shadow=None,fonts=None,ydelta=0):
    x=LABELS[idx]; g,x0,y0=canvas(x); H,W=g.shape; out=g.copy()
    ix0,iy0,ix1,iy1=margin,margin,W-margin,H-margin
    mask=g>=0
    if bg is None: bg={'dark':0,'gray':1,'light':3,'big':0}[style]
    if fg is None: fg={'dark':3,'gray':3,'light':1,'big':3}[style]
    fonts=fonts or (FONTSBIG if style=='big' else FONTS16)
    ft,tw,spec=fit(text,ix1-ix0,iy1-iy0,fonts)
    out[iy0:iy1,ix0:ix1]=np.where(mask[iy0:iy1,ix0:ix1],bg,out[iy0:iy1,ix0:ix1])
    # vertical placement: glyph box height ~ font size; centre in interior
    th=spec[1]; ty=iy0+(iy1-iy0-th)//2+ydelta
    tx=ix0+((ix1-ix0-tw)//2 if align=='center' else 0)
    bm=text_bitmap(text,ft,W,H,tx,ty)
    if shadow is not None:
        sh=np.zeros_like(bm); sh[1:,1:]=bm[:-1,:-1]
        out[(sh&~bm)&mask]=shadow
    out[bm&mask]=fg
    return out,mask,x0,y0
def write_tiles(label,out,rom4,written,conflicts,exp=0x200000):
    x=LABELS[label]; _,x0,y0=canvas(x)
    for w,y,xx in x['pieces']:
        addr=tile_addr(x,w)+exp
        blk=out[y-y0:y-y0+8,xx-x0:xx-x0+8]
        if (w&0xc000):  # flipped pieces: not supported
            conflicts.append((label,addr,'flip')); continue
        t=bytearray()
        for row in blk:
            lo=hi=0
            for b in range(8):
                v=int(row[b]); lo|=(v&1)<<(7-b); hi|=((v>>1)&1)<<(7-b)
            t+=bytes([lo,hi])
        t=bytes(t)
        if addr in written and written[addr][0]!=t: conflicts.append((label,addr,'conflict with %d'%written[addr][1]))
        elif addr not in written:
            written[addr]=(t,label); rom4[addr:addr+16]=t

# ---------------------------------------------------------------- apply to the 4MB ROM image
BANK=0x11; NEWBASE=0x000b           # all new tiles live in script/tile bank 0x11 at addresses = 11 (mod 16)
def apply(R,spec,exp=0x200000):
    """Give every translated label its own freshly drawn tiles. The original JP tiles are shared between
    labels (same kanji reused), so they cannot be edited in place: tiles are re-allocated (dedup) in the
    storage freed by the JP originals + the free tail of the bank, and the label's command base / piece
    tile numbers are repointed. Piece count and positions are untouched => same VRAM tile count."""
    import collections
    # who uses which original tile
    users=collections.defaultdict(set)
    allp=json.load(open('/home/user/pocketfighter/text/labels_all.json'))
    for lab in allp:
        for w,y,x in lab['pieces']: users[((lab['bank']&0x1f)<<16)+lab['base']+((w&0x1ffe)>>1)*16].add(lab['idx'])
    done=set(spec)
    free=[a for a,u in users.items() if u<=done]
    # free tail of bank 0x11
    b=(BANK<<16)
    tail=0xe5ab
    while tail+16<=0x10000: free.append(b+tail); tail+=16
    free=sorted(set(free))
    free=[a for a in free if (a&0xf)==0xb]
    # render everything
    rend={}
    blocks={}
    for idx,(t,st,kw) in spec.items():
        out,mask,x0,y0=render_label(idx,t,st,**kw); rend[idx]=(out,x0,y0)
        for w,y,xx in LABELS[idx]['pieces']:
            blk=out[y-y0:y-y0+8,xx-x0:xx-x0+8]
            blocks.setdefault(blk.tobytes(),blk)
    assert len(blocks)<=len(free),'not enough tile storage %d>%d'%(len(blocks),len(free))
    slot={}
    for k,(key,blk) in enumerate(blocks.items()):
        addr=free[k]; slot[key]=addr
        t=bytearray()
        for row in blk:
            lo=hi=0
            for bb in range(8):
                v=int(row[bb]); lo|=(v&1)<<(7-bb); hi|=((v>>1)&1)<<(7-bb)
            t+=bytes([lo,hi])
        R.b[addr+exp:addr+exp+16]=t
    # repoint commands and piece lists
    for idx in spec:
        lab=LABELS[idx]; out,x0,y0=rend[idx]
        at=lab['cmd']+exp
        assert R.b[at]==0x04, 'cmd mismatch %d'%idx
        struct.pack_into('<H',R.b,at+1,NEWBASE)
        plo=(lab['plbank']<<16)+lab['ptr']+exp
        for n,(w,y,xx) in enumerate(lab['pieces']):
            blk=out[y-y0:y-y0+8,xx-x0:xx-x0+8]
            addr=slot[blk.tobytes()]; tn=(addr-b-NEWBASE)//16
            assert 0<=tn<0x1000 and (addr-b-NEWBASE)%16==0
            nw=(w&~0x1ffe)|(tn<<1)
            struct.pack_into('<H',R.b,plo+4*n,nw)
    return len(blocks),len(free)

# ---------------------------------------------------------------- title buttons (raw 16-tiles-per-row sheet in ROM)
SHEET=0xd0490
def sheet_block(col0,row0,w=5,h=3,rom=rom0):
    g=np.zeros((h*8,w*8),np.int8)
    for r in range(h):
        for c in range(w):
            t=wsgfx.tile2(rom,SHEET+((row0+r)*16+col0+c)*16)
            for y in range(8):
                for x in range(8): g[r*8+y,c*8+x]=t[y][x]
    return g
def put_block(R,g,col0,row0,exp=0x200000):
    h,w=g.shape
    for r in range(h//8):
        for c in range(w//8):
            t=bytearray()
            for y in range(8):
                lo=hi=0
                for b in range(8):
                    v=int(g[r*8+y,c*8+b]); lo|=(v&1)<<(7-b); hi|=((v>>1)&1)<<(7-b)
                t+=bytes([lo,hi])
            a=SHEET+((row0+r)*16+col0+c)*16+exp; R.b[a:a+16]=t
def title_button(lines,col0,rect=(4,1,36,22),fonts=(('Galmuri9.ttf',10),)):
    g=sheet_block(col0,0); mask=g!=0
    x0,y0,x1,y1=rect
    # clear interior of the text area to the body colour (1), keep the silhouette
    sub=g[y0:y1,x0:x1]; m=mask[y0:y1,x0:x1]
    sub[m]=1
    n=len(lines); lh=(y1-y0)//n
    for k,t in enumerate(lines):
        for f in fonts:
            ft=ttf(*f)
            if int(ft.getlength(t))<=x1-x0: break
        tw=int(ft.getlength(t)); th=f[1]
        bm=text_bitmap(t,ft,g.shape[1],g.shape[0],x0+(x1-x0-tw)//2,y0+k*lh+(lh-th)//2)
        sub_full=bm[y0:y1,x0:x1]
        sub[sub_full&m]=3
    g[y0:y1,x0:x1]=sub
    return g
def apply_title(R,exp=0x200000):
    put_block(R,title_button(['카드','배틀'],0),0,0)
    put_block(R,title_button(['카드','갤러리'],10),10,0)
