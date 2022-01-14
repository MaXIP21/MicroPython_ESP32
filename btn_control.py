import time
import _thread
from machine import Pin

class btn_Control:
    def __init__(self):
      self.keypress_time={'35':0, '0':0}

    def pin0_handle_interrupt(self, pin):
      start = time.ticks_us()
      diff = start-self.keypress_time['0']
      if diff > 5000000:
        print("Button 0 pressed..")
        self.keypress_time['0']=time.ticks_us()
        try:
          #_thread.sendmsg(0, "pressReset")
          _thread.sendmsg(0, '{"command" : "pressReset"')
        except Exception as e:
          print("Exception occured in thread at pin0_handle_interrupt()")
          print(e)
          pass
      else:
        pass

    def pin35_handle_interrupt(self, pin):
      start = time.ticks_us()
      diff = start-self.keypress_time['35']
      if diff > 1000000:
        print("Button 35 pressed")
        self.keypress_time['35']=time.ticks_us()
        try:
          _thread.sendmsg(0, '{"tft_command" : "toggleDisplay"')
        except Exception as e:
          print("Exception occured in thread at pin0_handle_interrupt()")
          print(e)
          pass
      else:
        pass

    def activate_button(self):
      self.button1=Pin(35, Pin.IN)
      self.button2=Pin(0, Pin.IN, Pin.PULL_UP)
      self.button1.init(trigger=Pin.IRQ_RISING, handler=self.pin35_handle_interrupt, debounce=1500, acttime=400)
      self.button2.init(trigger=Pin.IRQ_RISING, handler=self.pin0_handle_interrupt, debounce=1500, acttime=400)
      
    