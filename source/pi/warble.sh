#!/bin/sh

USERNAME=$1
CODE=$2
URL=$3
TWEET=$4
MODE=$5
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
  curl -s -X POST $GRAALVISOR_IP:$GRAALVISOR_PORT/register?name=warble\&entryPoint=main\&language=python -H 'Content-Type: application/json' --data-binary @$WARBLE_HOME/graalvisor-entrypoint.py
}

pushd ../warble

if [ "$MODE" == "gv" ]
then
  check_environment
  GRAALVISOR_IP=127.0.0.1
  GRAALVISOR_PORT=8080

  # Checking if the default port of Graalvisor is in use.
  if [ -z "$(sudo lsof -i -P -n | grep LISTEN | grep $GRAALVISOR_PORT)" ]
  then
    # Graalvisor is down, we have to launch it and register the function.
    start_graalvisor &> /tmp/graalvisor.log &
    sleep 1
    register_function
  fi

  # Prepare code for Graalvisor - escape double quotes correctly.
  CODE=$(echo "$CODE" | sed 's/"/\\\\"/g')
  CODE=$(echo "$CODE" | sed 's/"/\\"/g')
  curl -s -X POST $GRAALVISOR_IP:$GRAALVISOR_PORT -H 'Content-Type: application/json' -d $'{"name":"warble","async":"false","arguments":"[\'-v\',\'--username\',\'\\"'$USERNAME$'\\"\',\''$CODE$'\']"}'
elif [ -z "$MODE" ] || [ "$MODE" == "python" ]
then
  python3 warblecc.py --username ${USERNAME} ${CODE}
else
  echo "Only 'python' (default) and 'gv' modes are supported."
  exit 1
fi

PROGRAM="out.py"
OUTPUT=$(python3 $PROGRAM)

if test -f $PROGRAM; then
  JSON_TEMPLATE='{ "tweet": "%s", "code": "%s", "output": "%s" }'

  JSON=""
  printf -v JSON "$JSON_TEMPLATE" "$TWEET" "$CODE" "$OUTPUT"
  #echo $JSON

  rm $PROGRAM

  if [ -n "$var" ]
  then
    curl -X POST -H "Content-Type: application/json" -d "$JSON" $URL
  fi

popd
