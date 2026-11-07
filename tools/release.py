"""Create verified IPS and xdelta3 packages without copying ROMs into the package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zlib


def hashes(data: bytes) -> dict[str, str | int]:
    return {"size": len(data), "crc32": f"{zlib.crc32(data):08x}", **{
        name: hashlib.new(name, data).hexdigest()
        for name in ("md5", "sha1", "sha256")
    }}


def make_ips(base: bytes, target: bytes) -> bytes:
    # Standard IPS has 24-bit offsets; EOF is itself a reserved offset.
    if max(len(base), len(target)) > 0xFFFFFF:
        raise ValueError("IPS supports this tool's files only up to 0xffffff bytes")
    patch = bytearray(b"PATCH")
    pos = 0
    while pos < len(target):
        if pos < len(base) and base[pos] == target[pos]:
            pos += 1
            continue
        start = pos
        if start == 0x454F46:
            start -= 1
        pos += 1
        while pos < len(target) and pos - start < 65535:
            if pos < len(base) and base[pos] == target[pos]:
                break
            pos += 1
        chunk = target[start:pos]
        patch += start.to_bytes(3, "big") + len(chunk).to_bytes(2, "big") + chunk
    patch += b"EOF"
    if len(target) < len(base):
        patch += len(target).to_bytes(3, "big")
    return bytes(patch)


def apply_ips(base: bytes, patch: bytes) -> bytes:
    if not patch.startswith(b"PATCH"):
        raise ValueError("invalid IPS header")
    result = bytearray(base)
    pos = 5

    def take(count: int) -> bytes:
        nonlocal pos
        value = patch[pos:pos + count]
        if len(value) != count:
            raise ValueError("truncated IPS")
        pos += count
        return value

    while True:
        address = take(3)
        if address == b"EOF":
            break
        offset = int.from_bytes(address, "big")
        size = int.from_bytes(take(2), "big")
        if size:
            data = take(size)
        else:
            count = int.from_bytes(take(2), "big")
            if count == 0:
                raise ValueError("empty IPS RLE record")
            data = take(1) * count
        end = offset + len(data)
        if end > 0xFFFFFF:
            raise ValueError("IPS record outside supported range")
        if end > len(result):
            result.extend(bytes(end - len(result)))
        result[offset:end] = data
    remainder = len(patch) - pos
    if remainder == 3:
        size = int.from_bytes(take(3), "big")
        if size > len(result):
            raise ValueError("invalid IPS truncation size")
        del result[size:]
    elif remainder:
        raise ValueError("trailing IPS garbage")
    return bytes(result)


def package(base_path: Path, target_path: Path, out: Path, xdelta: str) -> dict:
    base, target = base_path.read_bytes(), target_path.read_bytes()
    if not base or not target or base == target:
        raise ValueError("expected nonempty, distinct base and target")
    if out.exists():
        raise ValueError("output directory must be new; previous packages are preserved")
    exe = shutil.which(xdelta)
    if exe is None:
        raise ValueError("xdelta3 not found; use --xdelta3 /path/to/xdelta3")
    exe = str(Path(exe).resolve())
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="release-", dir=out.parent) as temp:
        stage = Path(temp)
        (stage / "base.bin").write_bytes(base)
        (stage / "target.bin").write_bytes(target)
        ips = make_ips(base, target)
        if apply_ips(base, ips) != target:
            raise ValueError("IPS round trip failed")
        (stage / "patch.ips").write_bytes(ips)
        subprocess.run([exe, "-e", "-9", "-S", "none", "-A", "-s", "base.bin",
                        "target.bin", "patch.xdelta"], cwd=stage, check=True)
        subprocess.run([exe, "-d", "-s", "base.bin", "patch.xdelta", "decoded.bin"],
                       cwd=stage, check=True)
        if (stage / "decoded.bin").read_bytes() != target:
            raise ValueError("xdelta round trip failed")
        report = {"base": hashes(base), "target": hashes(target),
                  "roundtrip": {"ips": "PASS", "xdelta3": "PASS"},
                  "runtime_qa": "NOT ASSESSED", "patches": {
                      name: hashes((stage / name).read_bytes())
                      for name in ("patch.ips", "patch.xdelta")}}
        (stage / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
        (stage / "README.txt").write_text(
            "Pocket Fighter WS patch package\n\n"
            "Apply either patch (not both) to the original matching manifest.json.\n"
            "xdelta3 -d -s original.ws patch.xdelta patched.ws\n"
            "IPS supports ROM expansion; use a compatible IPS patcher.\n"
            "Verify the resulting size and SHA-256 against manifest.json.\n"
            "No ROM or save files are included. Back up saves before changing builds.\n"
            "Round-trip success proves patch integrity, not runtime compatibility.\n"
            "Release owner: add version, supported emulator, tested scenes, known\n"
            "issues, credits and save compatibility before distribution.\n\n"
            + json.dumps({"base": report["base"], "target": report["target"]}, indent=2)
            + "\n", encoding="utf-8")
        # Publish only the explicit deliverables after both round trips pass.
        payload = stage / "payload"
        payload.mkdir()
        for name in ("patch.ips", "patch.xdelta", "manifest.json", "README.txt"):
            shutil.copy2(stage / name, payload / name)
        payload.rename(out)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--xdelta3", default="xdelta3")
    args = parser.parse_args()
    print(json.dumps(package(args.base, args.target, args.out, args.xdelta3), indent=2))


if __name__ == "__main__":
    main()
