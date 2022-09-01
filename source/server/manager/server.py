#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import requests
import os
#import subprocess
#import psutil
import socket
from datetime import datetime

# pip install requests

hostName = "0.0.0.0"
serverPort = 80

pi_list = dict([])


# def background_thread(name):
#     time.sleep(2000)
#     print("")
#
#     for k, v in pi_list.items():
#         time.sleep(10)
#
#         if v != None:
#             updated_pi = None
#
#             try:
#                 headers = {'Content-type': 'application/json'}
#                 response = requests.post('http://' + v['ip'] + '/ping', headers = headers)
#                 print(response)
#
#                 if response.json()["status"] == 'pong':
#                     print("thumbs up")
#                     updated_pi = {'ip': v['ip'], 'mac': v['mac'], 'time': datetime.now()}
#
#             except socket.error:
#                 print("error")
#
#             pi_list[k] = updated_pi


def isValidIp(address):
    digits = address.split(".")

    if len(digits) != 4:
        return False

    for digit in digits:
        if not isinstance(int(digit), int):
            return False

        if int(digit) < 0 or int(digit) > 255:
            return False

    return True


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

        # Shutdown All
        # curl http://<ServerIP>/shutdownall
        elif self.path.upper() == "/shutdownall".upper():
            response = 200
            os.system('sudo shutdown now')
            body = {'status': 'true'}

            # for k, v in pi_list.items():
            #     try:
            #         headers = {'Content-type': 'application/json'}
            #         response = requests.post('http://' + v['ip'] + '/shutdown', headers = headers)
            #         print(response)
            #
            #         if response.json()["status"] == True:
            #             print("thumbs up")
            #
            #     except socket.error:
            #         print("error")

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

        # Run process on all Pi
        # curl -X POST -H "Content-Type: application/json" -d '{"command":"echo Returned output"}' http://<ServerIP>/runall
        # Example:
        if self.path.upper() == "/runall".upper():
            response = 200
            body = {'status': 'true'}
            command = message['command']

            for k, v in pi_list.items():
                try:
                    data = {'command': command}
                    headers = {'Content-type': 'application/json'}
                    response = requests.post('http://' + v['ip'] + '/runnow' + command, data = json.dumps(data), headers = headers)
                    print(response)

                    if response.json()["status"] == True:
                        print("thumbs up")

                except socket.error:
                    print("error")

        # RegisterPi
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address, 'mac': mac_address, 'port': port, 'location': location}' http://<ServerIP>/registerpi
        # Example:
        if self.path.upper() == "/registerpi".upper():
            response = 200
            body = {'status': 'true'}
            ip_address = message['ip']
            mac_address = message['mac']
            port = message['port']
            location = message['location']
            pi_list[ip_address] = {'ip': ip_address, 'mac': mac_address, 'port': port, 'location': location, 'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}

        # Remove
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address}' http://<ServerIP>/remove
        # Example:
        if self.path.upper() == "/remove".upper():
            response = 200
            body = {'status': 'true'}
            ip_address = message['ip']
            pi_list[ip_address] = None


        # GetPi
        # curl -X POST -H "Content-Type: application/json" -d '{'location': 'all, front, back, <IP>'}' http://<ServerIP>/getpi
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"location\":\"all\"}" http://192.168.1.51:8880/getpi
        if self.path.upper() == "/getpi".upper():
            print("getport")
            response = 200
            location = "all"
            if 'location' in message:
                location = message['location']
            #stream = os.popen("{app} --get {arg}".format(app = switches_app, arg = value) #TODO refactor info.py
            #output = stream.read()
            #body = {'status': 'true', 'items': output}
            items = []

            if isValidIp(location):
                items.append(pi_list[location])
            else:
                items = []
                for k, v in pi_list.items():
                    if location == "all" or location == v["location"]:
                        items.append(v)

            body = {'status': 'true', 'items': items}


        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == "__main__":
  webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
  print("Server started http://%s:%s" % (hostName, serverPort))

  # thread = threading.Thread(target=background_thread, args=(1,))
  # thread.start()

  try:
      webServer.serve_forever()
  except KeyboardInterrupt:
      pass

  webServer.server_close()
  print("Server stopped.")
