#!/bin/bash


PIP=$(which pip3)
set -e
if [[ "$PIP" == "" ]]; then
  wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
  python3 /tmp/get-pip.py
fi
