#!/bin/sh

function check_environment {
  if [ -z "$JAVA_HOME" ] || [ -z "$WARBLE_HOME" ] || [ -z "$GRAALVISOR_PATH" ] || [ -z "$WARBLE_ENTRY_POINT" ]
  then
    echo "Please check your environment variables."
    exit 1
  fi
}

function register_function {
  curl -s -X POST $GRAALVISOR_IP:8080/register?name=warble\&entryPoint=main\&language=python -H 'Content-Type: application/json' --data-binary @$WARBLE_ENTRY_POINT
}

function start_svm {
  $GRAALVISOR_PATH &
  wait
}

function start_polyglot_svm {
  export lambda_timestamp="$(date +%s%N | cut -b1-13)"
  export lambda_port="8080"
  start_svm
}
