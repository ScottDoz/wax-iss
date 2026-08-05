#!/bin/bash

for dev in /dev/ttyUSB*; do
    echo "==== $dev ===="
    udevadm info -q property -n $dev | grep SERIAL
done

ls -l /dev/serial/by-id/


# Keep terminal open
exec bash
