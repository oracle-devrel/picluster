from vlc import MediaPlayer


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
    media = MediaPlayer(url)
    media.play()
