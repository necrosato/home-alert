#!/bin/bash
#
# Run this script to install the rtsp streaming server

set -e

while getopts "hd:" arg; do
  case $arg in
    h )
      echo "-h      : Print this help message."
      echo "-d DIR  : Give the directory to clone and make the streaming server"
      ;;
    d )
      CLONE_DIR=$OPTARG
      ;;
  esac
done

if [[ "$CLONE_DIR" == "" ]]; then
  echo "Must pass a directory with -d."
  exit 1
fi

CDIR=$(pwd)
sudo apt-get install git libmoose-perl liburi-perl libmoosex-getopt-perl libsocket6-perl libanyevent-perl ffmpeg
git clone https://github.com/revmischa/rtsp-server $CLONE_DIR
cd $CLONE_DIR
perl Makefile.PL
make
make test
sudo make install
cd $CDIR
