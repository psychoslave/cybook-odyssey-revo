#!/usr/bin/env python3
"""Register a dictionary URL in Cybook dictconfig.dat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def register(config_path: Path, url: str, selected: int) -> str:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("dictconfig.dat is not a JSON list")

    for entry in data:
        if entry.get("url") == url:
            entry["local"] = 1
            entry["selected"] = selected
            config_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return "updated"

    max_priority = max((int(entry.get("priority", -1)) for entry in data), default=-1)
    data.append(
        {
            "url": url,
            "local": 1,
            "selected": selected,
            "priority": max_priority + 1,
        }
    )
    config_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return "added"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a dictionary in Cybook dictconfig.dat")
    parser.add_argument("config", help="Path to dictconfig.dat")
    parser.add_argument("url", help="Dictionary URL, e.g. dict:///mnt/fat/Dictionaries/de.revo_eo.dict")
    parser.add_argument("--selected", type=int, choices=[0, 1], default=1)
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_file():
        raise SystemExit(f"Missing file: {config_path}")

    action = register(config_path, args.url, args.selected)
    print(f"{action}: {args.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

