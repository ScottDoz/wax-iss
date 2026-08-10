#!/bin/bash

uname -r
echo ">>lsmod | grep unicam"
lsmod | grep unicam
echo ""

echo ">> ls -l /dev/media*"
ls -l /dev/media*
echo ""


echo ">>dmesg | grep -Ei camera|csi|unicam"
dmesg | grep -Ei "camera|csi|unicam"
echo ""

#echo ">>libcamera-hello --qt-preview"
#libcamera-hello --qt-preview

echo ">>rpicam-vid"
rpicam-vid

# Keep terminal open
exec bash
