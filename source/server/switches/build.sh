#!/bin/sh

docker build -t switches --build-arg SWITCH_USER_ARG="${SWITCH_USER}" \
                         --build-arg SWITCH_PASS_ARG="${SWITCH_PASS}" \
                         --build-arg SWITCHES_BANK1_TOP_ARG="${SWITCHES_BANK1_TOP}" \
                         --build-arg SWITCHES_BANK1_BOTTOM_ARG="${SWITCHES_BANK1_BOTTOM}" \
                         --build-arg SWITCHES_BANK2_TOP_ARG="${SWITCHES_BANK2_TOP}" \
                         --build-arg SWITCHES_BANK2_BOTTOM_ARG="${SWITCHES_BANK2_BOTTOM}" \
                         --build-arg SWITCHES_BANK3_TOP_ARG="${SWITCHES_BANK3_TOP}" \
                         --build-arg SWITCHES_BANK3_BOTTOM_ARG="${SWITCHES_BANK3_BOTTOM}" \
                         --build-arg SWITCHES_BANK4_TOP_ARG="${SWITCHES_BANK4_TOP}" \
                         --build-arg SWITCHES_BANK4_BOTTOM_ARG="${SWITCHES_BANK4_BOTTOM}" \
                         --build-arg SWITCHES_BACK_ARG="${SWITCHES_BACK}" \
                         --build-arg SWITCHES_FRONT_ARG="${SWITCHES_FRONT}" \
                         --build-arg SWITCHES_ARG="${SWITCHES}" \
                         --build-arg SWITCHES_APP_ARG="${SWITCHES_APP}" \
                         -f Dockerfile .
