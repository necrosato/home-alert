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

# Increase swap size
sudo sed -i "/^CONF_SWAPSIZE=/c\CONF_SWAPSIZE=2048" /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

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

# Configure build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_opencv_python3=On -D INSTALL_PYTHON_EXAMPLES=OFF -D BUILD_EXAMPLES=OFF -D BUILD_DOCS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_TESTS=OFF ..

# Compile
if [[ "$MAKE_J" == "" ]]; then
  make
else
  make -j$MAKE_J
fi
sudo make install
sudo ldconfig

# Reset swap size
sudo sed -i "/^CONF_SWAPSIZE=/c\CONF_SWAPSIZE=100" /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
