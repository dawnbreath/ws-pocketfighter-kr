"""Capture a continuous hold from a pinned pre-control Chun-Li state, with render checks.

Each sample reloads the same state before one hold; repeated taps can trigger dash.
All ROM-derived outputs and saves must remain local.
"""

import argparse
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from regress import MCP, digest
from segment_frames import compose
from class_table import HEADER, FULL_RECORD, validate_table


def capture(args: argparse.Namespace) -> dict:
    if not args.frames or any(n < 1 or n > 120 for n in args.frames):
        raise ValueError("hold lengths must be 1..120 frames")
    blob = args.table.read_bytes()
    validate_table(blob)
    if HEADER.unpack_from(blob)[0] != b"CTB3":
        raise ValueError("walk capture requires CTB3")
    table = {
        raw: output
        for _, raw, output in [
            FULL_RECORD.unpack_from(blob, HEADER.size + i * FULL_RECORD.size)
            for i in range(HEADER.unpack_from(blob)[1])
        ]
    }
    pal = json.loads(args.palettes.read_text())["fighters"]["CHUN-LI"]
    colors = np.array([[int(n, 16) * 17 for n in word] for word in pal], dtype=np.uint8)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    rom = args.rom.resolve()
    state = args.state.resolve()
    c = None
    lid = None
    r = {
        "schema": 1,
        "character": "chunli",
        "side": 4,
        "rom_sha256": digest(rom),
        "status": "INCOMPLETE",
        "frames": [],
        "events": [],
        "table_sha256": digest(args.table),
        "emucap_sha256": digest(args.emucap_mcp),
        "mednafen_sha256": digest(args.mednafen),
        "state_sha256": digest(state),
        "settle_frames_after_load": 180,
        "input_protocol": "reload base; settle 180; single continuous hold",
    }
    try:
        c = MCP(args.emucap_mcp, out, args.mednafen)
        c.call("bootstrap")
        a = {"content_path": str(rom), "system": "wswan"}
        c.call("launch_plan", a)
        lid = c.call(
            "launch", {**a, "display": False, "sound": False, "start_frozen": True}
        )["launch_id"]
        r["launch_id"] = lid

        def read(a, n):
            return c.call(
                "read_memory", {"memory_type": "ram", "address": a, "length": n}
            )["hex"]

        for direction in ["left", "right"]:
            for tick, duration in enumerate(args.frames):
                c.call("load_state", {"path": str(state)})
                c.call("step", {"count": 180, "unit": "frames"})
                event = {
                    "buttons": [direction],
                    "press_frames": duration,
                    "after_frames": 0,
                }
                result = c.call(
                    "tap",
                    event,
                )
                r["events"].append(event)
                if result.get("status") == "interrupted":
                    raise RuntimeError("hold interrupted")
                g = c.call("get_state", {"groups": ["Gfx"]})["state"]
                r["frames"].append(
                    {
                        "oam": read(g["Gfx.SPRBase"] * 512, 512),
                        "vram": read(0x2000, 8192),
                        "sprite_start": g["Gfx.SpriteStart"],
                        "sprite_count": g["Gfx.SpriteCount"],
                        "direction": direction,
                        "requested_frames": duration,
                    }
                )
                f = r["frames"][-1]
                px, owner, sprites = compose(f, 4)
                expected = np.zeros((144, 224, 3), dtype=np.uint8)
                for sprite in sprites:
                    if sprite["side"] != 4:
                        continue
                    raw = sprite["raw"]
                    output = table.get(
                        raw, b"".join(raw[i : i + 2] + b"\0\0" for i in range(0, 16, 2))
                    )
                    for yy in range(8):
                        for xx in range(8):
                            x = (
                                sprite["x"]
                                + (7 - xx if sprite["word"] & 0x4000 else xx)
                            ) & 255
                            y = (
                                sprite["y"]
                                + (7 - yy if sprite["word"] & 0x8000 else yy)
                            ) & 255
                            if x < 224 and y < 144 and owner[y, x] == sprite["rank"]:
                                index = sum(
                                    ((output[yy * 4 + p] >> (7 - xx)) & 1) << p
                                    for p in range(4)
                                )
                                expected[y, x] = colors[index]
                shot = out / (direction + "-%02d.png" % tick)
                c.call("screenshot", {"save_path": str(shot)})
                actual = np.array(Image.open(shot).convert("RGB"))
                valid = px > 0
                f["render_matches"] = bool(
                    valid.any() and np.array_equal(expected[valid], actual[valid])
                )
                f["mismatched_pixels"] = int(
                    ((expected != actual).any(axis=2) & valid).sum()
                )
                if f["render_matches"]:
                    c.call(
                        "save_state",
                        {"path": str(out / (direction + "-%02d.mcs" % tick))},
                    )
            c.call("screenshot", {"save_path": str(out / (direction + ".png"))})
        r["status"] = "CAPTURED"
    finally:
        try:
            if c and lid:
                r["stop"] = c.call("stop", {"launch_id": lid})
                if not r["stop"].get("stopped"):
                    r["status"] = "STOP_UNCONFIRMED"
        finally:
            if c:
                c.close()
            (out / "capture.json").write_text(json.dumps(r))
    print("captured", len(r["frames"]))
    return r


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["rom", "state", "table", "palettes", "out"]:
        p.add_argument(name, type=Path)
    p.add_argument("--emucap-mcp", type=Path, required=True)
    p.add_argument("--mednafen", type=Path, required=True)
    p.add_argument("--frames", nargs="+", type=int, default=list(range(2, 45, 2)))
    capture(p.parse_args())
