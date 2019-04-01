#!/bin/bash


PIP=$(which pip3)
set -e
if [[ "$PIP" != "/usr/local/bin/pip3" ]]; then
  sudo apt-get remove --purge python3-pip
  wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
  sudo python3 /tmp/get-pip.py
fi
