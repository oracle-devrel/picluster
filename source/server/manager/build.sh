#!/bin/sh


#source setmanagerenv.sh

docker build -t manager --build-arg WARBLE_SERVER_ARG="${WARBLE_SERVER}" -f Dockerfile .
