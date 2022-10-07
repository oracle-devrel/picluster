#!/bin/sh


#source setmanagerenv.sh

docker build . -t manager --build-arg WARBLE_SERVER_ARG="${WARBLE_SERVER}" --build-arg WARBLE_OUTGOING_SERVER_ARG="${WARBLE_OUTGOING_SERVER}" -f Dockerfile
