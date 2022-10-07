#!/usr/bin/python3

import argparse
import sys
import requests
import os
import socket

# Run: python3 warblec.py -v "{PRINT(\"test\")}"

def main():
    argparser = argparse.ArgumentParser(description='Pre Warble')
    argparser.add_argument('code', type=str, help='code')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-u', '--username', required=False, help='username')
    #argparser.add_argument('-t', '--tweet', required=False, help='tweet')
    argparser.add_argument('-r', '--url', required=False, help='url')
    args = argparser.parse_args()
    input = args.code
    username = args.username
    url = args.url
    #tweet = args.tweet

    if args.verbose:
        utils.verbose = True

    input = input.replace("\"", "\\\"")

    stream = os.popen('python3 ../warble/warblecc.py --username {} \"{}\"'.format(username, input))
    output = stream.read()

    try:
        #data = { "tweet": tweet, "code": input, "output": output }
        data = { "code": input, "output": output }
        print(data)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

    except socket.error:
        print("error")


if __name__ == "__main__":
    main()
