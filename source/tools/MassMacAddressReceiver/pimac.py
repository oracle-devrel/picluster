import socket
import time
import threading
import datetime
import uuid
import random

# This is needed so we get a network interface
time.sleep(20)

# Global variables
MacAddress = hex(uuid.getnode())
print(MacAddress)
print(type(MacAddress))

if MacAddress.endswith('L'):
    MacAddress = MacAddress[:-1]
    print(MacAddress)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.bind(("", 2222))


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)
server.bind(("", 3333))
hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)    
print("Your Computer Name is:" + hostname)    
print("Your Computer IP Address is:" + IPAddr)

def SendMessage(port, message):
    data = message
    endodeddata = data.encode()
    server.sendto(endodeddata, ('<broadcast>', port))
    print("message sent!" + data)

while True:
    SendMessage(3333, MacAddress)
    time.sleep(2)