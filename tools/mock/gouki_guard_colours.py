"""Gouki's two registered guard transitions share the reviewed stance boundaries."""

from __future__ import annotations

import hashlib

import numpy as np

from roster_colours import RECIPES as STANCES
from roster_dash_colours import paint_materials

RECIPES = {
    "GOUKI": {
        "poses": (
            "6291d5f78a492d991250352b06c7f0ab",
            "767eb4459b2b4ceeeaed84cd9345adb9",
        )
    }
}


def author(character: str, source: np.ndarray) -> np.ndarray:
    key = hashlib.md5(source.tobytes() + bytes(source.shape)).hexdigest()
    if character != "GOUKI" or key not in RECIPES["GOUKI"]["poses"]:
        raise ValueError("unregistered Gouki guard drawing")
    return paint_materials(source, STANCES["GOUKI"]["regions"])
