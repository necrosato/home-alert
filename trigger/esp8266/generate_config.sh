#!/bin/bash

set -e

while getopts "hw:a:c:l:i:" arg; do
  case $arg in
    h )
      echo "Use this script to generate a config.h file"
      echo "to compile the esp8266 trigger arduino sketch."
      echo "-h : Desplay this help message."
      echo "-w : Local wifi network ssid."
      echo "-a : Local wifi network authentication password."
      echo "-c : Control server address."
      echo "-l : Main server location."
      echo "-i : Input pin to use on microcontroller."
      ;;
    w )
      SSID=$(echo -n "$OPTARG" | sed 's/\$/\\\$/g')
      ;;
    a )
      PASSWORD=$(echo -n "$OPTARG" | sed 's/\$/\\\$/g')
      ;;
    c )
      SERVER_ADDRESS=$(echo -n "$OPTARG" | sed 's/\$/\\\$/g')
      ;;
    l )
      LOCATION=$(echo -n "$OPTARG" | sed 's/\$/\\\$/g')
      ;;
    i )
      INPUT_PIN=$(echo -n "$OPTARG" | sed 's/\$/\\\$/g')
      ;;
  esac
done

if [[ "$SSID" == "" ]]; then
  echo "Must pass option -w."
  exit 1
fi
if [[ "$PASSWORD" == "" ]]; then
  echo "Must pass option -a."
  exit 1
fi
if [[ "$SERVER_ADDRESS" == "" ]]; then
  echo "Must pass option -c."
  exit 1
fi
if [[ "$LOCATION" == "" ]]; then
  echo "Must pass option -l."
  exit 1
fi
if [[ "$INPUT_PIN" == "" ]]; then
  echo "Must pass option -i."
  exit 1
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG_TEMPLATE=$DIR/trigger/config_template.h
CONFIG=$DIR/trigger/config.h
cp $CONFIG_TEMPLATE $CONFIG
perl -pi -e "s/_template//ig" $CONFIG
perl -pi -e "s/SSID/$SSID/g" $CONFIG
perl -pi -e "s/PASSWORD/$PASSWORD/g" $CONFIG
perl -pi -e "s/SERVER_ADDRESS/$SERVER_ADDRESS/g" $CONFIG
perl -pi -e "s/LOCATION/$LOCATION/g" $CONFIG
perl -pi -e "s/PIN/$INPUT_PIN/g" $CONFIG
