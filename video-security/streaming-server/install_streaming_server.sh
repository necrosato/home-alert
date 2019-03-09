#!/bin/bash

CDIR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
sudo apt-get install libmoose-perl liburi-perl libmoosex-getopt-perl libsocket6-perl libanyevent-perl ffmpeg
cd $DIR/rtsp-server
perl Makefile.PL
make
make test
sudo make install
cd $CDIR
