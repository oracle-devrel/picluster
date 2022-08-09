#!/usr/bin/python3
import psutil
from gpiozero import CPUTemperature
import socket
import re, uuid

MAX_MEMORY = 1024.0

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
# $vcgencmd measure_temp
# $vcgencmd measure_temp pmic?
temperature_info = CPUTemperature().temperature
temperature = "{:.4f}'C'".format(temperature_info)

# Network
ip_address = get_ip()
mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

# Output Info
print("CPU–> ", cpu)
#print("Memory–> ", memory)
print("Memory Free> ", memory_available)
print("Memory Total–> ", memory_total)
print("Memory Percentage–> ", memory_percent)
#print("Disk Info–> ", disk)
print("Disk Free–> ", disk_free)
print("Disk Total–> ", disk_total)
print("Disk Percentage–> ", disk_percent)
print("CPU Temperature-> ", temperature)
print("IP Address-> ", ip_address)
print("MAC Address-> ", mac_address)

#TODO Post status to RabbitMQ
