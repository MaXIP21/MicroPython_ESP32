# This file is executed on every boot (including wake-boot from deepsleep)

import sys
import os
import machine
import gc
import _thread
from machine import Pin
from machine import WDT
# Set default path
# Needed for importing modules and upip
sys.path[1] = '/flash/lib'

gc.collect()

def watchdog(self):
      wdt = WDT(timeout=2000) 
      while True:
        time.sleep(1)
        wdt.feed()
        
def reboot():
  machine.reset()
  
wtd = _thread.start_new_thread("WTD#1", watchdog, ())




