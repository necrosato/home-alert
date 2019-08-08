#!/bin/bash

while getopts "hj:" opt; do
  case $opt in
    h )
      echo "Build and install opencv with python3 support."
      echo " -h : Display this help message."
      echo " -j : The number of make jobs for compilation. Default max. ('make -j' value)"
      exit 0
      ;;
    j )
      MAKE_J=$OPTARG
      ;;
  esac
done

# If bindings already available, no need to build
python3 -c "import cv2"
if [[ "$?" == "0" ]]; then
  exit 0
fi

# Dependencies
## Build
sudo apt-get -y install build-essential cmake pkg-config
## Python
sudo apt-get -y install python3-dev python3-numpy libpython3-dev
## Audio/Video
sudo apt-get -y install libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgstreamer-plugins-base1.0-dev
## Image formats
sudo apt-get -y install libjpeg-dev libpng-dev libtiff5-dev libjasper-dev
## Multithreading
sudo apt-get -y install libtbb2 libtbb-dev
## Numerical optimizations for OpenCV
sudo apt-get -y install libatlas-base-dev

# Get source
CVDIR=/tmp/opencv_source
CVTAR=/tmp/opencv_source.tar.gz
CV_CONTRIBDIR=/tmp/opencv_contrib
CV_CONTRIBTAR=/tmp/opencv_contrib.tar.gz
## Get latest version
VERSION="$(curl -s https://github.com/opencv/opencv/releases/latest | sed 's#.*tag/\(.*\)\".*#\1#')"
echo "latest version: ${VERSION}"
## Download
echo "downloading: https://github.com/opencv/opencv/archive/${VERSION}.tar.gz"
wget -O ${CVTAR} "https://github.com/opencv/opencv/archive/${VERSION}.tar.gz"
echo "downloading: https://github.com/opencv/opencv_contrib/archive/${VERSION}.tar.gz"
wget -O ${CV_CONTRIBTAR} "https://github.com/opencv/opencv_contrib/archive/${VERSION}.tar.gz"
## Unpack
mkdir -p ${CVDIR}
tar -xzvf ${CVTAR} --strip=1 -C ${CVDIR}
rm ${CVTAR}
mkdir -p ${CV_CONTRIBDIR}
tar -xzvf ${CV_CONTRIBTAR} --strip=1 -C ${CV_CONTRIBDIR}
rm ${CV_CONTRIBTAR}
cd ${CVDIR}
mkdir build
cd build


###############  CMAKE FLAGS  ###############################################
#
#		
#		/* Release Flags */
#		CMAKE_BUILD_TYPE=RELEASE
#		CMAKE_INSTALL_PREFIX=/usr/local
#		/* Increase Build Speed */
#		BUILD_DOCS=OFF
#		BUILD_PERF_TESTS=OFF
#		BUILD_TESTS=OFF
#		BUILD_EXAMPLES=OFF
#		BUILD_opencv_apps=OFF
#		BUILD_JAVA=OFF
#		/* Multi-threading */
#		WITH_TBB=ON
#		/* Video 4 Linux support */
#		WITH_V4L=ON
#		/* Extra Modules */
#		OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules
#		OPENCV_ENABLE_NONFREE=ON
#		BUILD_opencv_python3=ON
#		/* Arm Optimizations */
#		ENABLE_NEON=ON
#		ENABLE_VFPV3=ON
#
##############################################################################
# Configure build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_DOCS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF -D BUILD_EXAMPLES=OFF -D BUILD_opencv_apps=OFF -D BUILD_opencv_apps=OFF -D BUILD_JAVA=OFF -D WITH_TBB=ON -D WITH_V4L=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D OPENCV_ENABLE_NONFREE=ON -D BUILD_opencv_python3=ON -D ENABLE_NEON=ON -D ENABLE_VFPV3=ON ..

# Compile
if [[ "$MAKE_J" == "" ]]; then
  make
else
  make -j$MAKE_J
fi
sudo make install
sudo ldconfig
