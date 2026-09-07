#!/usr/bin/env fish

set repo_dir (cd (dirname (status --current-filename)); pwd)
cd "$repo_dir"

if test -d "$repo_dir/penelope/.git"
    echo "Penelope submodule already present at $repo_dir/penelope"
    exit 0
end

echo "Adding Penelope as git submodule..."
git submodule add https://github.com/pettarin/penelope.git penelope
or exit 1

git submodule update --init --recursive penelope
or exit 1

echo "Done. Optional next step: install Penelope CLI globally."
echo "  python3 -m pip install --user penelope-dictionary-converter"

