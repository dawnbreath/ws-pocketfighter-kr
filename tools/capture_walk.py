"""Capture fighter movement or basic attacks from a pinned state, with render checks.

Each sample reloads the same state before its recorded hold or tap sequence.
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
from sharded_colour_table import read_catalogue, catalogue_digest
from colour_layout import CONTEXT_MAP_BASE, CONTEXT_MAP_SIZE
from fighter_contexts import ACTOR_CONTEXTS


def match_render(
    expected: np.ndarray,
    actual: np.ndarray,
    visible: np.ndarray,
    moving: bool,
    airborne: bool = False,
) -> tuple[bool, int, list[int] | None]:
    """Accept exact registration only; air motion also permits vertical displacement."""
    yy, xx = np.nonzero(visible)
    if not len(xx):
        return False, 0, None
    direct = int((expected[yy, xx] != actual[yy, xx]).any(axis=1).sum())
    if not direct:
        return True, 0, [0, 0]
    matches = []
    offsets = (
        ((0, dy) for dy in range(-8, 9))
        if airborne
        else (((dx, 0) for dx in range(-6, 7)) if moving else ())
    )
    for dx, dy in offsets:
        if (xx + dx).min() < 0 or (xx + dx).max() >= actual.shape[1]:
            continue
        if (yy + dy).min() < 0 or (yy + dy).max() >= actual.shape[0]:
            continue
        if np.array_equal(expected[yy, xx], actual[yy + dy, xx + dx]):
            matches.append([dx, dy])
    return (True, 0, matches[0]) if len(matches) == 1 else (False, direct, None)


def capture(args: argparse.Namespace) -> dict:
    if not args.frames or any(n < 1 or n > 120 for n in args.frames):
        raise ValueError("hold lengths must be 1..120 frames")
    if args.motion == "dash-repeat" and any(n % 2 for n in args.frames):
        raise ValueError("repeated two-frame taps require even durations")
    if args.settle_frames is not None and not 0 <= args.settle_frames <= 600:
        raise ValueError("settle override must be 0..600 frames")
    rows, _ = read_catalogue(
        args.table, context=ACTOR_CONTEXTS.get(args.character.upper(), 0)
    )
    table = {raw: output for _, raw, output in rows}
    palette_name = {"chunli": "CHUN-LI", "leilei": "LEI-LEI"}.get(
        args.character, args.character.upper()
    )
    config = json.loads(args.palettes.read_text())
    pal = config["fighters"].get(palette_name, config["fallback"])
    colors = np.array([[int(n, 16) * 17 for n in word] for word in pal], dtype=np.uint8)
    directions = {
        "low-air": ["crouch", "crouch-a", "crouch-b", "jump", "jump-a", "jump-b"],
        "idle": ["neutral"],
        "attack": ["a", "b"],
        "chain": ["a-b", "b-a"],
    }.get(args.motion, ["left", "right"])
    requested = getattr(args, "directions", None)
    if requested is not None:
        if (
            not requested
            or len(set(requested)) != len(requested)
            or any(value not in directions for value in requested)
        ):
            raise ValueError(
                "directions must be unique members of the selected motion protocol"
            )
        directions = requested
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    rom = args.rom.resolve()
    state = args.state.resolve()
    c = None
    lid = None
    r = {
        "schema": 1,
        "character": args.character,
        "side": 4,
        "rom_sha256": digest(rom),
        "status": "INCOMPLETE",
        "frames": [],
        "events": [],
        "table_sha256": catalogue_digest(args.table),
        "emucap_sha256": digest(args.emucap_mcp),
        "mednafen_sha256": digest(args.mednafen),
        "state_sha256": digest(state),
        "settle_frames_after_load": (
            240 if args.motion in ("dash", "attack", "low-air", "chain") else 180
        ),
        "input_protocol": (
            {
                "dash": "reload base; settle 240; tap 4 release 4 then hold",
                "dash-repeat": "reload base; settle 180; repeated two-frame taps",
                "walk": "reload base; settle 180; single continuous hold",
                "idle": "reload base; settle 180; single no-input step",
                "chain": "reload base; approach right20; first attack4-release4; second attack hold",
                "attack": "reload base; settle 240; single attack hold",
                "low-air": "reload base; settle 240; crouch12 or jump4-release8; action hold",
            }[args.motion]
        ),
    }
    if args.settle_frames is not None:
        r["settle_frames_after_load"] = args.settle_frames
        r["input_protocol"] += f"; settle override {args.settle_frames}"
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

        for direction in directions:
            for tick, duration in enumerate(args.frames):
                c.call("load_state", {"path": str(state)})
                if r["settle_frames_after_load"]:
                    c.call(
                        "step",
                        {"count": r["settle_frames_after_load"], "unit": "frames"},
                    )
                if args.motion == "chain":
                    first, second = direction.split("-")
                    events = [
                        dict(buttons=["right"], press_frames=20, after_frames=0),
                        dict(buttons=[first], press_frames=4, after_frames=4),
                        dict(buttons=[second], press_frames=duration, after_frames=0),
                    ]
                elif args.motion == "low-air":
                    airborne = direction.startswith("jump")
                    suffix = direction.split("-")[1:]
                    events = [
                        {
                            "buttons": ["up" if airborne else "down"],
                            "press_frames": 4 if airborne else 12,
                            "after_frames": 8 if airborne else 0,
                        },
                        {
                            "buttons": (
                                (suffix or ["up"]) if airborne else ["down", *suffix]
                            ),
                            "press_frames": duration,
                            "after_frames": 0,
                        },
                    ]
                else:
                    event = {
                        "buttons": [] if args.motion == "idle" else [direction],
                        "press_frames": duration,
                        "after_frames": 0,
                    }
                    prefix = (
                        [{**event, "press_frames": 4, "after_frames": 4}]
                        if args.motion == "dash"
                        else []
                    )
                    events = prefix + (
                        [{**event, "press_frames": 2}] * (duration // 2)
                        if args.motion == "dash-repeat"
                        else [event]
                    )
                for event in events:
                    result = (
                        c.call("tap", event)
                        if event["buttons"]
                        else c.call(
                            "step", {"count": event["press_frames"], "unit": "frames"}
                        )
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
                if args.read_colour_buffer:
                    f["colour_vram_base"] = 0x7000
                    f["colour_vram"] = read(0x7000, 4096)
                if getattr(args, "read_context_map", False):
                    f["context_map_base"] = CONTEXT_MAP_BASE
                    f["context_map"] = read(CONTEXT_MAP_BASE, CONTEXT_MAP_SIZE)
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
                matches, count, offset = match_render(
                    expected,
                    actual,
                    valid,
                    args.motion in ("dash", "dash-repeat"),
                    args.motion == "low-air" and direction.startswith("jump"),
                )
                f.update(
                    render_matches=matches,
                    mismatched_pixels=count,
                    render_offset=offset,
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
                status_before_stop = r["status"]
                r["status"] = "STOP_UNCONFIRMED"
                r["stop"] = c.call("stop", {"launch_id": lid})
                if r["stop"].get("stopped"):
                    r["status"] = status_before_stop
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
    p.add_argument(
        "--settle-frames",
        type=int,
        default=None,
        help="Override the default settle for an already playable pinned state (0..600).",
    )
    p.add_argument("--emucap-mcp", type=Path, required=True)
    p.add_argument(
        "--character",
        choices=[
            "ryu",
            "ken",
            "chunli",
            "sakura",
            "morrigan",
            "leilei",
            "felicia",
            "tabasa",
            "ibuki",
            "zangief",
            "dan",
            "gouki",
        ],
        default="chunli",
    )
    p.add_argument("--mednafen", type=Path, required=True)
    p.add_argument(
        "--read-colour-buffer",
        action="store_true",
        help="Read the fighter 4bpp mirror for hidden-tile verification; no writes.",
    )
    p.add_argument("--frames", nargs="+", type=int, default=list(range(2, 45, 2)))
    p.add_argument(
        "--directions",
        nargs="+",
        help="Capture only these directions/actions from the selected motion protocol.",
    )
    p.add_argument(
        "--read-context-map",
        action="store_true",
        help="Read the scoped CTB4 owner map for native verification; no writes.",
    )
    p.add_argument(
        "--motion",
        choices=["walk", "dash", "dash-repeat", "attack", "low-air", "chain", "idle"],
        default="walk",
    )
    capture(p.parse_args())
