"""Build or verify MANIFEST_SHA256.txt from the complete tracked tree."""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("MANIFEST_SHA256.txt")

def tracked_files():
    raw = subprocess.check_output(["git", "ls-files", "-z"])
    paths = [x.decode("utf-8") for x in raw.split(b"\x00") if x]
    return sorted(p for p in paths if p != str(MANIFEST))

def expected_manifest():
    lines = []
    for path in tracked_files():
        content = Path(path).read_bytes()
        lines.append(f"{hashlib.sha256(content).hexdigest()}  {path}\n")
    return "".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    calculated = expected_manifest()
    if args.write:
        MANIFEST.write_text(calculated, encoding="utf-8")
        print(f"Updated {MANIFEST} for {len(tracked_files())} tracked files")
        return 0
    if not MANIFEST.exists():
        print("ERROR: MANIFEST_SHA256.txt missing", file=sys.stderr)
        return 1
    original = MANIFEST.read_text(encoding="utf-8")
    if original != calculated:
        import difflib
        sys.stderr.writelines(difflib.unified_diff(original.splitlines(keepends=True), calculated.splitlines(keepends=True), fromfile="published manifest", tofile="actual tracked files"))
        return 1
    print(f"Verified SHA256 for {len(tracked_files())} tracked files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
