import struct
from pathlib import Path


def read_first_entries(prefix: str, limit: int = 5) -> None:
    idx_path = Path(prefix + ".idx")
    dict_path = Path(prefix + ".dict")

    with idx_path.open("rb") as idx_f, dict_path.open("rb") as dict_f:
        shown = 0
        while shown < limit:
            word_bytes = bytearray()
            while True:
                b = idx_f.read(1)
                if not b:
                    return
                if b == b"\x00":
                    break
                word_bytes.extend(b)

            payload = idx_f.read(8)
            if len(payload) < 8:
                return
            offset, size = struct.unpack(">II", payload)
            dict_f.seek(offset)
            text = dict_f.read(size).decode("utf-8", errors="replace")

            shown += 1
            print(f"{shown:02d}. {word_bytes.decode('utf-8', errors='replace')} -> {text[:120]}")


if __name__ == "__main__":
    read_first_entries("revo_eo", limit=10)

