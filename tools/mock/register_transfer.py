"""Registration-based label propagation between near-identical poses (T18, Claude). NO game data in this file.

For every non-transparent pixel of a target pose, find the pixel of an already-labelled source pose (within +-rad px) with the SAME shade
whose (2*pr+1)^2 shade patch differs least (ties: smaller shift); accept when at most `maxbad` patch pixels differ. Works well between
animation neighbours (e.g. the 4 idle "breathing" variants of Chun-Li: 80-96 % strict coverage, visually exact), and fails between
different drawings (walk/jump/attack: median coverage < 1 %) — those need their own reviewed seed. A chain (BFS) adds the pose with the
best strict coverage if >= TH; second pass (rad 4, maxbad 8) plus nearest-labelled fill (<= 3 px) completes the pose.

usage: python tools/mock/register_transfer.py CAPTURE.json SEEDS.pkl OUT.pkl [TH]
  SEEDS.pkl: {pose_number: {(y, x): class_name}} (see tools/mock/seed_recipe.py); OUT.pkl: (labels, depth, parent, coverage) — local, game-derived.
Pose numbering = tools/mock/propagate_proto.poses(): translation-normalised unique poses in capture order.
"""
import pickle, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import propagate_proto as PP


def transfer(src, labels, tgt, rad=3, pr=2, maxbad=3):
    Hs, Ws = src.shape; Ht, Wt = tgt.shape
    P = np.pad(src, pr + rad, constant_values=-1); T = np.pad(tgt, pr, constant_values=-1); out = {}
    for y in range(Ht):
        for x in range(Wt):
            if tgt[y, x] <= 0: continue
            tp = T[y:y + 2 * pr + 1, x:x + 2 * pr + 1]; best = None
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    sy, sx = y + dy, x + dx
                    if not (0 <= sy < Hs and 0 <= sx < Ws) or src[sy, sx] != tgt[y, x] or (sy, sx) not in labels: continue
                    sp = P[sy + rad:sy + rad + 2 * pr + 1, sx + rad:sx + rad + 2 * pr + 1]
                    key = (int((sp != tp).sum()), abs(dy) + abs(dx))
                    if best is None or key < best[0]: best = (key, labels[(sy, sx)])
            if best and best[0][0] <= maxbad: out[(y, x)] = best[1]
    return out


def complete(src, lab, tgt):
    out = transfer(src, lab, tgt, 3, 2, 2)
    for k, v in transfer(src, lab, tgt, 4, 2, 8).items(): out.setdefault(k, v)
    return out


def fill(tgt, out):
    if not out: return out
    lab = np.array(list(out.keys()))
    for y in range(tgt.shape[0]):
        for x in range(tgt.shape[1]):
            if tgt[y, x] > 0 and (y, x) not in out:
                d = (lab[:, 0] - y) ** 2 + (lab[:, 1] - x) ** 2; j = int(d.argmin())
                if d[j] <= 9: out[(y, x)] = out[tuple(lab[j])]
    return out


if __name__ == '__main__':
    cap, seeds, dest = sys.argv[1:4]; TH = float(sys.argv[4]) if len(sys.argv) > 4 else 0.55
    poses = PP.poses(cap); N = len(poses)
    labels = pickle.load(open(seeds, 'rb')); depth = {n: 0 for n in labels}; parent = {n: None for n in labels}; cov = {n: 1.0 for n in labels}
    while True:
        best = None
        for n in range(1, N + 1):
            if n in labels: continue
            tgt = poses[n - 1][2]; tot = int((tgt > 0).sum())
            for m, lab in list(labels.items()):
                s = poses[m - 1][2]
                if abs(s.shape[0] - tgt.shape[0]) > 8 or abs(s.shape[1] - tgt.shape[1]) > 10: continue
                c = len(transfer(s, lab, tgt, 3, 2, 2)) / tot
                if best is None or c > best[0]: best = (c, n, m)
        if best is None or best[0] < TH: break
        c, n, m = best; tgt = poses[n - 1][2]
        labels[n] = fill(tgt, complete(poses[m - 1][2], labels[m], tgt)); depth[n] = depth[m] + 1; parent[n] = m; cov[n] = c
        print('pose', n, 'from', m, 'strict coverage %.2f' % c, 'depth', depth[n], flush=True)
    pickle.dump((labels, depth, parent, cov), open(dest, 'wb')); print('labelled', len(labels), 'of', N, 'poses')
