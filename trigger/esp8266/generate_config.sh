#!/bin/bash

while getopts "h" arg; do
  case $arg in
    h )
      echo "Use this script to generate a config.h file"
      echo "to compile the esp8266 trigger arduino sketch."
      echo "-h : Desplay this help message."
      ;;
  esac
done

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG_TEMPLATE=$DIR/trigger/config_template.h
CONFIG=$DIR/trigger/config.h
cp $CONFIG_TEMPLATE $CONFIG
perl -pi -e 's/_template//ig' $CONFIG
# TODO: Fill out rest of config
