#!/bin/bash

set -e

N_KEEP="30"
while getopts "hn:d:" opt; do
  case $opt in
    h )
      echo "Keep n directories and delete the rest."
      echo "This keeps the last directories sorted alpha-numerically."
      echo "When directories are named according to date, ex 2019-04-20,"
      echo "then the most recent directories are kept."
      echo " -n : the n directories to keep. Default 30."
      echo " -d : the parent directory to clean."
      ;;
    n )
      N_KEEP="$OPTARG"
      ;;
    d )
      CLEAN_DIR="$OPTARG"
      ;;
  esac
done

if [[ "$CLEAN_DIR" == "" ]]; then
  echo "Must give a directory to clean."
  exit 1
fi

# First tail is to skip the parent dir
# sort to reverse order, then remove first n
# replace newlines with null bytes to account for directores with spaces in the name,
# remove all results.
find "$CLEAN_DIR" -maxdepth 1 | tail -n +2 | sort -r | tail -n +$(($N_KEEP+1)) | tr '\n' '\0' | xargs -0 -- rm -rf
