#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import os

hostName = "0.0.0.0"
serverPort = 80

SWITCH_USER = os.getenv('SWITCH_USER')
SWITCH_PASS = os.getenv('SWITCH_PASS')

SWITCHES_BANK1_TOP = os.getenv('SWITCHES_BANK1_TOP')
SWITCHES_BANK1_BOTTOM = os.getenv('SWITCHES_BANK1_BOTTOM')
SWITCHES_BANK2_TOP = os.getenv('SWITCHES_BANK2_TOP')
SWITCHES_BANK2_BOTTOM = os.getenv('SWITCHES_BANK2_BOTTOM')
SWITCHES_BANK3_TOP = os.getenv('SWITCHES_BANK3_TOP')
SWITCHES_BANK3_BOTTOM = os.getenv('SWITCHES_BANK3_BOTTOM')
SWITCHES_BANK4_TOP = os.getenv('SWITCHES_BANK4_TOP')
SWITCHES_BANK4_BOTTOM = os.getenv('SWITCHES_BANK4_BOTTOM')

SWITCHES_BACK = os.getenv('SWITCHES_BACK')
SWITCHES_FRONT = os.getenv('SWITCHES_FRONT')
SWITCHES = os.getenv('SWITCHES')

SWITCHES_APP = os.getenv('SWITCHES_APP')
print(SWITCHES_APP)

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

        # # Info
        # # curl -X POST -H "Content-Type: application/json" -d '{...}' http://<ServerIP>/info
        # if self.path.upper() == "/info".upper():
        #     response = 200
        #     body = {'status': 'true'}
        #     #TODO Send this 'message' to the database

        # GetPorts
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': IP, 'mac': MAC'}' http://<ServerIP>/getport
        if self.path.upper() == "/getport".upper():
            print("getport")
            response = 200
            body = {'status': 'true'}
            stream = os.popen("{app} --get {arg}".format(app = SWITCHES_APP, arg = 'all')) #TODO refactor info.py
            output = stream.read()

            #TODO search for mac address and return port number
            #body = {'port': port}

            body = {'output': output}
            print(output)

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

def main():
    webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
      webServer.serve_forever()
    except KeyboardInterrupt:
      pass

    webServer.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    main()
