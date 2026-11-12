"""One manually checked Chun-Li breathing neighbour; not arbitrary pose propagation."""

from __future__ import annotations
import hashlib
import numpy as np
from register_transfer import transfer

TARGET = "09b8001e109c1602f4b3d47951121a04"
SOURCE = "91f38eefec7d270fbdad21bd9208a7da"


def author(source: np.ndarray, indices: np.ndarray, target: np.ndarray) -> np.ndarray:
    for crop, key in [(source, SOURCE), (target, TARGET)]:
        if hashlib.md5(crop.tobytes() + bytes(crop.shape)).hexdigest() != key:
            raise ValueError("idle mapping requires exact source poses")
    labels = {(y, x): int(indices[y, x]) for y, x in zip(*np.nonzero(source))}
    strict = transfer(source, labels, target, 3, 2, 2)
    # New visible pixels reviewed against the original monochrome frame:
    # exposed arm/neck and the two pixels at the rising blue shoulder.
    revealed = {
        (3, 13): 0,
        (3, 14): 0,
        (8, 14): 1,
        (9, 14): 1,
        (21, 14): 0,
        (3, 15): 0,
        (3, 16): 0,
        (4, 16): 0,
    }
    out = np.zeros(target.shape, dtype=np.int8)
    for y, x in zip(*np.nonzero(target)):
        sy = y + (1 if 16 <= y < 29 else 0)
        if source[sy, x]:
            value = int(indices[sy, x])
            out[y, x] = (
                value
                if value == 4 or (value == 13 and source[sy, x] != 1)
                else (value // 4) * 4 + int(target[y, x])
            )
        elif (x, y) in revealed:
            out[y, x] = revealed[x, y] * 4 + int(target[y, x])
        elif (y, x) in strict:
            out[y, x] = strict[y, x]
        else:
            raise ValueError(f"unresolved neighbour pixel {x},{y}")
    return out
