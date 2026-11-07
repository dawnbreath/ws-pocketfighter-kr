"""Bounded Pocket Fighter sprite-piece parsing; no external wsgfx dependency."""
from __future__ import annotations
import re
from PIL import Image

def bankoff(bank: int) -> int:
    return (bank & 0x1f) << 16

def tile2(rom: bytes, offset: int) -> list[list[int]]:
    if offset < 0 or offset + 16 > len(rom):
        raise ValueError(f'tile outside ROM: {offset:#x}')
    return [[((rom[offset+2*y] >> (7-x)) & 1) |
             (((rom[offset+2*y+1] >> (7-x)) & 1) << 1)
             for x in range(8)] for y in range(8)]

def parse(rom: bytes, bank: int, ptr: int, maxn: int = 128) -> list[tuple[int,int,int]]:
    if not 0 <= ptr <= 0xffff or maxn < 1: raise ValueError('invalid piece pointer/limit')
    start = bankoff(bank); out = []
    for k in range(maxn):
        offset = start + ptr + k*4
        if offset+4 > min(start+0x10000,len(rom)): raise ValueError('piece list crosses bank')
        w = int.from_bytes(rom[offset:offset+2],'little')
        y,x = rom[offset+2:offset+4]
        out.append((w,y-256 if y>127 else y,x-256 if x>127 else x))
        if w & 1: return out
    raise ValueError('unterminated piece list')

def render(rom: bytes, bank: int, base: int, pl: list, shade=(0,85,170,255)) -> Image.Image:
    if not pl: raise ValueError('empty piece list')
    x0 = min(p[2] for p in pl); y0 = min(p[1] for p in pl)
    width = max(p[2] for p in pl)-x0+8; height = max(p[1] for p in pl)-y0+8
    if width>256 or height>256: raise ValueError('frame bounds exceed 256px')
    im = Image.new('L',(width,height),40)
    for w,y,x in pl:
        offset = bankoff(bank)+base+((w&0x1ffe)>>1)*16
        if offset+16 > bankoff(bank)+0x10000: raise ValueError('tile crosses bank')
        pixels = tile2(rom,offset)
        for yy in range(8):
            for xx in range(8):
                X = 7-xx if w&0x4000 else xx; Y = 7-yy if w&0x8000 else yy
                im.putpixel((x-x0+X,y-y0+Y),shade[pixels[yy][xx]])
    return im

def find_cmds(rom: bytes) -> list[tuple[int,int,int,int]]:
    result = []
    for m in re.finditer(rb'\x04(..)(.)\x00\x05\xff(..)',rom,re.S):
        result.append((m.start(),int.from_bytes(m[1],'little'),m[2][0],int.from_bytes(m[3],'little')))
    return result
