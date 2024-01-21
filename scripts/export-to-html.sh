#! /usr/bin/env bash

jupyter nbconvert \
    --to html \
    --TagRemovePreprocessor.remove_input_tags 'hide-input' \
    --TagRemovePreprocessor.remove_all_outputs_tags 'hide-output' \
    --TagRemovePreprocessor.remove_cell_tags 'hide-cell' \
    "$1"

filename=$(basename -- "$1")
filename="${filename%%.*}"

# pandoc "$(dirname "$1")/$filename.html" -t html5 --katex -o /tmp/test.pdf

xdg-open "$(dirname "$1")/$filename.html"