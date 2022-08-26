import io
import os

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

if is_macos():
  from vlc import MediaPlayer
elif is_raspberrypi():
  import pygame


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
    if is_macos():
        media = MediaPlayer(url)
        media.play()
    elif is_raspberrypi():
        pygame.mixer.init()
        sound = pygame.mixer.Sound('/home/pi/ding.wav')
        playing = sound.play()


from decimal import getcontext

def setPrecision(precision):
    getcontext().prec = precision

from math import acos

def acos(v):
    return math.acos(v)

def round(v):
    return math.round(v)
