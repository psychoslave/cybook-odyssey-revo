#!/usr/bin/env fish

set script_dir (cd (dirname (status --current-filename)); pwd)
cd "$script_dir"

set mode "native"
if test (count $argv) -gt 0
    switch "$argv[1]"
        case --with-penelope-bookeen
            set mode "penelope-bookeen"
        case --with-penelope
            set mode "penelope"
        case --native
            set mode "native"
        case '*'
            echo "Usage: ./build_cybook_dictionary.fish [--native|--with-penelope|--with-penelope-bookeen]"
            exit 2
    end
end

function run_penelope
    set args $argv
    if command -q penelope
        penelope $args
        return $status
    end
    if command -q python3.10; and test -d "$script_dir/penelope/penelope"
        pushd "$script_dir/penelope" >/dev/null
        python3.10 -m penelope $args
        set rc $status
        popd >/dev/null
        return $rc
    end
    echo "Penelope not found as CLI, and local source mode needs python3.10."
    echo "Run ./add_penelope_submodule.fish and ensure python3.10 is installed."
    return 1
end

echo "[1/3] Generating CSV from Revo XML..."
python3 convert_revo.py
or exit 1

if test "$mode" = "penelope"
    echo "[2/3] Building StarDict with Penelope..."
    run_penelope -i "$script_dir/vortaro.csv" -j csv -f eo -t eo -p stardict -o "$script_dir/revo_eo" --sd-no-dictzip --title "ReVo Esperanto"
    or exit 1
else if test "$mode" = "penelope-bookeen"
    echo "[2/3] Building Bookeen (Cybook native) with Penelope..."
    run_penelope -i "$script_dir/vortaro.csv" -j csv -f eo -t eo -p bookeen -o "$script_dir/eo.revo_eo" --title "ReVo Esperanto"
    or exit 1
else
    echo "[2/3] Building StarDict with local builder..."
    python3 build_stardict.py --input vortaro.csv --output-prefix revo_eo --book-name "ReVo Esperanto"
    or exit 1
end

if test "$mode" = "penelope-bookeen"
    echo "[3/4] Normalizing Bookeen metadata..."
    python3 "$script_dir/normalize_bookeen_idx.py" "$script_dir/eo.revo_eo.dict.idx"
    or exit 1

    echo "[4/4] Verifying output files..."
    test -f "$script_dir/eo.revo_eo.dict"
    or exit 1
    test -f "$script_dir/eo.revo_eo.dict.idx"
    or exit 1
else
    echo "[3/3] Verifying sample entries..."
    python3 check_stardict.py
    or exit 1
end

echo "Done. Output files:"
if test "$mode" = "penelope-bookeen"
    ls -lh eo.revo_eo.dict eo.revo_eo.dict.idx
else
    ls -lh revo_eo.ifo revo_eo.idx revo_eo.dict
end
