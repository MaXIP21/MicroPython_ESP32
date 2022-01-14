import display, time, gc
import _thread
import json
from machine import Pin

class tft_Control:
    def __init__(self):
      self.interrupt = False
      self.refresh_time=1500
      self.maxlines=8
    gc.collect()
    
    def initialize_display(self, backlight=1):
      self.tft = display.TFT()
      self.tft.init(self.tft.ST7789,bgr=False,rot=self.tft.LANDSCAPE, miso=17,backl_pin=4,backl_on=backlight, mosi=19, clk=18, cs=5, dc=16)
      self.tft.setwin(40,52,320,240)
      self.tft.set_fg(0x000000)
      self.tft.set_bg(0xFFFFFF)
      self.tft.font(self.tft.FONT_Ubuntu)
      self.fontwidth,self.fontheight=self.tft.fontSize()
      self.tft.clear()

    def clear_display(self):
      self.tft.clear()
      pass
    
    #tft.text(120-int(tft.textWidth(text)/2),67-int(tft.fontSize()[1]/2),text,0xFFFFFF)
    def print_message_to_tft(self):
      if "clear" in self.jsonobj:
        if self.jsonobj["clear"] == "True":
          self.tft.clear()
      for key, value in self.jsonobj.items():
        if isinstance(key, int):
          if 1 <= key <= self.maxlines:
            print("We got an integer which seems good")
            x_coord=(key-1)*self.fontheight
            self.tft.text(5,5+x_coord,value)
          else:
            print("Too high Line number")
        elif isinstance(key, str):
          if key == "center":
            self.tft.text(120-int(self.tft.textWidth(value)/2),67-int(self.tft.fontSize()[1]/2),value)
    
    def printjson_to_console(self):
      for key, value in self.jsonobj.items():
          print("Key:", key)
          print("Value:", str(value))
          
    def parse_json_message(self,jsonmessage):
        self.jsonobj=json.loads(jsonmessage)
        

    def tft_monitor_data(self):
      self.initialize_display()
      self.clear_display()
      while self.interrupt != True:
        try:
          ntf = _thread.getnotification()
          if ntf:
              if ntf == _thread.EXIT:
                  print("TH_FUNC: terminated")
                  return
              elif ntf == _thread.SUSPEND:
                  print("TH_FUNC: suspended")
                  while _thread.wait() != _thread.RESUME:
                      pass
              else:
                  pass
          ntf = _thread.wait(1000)
          typ, sender, msg = _thread.getmsg()
          if msg:
              _thread.sendmsg(sender, "[%s] Hi %s, received your message arrived to TFT class." % (_thread.getSelfName(), _thread.getThreadName(sender)))
              self.parse_json_message(msg)
              if "tft_command" in self.jsonobj:
                if self.jsonobj["tft_command"] == "message":
                  self.print_message_to_tft()
        except Exception as e:
          print("Exception in thread %s" % _thread.getSelfName())
          print(e)
          pass
        time.sleep_ms(self.refresh_time)
