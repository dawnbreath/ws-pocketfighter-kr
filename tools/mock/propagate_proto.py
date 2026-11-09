"""PROTOTYPE (T18, Claude): few-shot per-pixel part classifier for one fighter, trained on reviewed seed poses.
Reads a local capture (tools/capture_frames.py output, game-derived, git-ignored) and a local seeds pickle
{pose_number: {(y, x): class_index}} (reviewed labels, game-derived, never committed). Requires scikit-learn (not a project dependency).
Features per non-transparent pixel: 7x7 shade neighbourhood (-1 outside) + relative x/y (0..10) in the fighter bbox.
Known weaknesses (see docs/4bpp-plan.md T18): one seed pose gives plausible layout but legs/arms/thin parts are wrong;
outline-component majority smoothing made results worse. Use as a first-pass proposal generator only.
usage: python tools/mock/propagate_proto.py CAPTURE.json SEEDS.pkl OUT_DIR
"""
import hashlib, json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import segment_frames as SF
from sklearn.ensemble import RandomForestClassifier
from PIL import Image

CLASSES = ['skin', 'hair', 'blue', 'brown', 'tights', 'white', 'silver']   # fighter-specific; edit per character


def poses(capture):
    d = json.load(open(capture)); side = d['side']; seen = set(); out = []
    for i, f in enumerate(d['frames']):
        px, owner, sprites = SF.compose(f, side); ys, xs = np.where(px > 0)
        if len(ys) == 0: continue
        crop = px[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h = hashlib.md5(crop.tobytes() + bytes(crop.shape)).hexdigest()
        if h in seen: continue
        seen.add(h); out.append((len(out) + 1, i, crop))
    return out


def features(px, r=3):
    H, W = px.shape; P = np.pad(px, r, constant_values=-1); rows = []; pos = []
    for y in range(H):
        for x in range(W):
            if px[y, x] <= 0: continue
            rows.append(np.concatenate([P[y:y + 2 * r + 1, x:x + 2 * r + 1].ravel(), [x / W * 10, y / H * 10]])); pos.append((y, x))
    return np.array(rows, float), pos


def train(pose_list, seeds):
    X, y = [], []
    for n, labels in seeds.items():
        px = pose_list[n - 1][2]; Xe, pe = features(px)
        for row, p in zip(Xe, pe):
            if p in labels: X.append(row); y.append(labels[p])
    return RandomForestClassifier(n_estimators=200, random_state=0).fit(np.array(X), np.array(y))


def predict_pose(
    clf: RandomForestClassifier, pixels: np.ndarray
) -> tuple[list[tuple[int, int]], np.ndarray, np.ndarray]:
    """Return semantic class IDs, not probability-column indices."""
    rows, positions = features(pixels)
    probabilities = clf.predict_proba(rows)
    return positions, clf.classes_[probabilities.argmax(1)], probabilities.max(1)


if __name__ == '__main__':
    cap, seeds_path, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=False)
    P = poses(cap); clf = train(P, pickle.load(open(seeds_path, 'rb')))
    predictions = {n: predict_pose(clf, px) for n, i, px in P}
    pickle.dump(predictions, open(os.path.join(out, 'predictions.pkl'), 'wb'))
    print(len(P), 'poses; predictions (class + confidence) written, local only')
