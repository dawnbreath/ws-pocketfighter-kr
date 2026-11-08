"""Capture local-only Pocket Fighter OAM/VRAM samples from a fresh emucap run."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from regress import MCP, digest

CHARACTERS = {"chunli": ["down", "left"], "zangief": ["down", "down", "right"]}
BASE_SHA = "b47c8692ed9ab0c1ee598ae32126d30daef7f8bc8948c33d6919dd4c7505905e"


def memory(client: MCP, address: int, length: int) -> str:
    value = client.call(
        "read_memory", {"memory_type": "ram", "address": address, "length": length}
    )["hex"]
    if len(bytes.fromhex(value)) != length:
        raise ValueError("short memory read")
    return value


def capture(
    rom: Path, out: Path, binary: Path, mednafen: Path, character: str, samples: int
) -> dict:
    if digest(rom) != BASE_SHA:
        raise ValueError("route is verified only for the original PF ROM hash")
    if not 1 <= samples <= 1000:
        raise ValueError("samples must be 1..1000")
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": 1,
        "character": character,
        "side": 4,
        "rom_sha256": digest(rom),
        "emucap_sha256": digest(binary),
        "mednafen_sha256": digest(mednafen),
        "start": "cold boot; fresh runtime; no imported save",
        "status": "INCOMPLETE",
        "identity": "scripted selection; inspect selection.png and fight.png before accepting",
        "timing": "frozen frame boundary RAM; screenshots may show preceding latched frame",
        "events": [],
        "frames": [],
    }
    client = None
    launch_id = None
    elapsed = 0
    try:
        client = MCP(binary, out, mednafen)
        client.call("bootstrap")
        client.call(
            "launch_plan", {"content_path": str(rom.resolve()), "system": "wswan"}
        )
        client.call("status")
        launch = client.call(
            "launch",
            {
                "content_path": str(rom.resolve()),
                "system": "wswan",
                "display": False,
                "sound": False,
                "start_frozen": True,
            },
        )
        launch_id = launch.get("launch_id")
        if not launch.get("launched") or not launch_id:
            raise RuntimeError("launch failed")
        status = client.call("status")
        if (
            status.get("state") != "frozen"
            or status.get("contracts", {}).get("state") != "validated"
        ):
            raise RuntimeError("runtime must be frozen and validated")
        limit = status["contracts"]["constraints"]["execution.step.max_count"]

        def advance(buttons: list[str], press: int, after: int = 0) -> None:
            nonlocal elapsed
            if buttons:
                result = client.call(
                    "tap",
                    {"buttons": buttons, "press_frames": press, "after_frames": after},
                )
            else:
                if press > limit:
                    raise ValueError("step exceeds advertised bound")
                result = client.call("step", {"count": press, "unit": "frames"})
            if result.get("status") == "interrupted":
                raise RuntimeError("execution interrupted")
            elapsed += press + after
            report["events"].append(
                {"buttons": buttons, "press": press, "after": after}
            )

        def shot(name: str) -> None:
            client.call("screenshot", {"save_path": str(out / name)})

        advance([], 400)
        for key, press, after in [
            ("start", 4, 150),
            ("start", 4, 120),
            ("a", 3, 90),
            ("a", 3, 120),
        ]:
            advance([key], press, after)
        for key in CHARACTERS[character]:
            advance([key], 2, 15)
        shot("selection.png")
        advance(["a"], 3, 150)
        for _ in range(30):
            advance(["a"], 3, 50)
        shot("fight.png")
        # Short actions sample idle, attacks, crouch, jump and movement; not exhaustive moves.
        actions = [[], ["a"], [], ["b"], ["down"], ["up"], ["left"], ["right"]]
        for index in range(samples):
            gfx = client.call("get_state", {"groups": ["Gfx"]})["state"]
            start = gfx["Gfx.SpriteStart"]
            count = gfx["Gfx.SpriteCount"]
            base = gfx["Gfx.SPRBase"] * 512
            if (
                not 0 <= start < 128
                or not 0 <= count <= 128
                or not 0 <= base <= 0x10000 - 512
            ):
                raise ValueError("unsupported OAM range")
            # Read all slots, preserve active start/count instead of treating stale slots as sprites.
            oam = memory(client, base, 512)
            vram = memory(client, 0x2000, 8192)
            report["frames"].append(
                {
                    "index": index,
                    "elapsed_frames": elapsed,
                    "gfx": gfx,
                    "oam": oam,
                    "vram": vram,
                    "oam_base": base,
                    "sprite_start": start,
                    "sprite_count": count,
                }
            )
            if index % 32 == 0:
                shot(f"sample-{index:04d}.png")
            advance(actions[(index // 4) % len(actions)], 4)
        if digest(rom) != report["rom_sha256"]:
            raise ValueError("input ROM changed")
        if client.call("status").get("state") != "frozen":
            raise RuntimeError("runtime no longer frozen")
        report["status"] = "CAPTURED"
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        if client:
            try:
                if launch_id:
                    report["stop"] = client.call("stop", {"launch_id": launch_id})
                    if not report["stop"].get("stopped"):
                        report["status"] = "STOP_UNCONFIRMED"
            except Exception as error:
                report["stop_error"] = str(error)
                report["status"] = "STOP_UNCONFIRMED"
            finally:
                client.close()
        (out / "capture.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--character", choices=CHARACTERS, required=True)
    parser.add_argument("--samples", type=int, default=256)
    parser.add_argument("--emucap-mcp", type=Path, required=True)
    parser.add_argument("--mednafen", type=Path, required=True)
    args = parser.parse_args()
    report = capture(
        args.rom, args.out, args.emucap_mcp, args.mednafen, args.character, args.samples
    )
    print(json.dumps({"status": report["status"], "samples": len(report["frames"])}))
    if report["status"] != "CAPTURED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
