#!/bin/bash

BOARD_TYPE="${BOARD_TYPE:-arduino:avr:uno}"
ENABLE_UNSAFE_INSTALL="${ENABLE_UNSAFE_INSTALL:-true}"

build_dir=$(mktemp -d)
echo "Using temporary build directory: $build_dir"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for sketch_dir in "$script_dir"/custom/*/; do
  sketch_name=$(basename "$sketch_dir")
  echo "Compiling: $sketch_name"

  libraries_file="$sketch_dir/libraries.txt"
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
                  cd "$SKETCH" || { echo "Cannot cd to $sketch_dir" >&2; exit 1; }
                  arduino-cli lib install --zip-path "$line" || echo "Error installing ZIP library: $line" >&2
              )
          else
              arduino-cli lib install "$line" || echo "Error installing library: $line" >&2
      fi

      done < "$libraries_file"
  fi


  arduino-cli compile --fqbn "$BOARD_TYPE" "${sketch_dir}" --output-dir "$build_dir/$sketch_name"
done

