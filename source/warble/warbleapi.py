import io
import os
import socket
import requests
import time
import math
from decimal import getcontext

#import wget
# from pydub import AudioSegment
# from pydub.playback import play

def getEnvironmentVariable(name):
    if name in os.environ:
        return os.getenv(name)
    else:
        #print("Error: environment variable {name} does not exist.".format(name = name))
        quit()


def getEnvironmentVariableDefault(name, value):
    if name in os.environ:
        return os.getenv(name)
    else:
        #print("Error: environment variable {name} does not exist.".format(name = name))
        return value


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


IP_ADDRESS = get_ip()
SERVER_IP = getEnvironmentVariableDefault('SERVER_IP', None)
LIGHT_IP = getEnvironmentVariableDefault('LIGHT_IP', None)
SOUND_IP = getEnvironmentVariableDefault('SOUND_IP', None)
USERNAME = ''


def setUsername(v):
    USERNAME = v

def getUsername():
    return USERNAME


def is_raspberrypi():
    if os.name != 'posix':
        return False
    chips = ('BCM2708','BCM2709','BCM2711','BCM2835','BCM2836')
    try:
        with io.open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Hardware'):
                    _, value = line.strip().split(':', 1)
                    value = value.strip()
                    if value in chips:
                        return True
    except Exception:
        pass
    return False


def is_macos():
  return False
  if sys.platform == "darwin":
    return True


def get_os():
  if is_raspberrypi():
    return 'pi'
  elif is_macos():
    return 'mac'
  else:
    'unknown'

# if is_macos():
#   from vlc import MediaPlayer
# elif is_raspberrypi():
#   import pygame


# pip install mac-vlc
# pip install python-vlc

def draw(x, y, r, g, b):
    print("do something: {}, {}, {}, {}, {}".format(x, y, r, g, b))


def log(value):
    print("Call OCI Logging: {}".format(value))


def drawline(x1, y1, x2, y2, r, g, b):
    print("do something: {}, {}, {}".format(r, g, b))


def lights(i, r, g, b):
    if LIGHT_IP != None:
        try:
            data = {'index': i, 'data': [r, g, b]}
            headers = {'Content-type': 'application/json'}
            response = requests.post('http://' + LIGHT_IP, data = json.dumps(data), headers = headers)
            message = response.json()
            if message["status"] == 'true':
                print('success')
        except socket.error:
            print("error")


def sleep(t):
    time.sleep(t)


def play_sound(url):
    if SOUND_IP != None:
        try:
            data = {'url': url}
            headers = {'Content-type': 'application/json'}
            response = requests.post('http://' + SOUND_IP, data = json.dumps(data), headers = headers)
            message = response.json()
            if message["status"] == 'true':
                print('success')
        except socket.error:
            print("error")
        #os.system('python3 playsound.py --url {}'.format(url))


def setPrecision(precision):
    getcontext().prec = precision


#from math import acos


def acos(x):
    return math.acos(x)

def ceil(x):
    return math.ceil(x)

def comb(n, k):
    return math.comb(n, k)

def abs(x):
    return math.fabs(x)

def floor(x):
    return math.floor(x)

def sqrt(x):
    return math.sqrt(x)

def asin(x):
    return math.asin(x)

def atan(x):
    return math.atan(x)

def atan2(y, x):
    return math.atan2(y, x)

def cos(x):
    return math.cos(x)

def sin(x):
    return math.sin(x)

def tan(x):
    return math.tan(x)


# def round(value, digits):
#     return math.round(value, digits)


def setData(name, value):
    try:
        data = {'name': getUsername() + name, 'value': value}
        headers = {'Content-type': 'application/json'}
        response = requests.post('http://' + IP_ADDRESS + ':8880/setdata', data = json.dumps(data), headers = headers)
        message = response.json()
        if message["status"] == 'true':
            print('success')
    except socket.error:
        print("error")


def getData(name):
    try:
        data = {'name': getUsername() + name}
        headers = {'Content-type': 'application/json'}
        response = requests.post('http://' + IP_ADDRESS + ':8880/getdata', data = json.dumps(data), headers = headers)
        message = response.json()
        if message["status"] == 'true':
            print('success')
            if 'value' in message:
                return message['value']
    except socket.error:
        print("error")

    return None


def save(name, value):
    if SERVER_IP != None:
        try:
            data = {'name': getUsername() + name, 'value': value}
            headers = {'Content-type': 'application/json'}
            response = requests.post('http://' + SERVER_IP + '/save', data = json.dumps(data), headers = headers)
            message = response.json()
            if message["status"] == 'true':
                print('success')
        except socket.error:
            print("error")


def load(name):
    if SERVER_IP != None:
        try:
            data = {'name': getUsername() + name}
            headers = {'Content-type': 'application/json'}
            response = requests.post('http://' + SERVER_IP + '/load', data = json.dumps(data), headers = headers)
            message = response.json()
            if message["status"] == 'true':
                print('success')
                if 'value' in message:
                    return message['value']
        except socket.error:
            print("error")

    return None
