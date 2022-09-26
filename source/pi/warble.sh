#!/bin/sh

USERNAME=$1
CODE=$2
URL=$3
TWEET=$4

pushd ../warble

GRAALVISOR_IP=127.0.0.1
# Checking if the default port of GraalVisor is in use.
GRAALVISOR_UP=$(sudo lsof -i -P -n | grep LISTEN | grep 8080)
if [ -z "$GRAALVISOR_UP" ]
then
  # GraalVisor is down, we have to launch it and register the function.
  source ../pi/graalvisor_functions.sh
  check_environment
  start_polyglot_svm &> "$GRAALVISOR_PATH".log &
  sleep 1
  register_function
fi

# Prepare code for GraalVisor - escape double quotes correctly.
CODE=$(echo "$CODE" | sed 's/"/\\\\"/g')
CODE=$(echo "$CODE" | sed 's/"/\\"/g')

curl -s -X POST $GRAALVISOR_IP:8080 -H 'Content-Type: application/json' -d $'{"name":"warble","async":"false","arguments":"[\'-v\',\'--username\',\'\\"'$USERNAME$'\\"\',\''$CODE$'\']"}'
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
