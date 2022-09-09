#!/bin/sh

#source setmanagerenv.sh

SERVER=$SERVER_IP

function addSwitch {
  SWITCH_IP=$1
  IP=$2
  echo "addSwitch ${SWITCH_IP} ${IP}"

  URL="http://${SERVER}/addswitch"

  JSON_TEMPLATE='{ "switch_ip": "%s", "ip": "%s" }'

  JSON=""
  printf -v JSON "$JSON_TEMPLATE" "$SWITCH_IP" "$IP"
  echo $JSON

  curl -X POST -H "Content-Type: application/json" -d "$JSON" $URL
}

function setPort {
  IP=$1
  PORT=$2
  echo "setPort ${IP} ${PORT}"

  URL="http://${SERVER}/setport"

  JSON_TEMPLATE='{ "ip": "%s", "port": "%s" }'

  JSON=""
  printf -v JSON "$JSON_TEMPLATE" "$IP" "$PORT"
  echo $JSON

  curl -X POST -H "Content-Type: application/json" -d "$JSON" $URL
}

function setPiGroup {
  SWITCH_IP=$1
  LOCATION=$2
  echo "setPiGroup ${SWITCH_IP} ${LOCATION}"

  URL="http://${SERVER}/setpigroup"

  JSON_TEMPLATE='{ "location": "%s", "switch_ip": "%s" }'

  JSON=""
  printf -v JSON "$JSON_TEMPLATE" "$LOCATION" "$SWITCH_IP"
  echo $JSON

  curl -X POST -H "Content-Type: application/json" -d "$JSON" $URL
}

function register {
  echo "Server: ${SERVER}"
  LOCATION=$1
  SWITCH_IP=$2
  IP=$3
  PORT=$4

  #echo $LOCATION
  #echo $SWITCH_IP
  #echo $IP
  #echo $PORT

  addSwitch $SWITCH_IP $IP
  setPort $IP $PORT
  setPiGroup $SWITCH_IP $LOCATION
}


# TODO
# To fill out this script

# Front

BANK1_1="172.20.175.45"
register "front" $BANK1_1 "192.168.1.221" "1"


BANK1_2="172.20.71.208"
BANK1_3="172.20.180.193"
BANK1_4="172.20.1.49"
BANK1_5="172.20.1.48"
BANK1_6="172.20.1.47"
BANK1_7="172.20.1.50"

BANK2_1="172.20.71.199"
BANK2_2="172.20.9.24"
BANK2_3="172.20.80.211"
BANK2_4="172.20.181.81"
BANK2_5="172.20.10.14"
BANK2_6="172.20.9.216"

# Back

BANK3_1="172.20.74.148"
register "back" $BANK3_1 "192.168.1.221" "1"

BANK3_2="172.20.15.120"
BANK3_3="172.20.72.234"
BANK3_4="172.20.186.97"
BANK3_5="172.20.177.169"
BANK3_6="172.20.178.159"

BANK4_1="172.20.177.76"
BANK4_2="172.20.9.213"
BANK4_3="172.20.8.229"
BANK4_4="172.20.44.205"
BANK4_5="172.20.215.140"
BANK4_6="172.20.44.21"
