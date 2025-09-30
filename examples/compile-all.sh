#!/bin/bash

BOARD_TYPE="arduino:avr:uno"
ENABLE_UNSAFE_LIB_INSTALL=true

BUILD_DIR=$(mktemp -d)
echo "Using temporary build directory: $BUILD_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for SKETCH in "$SCRIPT_DIR"/custom/*/; do
  SKETCH_NAME=$(basename "$SKETCH")

  if [[ -f "${SKETCH}libraries.txt" ]]; then
    while IFS= read -r LIBRARY || [[ -n "$LIBRARY" ]]; do
      LIBRARY=$(echo "$LIBRARY" | xargs) # trim whitespace
      if [[ -z "$LIBRARY" ]]; then
        continue
      fi

      if [[ "$ENABLE_UNSAFE_LIB_INSTALL" == "true" ]]; then
        if [[ "$LIBRARY" == http*://*.git ]]; then
          # Git URL
          arduino-cli config set library.enable_unsafe_install true
          arduino-cli lib install --git-url "$LIBRARY"
        else
          # normal library name
          arduino-cli lib install "$LIBRARY"
        fi
      else
        # normal library name
        arduino-cli lib install "$LIBRARY"
      fi

    done < "${SKETCH}libraries.txt"
  fi

  arduino-cli compile --fqbn "$BOARD_TYPE" "${SKETCH}" --output-dir "$BUILD_DIR/$SKETCH_NAME"
done

