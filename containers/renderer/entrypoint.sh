#!/usr/bin/env bash
set -euo pipefail

SCENE_FILE="${1:-scene.py}"
SCENE_CLASS="${2:-GeneratedScene}"
QUALITY="${3:-1080p30}"

QUALITY_FLAG="-qh"
if [[ "$QUALITY" == "720p30" ]]; then
  QUALITY_FLAG="-qm"
elif [[ "$QUALITY" == "480p15" ]]; then
  QUALITY_FLAG="-ql"
fi

manim "$QUALITY_FLAG" "/workspace/${SCENE_FILE}" "$SCENE_CLASS" --media_dir /tmp/manim -o output.mp4

OUTPUT_PATH="$(find /tmp/manim -name output.mp4 | head -n 1)"
if [[ -z "$OUTPUT_PATH" ]]; then
  echo "output.mp4 not found"
  exit 1
fi

cp "$OUTPUT_PATH" /output/output.mp4
