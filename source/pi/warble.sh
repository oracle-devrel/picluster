#!/bin/sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

function check_environment {
  export WARBLE_HOME=$DIR/../warble
  if [ -z "$JAVA_HOME" ] || [ -z "$GRAALVISOR_PATH" ]
  then
    echo "Please check your environment variables."
    exit 1
  fi
}

function start_graalvisor {
  export lambda_timestamp="$(date +%s%N | cut -b1-13)"
  export lambda_port="$GRAALVISOR_PORT"
  $GRAALVISOR_PATH
}

function register_function {
  curl -s -X POST $GRAALVISOR_IP:$GRAALVISOR_PORT/register?name=warble\&entryPoint=main\&language=python -H 'Content-Type: application/json' --data-binary @$WARBLE_HOME/gv-warble-entrypoint.py
}

if [[ "$*" == *"-m graalvisor"* ]] || [[ "$*" == *"-m=graalvisor"* ]]
then
  # Prepare Graalvisor.
  check_environment
  GRAALVISOR_IP=127.0.0.1
  GRAALVISOR_PORT=8080
  # Checking if the default port of Graalvisor is in use.
  if [ -z "$(lsof -i -P -n | grep LISTEN | grep $GRAALVISOR_PORT)" ]
  then
    # Graalvisor is down, we have to launch it and register the function.
    start_graalvisor &
    sleep 5
    register_function
  fi
fi

python3 $DIR/warble.py "$@"
