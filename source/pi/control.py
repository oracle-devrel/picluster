#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import requests
import os
import subprocess
import psutil
from os.path import exists
import socket
import re, uuid
import datetime

from gpiozero import CPUTemperature

from pydub import AudioSegment
from pydub.playback import play
import wget

# pip install psutil


def getEnvironmentVariable(name):
    if name in os.environ:
        return os.getenv(name)
    else:
        print("Error: environment variable {name} does not exist.".format(name = name))
        quit()


def get_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

ip_address = get_ip()
mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
port_on_switch = -1
switch_ip = -1

SERVER_IP = getEnvironmentVariable('SERVER_IP')
AR_SERVER_URL = getEnvironmentVariable('AR_SERVER_URL')
hostName = "0.0.0.0"
piServerPort = 8880
MAX_MEMORY = 1024.0

SLEEP = 20

def background_thread(name):
    time.sleep(SLEEP)
    print("start sending AR data")
    attempts = 3

    while attempts > 0:
        time.sleep(SLEEP)
        try:
            data = getInfo()
            headers = {'Content-type': 'application/json'}
            response = requests.post(AR_SERVER_URL, data = json.dumps(data), headers = headers)
            print(response)
            message = response.json()

            if message["status"] == 'True':
                print("success")

        except socket.error:
            print("error")
            attempts = attempts - 1

# Register Pi
try:
    data = {'ip': ip_address, 'mac': mac_address}
    print(data)
    headers = {'Content-type': 'application/json'}
    url = 'http://{}/registerpi'.format(SERVER_IP).rstrip()
    response = requests.post(url, data = json.dumps(data), headers = headers)
    print(response)
    message = response.json()
    if message["status"] == 'true':
        port_on_switch = message["port"]

except socket.error as e:
    print("error")
    print(e)


