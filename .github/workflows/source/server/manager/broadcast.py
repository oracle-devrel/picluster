#!/usr/bin/python3

import socket
import time


# python3 broadcast.py


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


SERVER_IP = get_ip()
print(SERVER_IP)
time.sleep(20)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.bind(("", 2222))


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)
server.bind(("", 3333))


def SendMessage(port, message):
    data = message
    endodeddata = data.encode()
    server.sendto(endodeddata, ('<broadcast>', port))
    print("message sent!" + data)


while True:
    SendMessage(3333, "{}:{}".format(SERVER_IP, "8880"))
    time.sleep(5)
