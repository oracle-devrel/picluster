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
import pandas as pd
from pathlib import Path
import pandas as pd
from datetime import datetime


# pip install requests

hostName = "0.0.0.0"
serverPort = 80

tag = "#pi"
DEBUG = False

def getNextNum(path):
    #path = '.'
    files = os.listdir(path)

    csv_files = [i for i in files if i.endswith('.csv')]
    old_files = [i for i in files if i.endswith('.old')]

    return len(csv_files) + len(old_files)

class GetWarblesThread:
    def __init__(self):
        self._running = True
        self._count = 10

    def terminate(self):
        self._running = False

    def run(self):
        while True:
            if not self._running:
                break

            print("read warbles")
            #os.system('bash getwarbles.sh')
            os.system('source ../../../settwit.sh && bash getwarbles.sh')

            #time.sleep(60 * 10) # delay for 10 minutes
            time.sleep(10)


#WarblesThread = GetWarblesThread()
WarblesThread = None
t = None


def fileExistsWithExtension(path, ext):
    result = False
    files = os.listdir(path)
    csv_files = [i for i in files if i.endswith('.csv')]

    if len(csv_files) > 0:
        result = True

    return result


def getTweetBatch():
    result = []
    path = './warble_data'

    if fileExistsWithExtension(path, 'csv'):

        lfilename = ""
        i = 0

        while True:
            lfilename = path + '/scraped_tweets{}.csv'.format(i)

            if os.path.exists(lfilename):
                break
            i += 1

        print(lfilename)

        df = pd.read_csv(lfilename)

        for index, row in df.iterrows():

            text = row['text']
            code = text.replace(tag, "").strip()

            if code[0] == '{' and code[-1] == '}':
                print("we have code")

                username = row['username']
                description = row['description']
                location = row['location']
                following = row['following']
                followers = row['followers']
                totaltweets = row['totaltweets']
                retweetcount = row['retweetcount']
                text = row['text']
                hashtags = row['hashtags']
                created_at = row['created_at']

                item = {'code':code, 'tweet':{'username':username, 'description':description, 'location':location, 'following':following, 'followers':followers, 'totaltweets':totaltweets, 'retweetcount':retweetcount, 'text':text, 'hashtags':hashtags, 'created_at':created_at}}

                result.append(item)

        if not DEBUG:
            if os.path.exists(lfilename):
                p = Path(lfilename)
                print("renaming " + lfilename)
                p.rename(p.with_suffix('.old'))

    return result


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = 0
        body = {}

        # curl http://<ServerIP>/index.html
        if self.path == "/":
            print('running server...')

            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            content = open('index.html', 'rb').read()
            self.wfile.write(content)

        elif self.path.upper() == "/debug".upper():
            global DEBUG
            DEBUG = not DEBUG
            body = {'status': 'true'}

        # Start
        # curl http://<ServerIP>/start
        elif self.path.upper() == "/start".upper():
            response = 200
            body = {'status': 'true'}
            global t
            global WarblesThread
            WarblesThread = GetWarblesThread()
            t = threading.Thread(target = WarblesThread.run)
            t.start()
            print(body)

        # Stop
        # curl http://<ServerIP>/stop
        elif self.path.upper() == "/stop".upper():
            response = 200
            body = {'status': 'true'}
            WarblesThread.terminate()
            print(body)

        # Next Batch
        # curl http://<ServerIP>/nextbatch
        elif self.path.upper() == "/nextbatch".upper():
            response = 200
            #body = {'status': 'true', 'items': ['code': '\"{r=ROUND(ACOS(0.0),3);r=r*2;PRINT(r)}\""', 'tweet': {'username': 'joe', 'description':'TODO', 'location':'TODO', 'following':'TODO', 'followers':'TODO', 'totaltweets':'TODO', 'retweetcount':'TODO', 'text':'TODO', 'hashtags':'TODO', 'created_at':'TODO'}]}
            body = {'status': 'true', 'items': getTweetBatch()}
            print(body)

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))

    def do_POST(self):
        # refuse to receive non-json content
        if self.headers.get('content-type') != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        response = 0
        body = {}

        if self.path.upper() == "/code".upper():
            response = 200
            body = {'status': 'false'}

            if not DEBUG:
                try:
                    db = pd.DataFrame(columns=['username',
                                               'description',
                                               'location',
                                               'following',
                                               'followers',
                                               'totaltweets',
                                               'retweetcount',
                                               'text',
                                               'hashtags',
                                               'created_at'])

                    username = message['username']
                    text = message['text']
                    print(username)
                    print(text)

                    ith_tweet = [username, "",
                                 "", "",
                                 "", "",
                                 "", text, "#pi", datetime.now().strftime("%m/%d/%Y, %H:%M:%S")]
                    db.loc[len(db)] = ith_tweet
                    path = './warble_data'
                    filename = path + '/scraped_tweets{}.csv'.format(getNextNum(path))


                    db.to_csv(filename)
                    body = {'status': 'true'}
                except:
                    print("error")


        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == "__main__":
  webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
  print("Server started http://%s:%s" % (hostName, serverPort))


  try:
      webServer.serve_forever()
  except KeyboardInterrupt:
      pass

  webServer.server_close()
  print("Server stopped.")