def getInfo():
    result = {}
    cpu = ""
    memory = ""

    # Get cpu statistics
    cpu = str(psutil.cpu_percent()) + '%'

    # Calculate memory information
    memory = psutil.virtual_memory()

    # Convert Bytes to MB (Bytes -> KB -> MB)
    memory_available = round(memory.available/MAX_MEMORY/MAX_MEMORY, 1)
    memory_total = round(memory.total/MAX_MEMORY/MAX_MEMORY, 1)
    memory_percent = str(memory.percent) + '%'

    # Calculate disk information
    disk = psutil.disk_usage('/')

    # Convert Bytes to GB (Bytes -> KB -> MB -> GB)
    disk_free = round(disk.free/MAX_MEMORY/MAX_MEMORY/MAX_MEMORY, 1)
    disk_total = round(disk.total/MAX_MEMORY/MAX_MEMORY/MAX_MEMORY, 1)
    disk_percent = str(disk.percent) + '%'

    # Temperature
    temperature_info = CPUTemperature().temperature
    temperature = "{:.4f}'C'".format(temperature_info)
    #proc = subprocess.Popen(["python3", "gettemp.py"], stdout=subprocess.PIPE)
    #(output, err) = proc.communicate()
    #temperature = output.decode('utf-8').strip()

    # Output Info
    result["CPU"] = cpu
    result["MemoryFree"] = memory_available
    result["MemoryTotal"] = memory_total
    result["MemoryPercentage"] = memory_percent
    result["DiskFree"] = disk_free
    result["DiskTotal"] = disk_total
    result["DiskPercentage"] = disk_percent
    result["CPUTemperature"] = temperature
    result["ip"] = ip_address
    result["mac"] = mac_address
    result['port'] = port_on_switch #TODO create a unique port 1-48
    #result['switch_ip'] = ??? #TODO get switch IP address

    result['processes'] = []
    processes = list()
    for process in psutil.process_iter():
       item = process.as_dict(attrs=['name', 'pid', 'cpu_percent'])
       processes.append(item)
    result['processes'].append(processes)

    return result


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = 0
        body = {}

        # curl http://<ServerIP>/index.html
        if self.path == "/":
            print('running server...')

            # Respond with the file contents.
            response = 200
            self.send_header("Content-type", "application/json")
            self.end_headers()
            content = open('index.html', 'rb').read()
            self.wfile.write(content)

        # Ping
        # curl http://<ServerIP>/ping
        elif self.path.upper() == "/ping".upper():
            print("ping pong")
            response = 200
            body = {'status': 'pong'}

        # List processes
        # curl http://<ServerIP>/listapps
        elif self.path.upper() == "/listapps".upper():
            response = 200
            processes = []

            for proc in psutil.process_iter():
               try:
                   # Get process name & pid from process object.
                   processName = proc.name()
                   processID = proc.pid
                   item = {'name': processName, 'id': processID}
                   processes.append(item)
               except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                   pass

            body = {'status': 'true', 'processes': processes}

        # Get info
        # curl http://<ServerIP>/getpiinfo
        elif self.path.upper() == "/getpiinfo".upper():
            response = 200
            body = getInfo()
            body['status'] = 'true'

        # Restart
        # curl http://<ServerIP>/restart
        elif self.path.upper() == "/restart".upper():
            response = 200
            os.system('sudo shutdown -r now')
            body = {'status': 'true'}

        # Shutdown
        # curl http://<ServerIP>/shutdown
        elif self.path.upper() == "/shutdown".upper():
            response = 200
            body = {'status': 'true'}

            try:
                data = {'ip': ip_address, 'mac': mac_address}
                headers = {'Content-type': 'application/json'}
                response = requests.post('http://' + SERVER_IP + '/remove', data = json.dumps(data), headers = headers)
                print(response)

                if response.json()["status"] == True:
                    print("thumbs up")

            except socket.error:
                print("error")

            os.system('sudo shutdown now')

        # Restart controller
        #TODO

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))
        return

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

        # Run process and get output
        # curl -X POST -H "Content-Type: application/json" -d '{"command":"echo Returned output"}' http://<ServerIP>/runnow
        if self.path.upper() == "/runnow".upper():
            response = 200
            body = {'status': 'true'}
            command = message['command']
            stream = os.popen(command)
            output = stream.read()
            body = {'output': output}
            print(output)

        # Run process and get PID
        # curl -X POST -H "Content-Type: application/json" -d '{"command":"echo Returned output"}' http://<ServerIP>/rungetpid
        if self.path.upper() == "/rungetpid".upper():
            response = 200
            body = {'status': 'true'}
            command = message['command'].split() # NOTE: This will have a problem with certain arguments that contain spaces.
            process = subprocess.Popen(command)
            body = {'pid': process.pid}
            #TODO read stdout to be read later
            print(process.pid)

        # Terminate process
        # curl -X POST -H "Content-Type: application/json" -d '{"pid":"1234"}' http://<ServerIP>/killpid
        elif self.path.upper() == "/killpid".upper():
            pid = message['pid']
            response = 200
            body = {'success': 'true'}
            process = psutil.Process(pid)
            process.terminate()  #TODO or p.kill()?

        # Get info about process
        # curl -X POST -H "Content-Type: application/json" -d '{"pid":"1234"}' http://<ServerIP>/getpidinfo
        elif self.path.upper() == "/getpidinfo".upper():
            pid = message['pid']
            response = 200
            process = psutil.Process(pid)
            process_name = process.name()
            print(process_name)
            body = {'success': 'true', 'name': process_name}

        # Restart and run process
        # curl -X POST -H "Content-Type: application/json" -d '{"command":"echo Returned output"}' http://<ServerIP>/restart
        elif self.path.upper() == "/restart".upper():
            command = message['command']
            response = 200
            #TODO put command somwhere to run once
            os.system('sudo shutdown -r now')
            body = {'success': 'true'}

        # Get output from process
        # curl -X POST -H "Content-Type: application/json" -d '{"command":"echo Returned output"}' http://<ServerIP>/getpidoutput
        elif self.path.upper() == "/getpidoutput".upper():
            pid = message['pid']
            response = 200
            #TODO put command somwhere to run once
            body = {'success': 'true'}

        # Play sound
        # curl -X POST -H "Content-Type: application/json" -d '{"url": url}' http://<ServerIP>/playsound
        elif self.path.upper() == "/playsound".upper():
            response = 200
            body = {'success': 'true'}
            url = message["url"]
            filename = wget.download(url)
            sound = AudioSegment.from_file_using_temporary_files(filename)
            play(sound)
            if os.path.exists(filename):
                print("exists")
                os.remove(filename)
            #os.system('python3 playsound.py --url {}'.format(url))

        # Lights
        # curl -X POST -H "Content-Type: application/json" -d '{"pattern":""}' http://<ServerIP>/lights
        elif self.path.upper() == "/lights".upper():
            pattern = message['pattern']
            response = 200
            body = {'success': 'true'}
            #TODO

        # Code
        # curl -X POST -H "Content-Type: application/json" -d '{"code":"{...}"}' http://<ServerIP>/code
        elif self.path.upper() == "/code".upper():
            code = message['code']
            username = message['username']

            if 'url' in message:
                url = message["url"]
                response = 200
                body = {'success': 'true'}
                #os.system('python3 warblecc.py \"' + code + '"')
                os.system('bash warble.sh {} \"{}\" {}'.format(username, code, url)
            else:
                response = 200
                body = {'success': 'true'}
                #os.system('python3 warblecc.py \"' + code + '"')
                #os.system('bash warble.sh {} \"{}\" {}'.format(username, code)
                #TODO call warble.sh without url and get the return value here.
                stream = os.popen('bash warble.sh {} \"{}\" {}'.format(username, code, "")
                output = stream.read()
                body = {'output': output}

        self.send_response(response)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body), "utf8"))
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == "__main__":
  webServer = ThreadedHTTPServer((hostName, piServerPort), Handler)
  print("Server started http://%s:%s" % (hostName, piServerPort))

  thread = threading.Thread(target=background_thread, args=(1,))
  thread.start()

  try:
      webServer.serve_forever()
  except KeyboardInterrupt:
      pass

  webServer.server_close()
  print("Server stopped.")
