"""Static renderer: draws text straight out of a built ROM (Korean cells + the game's own SJIS glyphs)."""
import sys, struct, json
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import wsgfx, numpy as np
from PIL import Image, ImageDraw
EXP=0x200000
PAL=(255,170,85,0)
class Renderer:
    def __init__(s,path):
        s.rom=open(path,'rb').read(); s.o=s.rom[EXP:]   # original 2MB view
        t0=s.o[0x1cf070:0x1cf070+0x7c*2]; t1=s.o[0x1cf168:0x1cf168+0x59*2]
        s.map={}
        for i in range(0x7c): s.map[bytes(t0[2*i:2*i+2])]=(0,i)
        for i in range(0x59): s.map.setdefault(bytes(t1[2*i:2*i+2]),(1,i))
    def tile(s,rom,off):
        return wsgfx.tile2(rom,off)
    def glyph(s,code):
        b0,b1=code
        if b0>=0xA0:
            page=b0-0xA0; bank=page>>3; i=b1
            base=(bank<<16)+(page&7)*0x2000+(i//16)*0x200+(i%16)*16
            top=s.tile(s.rom,base); bot=s.tile(s.rom,base+0x100)
        else:
            pg,i=s.map.get(bytes(code),(0,0x3b))
            b=0xEBBDC if pg==0 else 0xECB9C
            base=b+(i//16)*0x200+(i%16)*16
            top=s.tile(s.o,base); bot=s.tile(s.o,base+0x100)
        return np.array(top+bot,dtype=np.uint8)
    def line(s,codes,scale=1):
        im=np.zeros((16,8*len(codes)),np.uint8)
        for k,c in enumerate(codes): im[:,k*8:k*8+8]=s.glyph(c)
        return im
    def img(s,rows,scale=3,pad=2):
        W=max(r.shape[1] for r in rows); H=len(rows)*(16+pad)
        a=np.full((H,W),255,np.uint8)
        lut=np.array([255,170,85,0],np.uint8)
        for k,r in enumerate(rows): a[k*(16+pad):k*(16+pad)+16,:r.shape[1]]=lut[r]
        return Image.fromarray(a).resize((W*scale,H*scale),0)
    def cells(s,off,n):
        d=s.rom[off:off+2*n]; return [d[2*i:2*i+2] for i in range(n)]
    def story_pages(s,sptr_bank,ptr):
        """decode one story page list from the new story bank -> list of pages of line images"""
        b=sptr_bank<<16; o=b+ptr; pages=[]; lines=[[]]
        while True:
            c=s.rom[o:o+2]
            if c==b'\x81\x94':
                L=chr(s.rom[o+2]); o+=3
                n={'C':2,'F':1,'T':1,'W':1,'M':1}.get(L,0); o+=n
                if L=='N': lines.append([])
                elif L in 'PE':
                    pages.append([s.line(l) for l in lines if l or True]); lines=[[]]
                    if L=='E': return pages
            else:
                lines[-1].append(bytes(c)); o+=2
