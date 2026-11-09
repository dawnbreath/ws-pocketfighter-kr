"""Proof-of-concept: outline flood-fill segmentation of ONE fighter frame (from a capture of OAM+VRAM) with per-character
geometry rules. Input is a JSON capture produced by the owner's local capture script (game data: never committed).
Usage: python tools/region_mock.py capture.json INDEX SIDE   (SIDE: 4 = P1 sprites, 5 = P2) -> region_mock.png"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import deque
from PIL import Image
import wsgfx
def frame(cap, i, side):
    r = cap[str(i)]; oam = bytes.fromhex(r['oam']); vram = bytes.fromhex(r['vram'])
    pts = [(oam[4*s] | oam[4*s+1] << 8, oam[4*s+3], oam[4*s+2]) for s in range(len(oam)//4)
           if ((oam[4*s] | oam[4*s+1] << 8) >> 9) & 7 == side]
    x0 = min(p[1] for p in pts); y0 = min(p[2] for p in pts); x1 = max(p[1] for p in pts)+8; y1 = max(p[2] for p in pts)+8
    g = np.full((y1-y0, x1-x0), -1, np.int8)
    for w, x, y in pts:
        p = wsgfx.tile2(vram, (w & 0x1ff)*16); hf = w & 0x4000; vf = w & 0x8000
        for yy in range(8):
            for xx in range(8):
                if p[yy][xx]: g[y-y0+(7-yy if vf else yy), x-x0+(7-xx if hf else xx)] = p[yy][xx]
    return g
def segment(g):
    H, W = g.shape; lab = np.zeros((H, W), int); n = 0
    for y in range(H):
        for x in range(W):
            if g[y, x] in (1, 2) and lab[y, x] == 0:
                n += 1; q = deque([(y, x)]); lab[y, x] = n
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = cy+dy, cx+dx
                        if 0 <= ny < H and 0 <= nx < W and lab[ny, nx] == 0 and g[ny, nx] in (1, 2): lab[ny, nx] = n; q.append((ny, nx))
    return lab, n
if __name__ == '__main__':
    cap = json.load(open(sys.argv[1])); g = frame(cap, sys.argv[2], int(sys.argv[3])) if False else frame(cap, int(sys.argv[2]), int(sys.argv[3]))
    lab, n = segment(g); print(n, 'regions')
