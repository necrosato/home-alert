#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
aws s3 cp s3://com.necrosato.home-alert.secrets/ $DIR/../secrets/ --recursive
