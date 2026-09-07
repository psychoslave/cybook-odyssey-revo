# Revo Ebook Dictionaries

Build Reta Vortaro dictionaries from `revo-fonto` for e-readers.

## Quick Start (fish)

- Local StarDict builder:
  - `./build_cybook_dictionary.fish --native`
- Penelope StarDict builder:
  - `./add_penelope_submodule.fish`
  - `./build_cybook_dictionary.fish --with-penelope`
- Penelope Bookeen builder (recommended for Cybook Odyssey):
  - `./add_penelope_submodule.fish`
  - `./build_cybook_dictionary.fish --with-penelope-bookeen`

## Why Bookeen Mode for Cybook

Penelope's Bookeen output matches the format documented for Cybook Odyssey:

- `*.dict`
- `*.dict.idx`

For this project, the output files are:

- `eo.revo_eo.dict`
- `eo.revo_eo.dict.idx`

## Install on Cybook Odyssey

1. Connect the device by USB.
2. Run `./install_cybook_bookeen_dictionary.fish`.
3. Safely eject and reboot the device.
4. Open an Esperanto book and test a common word lookup.

If the dictionary still does not show on your firmware, install it into a known language slot (for example German):

- `./install_cybook_bookeen_dictionary.fish --slot-lang de`
- `./install_cybook_bookeen_dictionary.fish --slot-lang de --dict-id revo`
- `./install_cybook_bookeen_dictionary.fish --slot-lang de --dict-id revo --keep-penelope-version`

This keeps ReVo content, but sets Bookeen metadata and filename prefix to that language slot (`de.revo.*`).
Use underscore-free IDs (`--dict-id revo`) while troubleshooting firmware scanners.
If needed, keep Penelope defaults (`stardict`/`11`) with `--keep-penelope-version`.

Important: only copying `eo.revo_eo.dict` and `eo.revo_eo.dict.idx` is usually not enough. The device also needs an entry in `system/user/dictconfig.dat`, which the installer script adds.

Note: Cybook chooses dictionaries based on ebook language metadata (`dc:language`).

## Manual Build Steps

1. Generate CSV from ReVo XML:
   - `python3 convert_revo.py`
2. Build StarDict with local builder:
   - `python3 build_stardict.py --input vortaro.csv --output-prefix revo_eo --book-name "ReVo Esperanto"`
3. Verify sample entries:
   - `python3 check_stardict.py`

## Notes

- `convert_revo.py` converts ReVo XML entities to Unicode characters.
- If you run Penelope from the local submodule source, this repo currently uses `python3.10 -m penelope`.
- `normalize_bookeen_idx.py` aligns `T_DictVersion` with built-in Cybook dictionaries (`WIKTIONARY`/`12`) for better compatibility.
- `register_cybook_dict.py` updates/adds the dictionary URL in `dictconfig.dat` and marks it selected.

## Quick Troubleshooting

- Ensure `dictconfig.dat` contains `dict:///mnt/fat/Dictionaries/eo.revo_eo.dict` (or your `--slot-lang` variant).
- Prefer dictionary filenames like `<lang>.<name>.dict` with `<name>` alnum/dash only.
- Reboot after USB eject; hot unplug is often not enough for dictionary refresh.
- Test on a book whose `dc:language` matches `F_LangFrom` (for example `eo` or `de`).

## License

- Top-level scripts and integration code: `GPL-2.0-or-later` (see `LICENSE`).
- Submodules keep their upstream licenses:
  - `revo-fonto/`: GNU GPL v2
  - `penelope/`: MIT
- See `NOTICE` for repository-level licensing notes.

