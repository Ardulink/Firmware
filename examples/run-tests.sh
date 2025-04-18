#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export SKETCH_FILE=$SCRIPT_DIR/custom/JoystickCustomMessages/
behave $SKETCH_FILE/tests/

