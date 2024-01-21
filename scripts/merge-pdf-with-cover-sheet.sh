#! /usr/bin/env nix-shell
#! nix-shell -i bash -p pdftk

pdftk $@ cat output merged.pdf