#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#only kill the process, venusos will start automatically
kill $(pgrep -f "python $SCRIPT_DIR/virtualbattery.py")