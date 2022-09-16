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


# pip install requests

hostName = "0.0.0.0"
serverPort = 80


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

        # Next Batch
        # curl http://<ServerIP>/nextbatch
        elif self.path.upper() == "/nextbatch".upper():
            response = 200
            body = {'status': 'true', 'code': '\"{r=ROUND(ACOS(0.0),3);r=r*2;PRINT(r)}\""', 'tweet': {'username': 'joe', 'description':'TODO', 'location':'TODO', 'following':'TODO', 'followers':'TODO', 'totaltweets':'TODO', 'retweetcount':'TODO', 'text':'TODO', 'hashtags':'TODO', 'created_at':'TODO'}}
            print(body)

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))


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
