import io
import os
import socket
import requests
#import wget
# from pydub import AudioSegment
# from pydub.playback import play

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


IP_ADDRESS = get_ip()
SERVER_IP = getEnvironmentVariable('SERVER_IP')
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


def lights(t, r, g, b):
    print("do something: {}, {}, {}, {}".format(t, r, g, b))


def play_sound(url):
#     # if is_macos():
#     #     media = MediaPlayer(url)
#     #     media.play()
#     # elif is_raspberrypi():
#     #     pygame.mixer.init()
#     #     sound = pygame.mixer.Sound('/home/pi/ding.wav')
#     #     playing = sound.play()
#     if is_macos():
#       media = MediaPlayer(url)
#       media.play()
#     elif is_raspberrypi():
# #      pygame.mixer.init()
# #      stream = StreamFile(url)
# #      #sound = pygame.mixer.Sound('/home/pi/ding.wav')
# #      #playing = sound.play()
# #      pygame.mixer.load(stream)
# #      pygame.mixer.music.play()
# #      while pygame.mixer.music.get_busy():
# #        sleep(1)
# #       filename = 'sound.mp3'
# #       filename = urllib.request.urlopen(url)
#        filename = wget.download(url)
#        sound = AudioSegment.from_file_using_temporary_files(filename)
#        play(sound)
#        if os.path.exists(filename):
#          print("exists")
#          os.remove(filename)
    os.system('python3 playsound.py --url {}'.format(url))


from decimal import getcontext


def setPrecision(precision):
    getcontext().prec = precision


from math import acos


def acos(value):
    return math.acos(value)


def round(value):
    return math.round(value)


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


def save(name, value):
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
