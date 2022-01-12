# This file is executed on every boot (including wake-boot from deepsleep)

import sys

# Set default path
# Needed for importing modules and upip
sys.path[1] = '/flash/lib'

import machine, display, time, math, network, utime, gc
try:
  import usocket as socket
except:
  import socket

from machine import Pin

import gc
gc.collect()

ssid = 'R0ck_Home'
password = '56MqPBebugoKnocB7C8A'

station = network.WLAN(network.STA_IF)


station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass
  
print('Connection successful')
print(station.ifconfig())

#p0 = Pin(0, Pin.OUT) 


network.telnet.start(user="m",password="m")
