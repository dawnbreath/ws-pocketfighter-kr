import re, sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import wsgfx
from PIL import Image, ImageDraw
def bankoff(bank): return (bank & 0x1f)<<16
def parse(rom, bank, ptr, maxn=128):
    o=bankoff(bank)+ptr; out=[]
    for k in range(maxn):
        w=rom[o]|rom[o+1]<<8; y=rom[o+2]; x=rom[o+3]
        y=y-256 if y>127 else y; x=x-256 if x>127 else x
        out.append((w,y,x)); o+=4
        if w&1: break
    return out
def render(rom, bank, base, pl, shade=(0,85,170,255)):
    xs=[p[2] for p in pl]; ys=[p[1] for p in pl]
    x0,y0=min(xs),min(ys); W=max(xs)-x0+8; H=max(ys)-y0+8
    if W>256 or H>256: return None
    im=Image.new('L',(W,H),40)
    for w,y,x in pl:
        t=(w&0x1ffe)>>1; src=bankoff(bank)+base+t*16
        if src+16>len(rom): return None
        p=wsgfx.tile2(rom,src); hf=w&0x4000; vf=w&0x8000
        for yy in range(8):
            for xx in range(8):
                v=p[yy][xx]; X=7-xx if hf else xx; Y=7-yy if vf else yy
                im.putpixel((x-x0+X,y-y0+Y),shade[v])
    return im
def find_cmds(rom):
    res=[]
    for m in re.finditer(rb'\x04(..)(.)\x00\x05\xff(..)',rom,re.S):
        base=m.group(1)[0]|m.group(1)[1]<<8; bank=m.group(2)[0]; ptr=m.group(3)[0]|m.group(3)[1]<<8
        res.append((m.start(),base,bank,ptr))
    return res
