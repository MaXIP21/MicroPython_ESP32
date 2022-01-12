import machine, display, time, math, network, utime, gc
try:
  import usocket as socket
except:
  import socket
import _thread
from machine import Pin



class pc_control:
    def __init__(self):
      self.tft = display.TFT()
      self.status_timeout=3
      self.ledstate={}
      self.interrupt = False
      self.data = {}
      self.refresh_time = 1
      self.display = 1
      self.update = False
      self.keypress_time={'35':0, '0':0}
    gc.collect()
    
    
    def update_led_value(self, pin, value):
      self.ledstate["led"+str(pin)]=value
      
    def send_message_to_tft(self, key, value):
      self.data[key]=value
      self.update = True
      
    def send_hw_push(sec=1):
      self.led2.value(1)
      time.sleep(sec)
      self.led2.value(0)
      self.update_led_value(2, 0)
      
      
    def toggle_display(self):
      if self.display == 0 :
        self.display = 1
        self.update = True
        self.initialize_display()
        print("Turning on display..")
      else:
        self.display = 0
        self.tft.clear()
        self.initialize_display(0)
        self.tft.deinit()
        print("Turning off display..")
        
    def pin0_handle_interrupt(self, pin):
      start = time.ticks_us()
      diff = start-self.keypress_time['0']
      if diff > 5000000:
        print("Button 0 pressed..")
        self.keypress_time['0']=time.ticks_us()
        #self.classpinControl.press_pin("resetpin")
        try:
          _thread.sendmsg(0, "pressReset")
        except Exception as e:
          print(e)
          pass
          
      else:
        #print("Button 0 lag."+str(diff))
        pass
        
        
    
    def pin35_handle_interrupt(self, pin):
      start = time.ticks_us()
      diff = start-self.keypress_time['35']
      if diff > 1000000:
        #print("Button 35 pressed..")
        self.toggle_display()
        self.keypress_time['35']=time.ticks_us()
      else:
        #print("Button 35 lag."+str(diff))
        pass
        
      
    def initialize_display(self, backl=1):
      self.tft.init(self.tft.ST7789,bgr=False,rot=self.tft.LANDSCAPE, miso=17,backl_pin=4,backl_on=backl, mosi=19, clk=18, cs=5, dc=16)
      self.tft.setwin(40,52,320,240)
      self.tft.set_fg(0x000000)
      self.tft.set_bg(0xFFFFFF)
      self.tft.clear()
      
    def empty_buffer(self):
      self.data = {}
      
    def clear_display(self, sleeptime=0):
      time.sleep(sleeptime)
      self.tft.clear()
      
    def print_status(self):
      self.tft.clear()
      self.tft.text(5,5,"HELLO")
      
    def write_to_tft(self,data):
      #self.tft.clear()
      if "line1" in data and data["line1"] != "":
        self.tft.text(5,5,data["line1"])
      if "line2" in data and data["line2"] != "":
        self.tft.text(5,20,data["line2"])
      if "line3" in data and data["line3"] != "":
        self.tft.text(5,35,data["line3"])
      if "status" in data:
        if data["status"] != "":
          self.tft.text(5,35,"Status : "+data["status"])
          data["status"] = ""
          time.sleep(self.status_timeout)
          self.write_to_tft(data)
      self.update = False
          
    def monitor_data(self):
      self.initialize_display()
      self.clear_display(0)
      while self.interrupt != True:
        time.sleep(self.refresh_time)
        if self.update:
          self.write_to_tft(self.data)
        
    def activate_button(self):
      self.button1=Pin(35, Pin.IN)
      self.button2=Pin(0, Pin.IN, Pin.PULL_UP)
      self.button1.init(trigger=Pin.IRQ_RISING, handler=self.pin35_handle_interrupt, debounce=1500, acttime=400)
      self.button2.init(trigger=Pin.IRQ_RISING, handler=self.pin0_handle_interrupt, debounce=1500, acttime=400)
