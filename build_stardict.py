import argparse
import csv
import struct
from collections import OrderedDict
from pathlib import Path


def load_entries(csv_path: Path) -> list[tuple[str, str]]:
    grouped: OrderedDict[str, list[str]] = OrderedDict()

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            word = row[0].strip()
            definition = row[1].strip()
            if not word or not definition:
                continue
            grouped.setdefault(word, []).append(definition)

    merged = [(word, "\n\n".join(defs)) for word, defs in grouped.items()]
    # StarDict readers expect sorted headwords for fast lookup.
    merged.sort(key=lambda item: item[0].casefold())
    return merged


def write_stardict(entries: list[tuple[str, str]], out_prefix: Path, book_name: str) -> tuple[Path, Path, Path]:
    dict_path = out_prefix.with_suffix(".dict")
    idx_path = out_prefix.with_suffix(".idx")
    ifo_path = out_prefix.with_suffix(".ifo")

    offset = 0
    idx_size = 0

    with dict_path.open("wb") as dict_f, idx_path.open("wb") as idx_f:
        for word, definition in entries:
            word_b = word.encode("utf-8")
            def_b = definition.encode("utf-8")

            dict_f.write(def_b)
            idx_record = word_b + b"\x00" + struct.pack(">II", offset, len(def_b))
            idx_f.write(idx_record)

            offset += len(def_b)
            idx_size += len(idx_record)

    with ifo_path.open("w", encoding="utf-8", newline="\n") as ifo_f:
        ifo_f.write("StarDict's dict ifo file\n")
        ifo_f.write("version=2.4.2\n")
        ifo_f.write(f"bookname={book_name}\n")
        ifo_f.write(f"wordcount={len(entries)}\n")
        ifo_f.write(f"idxfilesize={idx_size}\n")
        ifo_f.write("sametypesequence=m\n")

    return ifo_path, idx_path, dict_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a StarDict dictionary from a two-column CSV file.")
    parser.add_argument("--input", default="vortaro.csv", help="Input CSV path (default: vortaro.csv)")
    parser.add_argument("--output-prefix", default="revo_eo", help="Output prefix for .ifo/.idx/.dict")
    parser.add_argument("--book-name", default="ReVo Esperanto", help="Dictionary name in .ifo")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_prefix = Path(args.output_prefix)

    if not input_path.exists():
        raise SystemExit(f"Input CSV not found: {input_path}")

    entries = load_entries(input_path)
    if not entries:
        raise SystemExit("No valid entries found in input CSV")

    ifo_path, idx_path, dict_path = write_stardict(entries, out_prefix, args.book_name)

    print(f"Built {len(entries)} entries")
    print(f"- {ifo_path}")
    print(f"- {idx_path}")
    print(f"- {dict_path}")


if __name__ == "__main__":
    main()

