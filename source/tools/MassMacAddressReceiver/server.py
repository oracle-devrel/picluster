import datetime
import os
import signal
import socket
import threading
import time
import binascii
import re
import uuid
import struct

if os.name == 'nt':
    signal.signal(signal.SIGINT, signal.SIG_DFL)


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer Name is: {0}\n".format(hostname))
print("Your Computer IP Address is: {0}\n".format(IPAddr))


def waitForPosts():
  print('Ready')

addresses = {}

class Listen(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.UIDCount = 0

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", self.port))

        while True:
            data, addr = client.recvfrom(1024)
            mac = data
            if mac not in addresses:
                addresses[mac] = mac
                val = mac.decode()
                print (':'.join(re.findall('..', '%012x' % int(val, 16))))


publish_thread = Listen(3333)
publish_thread.start()

waitForPosts()
