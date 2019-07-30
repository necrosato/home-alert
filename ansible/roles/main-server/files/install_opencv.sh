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

# if bindings already available, no need to build
python3 -c "import cv2"
if [[ "$?" == "0" ]]; then
  exit 0
fi

# For compilation
sudo apt-get -y install build-essential
# Required
sudo apt-get -y install cmake git libgtk-3-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev
# Required for python3 cv2 module
sudo apt-get -y install python3-dev python3-numpy libjpeg-dev
# Numerical optimizations fro OpenCV
sudo apt-get -y install libatlas-base-dev gfortran

# Increase swap size
sudo sed -i "/^CONF_SWAPSIZE=/c\CONF_SWAPSIZE=2048" /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

# Get source
VERSION="$(curl -s https://github.com/opencv/opencv/releases/latest | sed 's#.*tag/\(.*\)\".*#\1#')"
echo "latest version: ${VERSION}"
echo "downloading: https://github.com/opencv/opencv/archive/${VERSION}.tar.gz"

CVDIR=/tmp/opencv_source
CVTAR=/tmp/opencv_source.tar.gz
wget -O ${CVTAR} "https://github.com/opencv/opencv/archive/${VERSION}.tar.gz"
mkdir -p ${CVDIR}
tar -xzvf ${CVTAR} --strip=1 -C ${CVDIR}
rm ${CVTAR}
cd ${CVDIR}
mkdir build
cd build
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
