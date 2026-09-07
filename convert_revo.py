import csv
import os
import re
import xml.etree.ElementTree as ET
from html.entities import html5

REVO_PATH = "revo-fonto/revo"
OUTPUT_FILE = "vortaro.csv"

# Revo files use Esperanto-specific SGML entities and some project-local entities.
# We decode known entities and drop unknown project-local references to keep parsing robust.
ENTITY_MAP = {
    "ccirc": "ĉ",
    "gcirc": "ĝ",
    "hcirc": "ĥ",
    "jcirc": "ĵ",
    "scirc": "ŝ",
    "ubreve": "ŭ",
    "Ccirc": "Ĉ",
    "Gcirc": "Ĝ",
    "Hcirc": "Ĥ",
    "Jcirc": "Ĵ",
    "Scirc": "Ŝ",
    "Ubreve": "Ŭ",
    "dash": "-",
}

ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9_.-]*);")
WHITESPACE_RE = re.compile(r"\s+")


def decode_entities(xml_text: str) -> str:
    xml_text = re.sub(r"<!DOCTYPE[^>]*>", "", xml_text)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in ENTITY_MAP:
            return ENTITY_MAP[name]
        if f"{name};" in html5:
            return html5[f"{name};"]
        return ""

    return ENTITY_RE.sub(replace, xml_text)


def normalize_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def render_with_tld(elem: ET.Element, radix: str) -> str:
    pieces: list[str] = []

    def walk(node: ET.Element) -> None:
        if node.text:
            pieces.append(node.text)
        for child in node:
            if child.tag == "tld":
                pieces.append(radix)
            else:
                walk(child)
            if child.tail:
                pieces.append(child.tail)

    walk(elem)
    return normalize_text("".join(pieces).replace("*", ""))


def parse_xml_file(path: str) -> ET.Element:
    with open(path, "r", encoding="utf-8") as f:
        cleaned = decode_entities(f.read())
    return ET.fromstring(cleaned)


print(f"Scanning XML files in {REVO_PATH}...")

written = 0
parsed_files = 0
failed_files = 0

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)

    for filename in sorted(os.listdir(REVO_PATH)):
        if not filename.endswith(".xml"):
            continue

        full_path = os.path.join(REVO_PATH, filename)

        try:
            root = parse_xml_file(full_path)
            parsed_files += 1
        except Exception:
            failed_files += 1
            continue

        article_rad = normalize_text("".join(root.findall(".//art/kap/rad")[0].itertext())) if root.findall(".//art/kap/rad") else ""

        for drv in root.findall(".//drv"):
            kap_elem = drv.find("kap")
            dif_elem = drv.find(".//dif")
            if kap_elem is None or dif_elem is None:
                continue

            headword = render_with_tld(kap_elem, article_rad)
            definition = normalize_text("".join(dif_elem.itertext()))

            if headword and definition:
                writer.writerow([headword, definition])
                written += 1

print(
    f"Done. Wrote {written} entries to {OUTPUT_FILE} "
    f"(parsed: {parsed_files} files, failed: {failed_files} files)."
)
