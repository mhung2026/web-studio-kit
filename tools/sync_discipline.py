#!/usr/bin/env python3
"""Đồng bộ khối '## Kỷ luật chung' của mọi agent với tools/discipline.md."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADING = "## Kỷ luật chung"


def sync(root):
    """Thay mọi thứ từ HEADING tới cuối file bằng bản gốc; thiếu thì nối vào cuối. Trả về tên file đã đổi."""
    block = (root / "tools" / "discipline.md").read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip() + "\n"
    changed = []
    for path in sorted((root / "agents").glob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        index = text.find("\n" + HEADING + "\n")
        body = text[: index + 1] if index != -1 else text.rstrip("\n") + "\n\n"
        new = body.rstrip("\n") + "\n\n" + block
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed.append(path.name)
    return changed


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    changed = sync(args.root.resolve())
    print(f"Đã cập nhật {len(changed)} agent" + (": " + ", ".join(changed) if changed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
