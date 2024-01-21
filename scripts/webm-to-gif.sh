#! /usr/bin/env nix-shell
#! nix-shell -i bash -p ffmpeg

# This script converts a webm video to a gif.
for video in images/*.webm; do
    filename=$(basename "$video" ".webm")
    if [ -f "images/$filename.gif" ]; then
        continue
    fi
    TMP=$(mktemp --suffix .png)
    ffmpeg -y -i "$video" -vf palettegen "$TMP"
    ffmpeg -y -i "$video" -i "$TMP" -filter_complex paletteuse -r 10  "images/$filename.gif"
    rm "$TMP"
done