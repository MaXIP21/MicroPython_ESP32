from machine import Pin
import time
import json
import _thread

class pin_Control:
    def __init__(self):
        self.resetpin=15
        self.powerpin=22
        self.pinstatus = {}
        self.pindefault=Pin.INOUT
        self.pindefaultstate=Pin.PULL_UP
        self.pindefaultvalue=1
        self.defaultBtnPressLength=1
        self.powerBtnLength=1
        self.interrupt=False
        self.refresh_time=10

    @classmethod
    def push_button(self, pin, seconds):
        if pin.value() == 1:
            pin.value(0)
            time.sleep(int(seconds))
            pin.value(1)
        else:
            pin.value(1)
            time.sleep(int(seconds))
            pin.value(0)

    def press_pin(self, pinName, time=-1):
      if time == -1:
        time = self.defaultBtnPressLength
      if pinName == "resetpin":
        print("Pressing reset button for "+str(time)+" seconds.")
        self.push_button(self.resetPinInstance, time)
        self.set_pin(self.resetpin, self.resetPinInstance.value())
        print("Pressing reset button for "+str(time)+" seconds completed.")
      elif pinName == "rebootpin":
        print("Pressing power button for "+str(time)+" seconds.")
        self.push_button(self.powerPinInstance, time)
        self.set_pin(self.powerpin, self.powerPinInstance.value())
        print("Pressing power button for "+str(time)+" seconds completed.")
      else:
        print("Unknown pin : "+pinName)
        pass
        
    def set_pin(self, pin, value):
        self.pinstatus[pin] = value

    def initialize_pins(self):
        self.resetPinInstance=Pin(self.resetpin, self.pindefault, self.pindefaultstate, value=self.pindefaultvalue)
        self.powerPinInstance=Pin(self.powerpin, self.pindefault, self.pindefaultstate, value=self.pindefaultvalue)

    def parse_json_message(self,jsonmessage):
        self.jsonobj=json.loads(jsonmessage)
        
    def startPinThread(self):
        #print("TH_FUNC: started")
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
                  #_thread.sendmsg(sender, "[%s] Hi %s, received your message." % (_thread.getSelfName(), _thread.getThreadName(sender)))
                  self.parse_json_message(msg)
                  if "command" in self.jsonobj:
                    if self.jsonobj["command"] == "pressReset":
                      self.press_pin("resetpin")
                    elif self.jsonobj["command"] == "pressPower":
                      if "seconds" in self.jsonobj.keys():
                        self.press_pin("rebootpin", self.jsonobj["seconds"])
                      else:
                        self.press_pin("rebootpin")
                    else:
                      pass
            except Exception as e:
              print("Exception occured in startPinThread() ")
              print(e)
              pass