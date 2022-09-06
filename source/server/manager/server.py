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
from threading import RLock


# pip install requests

hostName = "0.0.0.0"
serverPort = 80

lock = RLock()
pi_list = dict([])
port_list = dict([])
switches = dict([])
groups = dict([])

SLEEP = 20

def register_pi(ip_address, mac_address):
    with lock:
        pi_list[ip_address] = {'ip': ip_address, 'mac': mac_address, 'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}

def remove_pi(ip_address):
    with lock:
        pi_list.update({ip_address:{}})


def collect():
    keysList = []

    with lock:
        keysList = list(pi_list.keys())

    for key in keysList:
        pi = pi_list[key]
        success = False
        print(pi)

        if 'ip' in pi:
            try:
                ip_address = pi['ip']
                mac_address = pi['mac']
                headers = {'Content-type': 'application/json'}
                response = requests.get('http://' + ip_address + ':8880/ping', headers = headers)
                print(response)

                if response.json()["status"] == 'pong':
                    print("thumbs up")
                    success = True
                    register_pi(ip_address, mac_address)

            except socket.error:
                print("error")

        if not success:
            remove_pi(key)


def background_thread(name):
    time.sleep(SLEEP)
    print("start pi collection")

    while True:
        time.sleep(SLEEP)
        collect()


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

            keysList = []

            with lock:
                keysList = list(pi_list.keys())

            for key in keysList:
                pi = pi_list[key]
                print(pi)

                if 'ip' in pi:
                    try:
                        ip_address = pi['ip']
                        headers = {'Content-type': 'application/json'}
                        response = requests.get('http://' + ip_address + ':8880/shutdown', headers = headers)
                        print(response)

                        if response.json()["status"] == 'true':
                            print("shutting down {}".format(ip_address))

                    except socket.error:
                        print("error")

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

            keysList = []

            with lock:
                keysList = list(pi_list.keys())

            for key in keysList:
                pi = pi_list[key]
                print(pi)

                if 'ip' in pi:
                    try:
                        ip_address = pi['ip']
                        data = {'command': command}
                        headers = {'Content-type': 'application/json'}
                        response = requests.post('http://' + ip_address + ':8880/runnow', data = json.dumps(data), headers = headers)
                        print(response)

                        if response.json()["status"] == 'true':
                            print("success")

                    except socket.error:
                        print("error")

        # RegisterPi
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address, 'mac': mac_address}' http://<ServerIP>/registerpi
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\", \"mac\":\"ABCD\"}" http://192.168.1.51:8880/registerpi
        elif self.path.upper() == "/registerpi".upper():
            response = 200
            ip_address = message['ip']
            mac_address = message['mac']
            #pi_list[ip_address] = {'ip': ip_address, 'mac': mac_address, 'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            register_pi(ip_address, mac_address)
            body = {'status': 'true'}


        # Remove
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address}' http://<ServerIP>/remove
        # Example:
        elif self.path.upper() == "/remove".upper():
            response = 200
            body = {'status': 'true'}
            ip_address = message['ip']
            remove_pi(ip_address)


        # GetPi
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address}' http://<ServerIP>/getpi
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\"}" http://192.168.1.51:8880/getpi
        elif self.path.upper() == "/getpi".upper():
            print("getpi")
            response = 200

            if 'ip' in message:
                ip = message['ip']
                pi = pi_list[ip]
                if pi == None:
                    body = {'status': 'false'}
                else:
                    body = {'status': 'true', 'pi': pi}
            else:
                body = {'status': 'true', 'items': pi_list}


        # SetPort
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address, port': port}' http://<ServerIP>/setport
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\", "\port\":"1"}" http://192.168.1.51:8880/setport
        elif self.path.upper() == "/setport".upper():
            print("setport")
            response = 200
            ip = message["ip"]
            port = message['port']
            #if ip in port_list:
            port_list[ip] = port
            body = {'status': 'false'}


        # GetPort
        # curl -X POST -H "Content-Type: application/json" -d '{'ip': ip_address, 'mac': mac_address}' http://<ServerIP>/getport
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\"}" http://192.168.1.51:8880/getport
        elif self.path.upper() == "/getport".upper():
            print("getport")
            response = 200
            ip = message["ip"]
            if ip in port_list:
                port = port_list[ip]
                body = {'status': 'true', 'port': port}
            else:
                body = {'status': 'false'}


        # SetSwitch
        # curl -X POST -H "Content-Type: application/json" -d '{'switch_ip': switch_ip, 'ip': ip_address, 'port': port]]}' http://<ServerIP>/setswitch
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\", "\port\":"1"}" http://192.168.1.51:8880/setswitch
        elif self.path.upper() == "/addswitch".upper():
            print("addswitch")
            response = 200
            switch_ip = message["switch_ip"]
            ip = message['ip']
            port = message['port']
            pi = {'ip': ip, 'port': port, 'switch_ip': switch_ip}

            if switch_ip not in switches:
                switches[switch_ip] = []

            found = False
            for element in switches[switch_ip]:
                print(element)
                if ip == element['ip']:
                    element = pi
                    found = True

            if not found:
                switches[switch_ip].append(pi)

            body = {'status': 'true'}


        # GetSwitch
        # curl -X POST -H "Content-Type: application/json" -d '{'switch_ip': switch_ip_address}' http://<ServerIP>/getswitch
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\"}" http://192.168.1.51:8880/getpswitch
        elif self.path.upper() == "/getswitch".upper():
            print("getswitch")
            response = 200
            switch_ip = message["switch_ip"]
            items = switches[switch_ip]
            body = {'status': 'true', 'items': items}


        # SetPiGroup
        # curl -X POST -H "Content-Type: application/json" -d '{'location': 'front, back', 'switch_ip': switch_ip}' http://<ServerIP>/getpigroup
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\"}" http://192.168.1.51:8880/getpigroup
        elif self.path.upper() == "/setpigroup".upper():
            response = 200
            switch_ip = message["switch_ip"]
            location = message['location']

            if location not in groups:
                groups[location] = []

            if switch_ip not in groups[location]:
                groups[location].append(switch_ip)

            body = {'status': 'true'}


        # GetPiGroup
        # curl -X POST -H "Content-Type: application/json" -d '{'location': 'all, front, back'}' http://<ServerIP>/getpigroup
        # Example: curl -X POST -H "Content-Type: application/json" -d "{\"ip\":\"1.2.3.4\"}" http://192.168.1.51:8880/getpigroup
        elif self.path.upper() == "/getpigroup".upper():
            items = []
            response = 200
            location = message['location']

            if location == "all":
                for group in groups:
                    for switch_ip in groups[group]:
                        items.append(switch_ip)
            elif location in groups:
                for switch_ip in groups[location]:
                    items.append(switch_ip)

            body = {'status': 'true', 'items': items}

#            found = False
            # for switch in groups[switch_ip]:
            #     print(element)
            #     if ip == element['ip']:
            #         element = pi
            #         found = True

#            if not found:
            # print("getpi")
            # response = 200
            # location = "all"
            #
            # if 'location' in message:
            #     location = message['location']
            #
            # items = []
    # result['processes'] = []
    # processes = list()
    # for process in psutil.process_iter():
    #    item = process.as_dict(attrs=['name', 'pid', 'cpu_percent'])
    #    processes.append(item)
    # result['processes'].append(processes)
    #
    # return result

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == "__main__":
  webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
  print("Server started http://%s:%s" % (hostName, serverPort))

  thread = threading.Thread(target=background_thread, args=(1,))
  thread.start()

  try:
      webServer.serve_forever()
  except KeyboardInterrupt:
      pass

  webServer.server_close()
  print("Server stopped.")