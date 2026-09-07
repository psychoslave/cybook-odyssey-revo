#!/usr/bin/env python3
"""Normalize Cybook Bookeen metadata for better device compatibility."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def normalize(
    db_path: Path,
    dict_type: str,
    version: str,
    lang_from: str | None,
    lang_to: str | None,
    title: str | None,
) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        with conn:
            conn.execute(
                "UPDATE T_DictVersion SET F_DictType = ?, F_Version = ?",
                (dict_type, version),
            )
            # Some firmware gates visibility by language code in T_DictInfo.
            if lang_from is not None:
                conn.execute("UPDATE T_DictInfo SET F_LangFrom = ?", (lang_from,))
            if lang_to is not None:
                conn.execute("UPDATE T_DictInfo SET F_LangTo = ?", (lang_to,))
            if title is not None:
                conn.execute("UPDATE T_DictInfo SET F_Title = ?", (title,))
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set metadata in a Bookeen .dict.idx SQLite file."
    )
    parser.add_argument("idx", help="Path to .dict.idx SQLite file")
    parser.add_argument("--dict-type", default="WIKTIONARY")
    parser.add_argument("--version", default="12")
    parser.add_argument("--lang-from", default=None)
    parser.add_argument("--lang-to", default=None)
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    db_path = Path(args.idx)
    if not db_path.is_file():
        raise SystemExit(f"Missing file: {db_path}")

    normalize(
        db_path,
        args.dict_type,
        args.version,
        args.lang_from,
        args.lang_to,
        args.title,
    )
    print(
        f"Updated {db_path.name}: F_DictType={args.dict_type}, F_Version={args.version}, "
        f"F_LangFrom={args.lang_from or '<unchanged>'}, F_LangTo={args.lang_to or '<unchanged>'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
