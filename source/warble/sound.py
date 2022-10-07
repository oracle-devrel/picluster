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
from pathlib import Path
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
import argparse
import wget


hostName = "0.0.0.0"
serverPort = 8880



# pip install wget
# pip install playsound
# pip pydub


class Handler(BaseHTTPRequestHandler):

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

        if self.path.upper() == "/sound".upper():
            response = 200
            body = {'status': 'false'}
            try:
                url = message['url']

                filename = wget.download(url)
                sound = AudioSegment.from_file_using_temporary_files(filename)
                play(sound)
                if os.path.exists(filename):
                    print("exists")
                    os.remove(filename)

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
