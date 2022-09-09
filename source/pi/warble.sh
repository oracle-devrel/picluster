#!/bin/sh

USERNAME=$1
CODE=$2
URL=$3

pushd ../warble

OUTPUT=$(python3 warblecc.py ${CODE})
PROGRAM="out.py"
OUTPUT=$(python3 $PROGRAM)

if test -f $PROGRAM; then
  JSON_TEMPLATE='{ "username": "%s", "code": "%s", "output": "%s" }'

  JSON=""
  printf -v JSON "$JSON_TEMPLATE" "$USERNAME" "$CODE" "$OUTPUT"
  #echo $JSON

  rm $PROGRAM

  if [ -n "$var" ]
  then
    curl -X POST -H "Content-Type: application/json" -d "$JSON" $URL
  fi

popd
