#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export SKETCH_FILE=$SCRIPT_DIR/custom/EchoCustomMessages/
behave $SKETCH_FILE/tests/

export SKETCH_FILE=$SCRIPT_DIR/custom/JoystickCustomMessages/
behave $SKETCH_FILE/tests/

export SKETCH_FILE=$SCRIPT_DIR/custom/CustomPinIntensity/
behave $SKETCH_FILE/tests/

# export SKETCH_FILE=$SCRIPT_DIR/custom/ButtonQuest-ChipKIT/
# ADDITIONAL_URLS="https://github.com/chipKIT32/chipKIT-core/raw/master/package_chipkit_index.json" \
# INSTALL_CORES="chipKIT:pic32" \
# BUILD_FQBN="pic32:chipKIT:uno32" \
# behave $SKETCH_FILE/tests/

# TODO we can't play quest on attiny since it's missing serial
#export SKETCH_FILE=$SCRIPT_DIR/custom/ButtonQuest/
#ADDITIONAL_URLS="http://drazzy.com/package_drazzy.com_index.json" \
#INSTALL_CORES="ATTinyCore:avr" \
#BUILD_FQBN="ATTinyCore:avr:attinyx5:chip=85,clock=8internal" \
#behave $SKETCH_FILE/tests/

export SKETCH_FILE=$SCRIPT_DIR/custom/ButtonQuest/
BUILD_EXTRA_FLAGS="-DOLED_DISABLED=true" behave $SKETCH_FILE/tests/

