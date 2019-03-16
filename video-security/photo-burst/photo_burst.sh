#!/bin/bash

set -e

INPUT=""
PREFIX=""
FPS=""
NUM_FRAMES=""
WIDTH=""
HEIGHT=""
while getopts "hi:d:r:n:w:h:" opt; do
  case $opt in
    h )
      echo "Capture a burst of photos to a directory."
      echo "-h : Dislpay this help message."
      echo "-i : Input video device."
      echo "-d : Prefix directory to save images."
      echo "-r : Rate of frames, in frames/sec. For example, 30/1 for 30 fps."
      echo "-n : Number of photos to save."
      echo "-w : Width of photos in pixels."
      echo "-h : Height of photos in pixels."
      exit 1
      ;;
    i )
      INPUT=$OPTARG
      ;;
    d )
      PREFIX=$OPTARG
      ;;
    r )
      FPS=$OPTARG
      ;;
    n )
      NUM_FRAMES=$OPTARG
      ;;
    w )
      WIDTH=$OPTARG
      ;;
    h )
      HEIGHT=$OPTARG
      ;;
  esac
done

if [[ "$INPUT" == "" ]]; then
  echo "Must give video capture device with -i"
  exit 1
elif [[ ! -e "$INPUT" ]]; then
  echo "$INPUT is not a valid device"
  exit 1
fi

if [[ "$PREFIX" == "" ]]; then
  echo "Must give prefix directory with -d"
  exit 1
fi

if [[ "$FPS" == "" ]]; then
  echo "Must give frame rate with -r"
  exit 1
fi

if [[ "$NUM_FRAMES" == "" ]]; then
  echo "Must give number of photos with -n"
  exit 1
fi

DIR=$(TZ="America/Los_Angeles" date)
mkdir "$DIR"

DIMS="${WIDTH}x${HEIGHT}"

ffmpeg -video_size $DIMS -i $INPUT -vf fps=$FPS -vframes $NUM_FRAMES "$DIR/photo_%02d.jpg"
