from machine import Pin
import time
import _thread

class pinControl:
    def __init__(self):
        self.resetpin=15
        self.powerpin=22
        self.pinstatus = {}
        self.pindefault=Pin.INOUT
        self.pindefaultstate=Pin.PULL_UP
        self.pindefaultvalue=1
        self.resetBtnLength=1
        self.powerBtnLength=6
        self.interrupt=False
        self.refresh_time=10

    @classmethod
    def push_button(self, pin, seconds):
        if pin.value() == 1:
            pin.value(0)
            time.sleep(seconds)
            pin.value(1)
        else:
            pin.value(1)
            time.sleep(seconds)
            pin.value(0)

    def press_pin(self, pinName):
      if pinName == "resetpin":
        print("Pressing reset button for "+str(self.resetBtnLength)+" seconds.")

        self.push_button(self.resetPinInstance, self.resetBtnLength)
        self.set_pin(self.resetpin, self.resetPinInstance.value())
      elif pinName == "rebootpin":
        print("Pressing power button for "+str(self.powerBtnLength)+" seconds.")

        self.push_button(self.powerPinInstance, self.powerBtnLength)
        self.set_pin(self.powerpin, self.powerPinInstance.value())
      else:
        print("Unknown pin : "+pinName)
        pass
        
    def set_pin(self, pin, value):
        self.pinstatus[pin] = value

    def initialize_pins(self):
        self.resetPinInstance=Pin(self.resetpin, self.pindefault, self.pindefaultstate, value=self.pindefaultvalue)
        self.powerPinInstance=Pin(self.powerpin, self.pindefault, self.pindefaultstate, value=self.pindefaultvalue)

    def Convert(self,string):
      self.li = list(string.split(","))
      return self.li
      
    def startPinThread(self):
        print("TH_FUNC: started")
        _thread.allowsuspend(True)
        self.initialize_pins()
        while True:
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
                  # Reply to sender, we can analyze the message first
                  _thread.sendmsg(sender, "[%s] Hi %s, received your message." % (_thread.getSelfName(), _thread.getThreadName(sender)))
                  if type(self.Convert(msg)[0] == str):
                    if self.Convert(msg)[0] == "pressReset":
                      self.press_pin("resetpin")
                    elif self.Convert(msg)[0] == "pressPower":
                      self.press_pin("rebootpin")
            except Exception as e:
              print("Exception occured in startPinThread() ")
              print(e)
              pass