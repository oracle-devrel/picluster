#!/bin/sh

day=$(date +%d)
day=$((day-1))
from=$(date +%Y-%m--)
echo ${from}${day}


#python3 twitter.py BiGPiClusterInMyGarage ${from}${day}
python3 twitter.py pi ${from}${day}
