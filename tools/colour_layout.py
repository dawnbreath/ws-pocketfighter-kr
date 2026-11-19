"""Read the shared, static NASM colour-bank layout without evaluating code."""

from pathlib import Path
from paths import ROOT

_LAYOUT: dict[str, int] = {}
for _line in (Path(ROOT) / "src/colour_layout.inc").read_text().splitlines():
    if _line.startswith("%define "):
        _, _name, _value = _line.split()
        _LAYOUT[_name] = int(_value, 0)

FIGHTER_PALETTE_BASE = _LAYOUT["FIGHTER_PALETTE_BASE"]
CLASS_TABLE_BASE = _LAYOUT["CLASS_TABLE_BASE"]
COLOUR_BANK_END = _LAYOUT["COLOUR_BANK_END"]
if not 0x1000 < FIGHTER_PALETTE_BASE < CLASS_TABLE_BASE < COLOUR_BANK_END == 0x10000:
    raise ValueError("invalid shared colour-bank layout")

CLASS_SHARD_COUNT = _LAYOUT["CLASS_SHARD_COUNT"]
CLASS_SHARD_BANK_BASE = _LAYOUT["CLASS_SHARD_BANK_BASE"]
