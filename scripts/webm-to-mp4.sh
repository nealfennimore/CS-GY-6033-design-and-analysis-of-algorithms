#! /usr/bin/env nix-shell
#! nix-shell -i bash -p ffmpeg

# This script converts a webm video to an mp4 video.
for video in images/*.webm; do
    filename=$(basename "$video" ".webm")
    if [ -f "images/$filename.mp4" ]; then
        continue
    fi
    ffmpeg -i "$video" -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" "images/$filename.mp4"
done