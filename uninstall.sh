#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

rm /service/$SERVICE_NAME
kill $(pgrep -f 'supervise dbus-virtual-battery')
chmod a-x $SCRIPT_DIR/service/run

sed -i '/dbus-virtual-battery/d' /data/rc.local

./"$SCRIPT_DIR/restart.sh"