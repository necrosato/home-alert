#!/bin/bash

grep "bcm2835-v4l2" /etc/modules || echo "bcm2835-v4l2" >> /etc/modules
