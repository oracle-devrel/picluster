#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import requests
import os
import socket
from datetime import datetime
from threading import RLock

# This script will shut down one pi at a time so we can get the port it is attached to

# 1. Boot up all 42 Pi
# 2. Run this script to get all the IP addresses
# > bash 1piatatime.sh
# 3. The script will shut down one Pi at a time, printing out the IP address of the Pi that was shutdown
# 4. Look at the switch and note the port that is no longer active
# 5. The script will repeat steps 3-4 until there are no more Pi

def getEnvironmentVariable(name):
    if name in os.environ:
        return os.getenv(name)
    else:
        print("Error: environment variable {name} does not exist.".format(name = name))
        quit()

SERVER_IP = getEnvironmentVariable('SERVER_IP')
SLEEP = 4

def getAllPi():
    try:
        data = {}
        headers = {'Content-type': 'application/json'}
        response = requests.post('http://' + SERVER_IP + '/getpi', data = json.dumps(data), headers = headers)
        message = response.json()

        if message["status"] == 'true':

            if 'items' in message:
                return message['items']

    except socket.error:
        print("error")

    return []

def sendShutdown(ip):
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.get('http://' + ip + ':8880/shutdown', headers = headers)
        message = response.json()
        if message["status"] == 'true':
            print("{} shutdown success".format(ip))
    except socket.error:
        print("error")


pi_list = getAllPi()

# Check that all pi are good
for ip in pi_list:
    pi = pi_list[ip]
    if 'ip' not in pi:
        print("This pi is bad {}".format(ip))
        quit()

# For each good pi send a shutdown one at a time
for ip in pi_list:
    sendShutdown(ip)
    time.sleep(SLEEP)
    while True:
        time.sleep(SLEEP)
        current_list = getAllPi()
        pi = current_list[ip]
        if 'ip' not in pi:
            print("register \"front\" $BANK1_1 \"{}\" \"PORT\"".format(ip))
            input("Press Enter to continue...")
            break
