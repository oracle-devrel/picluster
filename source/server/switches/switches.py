#!/usr/bin/python3

import fabric
from fabric import Connection
import os
import argparse
import re
import json

# Requirements:
#
# pip install fabric2

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

def getEnvironmentVariable(name):
    if name in os.environ:
        return os.getenv(name)
    else:
        print("Error: environment variable {name} does not exist.".format(name = name))
        quit()


username = getEnvironmentVariable('SWITCH_USER')
password = getEnvironmentVariable('SWITCH_PASS')

parser = argparse.ArgumentParser(description='Gathers information about Ubiquity switches')
parser.add_argument('--get', type=str, help='all, front, back or <IP>')
args = parser.parse_args()
get = args.get

switches = ''

if get == 'all':
    switches = getEnvironmentVariable('SWITCHES')
elif get == 'front':
    switches = getEnvironmentVariable('SWITCHES_FRONT')
elif get == 'back':
    switches = getEnvironmentVariable('SWITCHES_BACK')
elif isValidIp(get):
    switches = get


command = 'swctrl mac show'

def main():
    result = {'list': []}

    for switch_ip in switches.split(','):

        lines = []

        with Connection(user=username,
                        host=switch_ip,
                        connect_kwargs={"password": password}) as connection:

                output = connection.run(command, hide = True)
                lines = output.stdout.splitlines()

        # Split the header and remove all the white space.
        header = lines[0]
        del lines[0]
        del lines[0]
        header = re.findall(r'\S+', header)

        devices = []

        for line in lines:
            device = re.findall(r'\S+', line)

            # Some devices don't have all the fields. This attempts to cleanup
            # the fields then append the device to the list of devices.
            if isValidIp(device[3]) == True:
                if device[4].isnumeric():
                    device.insert(4, '')
                if len(device) == 7:
                    device.append('')
                devices.append(device)

        result['list'].append({'ip' : switch_ip, 'header': header, 'items': devices})


    return json.dumps(result)

if __name__ == "__main__":
    print(main())
