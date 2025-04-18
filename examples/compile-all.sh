#!/bin/bash

BOARD_TYPE="arduino:avr:uno"

BUILD_DIR=$(mktemp -d)
echo "Using temporary build directory: $BUILD_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for SKETCH in "$SCRIPT_DIR"/custom/*/; do
  SKETCH_NAME=$(basename "$SKETCH")

  if [[ -f "${SKETCH}library.txt" ]]; then
    while IFS= read -r LIBRARY || [[ -n "$LIBRARY" ]]; do
      if [[ -n "$LIBRARY" ]]; then
        arduino-cli lib install "$LIBRARY"
      fi
    done < "${SKETCH}library.txt"
  fi

  arduino-cli compile --fqbn "$BOARD_TYPE" "${SKETCH}" --output-dir "$BUILD_DIR/$SKETCH_NAME"
done

