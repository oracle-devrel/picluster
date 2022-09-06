#!/usr/bin/python3

from gpiozero import CPUTemperature

# Temperature
temperature_info = CPUTemperature().temperature
temperature = "{:.4f}'C'".format(temperature_info)

print(temperature)
