#!/bin/bash

BOARD_TYPE="${BOARD_TYPE:-arduino:avr:uno}"
ENABLE_UNSAFE_LIB_INSTALL="${ENABLE_UNSAFE_LIB_INSTALL:-true}"

BUILD_DIR=$(mktemp -d)
echo "Using temporary build directory: $BUILD_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for SKETCH in "$SCRIPT_DIR"/custom/*/; do
  SKETCH_NAME=$(basename "$SKETCH")
  echo "Compiling: $SKETCH_NAME"

  libraries_file="$SKETCH/libraries.txt"
  if [[ -f "$libraries_file" ]]; then
      while IFS= read -r line; do
          line="$(echo "$line" | xargs)"
          [[ -z "$line" || "$line" == \#* ]] && continue

          if [[ "$line" == *"://"* ]] || [[ "$line" == git@* ]]; then
              [[ -n "${ENABLE_UNSAFE_INSTALL:-}" ]] && arduino-cli config set library.enable_unsafe_install "${ENABLE_UNSAFE_INSTALL}"
              arduino-cli lib install --git-url "$line" || echo "Error installing Git library: $line" >&2
          elif [[ "$line" == */* ]] || [[ "$line" == *.zip ]]; then
              [[ -n "${ENABLE_UNSAFE_INSTALL:-}" ]] && arduino-cli config set library.enable_unsafe_install "${ENABLE_UNSAFE_INSTALL}"
              (
                  cd "$SKETCH" || { echo "Cannot cd to $SKETCH" >&2; exit 1; }
                  arduino-cli lib install --zip-path "$line" || echo "Error installing ZIP library: $line" >&2
              )
          else
              arduino-cli lib install "$line" || echo "Error installing library: $line" >&2
      fi

      done < "$libraries_file"
  fi


  arduino-cli compile --fqbn "$BOARD_TYPE" "${SKETCH}" --output-dir "$BUILD_DIR/$SKETCH_NAME"
done

