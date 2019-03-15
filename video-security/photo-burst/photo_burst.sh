#!/bin/bash

set -e

while getopts "h" opt; do
  case $opt in
    h )
      echo "Capture a burst of photos to a directory."
      echo "-h : Dislpay this help message."
      exit 1
      ;;
  esac
done

DIR=$(TZ="America/Los_Angeles" date)
mkdir "$DIR"

INPUT=/dev/video0
FPS="1/2"
NUM_FRAMES=10
DIMS="1280x720"

ffmpeg -video_size $DIMS -i $INPUT -vf fps=$FPS -vframes $NUM_FRAMES /tmp/out%02d.jpg
