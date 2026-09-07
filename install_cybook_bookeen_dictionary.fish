#!/usr/bin/env fish

set script_dir (cd (dirname (status --current-filename)); pwd)
set cybook_mount "/Volumes/Cybook"
set dict_dir "$cybook_mount/Dictionaries"
set config_file "$cybook_mount/system/user/dictconfig.dat"
set source_base "eo.revo_eo"
set install_lang "eo"
set dict_id "revo"
set keep_penelope_version 0

set i 1
while test $i -le (count $argv)
    switch "$argv[$i]"
        case --slot-lang
            set i (math $i + 1)
            if test $i -gt (count $argv)
                echo "Usage: ./install_cybook_bookeen_dictionary.fish [--slot-lang <eo|de|en|fr|it>] [--dict-id <name>] [--keep-penelope-version]"
                exit 2
            end
            set install_lang "$argv[$i]"
        case --dict-id
            set i (math $i + 1)
            if test $i -gt (count $argv)
                echo "Usage: ./install_cybook_bookeen_dictionary.fish [--slot-lang <eo|de|en|fr|it>] [--dict-id <name>] [--keep-penelope-version]"
                exit 2
            end
            set dict_id "$argv[$i]"
        case --keep-penelope-version
            set keep_penelope_version 1
        case '*'
            echo "Usage: ./install_cybook_bookeen_dictionary.fish [--slot-lang <eo|de|en|fr|it>] [--dict-id <name>] [--keep-penelope-version]"
            exit 2
    end
    set i (math $i + 1)
end

if not string match -rq '^[A-Za-z0-9-]+$' -- "$dict_id"
    echo "Invalid --dict-id '$dict_id'. Use only letters, digits, and dashes."
    exit 2
end

set dict_base "$install_lang.$dict_id"

if not test -d "$dict_dir"
    echo "Cybook not mounted at $cybook_mount"
    exit 1
end

set src_dict "$script_dir/$source_base.dict"
set src_idx "$script_dir/$source_base.dict.idx"

if not test -f "$src_dict"
    echo "Missing $src_dict"
    echo "Build first: ./build_cybook_dictionary.fish --with-penelope-bookeen"
    exit 1
end

if not test -f "$src_idx"
    echo "Missing $src_idx"
    echo "Build first: ./build_cybook_dictionary.fish --with-penelope-bookeen"
    exit 1
end

echo "[1/5] Preparing Bookeen metadata..."
set temp_idx "$script_dir/$dict_base.dict.idx"
if test "$temp_idx" != "$src_idx"
    cp "$src_idx" "$temp_idx"
    or exit 1
end
if test $keep_penelope_version -eq 1
    python3 "$script_dir/normalize_bookeen_idx.py" "$temp_idx" --dict-type stardict --version 11 --lang-from "$install_lang" --lang-to "$install_lang" --title "ReVo Esperanto ($install_lang)"
    or exit 1
else
    python3 "$script_dir/normalize_bookeen_idx.py" "$temp_idx" --lang-from "$install_lang" --lang-to "$install_lang" --title "ReVo Esperanto ($install_lang)"
    or exit 1
end

echo "[2/5] Copying dictionary files..."
cp "$src_dict" "$dict_dir/$dict_base.dict"
or exit 1
cp "$temp_idx" "$dict_dir/$dict_base.dict.idx"
or exit 1
rm -f "$dict_dir/$dict_base.idx"

# Remove macOS sidecar files that can confuse simple file scanners on embedded devices.
find "$dict_dir" -name '._*' -type f -delete

echo "[3/5] Backing up dictconfig.dat..."
cp "$config_file" "$config_file.bak"
or exit 1

echo "[4/5] Registering dictionary in dictconfig.dat..."
python3 "$script_dir/register_cybook_dict.py" "$config_file" "dict:///mnt/fat/Dictionaries/$dict_base.dict" --selected 1
or exit 1

echo "[5/5] Done. Current dictionary files:"
ls -lh "$dict_dir/$dict_base.dict" "$dict_dir/$dict_base.dict.idx"

echo "Now safely eject and reboot the Cybook:"
echo "  diskutil eject $cybook_mount"
