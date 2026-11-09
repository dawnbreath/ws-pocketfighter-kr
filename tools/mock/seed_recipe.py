"""Source-only recipe for the owner-approved seed poses (Chun-Li idle, Zangief idle). NO game data in this file.

The approved masks are defined by (1) the pose, found in a local capture by the md5 of its translation-normalised 2bpp shade crop
(`pose_md5`) and (2) the rules below, applied to the outline components that `segment_frames.components` (== `region_mock.segment`:
barrier = shade 3) produces for exactly that crop. Component ids are therefore only valid for that crop. The rules were iterated with
the owner on rendered mocks (see docs/4bpp-plan.md and issue #20); `class_name` follows tools/mock/fighter_mock.py.

Verification (Claude, local): applying these rules to the original approved frames reproduces the approved mock exactly for Zangief
(0 of 1269 pixels differ) and within 2 of 677 pixels for Chun-Li (tie-breaking of the nearest-component fill). Rect coordinates are in
crop coordinates (top-left of the shade>0 bounding box).

usage: python tools/mock/seed_recipe.py CAPTURE.json CHARACTER(chunli|zangief) OUT.pkl
  -> pickle {pose_number: {(y, x): class_name}} for the matching pose of that capture (local, game-derived: do not commit).
"""
import hashlib, json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import segment_frames as SF

RECIPES = {
    # comp: outline-component id -> class; rects: (class, (x0, y0, x1, y1)[, only_component]) in crop coordinates, applied in order
    'zangief': dict(pose_md5='d6c38a439bca04684b9f7124e41d052e', comp={14: 'red'},
                    rects=[('red', (0, 37, 48, 45)), ('red', (20, 38, 36, 45)), ('pants', (15, 26, 22, 28)), ('pants', (15, 28, 21, 33))],
                    default='skin'),
    'chunli': dict(pose_md5='91f38eefec7d270fbdad21bd9208a7da',
                   comp={1: 'skin', 3: 'skin', 4: 'skin', 5: 'skin', 8: 'skin', 9: 'skin', 17: 'skin', 12: 'skin', 21: 'skin', 27: 'skin',
                         25: 'skin', 18: 'skin', 19: 'skin', 22: 'skin', 7: 'skin', 2: 'white', 16: 'blue', 20: 'blue', 28: 'skin',
                         26: 'brown', 29: 'white', 37: 'white'},
                   rects=[('brown', (5, 24, 10, 35)), ('skin', (10, 20, 15, 24), 16), ('blue', (6, 16, 10, 19)), ('skin', (3, 19, 9, 24)), ('silver', (4, 8, 10, 12)), ('white', (0, 35, 32, 39)), ('hair', (8, 1, 24, 4))],
                   default='nearest'),
}


def crop_md5(px):
    ys, xs = np.where(px > 0); c = px[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return hashlib.md5(c.tobytes() + bytes(c.shape)).hexdigest(), c


def classify(crop, recipe):
    comp, n = SF.components(crop); H, W = crop.shape
    cls = {}; known = set()
    for y in range(H):
        for x in range(W):
            if crop[y, x] > 0 and comp[y, x] in recipe['comp']: cls[(y, x)] = recipe['comp'][comp[y, x]]; known.add((y, x))
    for it in recipe['rects']:
        c, (x0, y0, x1, y1) = it[0], it[1]; only = it[2] if len(it) > 2 else None
        for y in range(H):
            for x in range(W):
                if crop[y, x] > 0 and x0 <= x < x1 and y0 <= y < y1 and (only is None or comp[y, x] == only):
                    cls[(y, x)] = c; known.add((y, x))
    kn = np.array(sorted(known)) if known else np.zeros((0, 2), int)
    for y in range(H):
        for x in range(W):
            if crop[y, x] > 0 and (y, x) not in cls:
                if recipe['default'] == 'skin' or len(kn) == 0: cls[(y, x)] = 'skin'
                else:
                    d = ((kn[:, 0] - y) ** 2 + (kn[:, 1] - x) ** 2); j = int(d.argmin()); cls[(y, x)] = cls[tuple(kn[j])]
    out = dict(cls)
    for y in range(H):
        for x in range(W):
            if crop[y, x] == 3 and (y, x) not in known:      # outline pixels follow neighbouring non-outline components (non-skin wins)
                nb = [cls[(yy, xx)] for yy in range(max(0, y - 1), min(H, y + 2)) for xx in range(max(0, x - 1), min(W, x + 2))
                      if crop[yy, xx] in (1, 2) and (yy, xx) in cls]
                if nb:
                    pri = [q for q in nb if q != 'skin']
                    out[(y, x)] = max(set(pri), key=pri.count) if pri else 'skin'
    return out


if __name__ == '__main__':
    cap, who, dest = sys.argv[1:4]
    d = json.load(open(cap)); side = d['side']; r = RECIPES[who]; seen = []; found = None
    for i, f in enumerate(d['frames']):
        px, _, _ = SF.compose(f, side)
        if not (px > 0).any(): continue
        h, crop = crop_md5(px)
        if h not in seen: seen.append(h)
        if r['pose_md5'] and h == r['pose_md5']: found = (seen.index(h) + 1, crop); break
    if not found: sys.exit('approved pose not found in this capture (md5 %s)' % r['pose_md5'])
    pickle.dump({found[0]: classify(found[1], r)}, open(dest, 'wb')); print('pose', found[0], 'labelled', len(classify(found[1], r)), 'pixels')
