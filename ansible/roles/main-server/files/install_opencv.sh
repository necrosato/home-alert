#!/bin/bash

while getopts "ht:" opt; do
  case $opt in
    h )
      echo "Build and install opencv with python3 support."
      echo " -h : Display this help message."
      echo " -j : The number of make jobs for compilation. Default max. ('make -j' value)"
      ;;
    t )
      MAKE_J=$OPTARG
      ;;
  esac
done

# if bindings already available, no need to build
python3 -c "import cv2"
if [[ "$?" == "0" ]]; then
  exit 0
fi

# For compilation
sudo apt-get install build-essential
# Required
sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
# Required for python3 cv2 module
sudo apt-get install python3-dev python3-numpy libjpeg-dev

CVDIR=/tmp/opencv_source
git clone https://github.com/opencv/opencv $CVDIR
cd $CVDIR
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_opencv_python3=On ..
if [[ "$MAKE_J" == "" ]]; then
  make
else
  make -j$MAKE_J
fi
sudo make install
