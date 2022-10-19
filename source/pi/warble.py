#!/usr/bin/python3

import argparse
import sys
import requests
import os
import socket
import json

# Run: python3 warblec.py -v "{PRINT(\"test\")}"

def main():
    argparser = argparse.ArgumentParser(description='Pre Warble')
    argparser.add_argument('code', type=str, help='code')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-u', '--username', required=False, help='username')
    #argparser.add_argument('-t', '--tweet', required=False, help='tweet')
    #argparser.add_argument('-r', '--url', required=False, help='url')
    argparser.add_argument('-m', '--mode', required=False, help='mode')
    args = argparser.parse_args()
    input = args.code
    username = args.username
    mode = args.mode
    #url = args.url
    #tweet = args.tweet
    # Hard coding URL because passed in as an argument it doesn't work for some reason.
    url = "https://g2f4dc3e5463897-ardata.adb.uk-london-1.oraclecloudapps.com/ords/picluster/AR/warble/"
    gv_url = "http://127.0.0.1:8080"

    if args.verbose:
        utils.verbose = True

    linput = input.replace("\"", "\\\"")

    if mode == "graalvisor" or mode == "gv":
        data = { "name": "warble", "async": "false", "arguments": '["--username", "{}", "{}"]'.format(username, linput) }
        headers = {'Content-type': 'application/json'}
        r = requests.post(gv_url, data=json.dumps(data), headers=headers)
        result = json.loads(r.text)["result"].replace("'", "\"")
        output = json.loads(result)["result"]
    else:
        stream = os.popen('python3 ../warble/warblecc.py --username {} \"{}\"'.format(username, linput))
        output = stream.read()

    try:
        data = { "username": username, "code": input, "output": output }
        print(data)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

    except socket.error:
        print("error")


if __name__ == "__main__":
    main()
